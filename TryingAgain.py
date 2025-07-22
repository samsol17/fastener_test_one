import asyncio
from playwright.async_api import async_playwright

async def scrape_fastenal(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        print("test 1")

        # Wait for price and title to load
        await page.wait_for_selector('utf-8')
        print ("test 2")
        price = await page.locator('span.font-weight-600').inner_text()

        sku_label = await page.locator("td.font-weight-600", has_text="Fastenal Part No. (SKU)").first
        title = await sku_label.locator("xpath=following-sibling::td[1]").inner_text()

        # Specs are in a table under #attributeTable
        specs = {}
        rows = await page.locator('#attributeTable tr').all()
        for row in rows:
            cells = await row.locator('td').all()
            if len(cells) == 2:
                key = (await cells[0].inner_text()).strip()
                val = (await cells[1].inner_text()).strip()
                specs[key] = val

        await browser.close()

        return {
            'title': title,
            'price': price,
            'specs': specs
        }

# Run it
if __name__ == "__main__":
    url = "https://www.fastenal.com/products/details/70144"  # example URL
    scraped = asyncio.run(scrape_fastenal(url))
    print(scraped)
