"""Configuration for FRED Economic Data Dashboard."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FRED API Configuration
FRED_API_KEY = os.getenv("FRED_API_KEY")

# FRED Series IDs for economic indicators
FRED_SERIES = {
    "unemployment": "UNRATE",  # Unemployment Rate
    "gdp": "GDP",              # Gross Domestic Product
    "gdp_growth": "A191RL1Q225SBEA",  # Real GDP Growth Rate
}

# Data cache settings
CACHE_DIR = "data_cache"
CACHE_EXPIRY_HOURS = 24  # Refresh data every 24 hours

# Dashboard settings
DASHBOARD_TITLE = "FRED Economic Data Dashboard"
DEFAULT_YEARS_BACK = 10  # Default historical data range
