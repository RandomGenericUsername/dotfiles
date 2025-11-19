"""CLI entry point for the daemon."""

import asyncio
import sys
from pathlib import Path

from .config import DaemonConfig
from .daemon import DotfilesDaemon
from .logger import Logger


async def main() -> int:
    """Main entry point."""
    # Parse command line arguments
    socket_dir = None
    if len(sys.argv) > 1:
        socket_dir = Path(sys.argv[1])

    # Create config
    config = DaemonConfig()
    if socket_dir:
        config.socket_dir = socket_dir

    # Create logger
    logger = Logger(name="dotfiles-daemon", level="INFO")

    # Create and run daemon
    daemon = DotfilesDaemon(config=config, logger=logger)

    try:
        await daemon.run()
        return 0
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        return 0
    except Exception as e:
        logger.error(f"Daemon failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
