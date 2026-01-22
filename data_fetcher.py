"""Module for fetching economic data from FRED API."""
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict

import pandas as pd
from fredapi import Fred

from config import FRED_API_KEY, FRED_SERIES, CACHE_DIR, CACHE_EXPIRY_HOURS


class FREDDataFetcher:
    """Fetches and caches economic data from FRED API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize FRED API client.

        Args:
            api_key: FRED API key. If None, will use FRED_API_KEY from config.
        """
        self.api_key = api_key or FRED_API_KEY
        if not self.api_key:
            raise ValueError(
                "FRED API key not found. Please set FRED_API_KEY in .env file. "
                "Get your free API key at: https://fred.stlouisfed.org/docs/api/api_key.html"
            )
        self.fred = Fred(api_key=self.api_key)
        self.cache_dir = Path(CACHE_DIR)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_path(self, series_id: str) -> Path:
        """Get cache file path for a series."""
        return self.cache_dir / f"{series_id}.pkl"

    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cached data is still valid."""
        if not cache_path.exists():
            return False

        cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        expiry_time = datetime.now() - timedelta(hours=CACHE_EXPIRY_HOURS)
        return cache_time > expiry_time

    def _load_from_cache(self, series_id: str) -> Optional[pd.Series]:
        """Load data from cache if valid."""
        cache_path = self._get_cache_path(series_id)
        if self._is_cache_valid(cache_path):
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        return None

    def _save_to_cache(self, series_id: str, data: pd.Series):
        """Save data to cache."""
        cache_path = self._get_cache_path(series_id)
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)

    def get_series(self, series_id: str, use_cache: bool = True) -> pd.Series:
        """Fetch a data series from FRED.

        Args:
            series_id: FRED series ID (e.g., 'UNRATE' for unemployment rate)
            use_cache: Whether to use cached data if available

        Returns:
            Pandas Series with the economic data
        """
        # Try to load from cache first
        if use_cache:
            cached_data = self._load_from_cache(series_id)
            if cached_data is not None:
                return cached_data

        # Fetch fresh data from FRED
        data = self.fred.get_series(series_id)

        # Save to cache
        self._save_to_cache(series_id, data)

        return data

    def get_unemployment_data(self, use_cache: bool = True) -> pd.Series:
        """Get unemployment rate data.

        Returns:
            Pandas Series with unemployment rate (%)
        """
        return self.get_series(FRED_SERIES["unemployment"], use_cache=use_cache)

    def get_gdp_data(self, use_cache: bool = True) -> pd.Series:
        """Get GDP data.

        Returns:
            Pandas Series with GDP (billions of dollars)
        """
        return self.get_series(FRED_SERIES["gdp"], use_cache=use_cache)

    def get_gdp_growth_data(self, use_cache: bool = True) -> pd.Series:
        """Get real GDP growth rate data.

        Returns:
            Pandas Series with GDP growth rate (%)
        """
        return self.get_series(FRED_SERIES["gdp_growth"], use_cache=use_cache)

    def get_all_data(self, use_cache: bool = True) -> Dict[str, pd.Series]:
        """Get all configured economic indicators.

        Returns:
            Dictionary mapping indicator names to their data series
        """
        return {
            "unemployment": self.get_unemployment_data(use_cache=use_cache),
            "gdp": self.get_gdp_data(use_cache=use_cache),
            "gdp_growth": self.get_gdp_growth_data(use_cache=use_cache),
        }

    def clear_cache(self):
        """Clear all cached data."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()

    def get_series_info(self, series_id: str) -> dict:
        """Get metadata about a FRED series.

        Args:
            series_id: FRED series ID

        Returns:
            Dictionary with series metadata
        """
        return self.fred.get_series_info(series_id)
