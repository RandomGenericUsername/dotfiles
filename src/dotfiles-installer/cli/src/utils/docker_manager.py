"""Docker management utilities for rendering templates and building images."""

import io
import subprocess
import tarfile
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template


class DockerError(Exception):
    """Base exception for Docker-related errors."""

    def __init__(
        self,
        message: str,
        command: str | None = None,
        exit_code: int | None = None,
    ):
        super().__init__(message)
        self.command = command
        self.exit_code = exit_code


class DockerTemplateRenderer:
    """Renders Dockerfile templates using Jinja2."""

    def __init__(self, template_dir: Path):
        """
        Initialize the template renderer.

        Args:
            template_dir: Directory containing Dockerfile templates
        """
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_dockerfile(
        self, template_name: str = "Dockerfile.j2", **kwargs: Any
    ) -> str:
        """
        Render a Dockerfile template with provided variables.

        Args:
            template_name: Name of the template file
            **kwargs: Template variables

        Returns:
            Rendered Dockerfile content as string

        Raises:
            DockerError: If template rendering fails
        """
        try:
            template: Template = self.env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            raise DockerError(
                f"Failed to render template {template_name}: {e}"
            ) from e

    def get_available_templates(self) -> list[str]:
        """
        Get list of available Dockerfile templates.

        Returns:
            List of template filenames
        """
        return [
            f.name
            for f in self.template_dir.iterdir()
            if f.is_file() and f.name.endswith((".j2", ".jinja2"))
        ]


class DockerImageBuilder:
    """Builds Docker images from rendered templates without writing files."""

    def __init__(self, docker_command: str = "docker"):
        """
        Initialize the Docker image builder.

        Args:
            docker_command: Docker command to use (default: 'docker')
        """
        self.docker_command = docker_command

    def _run_docker_command(
        self,
        command: list[str],
        input_data: bytes | None = None,
        timeout: int = 300,
    ) -> subprocess.CompletedProcess:
        """
        Run a Docker command with proper error handling.

        Args:
            command: Docker command and arguments
            input_data: Optional input data to pipe to command
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess result

        Raises:
            DockerError: If command fails
        """
        try:
            result = subprocess.run(
                command,
                input=input_data,
                capture_output=True,
                text=False,  # Use bytes for binary data
                check=True,
                timeout=timeout,
            )
            return result
        except subprocess.TimeoutExpired as e:
            cmd_str = " ".join(command)
            raise DockerError(
                f"Docker command timed out after {timeout}s: {cmd_str}",
                command=cmd_str,
            ) from e
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else "Unknown error"
            raise DockerError(
                f"Docker command failed: {error_msg}",
                command=" ".join(command),
                exit_code=e.returncode,
            ) from e
        except FileNotFoundError as e:
            raise DockerError(
                f"Docker executable not found: {self.docker_command}",
                command=" ".join(command),
            ) from e

    def _create_build_context_tar(
        self,
        dockerfile_content: str,
        context_files: dict[str, bytes] | None = None,
    ) -> bytes:
        """
        Create a tar archive for Docker build context.

        Args:
            dockerfile_content: Content of the Dockerfile
            context_files: Optional dict of filename -> file content

        Returns:
            Tar archive as bytes
        """
        tar_buffer = io.BytesIO()

        with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
            # Add Dockerfile
            dockerfile_info = tarfile.TarInfo(name="Dockerfile")
            dockerfile_bytes = dockerfile_content.encode("utf-8")
            dockerfile_info.size = len(dockerfile_bytes)
            tar.addfile(dockerfile_info, io.BytesIO(dockerfile_bytes))

            # Add additional context files
            if context_files:
                for filename, content in context_files.items():
                    file_info = tarfile.TarInfo(name=filename)
                    if isinstance(content, str):
                        content = content.encode("utf-8")
                    file_info.size = len(content)
                    tar.addfile(file_info, io.BytesIO(content))

        tar_buffer.seek(0)
        return tar_buffer.read()

    def build_image(
        self,
        dockerfile_content: str,
        image_name: str,
        context_files: dict[str, bytes] | None = None,
        build_args: dict[str, str] | None = None,
        timeout: int = 600,
    ) -> str:
        """
        Build a Docker image from Dockerfile content without writing files.

        Args:
            dockerfile_content: Content of the Dockerfile
            image_name: Name/tag for the built image
            context_files: Optional dict of filename -> file content for
                build context
            build_args: Optional build arguments
            timeout: Build timeout in seconds

        Returns:
            Image ID of the built image

        Raises:
            DockerError: If build fails
        """
        # Create build context tar
        build_context = self._create_build_context_tar(
            dockerfile_content, context_files
        )

        # Prepare Docker build command
        command = [self.docker_command, "build", "-t", image_name, "-"]

        # Add build arguments
        if build_args:
            for key, value in build_args.items():
                command.extend(["--build-arg", f"{key}={value}"])

        # Run build command
        result = self._run_docker_command(
            command, input_data=build_context, timeout=timeout
        )

        # Extract image ID from output
        output = result.stdout.decode()
        for line in output.split("\n"):
            if "Successfully built" in line:
                return line.split()[-1]

        # Fallback: try to get image ID by name
        return self._get_image_id(image_name)

    def _get_image_id(self, image_name: str) -> str:
        """
        Get image ID by image name.

        Args:
            image_name: Name/tag of the image

        Returns:
            Image ID

        Raises:
            DockerError: If image not found
        """
        command = [
            self.docker_command,
            "images",
            "--format",
            "{{.ID}}",
            image_name,
        ]
        result = self._run_docker_command(command)
        image_id = result.stdout.decode().strip()

        if not image_id:
            raise DockerError(f"Image {image_name} not found after build")

        return image_id

    def image_exists(self, image_name: str) -> bool:
        """
        Check if a Docker image exists.

        Args:
            image_name: Name/tag of the image

        Returns:
            True if image exists, False otherwise
        """
        try:
            self._get_image_id(image_name)
            return True
        except DockerError:
            return False


def render_and_build_docker_image(
    template_dir: Path,
    image_name: str,
    template_name: str = "Dockerfile.j2",
    template_vars: dict[str, Any] | None = None,
    context_files: dict[str, bytes] | None = None,
    build_args: dict[str, str] | None = None,
    timeout: int = 600,
) -> str:
    """
    Convenience function to render template and build Docker image.

    Args:
        template_dir: Directory containing Dockerfile templates
        image_name: Name/tag for the built image
        template_name: Name of the template file
        template_vars: Variables for template rendering
        context_files: Optional files to include in build context
        build_args: Optional Docker build arguments
        timeout: Build timeout in seconds

    Returns:
        Image ID of the built image

    Raises:
        DockerError: If rendering or building fails
    """
    # Render template
    renderer = DockerTemplateRenderer(template_dir)
    dockerfile_content = renderer.render_dockerfile(
        template_name, **(template_vars or {})
    )

    # Build image
    builder = DockerImageBuilder()
    return builder.build_image(
        dockerfile_content=dockerfile_content,
        image_name=image_name,
        context_files=context_files,
        build_args=build_args,
        timeout=timeout,
    )
