"""Chart building utilities for stock analysis."""

import pandas as pd
import plotly.graph_objects as go
import talib as ta
import yfinance as yf


class ChartBuilder:
    """Builds professional stock analysis charts with technical indicators."""

    PERIOD_MAPPING = {
        "1d": {"period": "1d", "interval": "1m"},
        "5d": {"period": "5d", "interval": "30m"},
        "1mo": {"period": "1mo", "interval": "1d"},
        "6mo": {"period": "6mo", "interval": "1d"},
        "ytd": {"period": "ytd", "interval": "1d"},
        "1y": {"period": "1y", "interval": "1d"},
        "5y": {"period": "5y", "interval": "1wk"},
        "max": {"period": "max", "interval": "1wk"},
    }

    @staticmethod
    def load_and_process_data(ticker: str, time_period: str) -> pd.DataFrame:
        """Load and process stock data."""
        period_config = ChartBuilder.PERIOD_MAPPING.get(time_period, ChartBuilder.PERIOD_MAPPING["1mo"])
        
        data = yf.download(
            ticker,
            period=period_config["period"],
            interval=period_config["interval"],
            auto_adjust=True,
            progress=False,
        )
        
        # Handle MultiIndex columns (multiple tickers) vs single ticker
        if isinstance(data.columns, pd.MultiIndex):
            data = data.xs(ticker, axis=1, level=1)
        
        # Timezone handling
        if data.index.tzinfo is None:
            data.index = data.index.tz_localize("UTC")
        data.index = data.index.tz_convert("US/Eastern")
        data.reset_index(inplace=True)
        data.rename(columns={"Date": "Datetime"}, inplace=True)
        
        return data

    @staticmethod
    def add_indicators(data: pd.DataFrame, indicators: dict) -> pd.DataFrame:
        """Add technical indicators to dataframe."""
        close_prices = data["Close"].to_numpy().flatten()
        
        if indicators.get("SMA 20"):
            data["SMA_20"] = ta.SMA(close_prices, timeperiod=20)
        if indicators.get("SMA 50"):
            data["SMA_50"] = ta.SMA(close_prices, timeperiod=50)
        if indicators.get("SMA 200"):
            data["SMA_200"] = ta.SMA(close_prices, timeperiod=200)
        if indicators.get("EMA 20"):
            data["EMA_20"] = ta.EMA(close_prices, timeperiod=20)
        if indicators.get("EMA 50"):
            data["EMA_50"] = ta.EMA(close_prices, timeperiod=50)
        if indicators.get("Bollinger Bands"):
            data["BB_Upper"], data["BB_Middle"], data["BB_Lower"] = ta.BBANDS(close_prices)
        
        return data

    @staticmethod
    def build_chart(
        data: pd.DataFrame,
        ticker: str,
        indicators: dict,
        time_period: str,
        chart_type: str = "Candlestick"
    ) -> go.Figure:
        """Build chart with indicators from data."""
        fig = go.Figure()
        
        # Add price chart
        if chart_type == "Candlestick":
            fig.add_trace(
                go.Candlestick(
                    x=data["Datetime"],
                    open=data["Open"],
                    high=data["High"],
                    low=data["Low"],
                    close=data["Close"],
                    name="Price",
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=data["Datetime"],
                    y=data["Close"],
                    mode="lines",
                    name="Close",
                    line=dict(color="blue"),
                )
            )
        
        for ma_col in ["SMA_20", "SMA_50", "SMA_200", "EMA_20", "EMA_50"]:
            if ma_col in data.columns:
                indicator_name = ma_col.replace("_", " ")
                if indicators.get(indicator_name):
                    fig.add_trace(
                        go.Scatter(
                            x=data["Datetime"],
                            y=data[ma_col],
                            mode="lines",
                            name=indicator_name,
                            line=dict(width=2),
                        )
                    )
        
        if "BB_Upper" in data.columns and indicators.get("Bollinger Bands"):
            fig.add_trace(
                go.Scatter(
                    x=data["Datetime"],
                    y=data["BB_Upper"],
                    mode="lines",
                    name="BB Upper",
                    line=dict(dash="dash", color="red", width=1),
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=data["Datetime"],
                    y=data["BB_Lower"],
                    mode="lines",
                    name="BB Lower",
                    line=dict(dash="dash", color="red", width=1),
                    fill="tonexty",
                    fillcolor="rgba(255,0,0,0.1)",
                )
            )
        
        fig.update_layout(
            title=f"{ticker} {time_period.upper()} Chart",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            height=600,
            hovermode="x unified",
            template="plotly_white",
        )
        
        return fig

    @staticmethod
    def create_chart(
        ticker: str,
        indicators: dict,
        time_period: str = "1mo",
        chart_type: str = "Candlestick"
    ) -> go.Figure:
        """Create complete chart from ticker."""
        try:
            data = ChartBuilder.load_and_process_data(ticker, time_period)
            data = ChartBuilder.add_indicators(data, indicators)
            fig = ChartBuilder.build_chart(data, ticker, indicators, time_period, chart_type)
            return fig
        except Exception as e:
            print(f"Chart generation error: {e}")
            import traceback
            traceback.print_exc()
            return None
