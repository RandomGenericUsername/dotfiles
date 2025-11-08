#!/usr/bin/env python3
"""Rebuild the wallust container with updated colorscheme-generator module."""

import sys
from pathlib import Path

# Add modules to path
repo_root = Path(__file__).parent
sys.path.insert(
    0, str(repo_root / "src/common/tools/colorscheme-orchestrator/src")
)
sys.path.insert(0, str(repo_root / "src/common/modules/container-manager/src"))

from colorscheme_orchestrator.containers.builder import ContainerBuilder
from colorscheme_orchestrator.containers.registry import BackendRegistry
from dotfiles_container_manager import DockerEngine


def main():
    """Rebuild wallust container."""
    # Setup paths
    containers_dir = (
        repo_root / "src/common/tools/colorscheme-orchestrator/containers"
    )
    colorscheme_generator_path = (
        repo_root / "src/common/modules/colorscheme-generator"
    )

    print("=" * 60)
    print("Rebuilding Wallust Container")
    print("=" * 60)
    print(f"Repository root: {repo_root}")
    print(f"Containers dir: {containers_dir}")
    print(f"Colorscheme generator: {colorscheme_generator_path}")
    print("=" * 60)
    print()

    # Create engine, registry and builder
    print("→ Initializing container engine...")
    engine = DockerEngine()
    print("✓ Container engine initialized")
    print()

    registry = BackendRegistry(containers_dir)
    builder = ContainerBuilder(engine, registry, colorscheme_generator_path)

    # Build wallust image
    try:
        print("Building wallust container image...")
        image_id = builder.build_backend_image(
            "wallust", rebuild=True, no_cache=False
        )
        print()
        print("=" * 60)
        print("✓ Wallust container rebuilt successfully!")
        print(f"  Image ID: {image_id}")
        print("=" * 60)
        return 0
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Failed to rebuild wallust container: {e}")
        print("=" * 60)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
