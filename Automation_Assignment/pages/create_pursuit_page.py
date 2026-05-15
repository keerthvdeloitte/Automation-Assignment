import re
import time
from playwright.sync_api import expect, TimeoutError


class CreatePursuitPage:
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
                    self.page.wait_for_timeout(500)
                    return
                except TimeoutError:
                    pass
                except Exception:
                    pass

        except TimeoutError:
            pass

    def _find_visible_in_frames(self, selector, timeout=15000):
        end_time = time.time() + (timeout / 1000)

        while time.time() < end_time:
            for frame in self.page.frames:
                locator = frame.locator(selector)
                count = locator.count()

                for i in range(count):
                    candidate = locator.nth(i)
                    try:
                        if candidate.is_visible():
                            return candidate
                    except Exception:
                        pass

            self.page.wait_for_timeout(250)

        raise AssertionError(f"No visible element found for selector: {selector}")

    def _get_pursuit_form(self):
        form = self.page.locator("form[id='Pursuit Form']").first
        expect(form).to_be_visible(timeout=15000)
        return form

    def _get_add_client_dialog(self):
        dialog = self.page.locator(
            "[role='dialog'], .ant-modal, .ant-drawer"
        ).filter(
            has=self.page.locator("input[placeholder='Add New Client']")
        ).last
        expect(dialog).to_be_visible(timeout=10000)
        return dialog

    def _find_form_item_by_text(self, field_text):
        form = self._get_pursuit_form()
        items = form.locator(".ant-form-item")
        count = items.count()

        for i in range(count):
            item = items.nth(i)
            try:
                text = item.inner_text().strip().lower()
                if field_text.lower() in text:
                    return item
            except Exception:
                pass

        return None

    def _find_text_input_by_form_label(self, field_text):
        item = self._find_form_item_by_text(field_text)
        if item is None:
            return None

        candidates = [
            item.locator("input").first,
            item.locator("textarea").first,
            item.locator("[contenteditable='true']").first,
        ]

        for candidate in candidates:
            try:
                if candidate.count() > 0 and candidate.is_visible():
                    return candidate
            except Exception:
                pass

        return None

    def _open_dropdown_from_item(self, item):
        candidates = [
            item.locator(".ant-select-selector").first,
            item.locator(".ant-select").first,
            item.locator("[role='combobox']").first,
            item.locator("input").first,
        ]

        for candidate in candidates:
            try:
                candidate.wait_for(state="visible", timeout=2000)
                candidate.scroll_into_view_if_needed()
                candidate.click()
                self.page.wait_for_timeout(700)
                return
            except TimeoutError:
                pass
            except Exception:
                pass

        raise AssertionError("Unable to open dropdown from form item")

    def _get_visible_dropdown(self, timeout=5000):
        dropdown = self.page.locator(".ant-select-dropdown:visible").last
        dropdown.wait_for(state="visible", timeout=timeout)
        return dropdown

    def _select_first_visible_dropdown_option(self):
        option = self.page.locator(
            ".ant-select-dropdown:visible .ant-select-item-option"
        ).first
        expect(option).to_be_visible(timeout=10000)
        option.click()

    def _select_first_dropdown_value(self, field_text):
        item = self._find_form_item_by_text(field_text)
        if item is None:
            raise AssertionError(f"Dropdown not found for field: {field_text}")

        self._open_dropdown_from_item(item)
        self._select_first_visible_dropdown_option()

    def _get_dropdown_search_input(self):
        candidates = [
            self.page.locator(".ant-select-dropdown:visible input[role='combobox']").last,
            self.page.locator(".ant-select-dropdown:visible input").last,
            self.page.locator(".ant-select-selection-search input").last,
        ]

        for candidate in candidates:
            try:
                candidate.wait_for(state="visible", timeout=1500)
                return candidate
            except TimeoutError:
                pass
            except Exception:
                pass

        return None

    def _select_dropdown_value_by_text(self, option_text, exact=False, timeout=10000):
        options = self.page.locator(".ant-select-dropdown:visible .ant-select-item-option")

        if exact:
            option = options.filter(
                has_text=re.compile(rf"^{re.escape(option_text)}$", re.I)
            ).first
        else:
            option = options.filter(
                has_text=re.compile(re.escape(option_text), re.I)
            ).first

        expect(option).to_be_visible(timeout=timeout)
        option.click()

    def _get_selected_value_from_item(self, item):
        candidates = [
            item.locator(".ant-select-selection-item").first,
            item.locator(".ant-select-selection-overflow").first,
            item.locator("[title]").first,
        ]

        for candidate in candidates:
            try:
                if candidate.count() > 0:
                    text = candidate.text_content()
                    if text:
                        return text.strip()
            except Exception:
                pass

        return ""


    def open_create_pursuit(self):
        self.dismiss_cookie_popup_if_present()

        try:
            create_pursuit = self._find_visible_in_frames(
                "button[aria-label='Create Pursuit']",
                timeout=8000
            )
            create_pursuit.click()
        except AssertionError:
            pass

        self._get_pursuit_form()

    def validate_bottom_buttons(self):
        cancel_button = self.page.locator(
            "button:has-text('Cancel'), "
            "input[type='button'][value='Cancel'], "
            "[role='button']:has-text('Cancel')"
        ).first

        save_button = self.page.get_by_role("button", name=re.compile(r"^Save$", re.I)).last

        expect(cancel_button).to_be_visible(timeout=10000)
        expect(save_button).to_be_visible(timeout=10000)

    def click_create_without_details(self):
        save_button = self.page.get_by_role("button", name=re.compile(r"^Save$", re.I)).last
        expect(save_button).to_be_visible(timeout=10000)
        save_button.click()

    def validate_required_field_errors(self, expected_min_errors=8):
        error_messages = self.page.locator(".ant-form-item-explain-error")
        expect(error_messages.first).to_be_visible(timeout=10000)

        actual_count = error_messages.count()
        assert actual_count >= expected_min_errors, (
            f"Expected at least {expected_min_errors} validation errors, but found {actual_count}"
        )

    # -------------------------
    # Add new client
    # -------------------------
    def click_add_new_client(self):
        add_client_button = self.page.get_by_role(
            "button",
            name=re.compile("Add New Client", re.I)
        )
        expect(add_client_button).to_be_visible(timeout=10000)
        add_client_button.click()

    def _get_add_client_field(self, container, label_text):
        items = container.locator(".ant-form-item")
        count = items.count()

        for i in range(count):
            item = items.nth(i)
            try:
                item_text = item.inner_text().strip().lower()
                if label_text.lower() in item_text:
                    return item
            except Exception:
                pass

        raise AssertionError(f"{label_text} field not found in Add Client form")

    def _select_first_option_from_field(self, field):
        dropdown = field.locator(".ant-select-selector, .ant-select").first
        expect(dropdown).to_be_visible(timeout=10000)
        dropdown.scroll_into_view_if_needed()
        dropdown.click()

        first_option = self.page.locator(
            ".ant-select-dropdown:visible .ant-select-item-option"
        ).first
        expect(first_option).to_be_visible(timeout=10000)
        first_option.click()

    def create_new_client(self, client_name):
        self.click_add_new_client()

        dialog = self._get_add_client_dialog()

        client_input = dialog.locator("input[placeholder='Add New Client']").first
        expect(client_input).to_be_visible(timeout=10000)
        client_input.fill(client_name)

        industry_field = self._get_add_client_field(dialog, "Industry")
        self._select_first_option_from_field(industry_field)

        self.page.wait_for_timeout(1000)

        sector_field = self._get_add_client_field(dialog, "Sector")
        self._select_first_option_from_field(sector_field)

        save_button = dialog.get_by_role("button", name=re.compile(r"^Save$", re.I)).last
        expect(save_button).to_be_visible(timeout=10000)
        save_button.click()

        expect(dialog).not_to_be_visible(timeout=15000)
        self.page.wait_for_timeout(2500)

    
    def select_client(self, client_name):
        client_item = None
        for label in ["client name", "client"]:
            client_item = self._find_form_item_by_text(label)
            if client_item is not None:
                break

        if client_item is None:
            raise AssertionError("Client field not found on pursuit form")

        current_value = self._get_selected_value_from_item(client_item)
        if current_value and client_name.lower() in current_value.lower():
            return

        self._open_dropdown_from_item(client_item)
        self._get_visible_dropdown(timeout=5000)

        search_input = self._get_dropdown_search_input()
        if search_input is not None:
            search_input.fill("")
            self.page.wait_for_timeout(300)
            search_input.fill(client_name)
            self.page.wait_for_timeout(1500)

        self._select_dropdown_value_by_text(client_name, exact=False, timeout=10000)

    def enter_pursuit_name(self, pursuit_name):
        pursuit_name_input = self.page.locator("input[placeholder='Enter pursuit name']").first
        expect(pursuit_name_input).to_be_visible(timeout=10000)
        pursuit_name_input.fill(pursuit_name)

    def select_proposal_type(self):
        self._select_first_dropdown_value("proposal type")

    def select_project_type(self):
        self._select_first_dropdown_value("project type")

    def select_country(self):
        self._select_first_dropdown_value("country")

    def select_billing_arrangement(self):
        self._select_first_dropdown_value("billing arrangement")

    def set_project_duration(self, start_date, end_date):
        start_input = self.page.locator("input[date-range='start']").first
        end_input = self.page.locator("input[date-range='end']").first

        expect(start_input).to_be_visible(timeout=10000)
        expect(end_input).to_be_visible(timeout=10000)

        start_input.evaluate("el => el.removeAttribute('readonly')")
        end_input.evaluate("el => el.removeAttribute('readonly')")

        start_input.fill(start_date)
        start_input.dispatch_event("input")
        start_input.dispatch_event("change")

        end_input.fill(end_date)
        end_input.dispatch_event("input")
        end_input.dispatch_event("change")
        end_input.press("Tab")

    def select_ai_assist_no(self):
        candidates = [
            self.page.get_by_role("radio", name=re.compile(r"^No$", re.I)).first,
            self.page.locator("label:has-text('No')").first,
            self.page.get_by_text(re.compile(r"^No$", re.I)).first,
        ]

        for candidate in candidates:
            try:
                if candidate.count() > 0 and candidate.is_visible():
                    try:
                        candidate.check()
                    except Exception:
                        candidate.click()
                    return
            except Exception:
                pass

        raise AssertionError("Unable to select AI Assist = No")

    def enter_description(self, description):
        candidates = [
            self.page.locator(
                ".ql-editor[contenteditable='true'][data-placeholder='Enter description']"
            ).first,
            self.page.locator(".ql-editor[contenteditable='true']").first,
            self._find_text_input_by_form_label("description"),
        ]

        for candidate in candidates:
            try:
                if candidate is not None and candidate.count() > 0 and candidate.is_visible():
                    candidate.fill(description)
                    return
            except Exception:
                pass

        raise AssertionError("Description field not found")

    def enter_reference(self, reference):
        if not reference:
            return

        candidates = [
            self.page.locator("input[placeholder*='Reference']").first,
            self.page.locator("textarea[placeholder*='Reference']").first,
            self.page.locator("input[placeholder*='reference']").first,
            self.page.locator("textarea[placeholder*='reference']").first,
            self._find_text_input_by_form_label("reference"),
            self._find_text_input_by_form_label("references"),
            self._find_text_input_by_form_label("external reference"),
        ]

        for candidate in candidates:
            try:
                if candidate is not None and candidate.count() > 0 and candidate.is_visible():
                    candidate.fill(reference)
                    return
            except Exception:
                pass

        print("Reference field not present on form. Skipping reference entry.")

    def click_create(self):
        save_button = self.page.get_by_role("button", name=re.compile(r"^Save$", re.I)).last
        expect(save_button).to_be_visible(timeout=10000)
        save_button.click()

    def validate_pursuit_created_successfully(self):
        success_candidates = [
            self.page.locator(".ant-message-notice").filter(
                has_text=re.compile("created|success", re.I)
            ).first,
            self.page.locator("[role='alert']").filter(
                has_text=re.compile("created|success", re.I)
            ).first,
            self.page.get_by_text(re.compile("created|success", re.I)).first,
        ]

        for candidate in success_candidates:
            try:
                expect(candidate).to_be_visible(timeout=15000)
                return
            except Exception:
                pass

        raise AssertionError("Pursuit success message was not found")

    def create_pursuit(
        self,
        client_name,
        pursuit_name,
        start_date,
        end_date,
        description,
        reference
    ):
        self.select_client(client_name)
        self.enter_pursuit_name(pursuit_name)
        self.select_proposal_type()
        self.select_project_type()
        self.select_country()
        self.select_billing_arrangement()
        self.set_project_duration(start_date, end_date)
        self.select_ai_assist_no()
        self.enter_description(description)
        self.enter_reference(reference)
        self.click_create()
        self.validate_pursuit_created_successfully()
