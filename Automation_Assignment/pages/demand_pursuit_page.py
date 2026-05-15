import re
from datetime import datetime
from playwright.sync_api import expect


class DemandPursuitPage:
    def __init__(self, page):
        self.page = page

    
    def open_demand_pursuit_page(self):
        expect(
            self.page.get_by_text(re.compile(r"^Demand Pursuits$", re.I))
        ).to_be_visible(timeout=15000)

        expect(
            self.page.locator(".pursuit-table-container, .pursuit-data-table").first
        ).to_be_visible(timeout=15000)

    def _normalize_date(self, value):
        if not value:
            return value

        value = value.strip()

        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"):
            try:
                return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
            except ValueError:
                pass

        return value

    def _safe_text(self, locator):
        try:
            return locator.inner_text().strip()
        except Exception:
            return ""

    def _get_search_input(self):
        candidates = [
            self.page.locator("input[placeholder*='Search']").last,
            self.page.locator("input[placeholder*='search']").last,
            self.page.get_by_role("searchbox").last,
            self.page.locator(".pursuit-table-header-flex input").last,
            self.page.locator(".pursuit-table-container input").last,
            self.page.locator("input.ant-input").last,
        ]

        for candidate in candidates:
            try:
                if candidate.count() > 0 and candidate.is_visible():
                    return candidate
            except Exception:
                pass

        return None

    def _open_search(self):
        search_input = self._get_search_input()
        if search_input is not None:
            return search_input

        search_button = self.page.locator("button.pursuit-search-button").first
        expect(search_button).to_be_visible(timeout=10000)
        search_button.click()
        self.page.wait_for_timeout(800)

        search_input = self._get_search_input()
        if search_input is None:
            raise AssertionError("Search input not found after clicking search button")

        return search_input

    def _get_category_card(self, category_name):
        return self.page.locator(".dna-card-tab").filter(
            has=self.page.get_by_text(re.compile(rf"^{re.escape(category_name)}$", re.I))
        ).first

    def _get_table_rows(self):
        return self.page.locator("tbody.ant-table-tbody tr.ant-table-row")

    def _get_row_by_client_name(self, client_name, timeout=15000):
        rows = self._get_table_rows()
        row_count = rows.count()

        for i in range(row_count):
            row = rows.nth(i)
            try:
                client_cell = row.locator("td").nth(0)
                client_text = self._safe_text(client_cell)
                if client_name.strip().lower() in client_text.strip().lower():
                    expect(row).to_be_visible(timeout=timeout)
                    return row
            except Exception:
                pass

        raise AssertionError(f"Row not found for client name: {client_name}")

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

    def _expect_visible_text(self, text_value, timeout=15000):
        if not text_value:
            return

        locator = self.page.get_by_text(re.compile(re.escape(text_value), re.I)).first
        expect(locator).to_be_visible(timeout=timeout)

    def _count_visible_exact_text(self, text_value):
        locator = self.page.get_by_text(re.compile(rf"^{re.escape(text_value)}$", re.I))
        count = locator.count()
        visible_count = 0

        for i in range(count):
            try:
                if locator.nth(i).is_visible():
                    visible_count += 1
            except Exception:
                pass

        return visible_count

    
    def click_category(self, category_name):
        card = self._get_category_card(category_name)
        expect(card).to_be_visible(timeout=10000)
        card.click()
        self.page.wait_for_timeout(1200)

    def search_by_client_name(self, client_name):
        search_input = self._open_search()
        expect(search_input).to_be_visible(timeout=10000)
        search_input.fill("")
        self.page.wait_for_timeout(300)
        search_input.fill(client_name)
        self.page.wait_for_timeout(1500)

        try:
            search_input.press("Enter")
        except Exception:
            pass

        self.page.wait_for_timeout(1500)

    def validate_pursuit_visible_by_client_name(self, category_name, client_name):
        self.click_category(category_name)
        self.search_by_client_name(client_name)
        self._get_row_by_client_name(client_name)

    
    def get_row_data_by_client_name(self, client_name):
        row = self._get_row_by_client_name(client_name)
        cells = row.locator("td")

        proposal_cell = cells.nth(1)
        proposal_name = self._safe_text(
            proposal_cell.locator("span.proposal-name-text").first
        )

        pursuit_id = ""
        proposal_spans = proposal_cell.locator("span")
        try:
            if proposal_spans.count() >= 2:
                pursuit_id = self._safe_text(proposal_spans.nth(1))
        except Exception:
            pass

        return {
            "client_name": self._safe_text(cells.nth(0)),
            "pursuit_name": proposal_name,
            "pursuit_id": pursuit_id,
            "jupiter_id": self._safe_text(cells.nth(2)),
            "country": self._safe_text(cells.nth(3)),
            "requester": self._safe_text(cells.nth(4)),
            "proposal_type": self._safe_text(cells.nth(5)),
            "status": self._safe_text(cells.nth(6)),
            "start_date": self._safe_text(cells.nth(7)),
            "end_date": self._safe_text(cells.nth(8)),
        }

    def validate_row_data_by_client_name(self, client_name, expected_data):
        actual = self.get_row_data_by_client_name(client_name)

        for key, expected_value in expected_data.items():
            if key not in actual:
                continue

            if expected_value is None or expected_value == "":
                continue

            actual_value = actual.get(key, "")

            if key in ("start_date", "end_date"):
                assert self._normalize_date(actual_value) == self._normalize_date(expected_value), (
                    f"Mismatch for {key}: expected '{expected_value}', got '{actual_value}'"
                )
            else:
                assert expected_value.strip().lower() in actual_value.strip().lower(), (
                    f"Mismatch for {key}: expected '{expected_value}', got '{actual_value}'"
                )

    
    def open_pursuit_from_table_by_client_name(self, client_name):
        row = self._get_row_by_client_name(client_name)
        row.click()
        self.page.wait_for_timeout(2000)

    
    def validate_pursuit_details(self, expected_data):
        text_fields = [
            "pursuit_name",
            "pursuit_id",
            "proposal_type",
            "billing_arrangement",
            "industry",
            "sector",
            "pursuit_creator",
            "project_type",
            "jupiter_id",
            "country",
            "utilizing_ai_assist",
            "reference",
            "description",
        ]

        for field in text_fields:
            value = expected_data.get(field)
            if value:
                self._expect_visible_text(value, timeout=15000)

        if expected_data.get("start_date"):
            self._expect_visible_text(
                self._normalize_date(expected_data["start_date"]),
                timeout=15000
            )

        if expected_data.get("end_date"):
            self._expect_visible_text(
                self._normalize_date(expected_data["end_date"]),
                timeout=15000
            )

        no_members_count = expected_data.get("no_members_assigned_count")
        if no_members_count:
            actual_count = self._count_visible_exact_text("No members assigned")
            assert actual_count >= no_members_count, (
                f"Expected at least {no_members_count} visible 'No members assigned' values, got {actual_count}"
            )
