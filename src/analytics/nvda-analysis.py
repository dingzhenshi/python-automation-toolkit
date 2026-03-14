import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# ==========================================
# 核心控制台：目标标的与初始资金
# ==========================================
TARGET_TICKER = "VNM"  # 你的观测目标
INITIAL_FUNDS = 14000.0  # 初始资金 (美元)

# --- 全局环境配置 (你的专属网络通道) ---
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'


def analyze_and_generate_signals(ticker):
    """负责数据获取与信号生成的黑盒"""
    print(f"[*] 正在获取 {ticker} 的历史数据并生成量化信号...")
    try:
        df = yf.Ticker(ticker).history(period="6mo")
        if df.empty: return None

        # 计算指标
        df['MA20'] = df['Close'].rolling(window=20).mean()
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + gain / loss))

        # 生成信号与标价
        df['Signal'] = 0
        df['Signal'] = np.where(df['RSI'] < 30, 1, df['Signal'])
        df['Signal'] = np.where(df['RSI'] > 70, -1, df['Signal'])
        df['Buy_Signal_Price'] = np.where(df['Signal'] == 1, df['Close'], np.nan)
        df['Sell_Signal_Price'] = np.where(df['Signal'] == -1, df['Close'], np.nan)

        return df
    except Exception as e:
        print(f"[-] 核心算法崩溃: {e}")
        return None


def run_backtest(df, initial_capital):
    """新增模块：历史回测引擎，计算真实收益率"""
    print(f"\n[*] 启动历史回测 (初始资金: ${initial_capital:,.2f})...")

    cash = initial_capital
    shares = 0
    trade_log = []

    # 遍历每一天的数据，模拟真实交易
    for date, row in df.iterrows():
        # 遇到买入信号，且手里有钱 -> 全仓买入
        if row['Signal'] == 1 and cash > 0:
            shares_to_buy = int(cash / row['Close'])  # 向下取整买入股数
            if shares_to_buy > 0:
                cost = shares_to_buy * row['Close']
                cash -= cost
                shares += shares_to_buy
                trade_log.append(
                    f"买入 | {date.strftime('%Y-%m-%d')} | 价格: ${row['Close']:.2f} | 数量: {shares_to_buy} | 剩余现金: ${cash:.2f}")

        # 遇到卖出信号，且手里有票 -> 全部清仓
        elif row['Signal'] == -1 and shares > 0:
            revenue = shares * row['Close']
            cash += revenue
            trade_log.append(
                f"卖出 | {date.strftime('%Y-%m-%d')} | 价格: ${row['Close']:.2f} | 数量: {shares} | 获得现金: ${cash:.2f}")
            shares = 0

    # 结算最终净值
    final_price = df['Close'].iloc[-1]
    portfolio_value = cash + (shares * final_price)
    roi = ((portfolio_value - initial_capital) / initial_capital) * 100

    print("\n--- 历史回测交易日志 ---")
    if not trade_log:
        print("过去半年内未触发任何完整交易信号。")
    else:
        for log in trade_log: print(log)

    print("\n--- 回测结果摘要 ---")
    print(f"初始资金: ${initial_capital:,.2f}")
    print(f"最终净值: ${portfolio_value:,.2f}")
    print(f"总收益率: {roi:.2f}%")
    print(f"当前状态: {'空仓' if shares == 0 else f'持仓 {shares} 股'}")


def plot_signals(df, ticker):
    """负责图表绘制的画笔"""
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    ax1.plot(df.index, df['Close'], label='Close Price', color='#3498db', alpha=0.6)
    ax1.plot(df.index, df['MA20'], label='MA20 Trend', color='#f39c12', linestyle='--')
    ax1.set_title(f'{ticker} - Automated Trading Signals', fontsize=14, fontweight='bold')
    ax1.scatter(df.index, df['Buy_Signal_Price'], marker='^', color='#2ecc71', s=100, zorder=5, label='Buy (RSI < 30)')
    ax1.scatter(df.index, df['Sell_Signal_Price'], marker='v', color='#e74c3c', s=100, zorder=5,
                label='Sell (RSI > 70)')
    ax1.set_ylabel('Price (USD)')
    ax1.legend(loc='upper left')

    ax2.plot(df.index, df['RSI'], label='RSI (14-day)', color='#9b59b6')
    ax2.axhline(70, color='#e74c3c', linestyle=':')
    ax2.axhline(30, color='#2ecc71', linestyle=':')
    ax2.fill_between(df.index, 70, 100, color='#e74c3c', alpha=0.1)
    ax2.fill_between(df.index, 0, 30, color='#2ecc71', alpha=0.1)
    ax2.set_title(f'{ticker} RSI Indicator', fontsize=12)
    ax2.set_ylabel('RSI Value')
    ax2.set_ylim(0, 100)
    ax2.legend(loc='upper left')

    plt.tight_layout()
    plt.show()


# --- 主程序大脑 ---
if __name__ == "__main__":
    result_data = analyze_and_generate_signals(TARGET_TICKER)

    if result_data is not None:
        # 1. 先跑回测算钱
        run_backtest(result_data, INITIAL_FUNDS)
        # 2. 再画图表看趋势
        plot_signals(result_data, TARGET_TICKER)