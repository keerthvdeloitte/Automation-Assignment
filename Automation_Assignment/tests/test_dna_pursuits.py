from pages.login_page import LoginPage
from utils.config import BASE_URL, USERNAME, PASSWORD


def test_login(page):
    login_page = LoginPage(page)
    login_page.login(BASE_URL, USERNAME, PASSWORD)
    login_page.validate_login_success()
