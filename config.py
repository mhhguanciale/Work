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
    # Housing Market Metrics
    "mortgage_rate": "MORTGAGE30US",  # 30-Year Fixed Rate Mortgage Average
    "median_home_price": "MSPUS",  # Median Sales Price of Houses Sold
    "home_price_index": "CSUSHPISA",  # S&P/Case-Shiller U.S. National Home Price Index
    "housing_starts": "HOUST",  # Housing Starts: Total New Privately Owned
    # Consumer Sentiment & Health Metrics
    "consumer_sentiment": "UMCSENT",  # University of Michigan Consumer Sentiment Index
    "initial_claims": "ICSA",  # Initial Claims (Unemployment Insurance Weekly Claims)
    "personal_saving_rate": "PSAVERT",  # Personal Saving Rate (%)
    "personal_consumption": "PCE",  # Personal Consumption Expenditures (Billions)
    "retail_sales": "RSXFS",  # Advance Retail Sales: Retail Trade (Millions)
    "consumer_credit": "TOTALSL",  # Total Consumer Credit Outstanding (Billions)
    "disposable_income": "DSPIC96",  # Real Disposable Personal Income (Billions, Chained 2017 $)
}

# Data cache settings
CACHE_DIR = "data_cache"
CACHE_EXPIRY_HOURS = 24  # Refresh data every 24 hours

# Dashboard settings
DASHBOARD_TITLE = "FRED Economic Data Dashboard"
DEFAULT_YEARS_BACK = 10  # Default historical data range
