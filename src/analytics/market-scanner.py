import yfinance as yf
import pandas as pd
import numpy as np
import os
import time

# --- 全局环境配置 (必须保留你的 VPN 端口) ---
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'

# ==========================================
# 雷达配置区：把你想监控的股票全扔进这个列表
# 注意：股票代码必须严格按照雅虎财经的标准格式！
# ==========================================
WATCHLIST = ["NVDA", "AAPL", "MSFT", "TSLA", "BRK-B", "VNM", "GOOGL"]
INITIAL_CAPITAL = 14000.0


def scan_single_stock(ticker):
    """静默扫描单只股票，只返回最终的核心数据，不打印废话"""
    try:
        # 静默获取数据，屏蔽冗长的报错
        df = yf.Ticker(ticker).history(period="6mo")
        if df.empty:
            return None

        # 核心逻辑计算 (与单体脚本保持一致)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + gain / loss))

        df['Signal'] = 0
        df['Signal'] = np.where(df['RSI'] < 30, 1, df['Signal'])
        df['Signal'] = np.where(df['RSI'] > 70, -1, df['Signal'])

        # 静默回测引擎
        cash = INITIAL_CAPITAL
        shares = 0
        for date, row in df.iterrows():
            if row['Signal'] == 1 and cash > 0:
                shares_to_buy = int(cash / row['Close'])
                if shares_to_buy > 0:
                    cash -= shares_to_buy * row['Close']
                    shares += shares_to_buy
            elif row['Signal'] == -1 and shares > 0:
                cash += shares * row['Close']
                shares = 0

        final_price = df['Close'].iloc[-1]
        portfolio_value = cash + (shares * final_price)
        roi = ((portfolio_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100

        # 获取当前最新状态
        current_rsi = df['RSI'].iloc[-1]
        current_price = final_price

        # 判定当前操作建议
        if current_rsi < 30:
            action = "🟢 BUY (超卖)"
        elif current_rsi > 70:
            action = "🔴 SELL (超买)"
        else:
            action = "⚪ HOLD (观望)"

        return {
            "Ticker": ticker,
            "Current Price": round(current_price, 2),
            "Current RSI": round(current_rsi, 2),
            "6mo ROI (%)": round(roi, 2),
            "Action": action
        }

    except Exception:
        # 遇到退市或错误代码，直接返回 None，不让系统崩溃
        return None


def run_scanner():
    print(f"[*] 雷达启动！正在扫描 {len(WATCHLIST)} 只标的...\n")
    results = []

    for ticker in WATCHLIST:
        print(f"  -> 正在扫描 {ticker}...")
        data = scan_single_stock(ticker)
        if data:
            results.append(data)
        else:
            print(f"     [!] 无法获取 {ticker} 的数据，已跳过。")

        # 停顿 0.5 秒，防止雅虎财经再次因为请求过快把你的 IP 关进小黑屋
        time.sleep(0.5)

    print("\n[*] 扫描完成！正在生成分析排行表...\n")

    # 将结果转化为 Pandas 数据表，方便排序和展示
    if results:
        df_results = pd.DataFrame(results)
        # 按照 6 个月的回测收益率 (ROI) 从高到低排序
        df_results = df_results.sort_values(by="6mo ROI (%)", ascending=False).reset_index(drop=True)

        print("===================== 量化扫描结果报告 =====================")
        print(df_results.to_string())
        print("============================================================")
    else:
        print("[-] 扫描失败，未能获取任何有效数据。请检查网络。")


if __name__ == "__main__":
    run_scanner()