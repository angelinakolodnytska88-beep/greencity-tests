import unittest
from datetime import datetime, date

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from utils import (
    BASE_URL,
    wait_for_element,
    wait_for_clickable,
    wait_for_all_elements,
    wait_for_url_change,
)


class BaseEventsTest(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(options=options)
        self.driver.get(BASE_URL)

    def tearDown(self):
        self.driver.quit()


class TestEventDetail(BaseEventsTest):

    def test_open_event_detail_page(self):
        driver = self.driver

        cards = wait_for_all_elements(driver, (By.CSS_SELECTOR, "app-events-list-item"))
        self.assertGreater(len(cards), 0, "No event cards found on the page.")

        card_title_el = cards[0].find_element(By.CSS_SELECTOR, ".event-title, h2, h3, .title")
        card_title = card_title_el.text.strip()
        self.assertTrue(card_title, "Event title on the card is empty.")

        read_more_btn = wait_for_clickable(
            driver,
            (By.XPATH,
             ".//button[contains(translate(., 'БІЛЬШЕ', 'більше'), 'більше')"
             " or contains(., 'More') or contains(., 'Детальніше')]"),
        )
        original_url = driver.current_url
        read_more_btn.click()

        wait_for_url_change(driver, original_url)
        self.assertNotEqual(driver.current_url, original_url,
                            "Browser did not navigate away from the list page.")

        detail_heading = wait_for_element(
            driver, (By.CSS_SELECTOR, "h1, h2, .event-name, .event-detail-title")
        )
        detail_title = detail_heading.text.strip()
        self.assertEqual(detail_title, card_title,
                         f"Detail page title '{detail_title}' does not match card title '{card_title}'.")


class TestInvalidLogin(BaseEventsTest):

    INVALID_EMAIL = "invalid_user_test@example.com"
    INVALID_PASSWORD = "WrongPassword123!"

    def test_login_with_invalid_credentials_shows_error(self):
        driver = self.driver

        sign_in_btn = wait_for_clickable(
            driver,
            (By.XPATH, "//button[contains(., 'Увійти') or contains(., 'Sign in') or contains(., 'Login')]"),
        )
        sign_in_btn.click()

        email_field = wait_for_element(
            driver,
            (By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[formcontrolname='email']"),
        )
        email_field.clear()
        email_field.send_keys(self.INVALID_EMAIL)

        password_field = driver.find_element(
            By.CSS_SELECTOR,
            "input[type='password'], input[name='password'], input[formcontrolname='password']",
        )
        password_field.clear()
        password_field.send_keys(self.INVALID_PASSWORD)

        submit_btn = wait_for_clickable(
            driver,
            (By.XPATH, "//button[@type='submit' or contains(., 'Увійти') or contains(., 'Sign in')]"),
        )
        submit_btn.click()

        error_message = wait_for_element(
            driver,
            (By.CSS_SELECTOR, ".error-message, .alert, .mat-error, [class*='error'], [class*='invalid']"),
        )
        self.assertTrue(error_message.is_displayed(),
                        "No error message appeared after submitting invalid credentials.")

        error_text = error_message.text.strip().lower()
        expected_fragments = ["невірна", "пароль", "пошта", "invalid", "wrong", "incorrect", "bad credentials"]
        self.assertTrue(
            any(fragment in error_text for fragment in expected_fragments),
            f"Error message '{error_message.text}' does not indicate an authentication failure.",
        )


class TestFilterUpcomingEvents(BaseEventsTest):

    def _parse_event_date(self, text: str):
        text = text.strip()
        for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d %b %Y", "%B %d, %Y", "%d %B %Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        return None

    def test_upcoming_filter_shows_future_events(self):
        driver = self.driver
        today = date.today()

        upcoming_filter = wait_for_clickable(
            driver,
            (By.XPATH,
             "//*[contains(text(), 'Майбутні') or contains(text(), 'Upcoming')]"
             "[self::button or self::a or self::span or self::li]"),
        )
        upcoming_filter.click()

        cards = wait_for_all_elements(driver, (By.CSS_SELECTOR, "app-events-list-item"))
        self.assertGreater(len(cards), 0, "No event cards visible after applying 'Upcoming' filter.")

        future_events_found = 0
        parse_failures = []

        for card in cards:
            date_text = None
            for sel in (".event-date", ".date", "[class*='date']", "time"):
                try:
                    el = card.find_element(By.CSS_SELECTOR, sel)
                    raw = el.get_attribute("datetime") or el.text
                    if raw.strip():
                        date_text = raw.strip()
                        break
                except Exception:
                    continue

            if date_text is None:
                continue

            parsed = self._parse_event_date(date_text)
            if parsed is None:
                parse_failures.append(date_text)
                continue

            self.assertGreaterEqual(
                parsed, today,
                f"Event date '{date_text}' is in the past. Expected only upcoming events.",
            )
            future_events_found += 1

        self.assertGreater(
            future_events_found, 0,
            f"Could not verify any event dates. Unparseable strings: {parse_failures}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)