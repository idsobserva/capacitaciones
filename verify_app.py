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

        # Give it some time to initialize Firebase and modules
        await page.wait_for_timeout(2000)

        # Check if basic functions are global
        funcs = ["doLogin", "doRegister", "authTab", "showView"]
        for f in funcs:
            is_func = await page.evaluate(f"typeof window.{f} === 'function'")
            print(f"window.{f} is function: {is_func}")

        # Try to click the 'Registrarse' tab
        try:
            await page.click("text=Registrarse")
            await page.wait_for_timeout(500)
            is_visible = await page.is_visible("#tab-reg")
            print(f"Register tab visible: {is_visible}")
        except Exception as e:
            print(f"Error clicking Registrarse: {e}")

        await page.screenshot(path="app_screenshot.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
