import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"PAGE ERROR: {exc}"))

        file_path = "file://" + os.path.abspath("index.html")
        await page.goto(file_path)

        await page.wait_for_timeout(1000)

        is_doLogin_global = await page.evaluate("typeof window.doLogin === 'function'")
        print(f"window.doLogin is function: {is_doLogin_global}")

        # Check tabs
        await page.click("text=Registrarse")
        await page.wait_for_timeout(500)
        is_reg_visible = await page.is_visible("#tab-reg")
        print(f"Register tab visible: {is_reg_visible}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
