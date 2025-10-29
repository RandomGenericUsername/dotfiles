"""Convenience orchestrator for common container + template workflows."""

from pathlib import Path
from typing import Any

from dotfiles_container_manager import (
    BuildContext,
    ContainerEngine,
    ContainerEngineFactory,
    ContainerRuntime,
    RunConfig,
)
from dotfiles_template_renderer import Jinja2Renderer, RenderConfig


def build_from_template(
    template_name: str,
    image_name: str,
    template_dir: Path | str,
    template_vars: dict[str, Any] | None = None,
    context_files: dict[str, bytes] | None = None,
    build_args: dict[str, str] | None = None,
    labels: dict[str, str] | None = None,
    runtime: ContainerRuntime = ContainerRuntime.DOCKER,
    timeout: int = 600,
    strict_mode: bool = True,
) -> str:
    """
    Convenience function to render a template and build a container image.

    This combines template rendering and image building in one call.

    Args:
        template_name: Name of the template file
        image_name: Name/tag for the built image
        template_dir: Directory containing templates
        template_vars: Variables for template rendering
        context_files: Additional files to include in build context
        build_args: Build arguments for container build
        labels: Labels to apply to the image
        runtime: Container runtime to use
        timeout: Build timeout in seconds
        strict_mode: Fail if template variables are missing

    Returns:
        Image ID of the built image

    Raises:
        TemplateError: If template rendering fails
        ImageBuildError: If image build fails

    Examples:
        >>> image_id = build_from_template(
        ...     template_name="python.j2",
        ...     image_name="myapp:latest",
        ...     template_dir="/path/to/templates",
        ...     template_vars={"base_image": "python:3.12"},
        ...     context_files={"app.py": b"print('hello')"},
        ... )
    """
    # Step 1: Render template
    renderer = Jinja2Renderer(
        template_dir,
        config=RenderConfig(strict_mode=strict_mode),
    )
    dockerfile = renderer.render(template_name, template_vars)

    # Step 2: Build image
    engine = ContainerEngineFactory.create(runtime)
    context = BuildContext(
        dockerfile=dockerfile,
        files=context_files or {},
        build_args=build_args or {},
        labels=labels or {},
    )

    image_id = engine.images.build(context, image_name, timeout=timeout)

    return image_id


def render_and_run(
    template_name: str,
    image_name: str,
    template_dir: Path | str,
    template_vars: dict[str, Any] | None = None,
    context_files: dict[str, bytes] | None = None,
    run_config: RunConfig | None = None,
    runtime: ContainerRuntime = ContainerRuntime.DOCKER,
    build_timeout: int = 600,
    strict_mode: bool = True,
) -> tuple[str, str]:
    """
    Render template, build image, and run container in one call.

    Args:
        template_name: Name of the template file
        image_name: Name/tag for the built image
        template_dir: Directory containing templates
        template_vars: Variables for template rendering
        context_files: Additional files to include in build context
        run_config: Container run configuration (if None, uses defaults)
        runtime: Container runtime to use
        build_timeout: Build timeout in seconds
        strict_mode: Fail if template variables are missing

    Returns:
        Tuple of (image_id, container_id)

    Raises:
        TemplateError: If template rendering fails
        ImageBuildError: If image build fails
        ContainerRuntimeError: If container fails to start

    Examples:
        >>> image_id, container_id = render_and_run(
        ...     template_name="python.j2",
        ...     image_name="myapp:latest",
        ...     template_dir="/path/to/templates",
        ...     template_vars={"base_image": "python:3.12"},
        ...     run_config=RunConfig(
        ...         image="myapp:latest",
        ...         name="myapp-container",
        ...         detach=True,
        ...     ),
        ... )
    """
    # Build image
    image_id = build_from_template(
        template_name=template_name,
        image_name=image_name,
        template_dir=template_dir,
        template_vars=template_vars,
        context_files=context_files,
        runtime=runtime,
        timeout=build_timeout,
        strict_mode=strict_mode,
    )

    # Run container
    engine = ContainerEngineFactory.create(runtime)

    if run_config is None:
        run_config = RunConfig(image=image_name)
    elif run_config.image != image_name:
        # Update image in run_config if different
        run_config.image = image_name

    container_id = engine.containers.run(run_config)

    return (image_id, container_id)


def get_engine(
    runtime: ContainerRuntime = ContainerRuntime.DOCKER,
) -> ContainerEngine:
    """
    Get a container engine instance.

    Convenience function for getting a configured engine.

    Args:
        runtime: Container runtime to use

    Returns:
        ContainerEngine instance

    Examples:
        >>> engine = get_engine(ContainerRuntime.DOCKER)
        >>> images = engine.images.list()
    """
    return ContainerEngineFactory.create(runtime)


def render_template(
    template_name: str,
    template_dir: Path | str,
    variables: dict[str, Any] | None = None,
    strict_mode: bool = True,
    **kwargs: Any,
) -> str:
    """
    Render a template.

    Convenience function for template rendering.

    Args:
        template_name: Name of the template file
        template_dir: Directory containing templates
        variables: Variables for template rendering
        strict_mode: Fail if template variables are missing
        **kwargs: Additional variables (merged with variables dict)

    Returns:
        Rendered template as string

    Examples:
        >>> dockerfile = render_template(
        ...     template_name="python.j2",
        ...     template_dir="/path/to/templates",
        ...     variables={"base_image": "python:3.12"},
        ... )
    """
    renderer = Jinja2Renderer(
        template_dir,
        config=RenderConfig(strict_mode=strict_mode),
    )
    return renderer.render(template_name, variables, **kwargs)
