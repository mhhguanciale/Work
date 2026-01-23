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

    def get_mortgage_rate_data(self, use_cache: bool = True) -> pd.Series:
        """Get 30-year fixed mortgage rate data.

        Returns:
            Pandas Series with mortgage rate (%)
        """
        return self.get_series(FRED_SERIES["mortgage_rate"], use_cache=use_cache)

    def get_median_home_price_data(self, use_cache: bool = True) -> pd.Series:
        """Get median sales price of houses sold data.

        Returns:
            Pandas Series with median home price (dollars)
        """
        return self.get_series(FRED_SERIES["median_home_price"], use_cache=use_cache)

    def get_home_price_index_data(self, use_cache: bool = True) -> pd.Series:
        """Get Case-Shiller home price index data.

        Returns:
            Pandas Series with home price index
        """
        return self.get_series(FRED_SERIES["home_price_index"], use_cache=use_cache)

    def get_housing_starts_data(self, use_cache: bool = True) -> pd.Series:
        """Get housing starts data.

        Returns:
            Pandas Series with housing starts (thousands of units)
        """
        return self.get_series(FRED_SERIES["housing_starts"], use_cache=use_cache)

    def get_consumer_sentiment_data(self, use_cache: bool = True) -> pd.Series:
        """Get University of Michigan Consumer Sentiment Index data.

        Returns:
            Pandas Series with consumer sentiment index
        """
        return self.get_series(FRED_SERIES["consumer_sentiment"], use_cache=use_cache)

    def get_initial_claims_data(self, use_cache: bool = True) -> pd.Series:
        """Get initial unemployment insurance claims data.

        Returns:
            Pandas Series with initial claims (thousands)
        """
        return self.get_series(FRED_SERIES["initial_claims"], use_cache=use_cache)

    def get_personal_saving_rate_data(self, use_cache: bool = True) -> pd.Series:
        """Get personal saving rate data.

        Returns:
            Pandas Series with personal saving rate (%)
        """
        return self.get_series(FRED_SERIES["personal_saving_rate"], use_cache=use_cache)

    def get_personal_consumption_data(self, use_cache: bool = True) -> pd.Series:
        """Get personal consumption expenditures data.

        Returns:
            Pandas Series with PCE (billions of dollars)
        """
        return self.get_series(FRED_SERIES["personal_consumption"], use_cache=use_cache)

    def get_retail_sales_data(self, use_cache: bool = True) -> pd.Series:
        """Get advance retail sales data.

        Returns:
            Pandas Series with retail sales (millions of dollars)
        """
        return self.get_series(FRED_SERIES["retail_sales"], use_cache=use_cache)

    def get_consumer_credit_data(self, use_cache: bool = True) -> pd.Series:
        """Get total consumer credit outstanding data.

        Returns:
            Pandas Series with consumer credit (billions of dollars)
        """
        return self.get_series(FRED_SERIES["consumer_credit"], use_cache=use_cache)

    def get_disposable_income_data(self, use_cache: bool = True) -> pd.Series:
        """Get real disposable personal income data.

        Returns:
            Pandas Series with disposable income (billions of chained 2017 dollars)
        """
        return self.get_series(FRED_SERIES["disposable_income"], use_cache=use_cache)

    def get_all_data(self, use_cache: bool = True) -> Dict[str, pd.Series]:
        """Get all configured economic indicators.

        Returns:
            Dictionary mapping indicator names to their data series
        """
        return {
            "unemployment": self.get_unemployment_data(use_cache=use_cache),
            "gdp": self.get_gdp_data(use_cache=use_cache),
            "gdp_growth": self.get_gdp_growth_data(use_cache=use_cache),
            "mortgage_rate": self.get_mortgage_rate_data(use_cache=use_cache),
            "median_home_price": self.get_median_home_price_data(use_cache=use_cache),
            "home_price_index": self.get_home_price_index_data(use_cache=use_cache),
            "housing_starts": self.get_housing_starts_data(use_cache=use_cache),
            "consumer_sentiment": self.get_consumer_sentiment_data(use_cache=use_cache),
            "initial_claims": self.get_initial_claims_data(use_cache=use_cache),
            "personal_saving_rate": self.get_personal_saving_rate_data(use_cache=use_cache),
            "personal_consumption": self.get_personal_consumption_data(use_cache=use_cache),
            "retail_sales": self.get_retail_sales_data(use_cache=use_cache),
            "consumer_credit": self.get_consumer_credit_data(use_cache=use_cache),
            "disposable_income": self.get_disposable_income_data(use_cache=use_cache),
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
