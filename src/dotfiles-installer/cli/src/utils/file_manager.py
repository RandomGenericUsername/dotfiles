import hashlib
import shutil
from pathlib import Path


def is_directory_empty(directory_path: Path) -> bool:
    """
    Check if a directory is empty (contains no files or subdirectories).

    Args:
        directory_path: Path to the directory to check

    Returns:
        True if directory is empty, False otherwise

    Raises:
        FileNotFoundError: If directory doesn't exist
        NotADirectoryError: If path is not a directory
    """
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory {directory_path} does not exist")

    if not directory_path.is_dir():
        raise NotADirectoryError(f"Path {directory_path} is not a directory")

    try:
        # Using next() with iter() is more efficient than list() for large dirs
        next(directory_path.iterdir())
        return False
    except StopIteration:
        return True


def has_any_contents(
    directory_path: Path, ignore_hidden: bool = False
) -> bool:
    """
    Check if a directory has any contents, optionally ignoring hidden files.

    Args:
        directory_path: Path to the directory to check
        ignore_hidden: If True, ignore files/directories starting with '.'

    Returns:
        True if directory has contents, False if empty

    Raises:
        FileNotFoundError: If directory doesn't exist
        NotADirectoryError: If path is not a directory
    """
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory {directory_path} does not exist")

    if not directory_path.is_dir():
        raise NotADirectoryError(f"Path {directory_path} is not a directory")

    try:
        for item in directory_path.iterdir():
            if ignore_hidden and item.name.startswith("."):
                continue
            return True
        return False
    except PermissionError:
        # If we can't read the directory, assume it has contents
        return True


def count_directory_contents(
    directory_path: Path,
    ignore_patterns: set[str] | None = None,
    ignore_extensions: set[str] | None = None,
) -> dict:
    """
    Count files and directories in a directory with optional filtering.

    Args:
        directory_path: Path to the directory to analyze
        ignore_patterns: Set of filename patterns to ignore
            (e.g., {'.git', '__pycache__'})
        ignore_extensions: Set of file extensions to ignore
            (e.g., {'.pyc', '.tmp'})

    Returns:
        Dictionary with counts:
            {'files': int, 'directories': int, 'total': int}

    Raises:
        FileNotFoundError: If directory doesn't exist
        NotADirectoryError: If path is not a directory
    """
    if not directory_path.exists():
        raise FileNotFoundError(f"Directory {directory_path} does not exist")

    if not directory_path.is_dir():
        raise NotADirectoryError(f"Path {directory_path} is not a directory")

    ignore_patterns = ignore_patterns or set()
    ignore_extensions = ignore_extensions or set()

    files_count = 0
    dirs_count = 0

    try:
        for item in directory_path.iterdir():
            # Skip if matches ignore patterns
            if item.name in ignore_patterns:
                continue

            # Skip if matches ignore extensions
            if item.is_file() and item.suffix.lower() in ignore_extensions:
                continue

            if item.is_file():
                files_count += 1
            elif item.is_dir():
                dirs_count += 1

    except PermissionError:
        # If we can't read the directory, return unknown counts
        return {"files": -1, "directories": -1, "total": -1}

    return {
        "files": files_count,
        "directories": dirs_count,
        "total": files_count + dirs_count,
    }


def copy_directory(src_path: Path, dest_path: Path) -> None:
    if not src_path.exists():
        raise FileNotFoundError(f"Source directory {src_path} does not exist")

    if not src_path.is_dir():
        raise NotADirectoryError(f"Source path {src_path} is not a directory")

    if src_path == dest_path:
        raise ValueError("Source and destination paths must be different")

    try:
        shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied while copying from {src_path} to "
            f"{dest_path}: {e}"
        ) from e
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Source or destination path not found: {e}"
        ) from e
    except FileExistsError as e:
        raise FileExistsError(
            f"Destination {dest_path} already exists: {e}"
        ) from e
    except shutil.Error as e:
        # This contains multiple errors from the copy operation
        error_details = "; ".join(str(error) for error in e.args[0])
        raise RuntimeError(
            f"Multiple errors occurred while copying {src_path} to "
            f"{dest_path}: {error_details}"
        ) from e
    except OSError as e:
        # Catch other OS-level errors (disk full, invalid paths, etc.)
        raise OSError(
            f"OS error while copying {src_path} to {dest_path}: {e}"
        ) from e


