#!/usr/bin/env python3
"""Script to manually update FRED data cache.

This script can be run manually or scheduled via cron/GitHub Actions
to refresh the data cache daily.
"""
import sys
from datetime import datetime

from data_fetcher import FREDDataFetcher
from config import FRED_SERIES


def main():
    """Update all FRED data series."""
    print(f"Starting data update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    try:
        # Initialize fetcher
        fetcher = FREDDataFetcher()
        print("✓ FRED API client initialized")

        # Clear existing cache
        fetcher.clear_cache()
        print("✓ Cache cleared")

        # Fetch fresh data for all series
        print("\nFetching data from FRED:")
        for name, series_id in FRED_SERIES.items():
            print(f"  - {name.upper()} ({series_id})...", end=" ")
            data = fetcher.get_series(series_id, use_cache=False)
            print(f"✓ ({len(data)} data points)")

            # Display latest value
            if len(data) > 0:
                latest = data.iloc[-1]
                latest_date = data.index[-1]
                print(f"    Latest: {latest:.2f} (as of {latest_date.strftime('%Y-%m-%d')})")

        print("-" * 60)
        print(f"✓ Data update completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return 0

    except ValueError as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        print("\nPlease ensure your FRED API key is set in the .env file.")
        print("Get your free API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        return 1

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
