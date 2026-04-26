from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

BASE_URL = "https://www.greencity.cx.ua/#/greenCity/events"
DEFAULT_TIMEOUT = 15


def wait_for_element(driver, locator, timeout=DEFAULT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )


def wait_for_clickable(driver, locator, timeout=DEFAULT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    )


def wait_for_all_elements(driver, locator, timeout=DEFAULT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located(locator)
    )


def wait_for_url_change(driver, original_url, timeout=DEFAULT_TIMEOUT):
    WebDriverWait(driver, timeout).until(
        lambda d: d.current_url != original_url
    )