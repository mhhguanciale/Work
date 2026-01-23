"""FRED Economic Data Dashboard - Streamlit Application."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from data_fetcher import FREDDataFetcher
from config import DASHBOARD_TITLE, DEFAULT_YEARS_BACK


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


def display_metric_cards(data: dict):
    """Display current values as metric cards."""
    col1, col2, col3 = st.columns(3)

    with col1:
        unemployment = data["unemployment"]
        current_val = unemployment.iloc[-1]
        prev_val = unemployment.iloc[-2] if len(unemployment) > 1 else current_val
        delta = current_val - prev_val

        st.metric(
            label="Current Unemployment Rate",
            value=f"{current_val:.1f}%",
            delta=f"{delta:.1f}%",
            delta_color="inverse",
        )
        st.caption(f"As of {unemployment.index[-1].strftime('%B %Y')}")

    with col2:
        gdp = data["gdp"]
        current_val = gdp.iloc[-1]
        prev_val = gdp.iloc[-2] if len(gdp) > 1 else current_val
        delta = current_val - prev_val
        delta_pct = (delta / prev_val * 100) if prev_val != 0 else 0

        st.metric(
            label="Current GDP",
            value=f"${current_val:,.0f}B",
            delta=f"{delta_pct:+.1f}%",
        )
        st.caption(f"As of {gdp.index[-1].strftime('%B %Y')}")

    with col3:
        gdp_growth = data["gdp_growth"]
        current_val = gdp_growth.iloc[-1]
        prev_val = gdp_growth.iloc[-2] if len(gdp_growth) > 1 else current_val
        delta = current_val - prev_val

        st.metric(
            label="Real GDP Growth Rate",
            value=f"{current_val:.2f}%",
            delta=f"{delta:.2f}%",
        )
        st.caption(f"As of {gdp_growth.index[-1].strftime('%B %Y')}")


def display_housing_metric_cards(data: dict):
    """Display housing market metrics as cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        mortgage_rate = data["mortgage_rate"]
        current_val = mortgage_rate.iloc[-1]
        prev_val = mortgage_rate.iloc[-2] if len(mortgage_rate) > 1 else current_val
        delta = current_val - prev_val

        st.metric(
            label="30-Year Mortgage Rate",
            value=f"{current_val:.2f}%",
            delta=f"{delta:.2f}%",
            delta_color="inverse",
        )
        st.caption(f"As of {mortgage_rate.index[-1].strftime('%B %Y')}")

    with col2:
        median_price = data["median_home_price"]
        current_val = median_price.iloc[-1]
        prev_val = median_price.iloc[-2] if len(median_price) > 1 else current_val
        delta = current_val - prev_val
        delta_pct = (delta / prev_val * 100) if prev_val != 0 else 0

        st.metric(
            label="Median Home Price",
            value=f"${current_val:,.0f}",
            delta=f"{delta_pct:+.1f}%",
        )
        st.caption(f"As of {median_price.index[-1].strftime('%B %Y')}")

    with col3:
        home_price_idx = data["home_price_index"]
        current_val = home_price_idx.iloc[-1]
        prev_val = home_price_idx.iloc[-2] if len(home_price_idx) > 1 else current_val
        delta = current_val - prev_val
        delta_pct = (delta / prev_val * 100) if prev_val != 0 else 0

        st.metric(
            label="Case-Shiller Index",
            value=f"{current_val:.1f}",
            delta=f"{delta_pct:+.1f}%",
        )
        st.caption(f"As of {home_price_idx.index[-1].strftime('%B %Y')}")

    with col4:
        housing_starts = data["housing_starts"]
        current_val = housing_starts.iloc[-1]
        prev_val = housing_starts.iloc[-2] if len(housing_starts) > 1 else current_val
        delta = current_val - prev_val
        delta_pct = (delta / prev_val * 100) if prev_val != 0 else 0

        st.metric(
            label="Housing Starts",
            value=f"{current_val:,.0f}K",
            delta=f"{delta_pct:+.1f}%",
        )
        st.caption(f"As of {housing_starts.index[-1].strftime('%B %Y')}")


