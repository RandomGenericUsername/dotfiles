#!/usr/bin/env python3
"""Rebuild colorscheme backend container images.

This script rebuilds container images for colorscheme backends
(pywal, wallust, etc.) with the latest version of the
colorscheme-generator module.

Usage:
    python scripts/rebuild_backend.py wallust
    python scripts/rebuild_backend.py pywal
    python scripts/rebuild_backend.py --all
    python scripts/rebuild_backend.py wallust --no-cache
"""

import argparse
import sys
from pathlib import Path

# Add modules to path
# This script is in: colorscheme-orchestrator/scripts/
# We need to go up to repo root
tool_root = Path(__file__).parent.parent
repo_root = tool_root.parent.parent.parent

sys.path.insert(0, str(tool_root / "src"))
sys.path.insert(0, str(repo_root / "src/common/modules/container-manager/src"))

# ruff: noqa: E402
from dotfiles_container_manager import DockerEngine

from colorscheme_orchestrator.containers.builder import ContainerBuilder
from colorscheme_orchestrator.containers.registry import BackendRegistry


def rebuild_backend(
    backend: str, no_cache: bool = False, verbose: bool = False
) -> bool:
    """Rebuild a specific backend container.

    Args:
        backend: Backend name (pywal, wallust, custom)
        no_cache: Force clean rebuild without cache
        verbose: Enable verbose output

    Returns:
        True if successful, False otherwise
    """
    # Setup paths
    containers_dir = tool_root / "containers"
    colorscheme_generator_path = (
        repo_root / "src/common/modules/colorscheme-generator"
    )

    if verbose:
        print("=" * 60)
        print(f"Rebuilding {backend.upper()} Container")
        print("=" * 60)
        print(f"Tool root: {tool_root}")
        print(f"Repository root: {repo_root}")
        print(f"Containers dir: {containers_dir}")
        print(f"Colorscheme generator: {colorscheme_generator_path}")
        print("=" * 60)
        print()

    # Create engine, registry and builder
    if verbose:
        print("→ Initializing container engine...")

    try:
        engine = DockerEngine()
        if verbose:
            print("✓ Container engine initialized")
            print()
    except Exception as e:
        print(f"✗ Failed to initialize container engine: {e}")
        return False

    registry = BackendRegistry(containers_dir)
    builder = ContainerBuilder(engine, registry, colorscheme_generator_path)

    # Verify backend exists
    available_backends = registry.list_backends()
    if backend not in available_backends:
        print(f"✗ Unknown backend: {backend}")
        print(f"  Available backends: {', '.join(available_backends)}")
        return False

    # Build backend image
    try:
        if verbose:
            print(f"Building {backend} container image...")
        else:
            print(f"→ Building {backend} container...")

        image_id = builder.build_backend_image(
            backend, rebuild=True, no_cache=no_cache
        )

        print()
        print("=" * 60)
        print(f"✓ {backend.upper()} container rebuilt successfully!")
        print(f"  Image ID: {image_id}")
        print("=" * 60)
        return True

    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Failed to rebuild {backend} container: {e}")
        print("=" * 60)

        if verbose:
            import traceback

            traceback.print_exc()

        return False


def rebuild_all_backends(
    no_cache: bool = False, verbose: bool = False
) -> bool:
    """Rebuild all backend containers.

    Args:
        no_cache: Force clean rebuild without cache
        verbose: Enable verbose output

    Returns:
        True if all successful, False if any failed
    """
    containers_dir = tool_root / "containers"
    registry = BackendRegistry(containers_dir)
    backends = registry.list_backends()

    print("=" * 60)
    print("Rebuilding All Backend Containers")
    print("=" * 60)
    print(f"Backends to rebuild: {', '.join(backends)}")
    print("=" * 60)
    print()

    results = {}
    for backend in backends:
        success = rebuild_backend(backend, no_cache=no_cache, verbose=verbose)
        results[backend] = success
        print()  # Spacing between backends

    # Summary
    print("=" * 60)
    print("Rebuild Summary")
    print("=" * 60)

    for backend, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {backend}")

    print("=" * 60)

    all_success = all(results.values())
    if all_success:
        print("✅ All backends rebuilt successfully!")
    else:
        failed = [b for b, s in results.items() if not s]
        print(f"❌ Failed to rebuild: {', '.join(failed)}")

    return all_success


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Rebuild colorscheme backend container images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s wallust              Rebuild wallust container
  %(prog)s pywal                Rebuild pywal container
  %(prog)s --all                Rebuild all backend containers
  %(prog)s wallust --no-cache   Force clean rebuild without cache
  %(prog)s --all --verbose      Rebuild all with verbose output
        """,
    )

    parser.add_argument(
        "backend",
        nargs="?",
        help="Backend to rebuild (pywal, wallust, custom)",
    )

    parser.add_argument(
        "--all", action="store_true", help="Rebuild all backends"
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Force clean rebuild without using cache",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Validate arguments
    if args.all and args.backend:
        parser.error("Cannot specify both --all and a specific backend")

    if not args.all and not args.backend:
        parser.error("Must specify either a backend or --all")

    # Execute
    try:
        if args.all:
            success = rebuild_all_backends(
                no_cache=args.no_cache, verbose=args.verbose
            )
        else:
            success = rebuild_backend(
                args.backend, no_cache=args.no_cache, verbose=args.verbose
            )

        return 0 if success else 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
