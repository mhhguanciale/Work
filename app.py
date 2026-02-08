"""FRED Economic Data Dashboard - Streamlit Application."""
import logging
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from data_fetcher import FREDDataFetcher
from config import DASHBOARD_TITLE, DEFAULT_YEARS_BACK

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# Page configuration
st.set_page_config(
    page_title=DASHBOARD_TITLE,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_data_fetcher():
    """Initialize and cache the FRED data fetcher."""
    try:
        return FREDDataFetcher()
    except ValueError as e:
        st.error(str(e))
        st.stop()


@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data(use_cache=True):
    """Load all economic data."""
    fetcher = get_data_fetcher()
    return fetcher.get_all_data(use_cache=use_cache)


def filter_data_by_date(series: pd.Series, years_back: int) -> pd.Series:
    """Filter series to show only recent years."""
    cutoff_date = datetime.now() - timedelta(days=years_back * 365)
    return series[series.index >= cutoff_date]


def calculate_yoy_growth(series: pd.Series) -> pd.Series:
    """Calculate year-over-year percentage growth rate.

    Args:
        series: Time series data (levels)

    Returns:
        Series with YoY growth rates (%)
    """
    # Calculate percentage change from 12 months ago (or 4 quarters for quarterly data)
    # Detect frequency
    if len(series) < 2:
        return pd.Series(dtype=float)

    # Try to infer the frequency
    time_diff = (series.index[1] - series.index[0]).days

    if time_diff > 60:  # Quarterly data (roughly 90 days)
        periods = 4
    elif time_diff > 20:  # Monthly data
        periods = 12
    else:  # Weekly or daily data
        periods = 52

    # Calculate YoY growth
    yoy_growth = series.pct_change(periods=periods) * 100
    return yoy_growth


def create_level_with_growth_chart(
    series: pd.Series,
    title: str,
    level_yaxis_title: str,
    level_color: str,
    series_name: str = None
):
    """Create a dual-axis chart showing level data and its YoY growth trend.

    Args:
        series: Time series data (levels)
        title: Chart title
        level_yaxis_title: Y-axis title for level data
        level_color: Color for level data line
        series_name: Name for the series (defaults to title)
    """
    if series_name is None:
        series_name = title

    # Calculate YoY growth
    growth = calculate_yoy_growth(series)

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add level data trace
    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=series.values,
            name=f"{series_name} (Level)",
            line=dict(color=level_color, width=2.5),
            mode="lines",
        ),
        secondary_y=False,
    )

    # Add growth trend trace
    fig.add_trace(
        go.Scatter(
            x=growth.index,
            y=growth.values,
            name=f"{series_name} (YoY Growth %)",
            line=dict(color="#FFA15A", width=2, dash="dash"),
            mode="lines",
        ),
        secondary_y=True,
    )

    # Update layout
    fig.update_layout(
        title=title,
        hovermode="x unified",
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Set y-axes titles
    fig.update_yaxes(title_text=level_yaxis_title, secondary_y=False)
    fig.update_yaxes(title_text="YoY Growth (%)", secondary_y=True)

    return fig


def create_dual_axis_chart(unemployment: pd.Series, gdp: pd.Series, title: str):
    """Create a dual-axis chart for unemployment and GDP."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add unemployment trace
    fig.add_trace(
        go.Scatter(
            x=unemployment.index,
            y=unemployment.values,
            name="Unemployment Rate",
            line=dict(color="#EF553B", width=2),
            mode="lines",
        ),
        secondary_y=False,
    )

    # Add GDP trace
    fig.add_trace(
        go.Scatter(
            x=gdp.index,
            y=gdp.values,
            name="GDP",
            line=dict(color="#00CC96", width=2),
            mode="lines",
        ),
        secondary_y=True,
    )

    # Update layout
    fig.update_layout(
        title=title,
        hovermode="x unified",
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Set y-axes titles
    fig.update_yaxes(title_text="Unemployment Rate (%)", secondary_y=False)
    fig.update_yaxes(title_text="GDP (Billions of $)", secondary_y=True)

    return fig


def create_single_chart(series: pd.Series, title: str, yaxis_title: str, color: str):
    """Create a single-line chart."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=series.index,
            y=series.values,
            name=title,
            line=dict(color=color, width=2),
            mode="lines",
            fill="tozeroy",
            fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)",
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=yaxis_title,
        hovermode="x",
        height=400,
    )

    return fig


