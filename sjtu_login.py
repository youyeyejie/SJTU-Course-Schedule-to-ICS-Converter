"""Read course arrangements through the official teaching portal."""

from urllib.parse import urlsplit

from playwright.sync_api import Error as BrowserError, TimeoutError as BrowserTimeout, sync_playwright

TEACHING_HOST = "i.sjtu.edu.cn"
TEACHING_URL = f"https://{TEACHING_HOST}"
SCHEDULE_URL = f"{TEACHING_URL}/kbcx/xskbcx_cxXsKb.html"


def fetch_course_rows(request, year, term):
    response = request.post(
        SCHEDULE_URL,
        params={"gnmkdm": "N2151"},
        form={"xnm": year, "xqm": (3, 12, 16)[term - 1]},
    )
    try:
        url = urlsplit(response.url)
        if url.hostname != TEACHING_HOST or url.path in ("/xtgl/login_slogin.html", "/jaccountlogin"):
            raise RuntimeError("教务网会话已失效，请重新运行并登录。")
        if not response.ok:
            raise RuntimeError(f"教务网课表查询失败（HTTP {response.status}）。")
        rows = response.json()["kbList"]
        if not isinstance(rows, list):
            raise ValueError("Invalid course list")
        return rows
    finally:
        response.dispose()


def fetch_courses(year, term):
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=False)
        except BrowserError:
            raise RuntimeError("无法启动登录浏览器，请运行 python -m playwright install chromium。") from None
        try:
            context = browser.new_context()
            page = context.new_page()
            print("请在交大官方页面完成 jAccount 登录，支持「交我办」扫码。", flush=True)
            page.goto(f"{TEACHING_URL}/jaccountlogin", wait_until="domcontentloaded")
            page.locator("input#sessionUserKey").wait_for(state="attached", timeout=300_000)
            if urlsplit(page.url).hostname != TEACHING_HOST:
                raise RuntimeError("未获取到教务网学生登录信息，请检查当前登录身份。")
            return fetch_course_rows(context.request, year, term)
        except BrowserTimeout:
            raise RuntimeError("教务网操作超时，请检查网络并重新登录。") from None
        except BrowserError:
            raise RuntimeError("教务网无法访问或浏览器已关闭，请重新运行。") from None
        except (ValueError, KeyError, TypeError):
            raise RuntimeError("教务网返回了无法识别的课表数据。") from None
        finally:
            browser.close()
