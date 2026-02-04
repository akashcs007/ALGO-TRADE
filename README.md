# ALGO-TRADE
# Hybrid Trend-Following & Mean Reversion Strategy

## Overview
[cite_start]This project implements an algorithmic trading strategy using the **Backtrader** framework[cite: 3]. The strategy combines trend-following filters with mean-reversion entry signals to trade hourly data (SPY). [cite_start]It includes advanced risk management features such as volatility-based position sizing.

## [cite_start]Setup Instructions [cite: 34]

### Prerequisites
* [cite_start]Python 3.8+ [cite: 44]
* Pip package manager

### Installation
1.  Clone this repository or unzip the project folder.
2.  Install the required dependencies:
    ```bash
    pip install backtrader yfinance matplotlib pandas
    ```

### Running the Strategy
Execute the main script to run the backtest:
```bash
python main.py

# 📈 EMA Trend-Following Trading Strategy (Backtrader)

This project implements a **trend-following tactical buy-and-hold trading strategy** using
**EMA(50/200) crossover** with **ATR-based risk management**, backtested on SPY market data
using **Backtrader** and **Yahoo Finance**.

The goal is to stay invested during strong market uptrends while exiting during trend reversals,
thereby maximizing returns and minimizing drawdowns.

---

## 🚀 Strategy Overview

**Core Idea:**  
Markets trend upward over the long term. Instead of frequent trading, this strategy:
- Enters only during confirmed uptrends
- Exits during trend reversals
- Uses wide ATR-based stops to avoid noise
- Minimizes overtrading

---

## 🧠 Trading Logic

### Entry Rule
- EMA(50) crosses **above** EMA(200) (Golden Cross)

### Exit Rules
- EMA(50) crosses **below** EMA(200) (Trend reversal)
- ATR-based stop loss is hit

### Risk Management
- 95% capital allocation per trade
- ATR(14) × 8 wide stop-loss
- Low trade frequency to reduce transaction costs