def copy_file(src_path: Path, dest_path: Path) -> None:
    """
    Copy a file from source to destination.

    Args:
        src_path: Source file path
        dest_path: Destination file path

    Raises:
        FileNotFoundError: If source file doesn't exist
        NotADirectoryError: If source path is not a file
        ValueError: If source and destination are the same
        PermissionError: If permission denied during copy
        OSError: For other OS-level errors
    """
    if not src_path.exists():
        raise FileNotFoundError(f"Source file {src_path} does not exist")

    if not src_path.is_file():
        raise ValueError(f"Source path {src_path} is not a file")

    if src_path == dest_path:
        raise ValueError("Source and destination paths must be different")

    # Ensure destination directory exists
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.copy2(src_path, dest_path)
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied while copying from {src_path} to "
            f"{dest_path}: {e}"
        ) from e
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Source or destination path not found: {e}"
        ) from e
    except OSError as e:
        raise OSError(
            f"OS error while copying {src_path} to {dest_path}: {e}"
        ) from e


def is_safe_to_delete(directory_path: Path) -> tuple[bool, str]:
    """
    Validate if a directory is safe to delete using configuration-based checks.

    Args:
        directory_path: Path to the directory to validate

    Returns:
        Tuple of (is_safe: bool, reason: str)
        - is_safe: True if safe to delete, False otherwise
        - reason: Explanation of why it's safe or unsafe
    """
    from src.config.settings import Settings

    # Get safety configuration
    settings = Settings.get()
    safety_config = settings.project.settings.safety.directory_deletion

    # Convert to absolute path for consistent checking
    abs_path = directory_path.resolve()
    path_str = str(abs_path)

    # Get configuration values
    protected_dirs = set(safety_config.protected_directories)

    # Check absolute blacklist
    if path_str in protected_dirs:
        return False, f"Directory '{path_str}' is a protected system directory"

    # Check if it's a direct user home directory (if enabled)
    if (
        safety_config.protect_user_homes
        and (path_str.startswith("/home/") or path_str.startswith("/Users/"))
        and len(abs_path.parts) == 3
    ):
        return False, f"Directory '{path_str}' is a user home directory"

    # Require minimum depth
    min_depth = safety_config.minimum_path_depth
    if len(abs_path.parts) < min_depth:
        return (
            False,
            f"Directory '{path_str}' is too close to root "
            f"(minimum {min_depth} levels required)",
        )

    # Check for dangerous keywords in path (only for shallow paths)
    keyword_threshold = safety_config.keyword_check_depth_threshold
    if len(abs_path.parts) < keyword_threshold:
        dangerous_keywords = set(safety_config.dangerous_keywords)
        path_lower = path_str.lower()
        for keyword in dangerous_keywords:
            if keyword in path_lower:
                return (
                    False,
                    f"Directory path contains dangerous keyword '{keyword}' "
                    f"(depth {len(abs_path.parts)} < {keyword_threshold})",
                )

    # Check if target is a parent of any protected directory
    for protected in protected_dirs:
        protected_path = Path(protected).resolve()
        try:
            # Check if protected path is a subdirectory of target path
            protected_path.relative_to(abs_path)
            return (
                False,
                f"Directory '{path_str}' is a parent of protected "
                f"directory '{protected}'",
            )
        except ValueError:
            # protected_path is not a subdirectory of abs_path, which is good
            continue

    return True, f"Directory '{path_str}' is safe to delete"


