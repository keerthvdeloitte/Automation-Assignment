from pages.login_page import LoginPage
from pages.dashboard import DashboardPage
from utils.config import BASE_URL, USERNAME, PASSWORD


def test_dashboard(page):
    login_page = LoginPage(page)
    dashboard_page = DashboardPage(page)

    login_page.login(BASE_URL, USERNAME, PASSWORD)
    login_page.validate_login_success()
    dashboard_page.validate_dashboard()
