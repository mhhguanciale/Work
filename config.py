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
    # Credit Market Indicators
    # Credit Spreads
    "baa_spread": "BAA10Y",  # Moody's Baa Corporate Bond Spread over 10-Year Treasury
    "aaa_spread": "AAA10Y",  # Moody's Aaa Corporate Bond Spread over 10-Year Treasury
    "ig_spread": "BAMLC0A0CM",  # ICE BofA US Corporate Index Option-Adjusted Spread
    "hy_spread": "BAMLH0A0HYM2",  # ICE BofA US High Yield Index Option-Adjusted Spread
    "yield_curve_10y2y": "T10Y2Y",  # 10-Year minus 2-Year Treasury Yield Spread
    "yield_curve_10y3m": "T10Y3M",  # 10-Year minus 3-Month Treasury Yield Spread
    # Borrowing Rates
    "treasury_10y": "DGS10",  # 10-Year Treasury Constant Maturity Rate
    "personal_loan_rate": "TERMCBPER24NS",  # 24-Month Personal Loan Rate at Commercial Banks
    "auto_loan_rate": "TERMCBCCINTNS",  # 48-Month New Auto Loan Rate at Commercial Banks
    "credit_card_rate": "TERMCBCCALLNS",  # Credit Card Interest Rate (All Accounts)
    # Leverage & Debt Metrics
    "corporate_debt": "BCNSDODNS",  # Nonfinancial Corporate Business Debt Securities
    "household_debt": "HHDTSDODNS",  # Households and Nonprofit Organizations Debt
    "federal_debt_gdp": "GFDEGDQ188S",  # Federal Debt: Total Public Debt as Percent of GDP
    "total_credit_gap": "QUSCAM",  # Credit to Non-Financial Sector Gap (% of GDP)
    # Healthcare Indicators
    # Healthcare Spending
    "healthcare_pce": "HLTHSCPCHCSA",  # Personal Consumption Expenditures: Health Care (Billions)
    "healthcare_gdp_pct": "DHCERA3Q086SBEA",  # Health Care Expenditures as % of GDP
    # Healthcare Costs & Inflation
    "cpi_medical": "CPIMEDSL",  # CPI: Medical Care
    "cpi_hospital": "CPIHOSSL",  # CPI: Hospital Services
    "cpi_prescription": "CPIPRSLS",  # CPI: Prescription Drugs
    # Healthcare Employment & Wages
    "healthcare_employment": "USEHS",  # All Employees: Health Care and Social Assistance (Thousands)
    "healthcare_wages": "CES6562000003",  # Average Hourly Earnings: Health Care (Dollars per Hour)
    # Health Insurance Coverage
    "uninsured_number": "NILFR",  # Number of Persons Without Health Insurance (Millions)
}

# Data cache settings
CACHE_DIR = "data_cache"
CACHE_EXPIRY_HOURS = 24  # Refresh data every 24 hours

# Dashboard settings
DASHBOARD_TITLE = "FRED Economic Data Dashboard"
DEFAULT_YEARS_BACK = 10  # Default historical data range
