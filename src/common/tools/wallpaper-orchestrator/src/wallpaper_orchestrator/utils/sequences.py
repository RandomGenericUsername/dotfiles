"""Utility functions for sending terminal sequences to open terminals."""

import glob
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def send_sequences_to_terminals(sequences_file: Path) -> tuple[int, int]:
    """Send sequences file content to all open terminals.

    This mimics pywal's behavior of writing escape sequences directly
    to all open terminal devices, allowing instant color updates without
    requiring terminal restart or manual sourcing.

    Args:
        sequences_file: Path to the sequences file containing ANSI escape codes

    Returns:
        tuple[int, int]: (successful_count, failed_count)
    """
    if not sequences_file.exists():
        logger.warning(f"Sequences file not found: {sequences_file}")
        return 0, 0

    # Read sequences file content (binary)
    try:
        with open(sequences_file, "rb") as f:
            sequences = f.read()
    except Exception as e:
        logger.error(f"Failed to read sequences file: {e}")
        return 0, 0

    # Determine terminal device pattern based on OS
    if sys.platform == "darwin":
        # macOS
        tty_pattern = "/dev/ttys00[0-9]*"
    else:
        # Linux and other Unix-like systems
        tty_pattern = "/dev/pts/[0-9]*"

    # Find all open terminal devices
    terminals = glob.glob(tty_pattern)

    if not terminals:
        logger.debug("No open terminals found")
        return 0, 0

    successful = 0
    failed = 0

    # Write sequences to each terminal
    for term in terminals:
        try:
            with open(term, "wb") as f:
                f.write(sequences)
            successful += 1
            logger.debug(f"Sent sequences to {term}")
        except (PermissionError, OSError) as e:
            # Some terminals may not be accessible (different user, etc.)
            logger.debug(f"Failed to send sequences to {term}: {e}")
            failed += 1

    return successful, failed
