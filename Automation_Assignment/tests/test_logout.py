from pages.login_page import LoginPage
from pages.logout import LogoutPage
from utils.config import BASE_URL, USERNAME, PASSWORD


def test_validate_logout(page):

    login_page = LoginPage(page)
    login_page.login(BASE_URL, USERNAME, PASSWORD)
    login_page.validate_login_success()

    logout_page = LogoutPage(page)
    logout_page.logout()