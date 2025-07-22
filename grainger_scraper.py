import asyncio
from playwright.async_api import async_playwright

URL = "https://www.grainger.com/category/fasteners/washers/flat-washers?attrs=Material%7CTitanium"

async def scrape_flat_washers():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Set headless=False to watch the browser
        page = await browser.new_page()
        await page.goto(URL)
        await page.wait_for_selector('tr[aria-label^="Product"]')

        rows = await page.query_selector_all('tr[aria-label^="Product"]')
        print(f"Found {len(rows)} product rows")

        for row in rows:
            cells = await row.query_selector_all('td')
            size = await cells[0].get_attribute('title')
            inside_dia = await cells[1].get_attribute('title')
            outside_dia = await cells[2].get_attribute('title')
            thickness = await cells[3].get_attribute('title')
            standard = await cells[4].get_attribute('title')
            price_span = await cells[5].query_selector('span.O6u-EO')
            price = await price_span.inner_text() if price_span else "N/A"
            sku_link = await cells[5].query_selector('a')
            sku = await sku_link.inner_text() if sku_link else "N/A"
            product_url = await sku_link.get_attribute('href') if sku_link else None
            if product_url:
                product_url = "https://www.grainger.com" + product_url

            print(f"SKU: {sku}, Price: {price}, Size: {size}, Inside Dia: {inside_dia}, URL: {product_url}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_flat_washers())
