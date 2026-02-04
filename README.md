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
