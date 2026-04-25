import numpy as np
import pandas as pd
import talib
import yfinance as yf


class YahooTechnicalAnalyser:
    def __init__(self, ticker: str):
        self.ticker = ticker

    def _enrich_with_technical_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Enriches a DataFrame containing stock data with various technical indicators.
        Args:
            data (pd.DataFrame): Input DataFrame with columns like 'Close', 'High', 'Low', 'Volume'.
        Returns:
            pd.DataFrame: The original DataFrame with added technical indicator columns.
        """
        enriched_data = data.copy()

        close_prices = data["Close"].values.flatten().astype("float64")
        high_prices = data["High"].values.flatten().astype("float64")
        low_prices = data["Low"].values.flatten().astype("float64")
        volume = data["Volume"].values.flatten().astype("float64")

        # Basic Moving Averages (SMA)
        for ma_period in [20, 50, 100, 200]:
            enriched_data[f"{ma_period}_MA"] = talib.SMA(close_prices, timeperiod=ma_period)

        # Exponential Moving Averages (EMA)
        for ema_period in [20, 50, 100, 200]:
            enriched_data[f"{ema_period}_EMA"] = talib.EMA(close_prices, timeperiod=ema_period)

        # MACD
        macd_line, signal_line, macd_hist = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
        enriched_data["MACD"] = macd_line
        enriched_data["Signal_Line"] = signal_line
        enriched_data["MACD_Histogram"] = macd_hist

        # RSI
        enriched_data["RSI"] = talib.RSI(close_prices, timeperiod=14)

        # Bollinger Bands
        upper_band, middle_band, lower_band = talib.BBANDS(close_prices)
        enriched_data["Upper_Band"] = upper_band
        enriched_data["Middle_Band"] = middle_band
        enriched_data["Lower_Band"] = lower_band

        # Stochastic Oscillator
        fastk, fastd = talib.STOCHF(high_prices, low_prices, close_prices)
        enriched_data["%K"] = fastk
        enriched_data["%D"] = fastd

        # Average True Range (ATR)
        enriched_data["ATR"] = talib.ATR(high_prices, low_prices, close_prices, timeperiod=14)

        # On-Balance Volume (OBV)
        enriched_data["OBV"] = talib.OBV(close_prices, volume)

        # Volume Moving Average
        enriched_data["Volume_MA"] = talib.SMA(volume, timeperiod=20)

        return enriched_data

    def _enrich_with_advanced_features(
        self,
        df: pd.DataFrame,
        rsi_oversold_threshold: float = 30.0,
        rsi_overbought_threshold: float = 70.0,
        stoch_oversold_threshold: float = 20.0,
        stoch_overbought_threshold: float = 80.0,
        stoch_cross_oversold_zone: float = 30.0,
        stoch_cross_overbought_zone: float = 70.0,
        bollinger_squeeze_threshold_pct: float = 0.05,
        volume_spike_multiplier: float = 2.0,
        slope_period_short: int = 5,
    ) -> pd.DataFrame:
        """
        Enriches a DataFrame containing financial technical indicators with additional
        event-based, state-based, and relational features.

        Args:
            df (pd.DataFrame): Input DataFrame with columns like 'Close', '20_MA', '50_MA',
                            '200_MA', 'RSI', 'MACD', 'Signal_Line', 'MACD_Histogram',
                            'Upper_Band', 'Middle_Band', 'Lower_Band', '%K', '%D',
                            'ATR', 'OBV', 'Volume', 'Volume_MA'.
            rsi_oversold_threshold (float): RSI value below which it's considered oversold.
            rsi_overbought_threshold (float): RSI value above which it's considered overbought.
            stoch_oversold_threshold (float): Stochastic %K value below which it's considered oversold.
            stoch_overbought_threshold (float): Stochastic %K value above which it's considered overbought.
            stoch_cross_oversold_zone (float): %K must be below this for a bullish stochastic cross to be valid.
            stoch_cross_overbought_zone (float): %K must be above this for a bearish stochastic cross to be valid.
            bollinger_squeeze_threshold_pct (float): Percentage width ((Upper-Lower)/Middle)
                                                    below which a Bollinger Squeeze is identified.
            volume_spike_multiplier (float): Multiplier for Volume_MA to identify a volume spike.
            slope_period_short (int): Lookback period for simple slope/trend calculations.


        Returns:
            pd.DataFrame: The original DataFrame with added enriched feature columns.
        """
        enriched_df = df.copy()

        # --- 1. MA Crossovers ---
        # Golden Cross (50_MA crosses above 200_MA)
        enriched_df["Golden_Cross_50_200"] = (enriched_df["50_MA"] > enriched_df["200_MA"]) & (
            enriched_df["50_MA"].shift(1) <= enriched_df["200_MA"].shift(1)
        )
        # Death Cross (50_MA crosses below 200_MA)
        enriched_df["Death_Cross_50_200"] = (enriched_df["50_MA"] < enriched_df["200_MA"]) & (
            enriched_df["50_MA"].shift(1) >= enriched_df["200_MA"].shift(1)
        )
        # Short-Term Bullish Cross (20_MA crosses above 50_MA)
        enriched_df["Short_Term_Bullish_Cross_20_50"] = (enriched_df["20_MA"] > enriched_df["50_MA"]) & (
            enriched_df["20_MA"].shift(1) <= enriched_df["50_MA"].shift(1)
        )
        # Short-Term Bearish Cross (20_MA crosses below 50_MA)
        enriched_df["Short_Term_Bearish_Cross_20_50"] = (enriched_df["20_MA"] < enriched_df["50_MA"]) & (
            enriched_df["20_MA"].shift(1) >= enriched_df["50_MA"].shift(1)
        )

        # --- 2. Price vs. MAs ---
        for ma_col in ["20_MA", "50_MA", "100_MA", "200_MA"]:
            if ma_col in enriched_df.columns:
                enriched_df[f"Price_Above_{ma_col}"] = enriched_df["Close"] > enriched_df[ma_col]
                enriched_df[f"Price_Below_{ma_col}"] = enriched_df["Close"] < enriched_df[ma_col]

        # --- 3. RSI States ---
        if "RSI" in enriched_df.columns:
            enriched_df["RSI_Oversold"] = enriched_df["RSI"] < rsi_oversold_threshold
            enriched_df["RSI_Overbought"] = enriched_df["RSI"] > rsi_overbought_threshold

            conditions = [
                (enriched_df["RSI"] < rsi_oversold_threshold),
                (enriched_df["RSI"] > rsi_overbought_threshold),
                (enriched_df["RSI"] >= rsi_oversold_threshold) & (enriched_df["RSI"] <= rsi_overbought_threshold),
            ]
            choices = ["Oversold", "Overbought", "Neutral"]
            enriched_df["RSI_State"] = np.select(conditions, choices, default="Neutral")

            # RSI Trend (simple check over slope_period_short)
            enriched_df[f"RSI_Trending_Up_{slope_period_short}d"] = enriched_df["RSI"].diff(slope_period_short) > 0
            enriched_df[f"RSI_Trending_Down_{slope_period_short}d"] = enriched_df["RSI"].diff(slope_period_short) < 0

        # --- 4. MACD Events ---
        if (
            "MACD" in enriched_df.columns
            and "Signal_Line" in enriched_df.columns
            and "MACD_Histogram" in enriched_df.columns
        ):
            enriched_df["MACD_Bullish_Cross"] = (enriched_df["MACD"] > enriched_df["Signal_Line"]) & (
                enriched_df["MACD"].shift(1) <= enriched_df["Signal_Line"].shift(1)
            )
            enriched_df["MACD_Bearish_Cross"] = (enriched_df["MACD"] < enriched_df["Signal_Line"]) & (
                enriched_df["MACD"].shift(1) >= enriched_df["Signal_Line"].shift(1)
            )

            # MACD Histogram Analysis
            hist_diff = enriched_df["MACD_Histogram"].diff(1)
            enriched_df["MACD_Histogram_Positive_Increasing"] = (enriched_df["MACD_Histogram"] > 0) & (hist_diff > 0)
            enriched_df["MACD_Histogram_Positive_Decreasing"] = (enriched_df["MACD_Histogram"] > 0) & (hist_diff < 0)
            enriched_df["MACD_Histogram_Negative_Increasing"] = (enriched_df["MACD_Histogram"] < 0) & (hist_diff > 0)
            enriched_df["MACD_Histogram_Negative_Decreasing"] = (enriched_df["MACD_Histogram"] < 0) & (hist_diff < 0)

        # --- 5. Bollinger Bands Events ---
        if (
            "Upper_Band" in enriched_df.columns
            and "Lower_Band" in enriched_df.columns
            and "Middle_Band" in enriched_df.columns
        ):
            enriched_df["Price_Above_Upper_Band"] = enriched_df["Close"] > enriched_df["Upper_Band"]
            enriched_df["Price_Below_Lower_Band"] = enriched_df["Close"] < enriched_df["Lower_Band"]

            band_width = (enriched_df["Upper_Band"] - enriched_df["Lower_Band"]) / enriched_df["Middle_Band"]
            enriched_df["Bollinger_Squeeze"] = band_width < bollinger_squeeze_threshold_pct
            enriched_df["Bollinger_Band_Width_Pct"] = band_width * 100

        # --- 6. Stochastic Oscillator States (%K, %D) ---
        if "%K" in enriched_df.columns and "%D" in enriched_df.columns:
            enriched_df["Stoch_Oversold"] = enriched_df["%K"] < stoch_oversold_threshold
            enriched_df["Stoch_Overbought"] = enriched_df["%K"] > stoch_overbought_threshold

            # Stochastic Bullish Cross (K crosses above D in/from oversold zone)
            enriched_df["Stoch_Bullish_Cross"] = (
                (enriched_df["%K"] > enriched_df["%D"])
                & (enriched_df["%K"].shift(1) <= enriched_df["%D"].shift(1))
                & (enriched_df["%K"].shift(1) < stoch_cross_oversold_zone)
            )

            # Stochastic Bearish Cross (K crosses below D in/from overbought zone)
            enriched_df["Stoch_Bearish_Cross"] = (
                (enriched_df["%K"] < enriched_df["%D"])
                & (enriched_df["%K"].shift(1) >= enriched_df["%D"].shift(1))
                & (enriched_df["%K"].shift(1) > stoch_cross_overbought_zone)
            )

        # --- 7. Volume Spikes ---
        if "Volume" in enriched_df.columns and "Volume_MA" in enriched_df.columns:
            enriched_df["Volume_Spike"] = enriched_df["Volume"] > (enriched_df["Volume_MA"] * volume_spike_multiplier)

        # --- 8. Relational/Comparative Features ---
        for ma_col in ["20_MA", "50_MA", "100_MA", "200_MA"]:
            if ma_col in enriched_df.columns and "Close" in enriched_df.columns:
                enriched_df[f"Pct_Diff_Price_vs_{ma_col}"] = (
                    (enriched_df["Close"] - enriched_df[ma_col]) / enriched_df[ma_col].replace(0, np.nan)
                ) * 100

        if "ATR" in enriched_df.columns and "Close" in enriched_df.columns:
            enriched_df["ATR_Pct"] = (enriched_df["ATR"] / enriched_df["Close"].replace(0, np.nan)) * 100

        # --- 9. Simple Trend/Momentum (Slope) ---
        for ma_col in ["20_MA", "50_MA", "100_MA", "200_MA"]:
            if ma_col in enriched_df.columns:
                ma_diff = enriched_df[ma_col].diff(slope_period_short)
                conditions = [ma_diff > 0, ma_diff < 0]
                choices = ["Positive", "Negative"]
                enriched_df[f"Slope_{ma_col}_{slope_period_short}d"] = np.select(conditions, choices, default="Flat")

        return enriched_df

    def get_technical_data(self, period: str = "1y") -> dict:
        """
        Fetch historical market data and enrich it with technical indicators.
        Args:
            period (str): The period for which to fetch historical data. Default is '1y'.
        Returns:
            dict: A dictionary containing the ticker, last update date, and the latest data.
        """
        data = yf.download(self.ticker, period=period, auto_adjust=True)
        data.columns = data.columns.get_level_values(0)

        enriched_data = self._enrich_with_technical_data(data)
        enriched_data = self._enrich_with_advanced_features(enriched_data)

        latest_data = enriched_data.iloc[-1]
        latest_data_date = latest_data.name.strftime("%Y-%m-%d")

        return {
            "ticker": self.ticker,
            "last_update_date": latest_data_date,
            "latest_data": latest_data.to_dict(),
        }
