import time
import re

from playwright.sync_api import expect, TimeoutError


class LogoutPage:

    def __init__(self, page):
        self.page = page

    def dismiss_cookie_popup_if_present(self):
        banner = self.page.locator("#onetrust-banner-sdk, #onetrust-group-container").first

        try:
            banner.wait_for(state="visible", timeout=8000)

            possible_buttons = [
                self.page.locator("#onetrust-reject-all-handler"),
                self.page.locator("#onetrust-close-btn-container button"),
                self.page.get_by_role("button", name=re.compile("cancel", re.I)),
                self.page.get_by_role("button", name=re.compile("reject", re.I)),
                self.page.get_by_role("button", name=re.compile("close", re.I)),
                self.page.locator("button:has-text('Cancel')"),
                self.page.locator("button:has-text('Reject')"),
                self.page.locator("button:has-text('Close')"),
            ]

            for button in possible_buttons:
                try:
                    button.first.wait_for(state="visible", timeout=2000)
                    button.first.click()
                    return
                except TimeoutError:
                    pass

        except TimeoutError:
            pass

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

    def click_profile_button(self):
        profile_button = self._find_visible_in_frames(
            "div.user-profile-trigger, button[aria-label*='Profile'], button[aria-label*='profile']",
            timeout=10000
        )
        profile_button.click()

    def click_logout_option(self):
        logout_option = self._find_visible_in_frames(
            "a.user-profile-menu-item:has-text('Logout'), a[href*='auth'][href*='logout'], a[href*='logout']",
            timeout=10000
        )
        logout_option.click()

    def validate_logout_success(self):
        login_sso_button = self._find_visible_in_frames(
            "text=Login using SSO",
            timeout=20000
        )
        expect(login_sso_button).to_be_visible(timeout=20000)

    def logout(self):
        self.dismiss_cookie_popup_if_present()
        self.click_profile_button()
        self.click_logout_option()
        self.validate_logout_success()
