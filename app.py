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
    fig.update_yaxis(title_text="Unemployment Rate (%)", secondary_y=False)
    fig.update_yaxis(title_text="GDP (Billions of $)", secondary_y=True)

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
            - **Unemployment Rate**: Percentage of unemployed in labor force
            - **GDP**: Gross Domestic Product in billions of dollars
            - **GDP Growth**: Real GDP growth rate (year-over-year)

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

    # Data table (expandable)
    with st.expander("📊 View Raw Data"):
        st.subheader("Recent Data Points")

        # Combine data into a DataFrame
        df = pd.DataFrame(
            {
                "Unemployment Rate (%)": filtered_data["unemployment"],
                "GDP (Billions $)": filtered_data["gdp"],
                "GDP Growth Rate (%)": filtered_data["gdp_growth"],
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
