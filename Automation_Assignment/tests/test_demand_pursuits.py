from pages.login_page import LoginPage
from pages.demand_pursuit_page import DemandPursuitPage
from utils.config import BASE_URL, USERNAME, PASSWORD


def test_existing_demand_pursuit_search_by_client_name(page):
    login_page = LoginPage(page)
    login_page.login(BASE_URL, USERNAME, PASSWORD)
    login_page.validate_login_success()
    demand_pursuit_page = DemandPursuitPage(page)
    demand_pursuit_page.close_cookies_if_present()
    demand_pursuit_page.open_demand_pursuit_page()

    row_expected = {
        "client_name": "UI191405",
        "pursuit_name": "Devvvv",
        "pursuit_id": "PS-490",
        "jupiter_id": "D22",
        "country": "Albania",
        "proposal_type": "Orals",
        "status": "New",
        "start_date": "2026-05-15",
        "end_date": "2026-06-30",
    }

    detail_expected = {
        "pursuit_name": "Devvvv",
        "pursuit_id": "PS-490",
        "start_date": "2026-05-15",
        "end_date": "2026-06-30",
        "proposal_type": "Orals",
        "billing_arrangement": "T&M",
        "industry": "Cross Industry",
        "sector": "Not applicable",
        "pursuit_creator": "hashedintestuser108FirstN hashedintestuser108LastN",
        "project_type": "Data Modernization",
        "jupiter_id": "D22",
        "country": "Albania",
        "utilizing_ai_assist": "Yes",
        "reference": "No reference links available",
        "description": "No description available",
        "no_members_assigned_count": 4,
    }

    demand_pursuit_page.validate_pursuit_visible_by_client_name(
        category_name="All",
        client_name=row_expected["client_name"]
    )

    demand_pursuit_page.validate_row_data_by_client_name(
        client_name=row_expected["client_name"],
        expected_data=row_expected
    )

    demand_pursuit_page.open_pursuit_from_table_by_client_name(
        client_name=row_expected["client_name"]
    )

    demand_pursuit_page.validate_pursuit_details(detail_expected)
