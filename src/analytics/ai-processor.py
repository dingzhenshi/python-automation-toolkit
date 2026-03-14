import json
import requests
import os

def process_data_with_ai(api_key):
    # 逻辑检查：确保刚才抓取的数据文件存在
    input_file = '../../../output/scraped_data.json'
    if not os.path.exists(input_file):
        print(f"[!] 找不到文件 {input_file}，请先运行抓取脚本！")
        return

    # 1. 读取抓取到的原始数据
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 2. 构造给 AI 的指令（这是你值钱的地方）
    prompt = f"""You are an AI Data Scientist specializing in LLM Fine-tuning.I have scraped the following raw JSON data:{json.dumps(raw_data, ensure_ascii=False)}"
    prompt += "TASK: Convert this raw data into a high-quality 'Synthetic Dataset' for AI Training.
REQUIREMENTS:
1. Translate all content into English.
2. For each significant data point, generate a 'Context-Question-Answer' triplet.
3. Format the output as a clean JSONL-style structure.
4. Focus on extracting factual entities and their relationships."""

    # 3. 调用 API
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}]
    }

    print("[*] 正在请求 DeepSeek 处理数据，请稍候...")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=300)
        if response.status_code == 200:
            result = response.json()['choices'][0]['message']['content']
            # 保存成果
            with open('../../../output/ai_analysis_report.txt', 'w', encoding='utf-8') as f:
                f.write(result)
            print("[+] 处理成功！请查看 output/ai_analysis_report.txt")
        else:
            print(f"[!] API 报错：{response.status_code} - {response.text}")
    except Exception as e:
        print(f"[!] 网络连接失败：{str(e)}")

# --- 关键：在这里扣动扳机 ---
if __name__ == "__main__":
    # 替换成你刚才在官网申请的那个 sk- 开头的字符串
    MY_SECRET_KEY = ""
    process_data_with_ai(MY_SECRET_KEY)