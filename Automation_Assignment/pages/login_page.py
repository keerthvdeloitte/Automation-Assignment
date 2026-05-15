import time
from playwright.sync_api import expect


class LoginPage:
    def __init__(self, page):
        self.page = page

    def open_url(self, url):
        self.page.goto(url)

    def click_login_sso(self):
        self.page.get_by_text("Login using SSO").click()
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_timeout(1500)

    def _find_visible_in_frames(self, selector, timeout=15000):
        end_time = time.time() + (timeout / 1000)

        while time.time() < end_time:
            for frame in self.page.frames:
                locators = frame.locator(selector)
                count = locators.count()

                for i in range(count):
                    candidate = locators.nth(i)
                    if candidate.is_visible():
                        return candidate

            self.page.wait_for_timeout(250)

        raise AssertionError(f"No visible element found for selector: {selector}")

    def enter_username(self, username):
        username_input = self._find_visible_in_frames(
            "#signInFormUsername, input[name='username'], input[placeholder='Username']"
        )
        username_input.fill(username)

    def click_next_if_present(self):
        try:
            next_button = self._find_visible_in_frames(
                "button:has-text('Next'), input[value='Next']",
                
            )
            next_button.click()
        except AssertionError:
            pass

    def enter_password(self, password):
        password_input = self._find_visible_in_frames("input[type='password']")
        password_input.fill(password)

    def click_sign_in(self):
        try:
            sign_in_button = self._find_visible_in_frames(
                "button:has-text('Sign in'), button:has-text('Login'), input[type='submit']",
                timeout=5000
            )
            sign_in_button.click()
        except AssertionError:
            pass

    def handle_stay_signed_in_if_present(self):
        try:
            no_button = self._find_visible_in_frames(
                "button:has-text('No'), input[value='No']",
                timeout=5000
            )
            no_button.click()
        except AssertionError:
            pass

    def login(self, url, username, password):
        self.open_url(url)
        self.click_login_sso()
        self.enter_username(username)
        #self.click_next_if_present()
        self.enter_password(password)
        self.click_sign_in()
        self.handle_stay_signed_in_if_present()

    def validate_login_success(self):
        expect(self.page.get_by_text("Demand Pursuits")).to_be_visible(timeout=15000)
        assert "pursuits" in self.page.url.lower()
