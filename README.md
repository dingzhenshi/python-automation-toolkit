# Python Quantitative Trading Automation Toolkit

A lightweight, robust Python toolkit designed for automated stock market analysis, quantitative signal generation, and historical backtesting. Built to bypass basic API rate limits and deliver actionable trading insights.

## 🛠️ Core Modules

### 1. Market Radar Scanner (`src/analytics/market_scanner.py`)
A batch-processing engine that scans a customizable watchlist of assets to identify market extremes.
* **Silent Execution**: Gracefully handles delisted or erroneous tickers without crashing the pipeline.
* **Historical Backtesting Engine**: Simulates trading over a 6-month period based on RSI thresholds (Buy < 30, Sell > 70) with a hypothetical $14,000 initial capital.
* **Automated Ranking**: Outputs a sorted terminal dashboard ranking assets by absolute ROI (Return on Investment).

### 2. Deep-Dive Visualizer (`src/analytics/nvda-analysis.py`)
A single-asset diagnostic tool that translates raw financial data into professional-grade trading charts.
* **Dynamic Target Selection**: Easily switch analyzing targets (e.g., AAPL, TSLA, NVDA) via a single global variable.
* **Algorithmic Signal Plotting**: Automatically renders absolute Buy (▲) and Sell (▼) markers directly onto historical price curves.
* **Matplotlib Rendering**: Generates dual-axis charts featuring price action, moving averages (MA20), and overbought/oversold indicator zones.

## ⚙️ Technical Highlights
* **Data Sourcing**: Integrates `yfinance` for reliable historical market data extraction.
* **Vectorized Logic**: Utilizes `numpy.where()` for high-speed, loop-free signal generation.
* **Anti-Scraping**: Configured with local proxy routing mechanisms (HTTP/HTTPS) to bypass API connection resets and rate limits.

## 🚀 How to Run
1. Ensure dependencies are installed: `pip install yfinance pandas matplotlib numpy`
2. Run the market scanner to find the best ROI:
   ```bash
   python src/analytics/market_scanner.py
