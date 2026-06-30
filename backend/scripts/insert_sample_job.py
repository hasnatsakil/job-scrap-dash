import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.services.database import db_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SAMPLE_DATA_PATH = Path(__file__).resolve().parents[1] / "sample_data" / "format_parser.json"


def load_sample_job() -> dict:
    if not SAMPLE_DATA_PATH.exists():
        logger.error(f"Sample data file not found: {SAMPLE_DATA_PATH}")
        sys.exit(1)
    with open(SAMPLE_DATA_PATH, "r") as f:
        return json.load(f)


def main():
    job = load_sample_job()

    if not db_client.verify_connection():
        logger.error("Could not connect to Supabase. Check your .env configuration.")
        sys.exit(1)

    logger.info(f"Inserting job: {job['title']} at {job['company']}")
    db_client.insert("jobs", [job])
    logger.info("Job inserted successfully.")


if __name__ == "__main__":
    main()
