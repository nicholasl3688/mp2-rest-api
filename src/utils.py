import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def setup_logging(verbose=False):
# configure looping for te pipeline
    if verbose==False:
        logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S"
        )
    else:
        logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S"
        )

def validate_input(filepath):
    # """Check whether the input path exists and is a file."""
    p = Path(filepath)
    if not p.is_file():
        logger.error(f"Input file not found: {filepath}")
        return False
    else:
        logger.info(f"Input file validated: {filepath}")
        return True