def delete_directory_safe(directory_path: Path) -> None:
    """
    Safely delete a directory with comprehensive safety validation.

    Args:
        directory_path: Path to the directory to delete

    Raises:
        ValueError: If directory is not safe to delete
        PermissionError: If permission denied during deletion
        FileNotFoundError: If directory doesn't exist
        OSError: For other OS-level errors during deletion
    """
    # Validate safety first
    is_safe, reason = is_safe_to_delete(directory_path)
    if not is_safe:
        raise ValueError(f"Unsafe directory deletion blocked: {reason}")

    # Convert to absolute path
    abs_path = directory_path.resolve()

    # Check if directory exists
    if not abs_path.exists():
        raise FileNotFoundError(f"Directory {abs_path} does not exist")

    if not abs_path.is_dir():
        raise NotADirectoryError(f"Path {abs_path} is not a directory")

    try:
        # Perform the deletion
        shutil.rmtree(abs_path)
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied while deleting directory {abs_path}: {e}"
        ) from e
    except FileNotFoundError:
        # Directory was deleted by another process, which is fine
        pass
    except OSError as e:
        # Catch other OS-level errors (disk issues, file locks, etc.)
        raise OSError(
            f"OS error while deleting directory {abs_path}: {e}"
        ) from e


def copy_directory_filtered(
    src_path: Path,
    dest_path: Path,
    ignore_patterns: set[str] | None = None,
    ignore_extensions: set[str] | None = None,
    ignore_hidden: bool = False,
) -> None:
    """
    Copy directory with filtering capabilities.

    Args:
        src_path: Source directory path
        dest_path: Destination directory path
        ignore_patterns: Set of filename patterns to ignore
            (e.g., {'.git', '__pycache__', 'node_modules'})
        ignore_extensions: Set of file extensions to ignore
            (e.g., {'.pyc', '.tmp', '.log'})
        ignore_hidden: If True, ignore files/directories starting with '.'

    Raises:
        FileNotFoundError: If source directory doesn't exist
        NotADirectoryError: If source path is not a directory
        ValueError: If source and destination are the same
        PermissionError: If permission denied during copy
        OSError: For other OS-level errors
    """

    if not src_path.exists():
        raise FileNotFoundError(f"Source directory {src_path} does not exist")

    if not src_path.is_dir():
        raise NotADirectoryError(f"Source path {src_path} is not a directory")

    if src_path == dest_path:
        raise ValueError("Source and destination paths must be different")

    ignore_patterns = ignore_patterns or set()
    ignore_extensions = ignore_extensions or set()

    def should_ignore(path: Path) -> bool:
        """Check if a path should be ignored based on filtering rules."""
        # Check hidden files
        if ignore_hidden and path.name.startswith("."):
            return True

        # Check ignore patterns
        if path.name in ignore_patterns:
            return True

        # Check ignore extensions (for files only)
        return path.is_file() and path.suffix.lower() in ignore_extensions

    def ignore_function(directory: str, contents: list) -> list:
        """Function to pass to shutil.copytree for filtering."""
        ignored = []
        dir_path = Path(directory)

        for item in contents:
            item_path = dir_path / item
            if should_ignore(item_path):
                ignored.append(item)

        return ignored

    try:
        shutil.copytree(
            src_path, dest_path, dirs_exist_ok=True, ignore=ignore_function
        )
    except PermissionError as e:
        raise PermissionError(
            f"Permission denied while copying from {src_path} to "
            f"{dest_path}: {e}"
        ) from e
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Source or destination path not found: {e}"
        ) from e
    except FileExistsError as e:
        raise FileExistsError(
            f"Destination {dest_path} already exists: {e}"
        ) from e
    except shutil.Error as e:
        # This contains multiple errors from the copy operation
        error_details = "; ".join(str(error) for error in e.args[0])
        raise RuntimeError(
            f"Multiple errors occurred while copying {src_path} to "
            f"{dest_path}: {error_details}"
        ) from e
    except OSError as e:
        # Catch other OS-level errors (disk full, invalid paths, etc.)
        raise OSError(
            f"OS error while copying {src_path} to {dest_path}: {e}"
        ) from e


def get_file_hash(filepath: Path) -> str:
    """Calculate SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with filepath.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
