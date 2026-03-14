import asyncio
import json
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def run_scraper(url):
    # 确保 output 文件夹存在（逻辑严密性的体现）
    if not os.path.exists('../../../output'):
        os.makedirs('../../../output')

    async with async_playwright() as p:
        # 模拟真实浏览器，防止被反爬虫瞬间封杀
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            html_content = await page.content()
            soup = BeautifulSoup(html_content, 'html.parser')

            # 提取逻辑：这里只抓取有意义的文本
            data_points = []
            for element in soup.find_all(['h1', 'h2', 'p']):
                text = element.get_text(strip=True)
                if len(text) > 5:  # 过滤掉无意义的短字符
                    data_points.append({"type": element.name, "text": text})

            # 保存到指定的 output 文件夹
            file_path = '../../../output/scraped_data.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_points, f, ensure_ascii=False, indent=4)

            print(f"Success: Processed {len(data_points)} items. Saved to {file_path}")

        except Exception as e:
            print(f"Error: {str(e)}")
        finally:
            await browser.close()


if __name__ == "__main__":
    target = "https://bing.com"  # 练习时改这里
    asyncio.run(run_scraper(target))