def display_consumer_metric_cards(data: dict):
    """Display consumer sentiment and health metrics as cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        consumer_sentiment = data["consumer_sentiment"]
        current_val = consumer_sentiment.iloc[-1]
        prev_val = consumer_sentiment.iloc[-2] if len(consumer_sentiment) > 1 else current_val
        delta = current_val - prev_val

        st.metric(
            label="Consumer Sentiment",
            value=f"{current_val:.1f}",
            delta=f"{delta:.1f}",
        )
        st.caption(f"As of {consumer_sentiment.index[-1].strftime('%B %Y')}")

    with col2:
        personal_saving = data["personal_saving_rate"]
        current_val = personal_saving.iloc[-1]
        prev_val = personal_saving.iloc[-2] if len(personal_saving) > 1 else current_val
        delta = current_val - prev_val

        st.metric(
            label="Personal Saving Rate",
            value=f"{current_val:.1f}%",
            delta=f"{delta:.1f}%",
        )
        st.caption(f"As of {personal_saving.index[-1].strftime('%B %Y')}")

    with col3:
        retail_sales = data["retail_sales"]
        current_val = retail_sales.iloc[-1]
        prev_val = retail_sales.iloc[-2] if len(retail_sales) > 1 else current_val
        delta = current_val - prev_val
        delta_pct = (delta / prev_val * 100) if prev_val != 0 else 0

        st.metric(
            label="Retail Sales",
            value=f"${current_val:,.0f}M",
            delta=f"{delta_pct:+.1f}%",
        )
        st.caption(f"As of {retail_sales.index[-1].strftime('%B %Y')}")

    with col4:
        initial_claims = data["initial_claims"]
        current_val = initial_claims.iloc[-1]
        prev_val = initial_claims.iloc[-2] if len(initial_claims) > 1 else current_val
        delta = current_val - prev_val
        delta_pct = (delta / prev_val * 100) if prev_val != 0 else 0

        st.metric(
            label="Initial Jobless Claims",
            value=f"{current_val:,.0f}K",
            delta=f"{delta_pct:+.1f}%",
            delta_color="inverse",
        )
        st.caption(f"As of {initial_claims.index[-1].strftime('%B %Y')}")


def display_credit_metric_cards(data: dict):
    """Display credit market metrics as cards."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        hy_spread = data["hy_spread"]
        current_val = hy_spread.iloc[-1]
        prev_val = hy_spread.iloc[-2] if len(hy_spread) > 1 else current_val
        delta = current_val - prev_val

        st.metric(
            label="High Yield Spread",
            value=f"{current_val:.2f}%",
            delta=f"{delta:+.2f}%",
            delta_color="inverse",  # Higher spread is worse
        )
        st.caption(f"As of {hy_spread.index[-1].strftime('%B %Y')}")

    with col2:
        baa_spread = data["baa_spread"]
        current_val = baa_spread.iloc[-1]
        prev_val = baa_spread.iloc[-2] if len(baa_spread) > 1 else current_val
        delta = current_val - prev_val

        st.metric(
            label="Baa Spread",
            value=f"{current_val:.2f}%",
            delta=f"{delta:+.2f}%",
            delta_color="inverse",
        )
        st.caption(f"As of {baa_spread.index[-1].strftime('%B %Y')}")

    with col3:
        yield_curve = data["yield_curve_10y2y"]
        current_val = yield_curve.iloc[-1]
        prev_val = yield_curve.iloc[-2] if len(yield_curve) > 1 else current_val
        delta = current_val - prev_val

        st.metric(
            label="10Y-2Y Yield Curve",
            value=f"{current_val:.2f}%",
            delta=f"{delta:+.2f}%",
        )
        st.caption(f"As of {yield_curve.index[-1].strftime('%B %Y')}")

    with col4:
        federal_debt = data["federal_debt_gdp"]
        current_val = federal_debt.iloc[-1]
        prev_val = federal_debt.iloc[-2] if len(federal_debt) > 1 else current_val
        delta = current_val - prev_val

        st.metric(
            label="Federal Debt/GDP",
            value=f"{current_val:.1f}%",
            delta=f"{delta:+.1f}%",
            delta_color="inverse",
        )
        st.caption(f"As of {federal_debt.index[-1].strftime('%B %Y')}")


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
            - **Credit Spreads**: Corporate bond spreads (Aaa, Baa, IG, High Yield)
            - **Yield Curve**: Treasury yield spreads (10Y-2Y, 10Y-3M)
            - **Borrowing Rates**: Consumer rates (credit card, auto, personal, mortgage)
            - **Debt Levels**: Corporate and household debt securities
            - **Leverage Metrics**: Federal debt/GDP ratio, credit gap

            **Note**: Charts with dual Y-axes show both level data and year-over-year growth trends.

            **Data Source**: [FRED](https://fred.stlouisfed.org/)
            """
        )

    # Load data
    with st.spinner("Loading economic data..."):
        try:
            data = load_data()
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.stop()

    # Filter data by selected time range
    filtered_data = {
        key: filter_data_by_date(series, years_back) for key, series in data.items()
    }

    # Display metric cards
    st.subheader("Current Economic Indicators")
    display_metric_cards(data)

    st.markdown("---")

    # Main chart: Unemployment vs GDP (dual axis)
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
        st.subheader("Unemployment Rate")
        unemployment_chart = create_single_chart(
            filtered_data["unemployment"],
            "Unemployment Rate Over Time",
            "Unemployment Rate (%)",
            "#EF553B",
        )
        st.plotly_chart(unemployment_chart, use_container_width=True)

    with col2:
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
        st.subheader("30-Year Mortgage Rate")
        mortgage_chart = create_single_chart(
            filtered_data["mortgage_rate"],
            "30-Year Fixed Mortgage Rate Over Time",
            "Rate (%)",
            "#AB63FA",
        )
        st.plotly_chart(mortgage_chart, use_container_width=True)

    with col2:
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
        st.subheader("Case-Shiller Home Price Index")
        price_index_chart = create_single_chart(
            filtered_data["home_price_index"],
            "S&P/Case-Shiller Home Price Index",
            "Index",
            "#19D3F3",
        )
        st.plotly_chart(price_index_chart, use_container_width=True)

    with col4:
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
        st.subheader("Personal Saving Rate")
        saving_chart = create_single_chart(
            filtered_data["personal_saving_rate"],
            "Personal Saving Rate Over Time",
            "Saving Rate (%)",
            "#19D3F3",
        )
        st.plotly_chart(saving_chart, use_container_width=True)

    # Initial Claims chart (weekly data, inverted for better visualization)
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
        st.markdown("**Corporate Credit Spreads**")
        spreads_chart = create_multi_series_chart(
            {
                "High Yield": filtered_data["hy_spread"],
                "Investment Grade": filtered_data["ig_spread"],
                "Baa": filtered_data["baa_spread"],
                "Aaa": filtered_data["aaa_spread"],
            },
            "Corporate Bond Spreads Over Treasuries",
            "Spread (percentage points)",
            colors=["#EF553B", "#FFA15A", "#636EFA", "#00CC96"]
        )
        st.plotly_chart(spreads_chart, use_container_width=True)
        st.caption("Higher spreads indicate greater credit risk and investor concern")

    with col2:
        st.markdown("**Treasury Yield Curve**")
        yield_curve_chart = create_multi_series_chart(
            {
                "10Y-2Y Spread": filtered_data["yield_curve_10y2y"],
                "10Y-3M Spread": filtered_data["yield_curve_10y3m"],
            },
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
        st.markdown("**Consumer Loan Rates**")
        consumer_rates_chart = create_multi_series_chart(
            {
                "Credit Card": filtered_data["credit_card_rate"],
                "Personal Loan (24mo)": filtered_data["personal_loan_rate"],
                "Auto Loan (48mo)": filtered_data["auto_loan_rate"],
                "Mortgage (30yr)": filtered_data["mortgage_rate"],
            },
            "Consumer Borrowing Rates",
            "Interest Rate (%)",
            colors=["#EF553B", "#FFA15A", "#636EFA", "#00CC96"]
        )
        st.plotly_chart(consumer_rates_chart, use_container_width=True)

    with col4:
        st.markdown("**Treasury Rate vs. Mortgage Rate**")
        treasury_mortgage_chart = create_multi_series_chart(
            {
                "30-Year Mortgage": filtered_data["mortgage_rate"],
                "10-Year Treasury": filtered_data["treasury_10y"],
            },
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
        debt_chart = create_level_with_growth_chart(
            filtered_data["corporate_debt"],
            "Nonfinancial Corporate Debt Securities",
            "Billions of $",
            "#636EFA",
            "Corporate Debt"
        )
        st.plotly_chart(debt_chart, use_container_width=True)

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
        federal_debt_chart = create_single_chart(
            filtered_data["federal_debt_gdp"],
            "Federal Debt as % of GDP",
            "Percent of GDP (%)",
            "#AB63FA"
        )
        st.plotly_chart(federal_debt_chart, use_container_width=True)

        credit_gap_chart = create_single_chart(
            filtered_data["total_credit_gap"],
            "Credit to Non-Financial Sector Gap",
            "% of GDP",
            "#FFA15A"
        )
        st.plotly_chart(credit_gap_chart, use_container_width=True)
        st.caption("Credit gap shows deviation from long-term trend; positive values may signal excess credit")

    st.markdown("---")

    # Data table (expandable)
    with st.expander("📊 View Raw Data"):
        st.subheader("Recent Data Points")

        # Combine data into a DataFrame
        df = pd.DataFrame(
            {
                "Unemployment Rate (%)": filtered_data["unemployment"],
                "GDP (Billions $)": filtered_data["gdp"],
                "GDP Growth Rate (%)": filtered_data["gdp_growth"],
                "30-Year Mortgage Rate (%)": filtered_data["mortgage_rate"],
                "Median Home Price ($)": filtered_data["median_home_price"],
                "Case-Shiller Index": filtered_data["home_price_index"],
                "Housing Starts (K)": filtered_data["housing_starts"],
                "Consumer Sentiment": filtered_data["consumer_sentiment"],
                "Personal Saving Rate (%)": filtered_data["personal_saving_rate"],
                "Personal Consumption (Billions $)": filtered_data["personal_consumption"],
                "Retail Sales (Millions $)": filtered_data["retail_sales"],
                "Consumer Credit (Billions $)": filtered_data["consumer_credit"],
                "Disposable Income (Billions $)": filtered_data["disposable_income"],
                "Initial Claims (K)": filtered_data["initial_claims"],
                # Credit Market Indicators
                "HY Spread (%)": filtered_data["hy_spread"],
                "Baa Spread (%)": filtered_data["baa_spread"],
                "Aaa Spread (%)": filtered_data["aaa_spread"],
                "IG Spread (%)": filtered_data["ig_spread"],
                "10Y-2Y Yield (%)": filtered_data["yield_curve_10y2y"],
                "10Y-3M Yield (%)": filtered_data["yield_curve_10y3m"],
                "10Y Treasury (%)": filtered_data["treasury_10y"],
                "Credit Card Rate (%)": filtered_data["credit_card_rate"],
                "Personal Loan Rate (%)": filtered_data["personal_loan_rate"],
                "Auto Loan Rate (%)": filtered_data["auto_loan_rate"],
                "Corporate Debt (Billions $)": filtered_data["corporate_debt"],
                "Household Debt (Billions $)": filtered_data["household_debt"],
                "Federal Debt/GDP (%)": filtered_data["federal_debt_gdp"],
                "Credit Gap (% GDP)": filtered_data["total_credit_gap"],
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
