from pathlib import Path

install_dir_name: str = "dotfiles"
install_parent_path: Path = Path.home()

install_path: Path = install_parent_path / install_dir_name
log_directory: Path = Path.home() / "logs"
backup_directory: Path = Path.home() / "backup"
wallpapers_directory: Path = Path.home() / "wallpapers"
screenshots_directory: Path = Path.home() / "Pictures" / "Screenshots"
log_level: str = "error"
output_to_file: bool = False
