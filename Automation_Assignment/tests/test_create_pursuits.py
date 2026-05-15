import time

from pages.login_page import LoginPage
from pages.create_pursuit_page import CreatePursuitPage
from utils.config import BASE_URL, USERNAME, PASSWORD


def test_create_pursuit(page):
    login_page = LoginPage(page)
    login_page.login(BASE_URL, USERNAME, PASSWORD)
    login_page.validate_login_success()

    create_pursuit_page = CreatePursuitPage(page)
    create_pursuit_page.open_create_pursuit()
    unique_id = int(time.time())
    client_name = f"Auto Client {unique_id}"
    pursuit_name = f"Auto Pursuit {unique_id}"
    create_pursuit_page.create_new_client(client_name)



    create_pursuit_page.create_pursuit(
        client_name=client_name,
        pursuit_name=pursuit_name,
        start_date="05/20/2026",
        end_date="06/20/2026",
        description="Automation-created pursuit for validation.",
        reference="Automation reference"
    )

