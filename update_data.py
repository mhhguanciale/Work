#!/usr/bin/env python3
"""Script to manually update FRED data cache.

This script can be run manually or scheduled via cron/GitHub Actions
to refresh the data cache daily.
"""
import logging
import sys
from datetime import datetime

from data_fetcher import FREDDataFetcher
from config import FRED_SERIES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Update all FRED data series."""
    logger.info("Starting data update at %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    try:
        # Initialize fetcher
        fetcher = FREDDataFetcher()
        logger.info("FRED API client initialized")

        # Clear existing cache
        fetcher.clear_cache()
        logger.info("Cache cleared")

        # Fetch fresh data for all series
        logger.info("Fetching data from FRED:")
        failed = []
        for name, series_id in FRED_SERIES.items():
            data = fetcher.get_series(series_id, use_cache=False)
            if data is None:
                logger.error("FAILED: %s (%s)", name, series_id)
                failed.append(f"{name} ({series_id})")
                continue
            logger.info(
                "  %s (%s): %d data points, latest: %.2f (as of %s)",
                name, series_id, len(data),
                data.iloc[-1] if len(data) > 0 else 0,
                data.index[-1].strftime('%Y-%m-%d') if len(data) > 0 else "N/A",
            )

        if failed:
            logger.warning(
                "Data update finished with %d failures: %s",
                len(failed), ", ".join(failed),
            )
        else:
            logger.info("Data update completed successfully")
        return 1 if failed else 0

    except ValueError as e:
        logger.error("Configuration error: %s", e)
        logger.error("Please ensure your FRED API key is set in the .env file.")
        return 1

    except Exception:
        logger.exception("Unexpected error during data update")
        return 1


if __name__ == "__main__":
    sys.exit(main())
