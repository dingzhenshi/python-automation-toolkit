import asyncio
import csv
from datetime import datetime
from playwright.async_api import async_playwright


class UniversalScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.results = []

    async def scroll_to_bottom(self, page):
        """处理动态加载：自动滚动到底部"""
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2)  # 等待新内容加载

    async def scrape(self, url, selector):
        async with async_playwright() as p:
            # 模拟真实浏览器，防止第一秒就被封
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            print(f"[*] 正在访问: {url}")
            await page.goto(url, wait_until="networkidle")

            # 自动处理动态加载
            await self.scroll_to_bottom(page)

            # 抓取逻辑
            elements = await page.query_selector_all(selector)
            for el in elements:
                text = await el.inner_text()
                if text:
                    self.results.append({
                        "content": text.strip(),
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

            await browser.close()
            print(f"[+] 抓取完成，共获得 {len(self.results)} 条数据")

    def save_to_csv(self, filename="../../examples/scraped_data.csv"):
        """专业的数据导出逻辑"""
        if not self.results:
            return
        keys = self.results[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.results)
        print(f"[!] 数据已存入: {filename}")


async def main():
    # 测试案例：抓取百度热搜（或者任何你想测试的简单页面）
    scraper = UniversalScraper(headless=False)
    await scraper.scrape("https://www.baidu.com", "span.title-content-title")
    scraper.save_to_csv()


if __name__ == "__main__":
    asyncio.run(main())