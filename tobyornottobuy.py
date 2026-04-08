#!/usr/bin/env python3

import yfinance as yf
import pandas as pd
import steamlit as st

def grade_stock(ticker_symbol):
    try:
        # 1. Fetch 1 month of data to ensure we have a solid 2-week buffer
        stock = yf.Ticker(ticker_symbol)
        df = stock.history(period="1mo")

        if len(df) < 10:
            return {"error": "Not enough historical data."}

        # Slice for the last 14 days
        two_weeks = df.tail(14)
        
        # --- METRIC 1: PRICE MOMENTUM (0-50 points) ---
        start_price = two_weeks['Close'].iloc[0]
        end_price = two_weeks['Close'].iloc[-1]
        price_change_pct = ((end_price - start_price) / start_price) * 100
        
        # Score: 5% gain gives full points, negative gain gives 0
        momentum_score = max(0, min(50, (price_change_pct / 5) * 50))

        # --- METRIC 2: VOLATILITY STABILITY (0-25 points) ---
        # We calculate the standard deviation of daily returns
        daily_returns = two_weeks['Close'].pct_change()
        volatility = daily_returns.std()
        
        # Lower volatility is better for a "safe" grade. 
        # Benchmark: 0.02 (2%) is standard. 0.05 is high.
        vol_score = max(0, 25 - (volatility * 500)) 

        # --- METRIC 3: VOLUME STRENGTH (0-25 points) ---
        # Comparing the last 14 days avg volume to the previous month's avg
        avg_vol_2w = two_weeks['Volume'].mean()
        avg_vol_1m = df['Volume'].mean()
        volume_ratio = avg_vol_2w / avg_vol_1m
        
        # If volume is higher than the monthly average, it's a "confirmed" move
        volume_score = max(0, min(25, (volume_ratio * 12.5)))

        # --- FINAL CALCULATION ---
        total_score = momentum_score + vol_score + volume_score
        
        return {
            "ticker": ticker_symbol.upper(),
            "final_score": round(total_score, 2),
            "price_change": f"{round(price_change_pct, 2)}%",
            "grade": "A" if total_score > 80 else "B" if total_score > 60 else "C" if total_score > 40 else "D"
        }

    except Exception as e:
        return {"error": str(e)}

# --- WHAT SHOWS TO SCREEN ---
symbol = st.text_input("Enter an NYSE Ticker (e.g., AAPL): ")
result = grade_stock(symbol)

if "error" in result:
    st.write(f"Error: {result['error']}")
else:
    st.write(f"\n--- {result['ticker']} REPORT ---")
    st.write(f"Score: {result['final_score']}/100")
    st.write(f"Grade: {result['grade']}")
    st.write(f"2-Week Movement: {result['price_change']}")
