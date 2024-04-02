import asyncio
from PIL import Image
from playwright.async_api import async_playwright
from tools import utils
import sys

class DianPingLogin:
    def __init__(self, login_type, browser):
        self.login_type = login_type
        self.browser = browser
        self.browser_context = None
        self.playwright_page = None
        self.cookies = None

    async def begin(self):
        """Start login zhihu"""
        utils.logger.info("[DianPingLogin.begin] Begin login dianping ...")
        if self.login_type == "qrcode":
            await self.login_by_qrcode()
        elif self.login_type == "cookie":
            await self.login_by_cookie()
        else:
            raise ValueError("[DianPingLogin.begin] Invalid Login Type. Currently only supported qrcode or cookie ...")

    async def login_by_qrcode(self):
        utils.logger.info("[DianPingLogin.login_by_qrcode] Begin login dianping by qrcode ...")
        login_status = False
        self.browser_context = await self.browser.new_context()
        await self.browser_context.add_init_script(path="stealth.min.js")
        self.playwright_page = await self.browser_context.new_page()
        await self.playwright_page.goto("https://www.dianping.com/")
        await self.playwright_page.locator("#userinfo > div > div.user-opt > div.user-opt-nologin > a").click()
        utils.logger.info("[DianPingLogin.login_by_qrcode] Waiting for scan code login, remaining time is 20s")
        await self.playwright_page.locator("#app > div > div.main-content > div > div > div.scan-side > img").screenshot(path='qrcode.png')
        qrcode = Image.open('qrcode.png')
        qrcode.show()
        for _ in range(20):
            try:
                if await self.check_login_status():
                    utils.logger.info("[DianPingLogin.login_by_qrcode] login successful!")
                    login_status = True
                    qrcode.close()
                    await self.update_cookie()
                    break
                else:
                    await asyncio.sleep(1)
            except Exception as e:
                utils.logger.error(f"[DianPingLogin.login_by_qrcode] login error: {e}")
                continue
        if not login_status:
            utils.logger.info("[DianPingLogin.login_by_qrcode] login failed, please check ....")
            sys.exit()

    async def login_by_cookie(self):
        utils.logger.info("[DianPingLogin.login_by_cookie] Begin login dianping by cookie ...")
        self.browser_context = await self.browser.new_context(storage_state='login_data.json')
        await self.browser_context.add_init_script(path="stealth.min.js")
        self.playwright_page = await self.browser_context.new_page()
        await self.playwright_page.goto("https://www.dianping.com/")
        # try:
        if await self.check_login_status():
            utils.logger.info("[DianPingLogin.login_by_cookie] dianping login successful!")
            await self.update_cookie()
        else:
            utils.logger.info("[DianPingLogin.login_by_cookie] dianping login failed: cookies has expired!")
            sys.exit()
        # except Exception as e:
        #     utils.logger.error(f"[ZhiHuLogin.login_by_cookie] zhihu login failed: {e}, and try to login again...")
        #     sys.exit()

    async def update_cookie(self):
        cookies = await self.browser_context.cookies()
        await self.browser_context.storage_state(path='login_data.json')
        self.cookies = await self.std_cookies(cookies)


    async def std_cookies(self, cookies: list):
        cookies_std = {}
        for cookie in cookies:
            cookies_std[cookie['name']] = cookie['value']
        return cookies_std

    async def check_login_status(self) -> bool:
        cookies = await self.browser_context.cookies()
        cookies_std = await self.std_cookies(cookies)
        if cookies_std.get("qruuid", "") or cookies_std.get("ll"):
            return True
        return False

# async def main(login_type):
#     async with async_playwright() as playwright:
#         browser = await playwright.chromium.launch(headless=False)
#         dplogin = DianPingLogin(login_type=login_type, browser=browser)
#         await dplogin.begin()
#
# if __name__ == '__main__':
#     asyncio.run(main("qrcode"))