def create_multi_series_chart(
    series_dict: dict,
    title: str,
    yaxis_title: str,
    colors: list = None
):
    """Create a chart with multiple data series.

    Args:
        series_dict: Dictionary mapping series names to pd.Series objects
        title: Chart title
        yaxis_title: Y-axis title
        colors: Optional list of colors for each series
    """
    fig = go.Figure()

    default_colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA", "#FFA15A", "#19D3F3"]
    if colors is None:
        colors = default_colors

    for i, (name, series) in enumerate(series_dict.items()):
        color = colors[i % len(colors)]
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                name=name,
                line=dict(color=color, width=2),
                mode="lines",
            )
        )

    fig.update_layout(
        title=title,
        yaxis_title=yaxis_title,
        hovermode="x unified",
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig


def _render_metric(col, data, key, label, fmt_value, fmt_delta, delta_color="normal", caption_fmt="%B %Y"):
    """Render a single metric card if data is available."""
    if key not in data:
        with col:
            st.metric(label=label, value="N/A")
            st.caption("Data unavailable")
        return
    series = data[key]
    current_val = series.iloc[-1]
    prev_val = series.iloc[-2] if len(series) > 1 else current_val
    delta = current_val - prev_val
    with col:
        st.metric(
            label=label,
            value=fmt_value(current_val),
            delta=fmt_delta(delta, current_val, prev_val),
            delta_color=delta_color,
        )
        st.caption(f"As of {series.index[-1].strftime(caption_fmt)}")


def display_metric_cards(data: dict):
    """Display current values as metric cards."""
    col1, col2, col3 = st.columns(3)

    _render_metric(
        col1, data, "unemployment", "Current Unemployment Rate",
        lambda v: f"{v:.1f}%",
        lambda d, c, p: f"{d:.1f}%",
        delta_color="inverse",
    )
    _render_metric(
        col2, data, "gdp", "Current GDP",
        lambda v: f"${v:,.0f}B",
        lambda d, c, p: f"{(d / p * 100) if p != 0 else 0:+.1f}%",
    )
    _render_metric(
        col3, data, "gdp_growth", "Real GDP Growth Rate",
        lambda v: f"{v:.2f}%",
        lambda d, c, p: f"{d:.2f}%",
    )


def display_housing_metric_cards(data: dict):
    """Display housing market metrics as cards."""
    col1, col2, col3, col4 = st.columns(4)

    _render_metric(
        col1, data, "mortgage_rate", "30-Year Mortgage Rate",
        lambda v: f"{v:.2f}%",
        lambda d, c, p: f"{d:.2f}%",
        delta_color="inverse",
    )
    _render_metric(
        col2, data, "median_home_price", "Median Home Price",
        lambda v: f"${v:,.0f}",
        lambda d, c, p: f"{(d / p * 100) if p != 0 else 0:+.1f}%",
    )
    _render_metric(
        col3, data, "home_price_index", "Case-Shiller Index",
        lambda v: f"{v:.1f}",
        lambda d, c, p: f"{(d / p * 100) if p != 0 else 0:+.1f}%",
    )
    _render_metric(
        col4, data, "housing_starts", "Housing Starts",
        lambda v: f"{v:,.0f}K",
        lambda d, c, p: f"{(d / p * 100) if p != 0 else 0:+.1f}%",
    )


def display_consumer_metric_cards(data: dict):
    """Display consumer sentiment and health metrics as cards."""
    col1, col2, col3, col4 = st.columns(4)

    _render_metric(
        col1, data, "consumer_sentiment", "Consumer Sentiment",
        lambda v: f"{v:.1f}",
        lambda d, c, p: f"{d:.1f}",
    )
    _render_metric(
        col2, data, "personal_saving_rate", "Personal Saving Rate",
        lambda v: f"{v:.1f}%",
        lambda d, c, p: f"{d:.1f}%",
    )
    _render_metric(
        col3, data, "retail_sales", "Retail Sales",
        lambda v: f"${v:,.0f}M",
        lambda d, c, p: f"{(d / p * 100) if p != 0 else 0:+.1f}%",
    )
    _render_metric(
        col4, data, "initial_claims", "Initial Jobless Claims",
        lambda v: f"{v:,.0f}K",
        lambda d, c, p: f"{(d / p * 100) if p != 0 else 0:+.1f}%",
        delta_color="inverse",
    )


def display_credit_metric_cards(data: dict):
    """Display credit market metrics as cards."""
    col1, col2, col3, col4 = st.columns(4)

    _render_metric(
        col1, data, "hy_spread", "High Yield Spread",
        lambda v: f"{v:.2f}%",
        lambda d, c, p: f"{d:+.2f}%",
        delta_color="inverse",
    )
    _render_metric(
        col2, data, "baa_spread", "BBB Spread",
        lambda v: f"{v:.2f}%",
        lambda d, c, p: f"{d:+.2f}%",
        delta_color="inverse",
    )
    _render_metric(
        col3, data, "yield_curve_10y2y", "10Y-2Y Yield Curve",
        lambda v: f"{v:.2f}%",
        lambda d, c, p: f"{d:+.2f}%",
    )
    _render_metric(
        col4, data, "federal_debt_gdp", "Federal Debt/GDP",
        lambda v: f"{v:.1f}%",
        lambda d, c, p: f"{d:+.1f}%",
        delta_color="inverse",
    )


def display_healthcare_metric_cards(data: dict):
    """Display healthcare metrics as cards."""
    col1, col2, col3, col4 = st.columns(4)

    _render_metric(
        col1, data, "healthcare_gdp_pct", "Healthcare % of GDP",
        lambda v: f"{v:.1f}%",
        lambda d, c, p: f"{d:+.2f}%",
    )
    _render_metric(
        col2, data, "healthcare_pce", "Healthcare Spending",
        lambda v: f"${v:,.0f}B",
        lambda d, c, p: f"{(d / p * 100) if p != 0 else 0:+.1f}%",
    )
    _render_metric(
        col3, data, "healthcare_employment", "Healthcare Employment",
        lambda v: f"{v:,.0f}K",
        lambda d, c, p: f"{(d / p * 100) if p != 0 else 0:+.1f}%",
    )
    _render_metric(
        col4, data, "uninsured_pct", "Health Insurance Rate",
        lambda v: f"{v:.1f}%",
        lambda d, c, p: f"{d:+.1f}%",
    )


def main():
    """Main dashboard application."""
    # Header
    st.title(DASHBOARD_TITLE)
    st.markdown(
        "Real-time economic indicators from the Federal Reserve Economic Data (FRED) database. "
        "Data is cached and refreshes automatically every 24 hours."
    )

    # Sidebar
    with st.sidebar:
        st.header("Settings")

        # Time range selector
        years_back = st.slider(
            "Years of historical data",
            min_value=1,
            max_value=30,
            value=DEFAULT_YEARS_BACK,
            help="Select how many years of historical data to display",
        )

        # Refresh button
        if st.button("🔄 Refresh Data", help="Force refresh data from FRED"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            """
            This dashboard displays key U.S. economic indicators:

            **Economic Indicators:**
            - **Unemployment Rate**: Percentage of unemployed in labor force
            - **GDP**: Gross Domestic Product in billions of dollars
            - **GDP Growth**: Real GDP growth rate (year-over-year)

            **Housing Market:**
            - **Mortgage Rate**: 30-year fixed mortgage rate
            - **Median Home Price**: Median sales price of houses sold
            - **Case-Shiller Index**: National home price index
            - **Housing Starts**: New privately owned housing units started

            **Consumer Sentiment & Health:**
            - **Consumer Sentiment**: University of Michigan Consumer Sentiment Index
            - **Personal Saving Rate**: Personal savings as % of disposable income
            - **Personal Consumption**: Personal consumption expenditures
            - **Retail Sales**: Advance retail trade sales
            - **Consumer Credit**: Total consumer credit outstanding
            - **Disposable Income**: Real disposable personal income
            - **Initial Claims**: Weekly initial unemployment insurance claims

            **Credit Market Indicators:**
            - **Credit Spreads**: Corporate bond spreads (AAA, BBB, IG, High Yield)
            - **Yield Curve**: Treasury yield spreads (10Y-2Y, 10Y-3M)
            - **Borrowing Rates**: Consumer rates (credit card, auto, prime, mortgage)
            - **Debt Levels**: Corporate and household debt securities
            - **Leverage Metrics**: Federal debt/GDP ratio, household debt service

            **Healthcare Indicators:**
            - **Healthcare Spending**: Personal health care expenditures (PCE)
            - **Healthcare % of Consumption**: Health expenditures as share of personal consumption
            - **Healthcare Costs**: CPI for medical care, hospital services, prescription drugs
            - **Healthcare Employment**: Healthcare and social assistance sector jobs
            - **Healthcare Wages**: Average hourly earnings in healthcare
            - **Health Insurance**: Percent of people with health insurance coverage

            **Note**: Charts with dual Y-axes show both level data and year-over-year growth trends.

            **Data Source**: [FRED](https://fred.stlouisfed.org/)
            """
        )

    # Load data
    with st.spinner("Loading economic data..."):
        try:
            data = load_data()
        except Exception as e:
            logger.exception("Fatal error loading data")
            st.error(f"Error loading data: {e}")
            st.stop()

    if not data:
        st.error("No data could be loaded. Check the logs for details.")
        st.stop()

    # Show a warning banner if any series failed to load
    from config import FRED_SERIES
    missing = [name for name in FRED_SERIES if name not in data]
    if missing:
        logger.warning("Dashboard missing series: %s", ", ".join(missing))
        st.warning(
            f"Some indicators could not be loaded and will be hidden: {', '.join(missing)}. "
            "Check the application logs for details."
        )

    # Filter data by selected time range
    filtered_data = {
        key: filter_data_by_date(series, years_back) for key, series in data.items()
    }

    # Display metric cards
    st.subheader("Current Economic Indicators")
    display_metric_cards(data)

    st.markdown("---")

    # Main chart: Unemployment vs GDP (dual axis)
    if "unemployment" in filtered_data and "gdp" in filtered_data:
        st.subheader("Unemployment Rate vs GDP")
        st.markdown("Compare unemployment trends with GDP over time")
        dual_chart = create_dual_axis_chart(
            filtered_data["unemployment"],
            filtered_data["gdp"],
            "Unemployment Rate and GDP Over Time",
        )
        st.plotly_chart(dual_chart, use_container_width=True)

    st.markdown("---")

    # Individual charts
    col1, col2 = st.columns(2)

    with col1:
        if "unemployment" in filtered_data:
            st.subheader("Unemployment Rate")
            unemployment_chart = create_single_chart(
                filtered_data["unemployment"],
                "Unemployment Rate Over Time",
                "Unemployment Rate (%)",
                "#EF553B",
            )
            st.plotly_chart(unemployment_chart, use_container_width=True)

    with col2:
        if "gdp_growth" in filtered_data:
            st.subheader("Real GDP Growth Rate")
            gdp_growth_chart = create_single_chart(
                filtered_data["gdp_growth"],
                "Real GDP Growth Rate Over Time",
                "Growth Rate (%)",
                "#636EFA",
            )
            st.plotly_chart(gdp_growth_chart, use_container_width=True)

    st.markdown("---")

    # Housing Market Section
    st.subheader("Housing Market & Mortgage Metrics")
    display_housing_metric_cards(data)

    st.markdown("---")

    # Housing charts
    col1, col2 = st.columns(2)

    with col1:
        if "mortgage_rate" in filtered_data:
            st.subheader("30-Year Mortgage Rate")
            mortgage_chart = create_single_chart(
                filtered_data["mortgage_rate"],
                "30-Year Fixed Mortgage Rate Over Time",
                "Rate (%)",
                "#AB63FA",
            )
            st.plotly_chart(mortgage_chart, use_container_width=True)

    with col2:
        if "median_home_price" in filtered_data:
            st.subheader("Median Home Price")
            home_price_chart = create_single_chart(
                filtered_data["median_home_price"],
                "Median Sales Price of Houses Over Time",
                "Price ($)",
                "#FFA15A",
            )
            st.plotly_chart(home_price_chart, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        if "home_price_index" in filtered_data:
            st.subheader("Case-Shiller Home Price Index")
            price_index_chart = create_single_chart(
                filtered_data["home_price_index"],
                "S&P/Case-Shiller Home Price Index",
                "Index",
                "#19D3F3",
            )
            st.plotly_chart(price_index_chart, use_container_width=True)

    with col4:
        if "housing_starts" in filtered_data:
            st.subheader("Housing Starts")
            housing_starts_chart = create_single_chart(
                filtered_data["housing_starts"],
                "Housing Starts Over Time",
                "Thousands of Units",
                "#FF6692",
            )
            st.plotly_chart(housing_starts_chart, use_container_width=True)

    st.markdown("---")

    # Consumer Sentiment & Health Section
    st.subheader("Consumer Sentiment & Health Metrics")
    display_consumer_metric_cards(data)

    st.markdown("---")

    # Consumer sentiment charts
    col1, col2 = st.columns(2)

    with col1:
        if "consumer_sentiment" in filtered_data:
            st.subheader("Consumer Sentiment Index")
            consumer_sentiment_chart = create_level_with_growth_chart(
                filtered_data["consumer_sentiment"],
                "University of Michigan Consumer Sentiment Index",
                "Index Level",
                "#636EFA",
                "Consumer Sentiment"
            )
            st.plotly_chart(consumer_sentiment_chart, use_container_width=True)

    with col2:
        if "personal_consumption" in filtered_data:
            st.subheader("Personal Consumption Expenditures")
            pce_chart = create_level_with_growth_chart(
                filtered_data["personal_consumption"],
                "Personal Consumption Expenditures",
                "Billions of $",
                "#00CC96",
                "PCE"
            )
            st.plotly_chart(pce_chart, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        if "disposable_income" in filtered_data:
            st.subheader("Real Disposable Personal Income")
            income_chart = create_level_with_growth_chart(
                filtered_data["disposable_income"],
                "Real Disposable Personal Income",
                "Billions of Chained 2017 $",
                "#AB63FA",
                "Disposable Income"
            )
            st.plotly_chart(income_chart, use_container_width=True)

    with col4:
        if "consumer_credit" in filtered_data:
            st.subheader("Consumer Credit Outstanding")
            credit_chart = create_level_with_growth_chart(
                filtered_data["consumer_credit"],
                "Total Consumer Credit Outstanding",
                "Billions of $",
                "#EF553B",
                "Consumer Credit"
            )
            st.plotly_chart(credit_chart, use_container_width=True)

    col5, col6 = st.columns(2)

    with col5:
        if "retail_sales" in filtered_data:
            st.subheader("Advance Retail Sales")
            retail_chart = create_level_with_growth_chart(
                filtered_data["retail_sales"],
                "Advance Retail Sales",
                "Millions of $",
                "#FFA15A",
                "Retail Sales"
            )
            st.plotly_chart(retail_chart, use_container_width=True)

    with col6:
        if "personal_saving_rate" in filtered_data:
            st.subheader("Personal Saving Rate")
            saving_chart = create_single_chart(
                filtered_data["personal_saving_rate"],
                "Personal Saving Rate Over Time",
                "Saving Rate (%)",
                "#19D3F3",
            )
            st.plotly_chart(saving_chart, use_container_width=True)

    # Initial Claims chart (weekly data, inverted for better visualization)
    if "initial_claims" in filtered_data:
        st.subheader("Initial Jobless Claims (Weekly)")
        st.markdown("Lower values indicate a healthier job market")
        claims_chart = create_level_with_growth_chart(
            filtered_data["initial_claims"],
            "Initial Unemployment Insurance Claims",
            "Thousands of Claims",
            "#FF6692",
            "Initial Claims"
        )
        st.plotly_chart(claims_chart, use_container_width=True)

    st.markdown("---")

    # Credit Market Indicators Section
    st.subheader("Credit Market Indicators")
    display_credit_metric_cards(data)

    st.markdown("---")

    # Credit Spreads
    st.subheader("Credit Spreads Analysis")
    col1, col2 = st.columns(2)

    with col1:
        spread_series = {
            name: filtered_data[key]
            for name, key in [("High Yield", "hy_spread"), ("Investment Grade", "ig_spread"),
                              ("BBB", "baa_spread"), ("AAA", "aaa_spread")]
            if key in filtered_data
        }
        if spread_series:
            st.markdown("**Corporate Credit Spreads**")
            spreads_chart = create_multi_series_chart(
                spread_series,
                "Corporate Bond Spreads Over Treasuries",
                "Spread (percentage points)",
                colors=["#EF553B", "#FFA15A", "#636EFA", "#00CC96"]
            )
            st.plotly_chart(spreads_chart, use_container_width=True)
            st.caption("Higher spreads indicate greater credit risk and investor concern")

    with col2:
        yield_series = {
            name: filtered_data[key]
            for name, key in [("10Y-2Y Spread", "yield_curve_10y2y"), ("10Y-3M Spread", "yield_curve_10y3m")]
            if key in filtered_data
        }
        if yield_series:
            st.markdown("**Treasury Yield Curve**")
            yield_curve_chart = create_multi_series_chart(
                yield_series,
                "Treasury Yield Curve Spreads",
                "Spread (percentage points)",
                colors=["#636EFA", "#AB63FA"]
            )
            st.plotly_chart(yield_curve_chart, use_container_width=True)
            st.caption("Inverted yield curve (negative spread) may signal recession risk")

    st.markdown("---")

    # Borrowing Rates
    st.subheader("Consumer Borrowing Rates")
    col3, col4 = st.columns(2)

    with col3:
        rate_series = {
            name: filtered_data[key]
            for name, key in [("Credit Card", "credit_card_rate"), ("Prime Rate", "personal_loan_rate"),
                              ("Auto Loan (48mo)", "auto_loan_rate"), ("Mortgage (30yr)", "mortgage_rate")]
            if key in filtered_data
        }
        if rate_series:
            st.markdown("**Consumer Loan Rates**")
            consumer_rates_chart = create_multi_series_chart(
                rate_series,
                "Consumer Borrowing Rates",
                "Interest Rate (%)",
                colors=["#EF553B", "#FFA15A", "#636EFA", "#00CC96"]
            )
            st.plotly_chart(consumer_rates_chart, use_container_width=True)

    with col4:
        treasury_series = {
            name: filtered_data[key]
            for name, key in [("30-Year Mortgage", "mortgage_rate"), ("10-Year Treasury", "treasury_10y")]
            if key in filtered_data
        }
        if treasury_series:
            st.markdown("**Treasury Rate vs. Mortgage Rate**")
            treasury_mortgage_chart = create_multi_series_chart(
                treasury_series,
                "Mortgage Rate vs. Treasury Rate",
                "Interest Rate (%)",
                colors=["#636EFA", "#00CC96"]
            )
            st.plotly_chart(treasury_mortgage_chart, use_container_width=True)
            st.caption("Mortgage rates typically track Treasury rates with a spread")

    st.markdown("---")

    # Debt and Leverage
    st.subheader("Debt & Leverage Metrics")
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("**Corporate & Household Debt**")
        if "corporate_debt" in filtered_data:
            debt_chart = create_level_with_growth_chart(
                filtered_data["corporate_debt"],
                "Nonfinancial Corporate Debt Securities",
                "Billions of $",
                "#636EFA",
                "Corporate Debt"
            )
            st.plotly_chart(debt_chart, use_container_width=True)

        if "household_debt" in filtered_data:
            household_debt_chart = create_level_with_growth_chart(
                filtered_data["household_debt"],
                "Household & Nonprofit Debt",
                "Billions of $",
                "#EF553B",
                "Household Debt"
            )
            st.plotly_chart(household_debt_chart, use_container_width=True)

    with col6:
        st.markdown("**Debt Ratios & Credit Gap**")
        if "federal_debt_gdp" in filtered_data:
            federal_debt_chart = create_single_chart(
                filtered_data["federal_debt_gdp"],
                "Federal Debt as % of GDP",
                "Percent of GDP (%)",
                "#AB63FA"
            )
            st.plotly_chart(federal_debt_chart, use_container_width=True)

        if "total_credit_gap" in filtered_data:
            debt_service_chart = create_single_chart(
                filtered_data["total_credit_gap"],
                "Household Debt Service Payments",
                "% of Disposable Income",
                "#FFA15A"
            )
            st.plotly_chart(debt_service_chart, use_container_width=True)
            st.caption("Higher values indicate households spending more income on debt payments")

    st.markdown("---")

    # Healthcare Indicators Section
    st.subheader("Healthcare Indicators")
    display_healthcare_metric_cards(data)

    st.markdown("---")

    # Healthcare spending and costs
    st.subheader("Healthcare Spending & Costs")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Healthcare Expenditures**")
        if "healthcare_pce" in filtered_data:
            healthcare_pce_chart = create_level_with_growth_chart(
                filtered_data["healthcare_pce"],
                "Personal Health Care Expenditures",
                "Billions of $",
                "#636EFA",
                "Healthcare PCE"
            )
            st.plotly_chart(healthcare_pce_chart, use_container_width=True)

        if "healthcare_gdp_pct" in filtered_data:
            healthcare_pce_pct_chart = create_single_chart(
                filtered_data["healthcare_gdp_pct"],
                "Healthcare as % of GDP",
                "Percent of GDP (%)",
                "#AB63FA"
            )
            st.plotly_chart(healthcare_pce_pct_chart, use_container_width=True)

    with col2:
        cpi_series = {
            name: filtered_data[key]
            for name, key in [("Medical Care", "cpi_medical"), ("Hospital Services", "cpi_hospital"),
                              ("Prescription Drugs", "cpi_prescription")]
            if key in filtered_data
        }
        if cpi_series:
            st.markdown("**Healthcare Cost Inflation**")
            healthcare_cpi_chart = create_multi_series_chart(
                cpi_series,
                "Healthcare Price Indices (CPI)",
                "Index (1982-84=100)",
                colors=["#636EFA", "#EF553B", "#00CC96"]
            )
            st.plotly_chart(healthcare_cpi_chart, use_container_width=True)
            st.caption("Tracks inflation in different healthcare segments")

    st.markdown("---")

    # Healthcare employment and insurance
    st.subheader("Healthcare Employment & Coverage")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**Healthcare Sector Employment**")
        if "healthcare_employment" in filtered_data:
            employment_chart = create_level_with_growth_chart(
                filtered_data["healthcare_employment"],
                "Healthcare & Social Assistance Employment",
                "Thousands of Employees",
                "#00CC96",
                "Healthcare Jobs"
            )
            st.plotly_chart(employment_chart, use_container_width=True)

        if "healthcare_wages" in filtered_data:
            wages_chart = create_level_with_growth_chart(
                filtered_data["healthcare_wages"],
                "Average Hourly Earnings in Healthcare",
                "Dollars per Hour",
                "#FFA15A",
                "Healthcare Wages"
            )
            st.plotly_chart(wages_chart, use_container_width=True)

    with col4:
        if "uninsured_pct" in filtered_data:
            st.markdown("**Health Insurance Coverage**")
            insured_chart = create_single_chart(
                filtered_data["uninsured_pct"],
                "Percent of People With Health Insurance",
                "Percent (%)",
                "#00CC96"
            )
            st.plotly_chart(insured_chart, use_container_width=True)
            st.caption("Higher values indicate better insurance coverage")

    st.markdown("---")

    # Data table (expandable)
    with st.expander("📊 View Raw Data"):
        st.subheader("Recent Data Points")

        # Build DataFrame only from available series
        column_map = {
            "unemployment": "Unemployment Rate (%)",
            "gdp": "GDP (Billions $)",
            "gdp_growth": "GDP Growth Rate (%)",
            "mortgage_rate": "30-Year Mortgage Rate (%)",
            "median_home_price": "Median Home Price ($)",
            "home_price_index": "Case-Shiller Index",
            "housing_starts": "Housing Starts (K)",
            "consumer_sentiment": "Consumer Sentiment",
            "personal_saving_rate": "Personal Saving Rate (%)",
            "personal_consumption": "Personal Consumption (Billions $)",
            "retail_sales": "Retail Sales (Millions $)",
            "consumer_credit": "Consumer Credit (Billions $)",
            "disposable_income": "Disposable Income (Billions $)",
            "initial_claims": "Initial Claims (K)",
            "hy_spread": "HY Spread (%)",
            "baa_spread": "BBB Spread (%)",
            "aaa_spread": "AAA Spread (%)",
            "ig_spread": "IG Spread (%)",
            "yield_curve_10y2y": "10Y-2Y Yield (%)",
            "yield_curve_10y3m": "10Y-3M Yield (%)",
            "treasury_10y": "10Y Treasury (%)",
            "credit_card_rate": "Credit Card Rate (%)",
            "personal_loan_rate": "Prime Rate (%)",
            "auto_loan_rate": "Auto Loan Rate (%)",
            "corporate_debt": "Corporate Debt (Billions $)",
            "household_debt": "Household Debt (Billions $)",
            "federal_debt_gdp": "Federal Debt/GDP (%)",
            "total_credit_gap": "Household Debt Service (%)",
            "healthcare_pce": "Healthcare PCE (Billions $)",
            "healthcare_gdp_pct": "Healthcare % of GDP",
            "cpi_medical": "CPI Medical Care",
            "cpi_hospital": "CPI Hospital Services",
            "cpi_prescription": "CPI Prescription Drugs",
            "healthcare_employment": "Healthcare Employment (K)",
            "healthcare_wages": "Healthcare Wages ($/hr)",
            "uninsured_pct": "Health Insurance Rate (%)",
        }
        df = pd.DataFrame(
            {
                label: filtered_data[key]
                for key, label in column_map.items()
                if key in filtered_data
            }
        )

        # Show most recent data first
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)

        # Download button
        csv = df.to_csv()
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"fred_economic_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    # Footer
    st.markdown("---")
    st.caption(
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Data source: FRED (Federal Reserve Economic Data)"
    )


if __name__ == "__main__":
    main()
