import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navigating to frontend...")
        await page.goto("http://localhost:5173/keywords", wait_until="networkidle")
        
        print("Waiting for input...")
        await page.wait_for_selector('input[placeholder="New keyword..."]')
        await page.fill('input[placeholder="New keyword..."]', "Test Playwright")
        
        print("Clicking Add button...")
        await page.click('button:has-text("Add")')
        
        print("Waiting for a moment...")
        await asyncio.sleep(2)
        
        # Check if toast appeared
        content = await page.content()
        if "Keyword Added" in content:
            print("SUCCESS: Keyword Added toast appeared.")
        elif "Failed" in content:
            print("ERROR: Failed toast appeared.")
        else:
            print("WARNING: No toast appeared.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
