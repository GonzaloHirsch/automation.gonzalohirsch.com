import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

from custom_driver import CustomDriver
from utils import (
    compute_last_month_range,
    prep_download_folder,
)

# Need to set the date this way to trigger the update of the input field.
JS_SET_DATE = """
var input = arguments[0];
var value = arguments[1];
input.value = value;
input.dispatchEvent(new Event('change', { bubbles: true }));
input.dispatchEvent(new Event('input', { bubbles: true }));
"""

# Load the dotenv given the environment.
load_dotenv(dotenv_path=".env.dev")
AMEX_PREFIX = os.getenv("AMEX_DOWNLOAD_PREFIX", "hsbc")

# Preparing downloads.
download_filepath = prep_download_folder(
    os.getenv("AMEX_DOWNLOAD_LOCATION", "chrome_downloads")
)

custom_driver = CustomDriver(download_filepath)
driver = custom_driver.get_driver()

# Navigate to login page
driver.get("https://www.americanexpress.com/en-gb/account/login")

# Give cookies time to load.
time.sleep(2)

# Accept cookies.
driver.find_element(
    By.ID, "user-consent-management-granular-banner-decline-all-button"
).click()

# Fill in login
driver.find_element(By.ID, "eliloUserID").send_keys(os.getenv("AMEX_USERNAME"))

# Pause: Wait for human to enter password.
print("🛑 Waiting for human to complete security step in browser...")

# OTP step.
try:
    WebDriverWait(driver, timeout=60).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@data-module-name="identity-components-otp"]')
        )
    )
    print("✅ OTP step completed! Continuing...")
except:
    print("⏰ Timeout waiting for OTP step.")
    driver.quit()
    exit()

# Select the mobile option for OTP.
element = driver.find_element(
    By.CSS_SELECTOR, f"[id*='channel_********{os.getenv('AMEX_LAST_5')}']"
)
driver.find_element(By.XPATH, '//*[@element="Continue"]').click()

# Remember me step.
try:
    WebDriverWait(driver, timeout=60).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@data-module-name="identity-two-step-verification"]')
        )
    )
    print("✅ OTP step completed! Continuing...")
except:
    print("⏰ Timeout waiting for OTP step.")
    driver.quit()
    exit()

driver.find_element(By.XPATH, '//*[@type="submit"]').click()

try:
    WebDriverWait(driver, timeout=60).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//*[@title="Statements &amp; Activity"]')
        )
    )
    print("✅ OTP step completed! Continuing...")
except:
    print("⏰ Timeout waiting for OTP step.")
    driver.quit()
    exit()

# Look at the custom search.
driver.find_element(By.XPATH, '//*[@title="Statements &amp; Activity"]').click()
driver.find_element(By.XPATH, '//*[@title="Custom Date Range"]').click()

# Update the search.
from_date, to_date = compute_last_month_range()
input_from = driver.find_element(By.ID, "undefined-start")
input_to = driver.find_element(By.ID, "undefined-end")
custom_driver.set_element_value(input_from, from_date.strftime("%Y-%m-%d"))
custom_driver.set_element_value(input_to, to_date.strftime("%Y-%m-%d"))

# Perform the search.
driver.find_element(By.XPATH, '//*[@type="button" and @element="null"]').click()

# Click on download.
input_to = driver.find_element(By.ID, "action-icon-dls-icon-download-").click()

input_to = driver.find_element(
    By.ID, "axp-activity-download-body-selection-options-type_csv"
).click()
input_to = driver.find_element(
    By.ID, "axp-activity-download-footer-download-confirm"
).click()
