import calendar
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import os

from custom_driver import CustomDriver
from utils import (
    compute_last_month_range,
    prep_download_folder,
    wait_for_download_to_finish,
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
HSBC_PREFIX = os.getenv("HSBC_DOWNLOAD_PREFIX", "hsbc")

# Preparing downloads.
download_filepath = prep_download_folder(
    os.getenv("HSBC_DOWNLOAD_LOCATION", "chrome_downloads")
)

custom_driver = CustomDriver(download_filepath)
driver = custom_driver.get_driver()

# Navigate to login page
driver.get("https://www.hsbc.co.uk/security")

# Accept cookies.
driver.find_element(By.ID, "consent_prompt_decline").click()

# Fill in login
driver.find_element(By.ID, "username").send_keys(os.getenv("HSBC_USERNAME"))
driver.find_element(By.ID, "username_submit_btn").click()

# Pause: Wait for human to enter security code or solve CAPTCHA
print("🛑 Waiting for human to complete security step in browser...")

# Expect the account list to be visible after we log in.
try:
    WebDriverWait(driver, timeout=300).until(  # wait up to 5 minutes
        EC.presence_of_element_located((By.ID, "domestic-account-list"))
    )
    print("✅ Security step completed! Continuing...")
except:
    print("⏰ Timeout waiting for security step.")
    driver.quit()
    exit()

# Traverse through the account list.
account_list_parent = driver.find_element(By.ID, "domestic-account-list")
account_list = account_list_parent.find_elements(By.CLASS_NAME, "account-card")

total_accounts = len(account_list)
print(f"✅ Working through {total_accounts} accounts...")

# Need to compute the right date range for the previous complete month.
from_date, to_date = compute_last_month_range()

for i in range(total_accounts):
    account_id = i + 1
    print(f"\t✅ Working through {account_id}/{total_accounts} account...")

    account_element = driver.find_element(By.ID, f"account-{account_id}")

    # Find the account information.
    account_name = (
        account_element.find_element(By.TAG_NAME, "account-title")
        .find_element(By.CLASS_NAME, "account-title")
        .text
    )

    # Open the account and expand the filter options.
    account_element.click()
    driver.find_element(By.ID, "search-filter-button").click()

    # Add the right date range.
    input_from = driver.find_element(By.ID, "txnDate-0-InputField")
    input_to = driver.find_element(By.ID, "txnDate-1-InputField")
    driver.execute_script(JS_SET_DATE, input_from, from_date.strftime("%d/%m/%Y"))
    driver.execute_script(JS_SET_DATE, input_to, to_date.strftime("%d/%m/%Y"))

    # Perform the search and give it time to finish.
    driver.find_element(By.ID, "search-results-button").click()
    time.sleep(1)

    # Compute if there are any transactions.
    txn_list = driver.find_elements(
        By.XPATH, '//*[@aria-label="Transactions table"]/tbody'
    )
    visible_elements = [tx for tx in txn_list if tx.is_displayed()]

    if not any(visible_elements):
        print(
            f"❌ No transactions found for account {account_id}. Continuing to next account..."
        )
        driver.find_element(By.ID, "back-to-accounts").click()
        continue

    # Wait for the download button to appear.
    try:
        WebDriverWait(driver, timeout=60).until(
            EC.element_to_be_clickable((By.ID, "download-button"))
        )
        print(f"✅ Download button appeared for account {account_id}! Continuing...")
    except:
        print("⏰ Timeout waiting for download button to appear.")
        driver.quit()
        exit()

    # Download the results.
    button = driver.find_element(By.ID, "download-button")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
    WebDriverWait(driver, timeout=60)
    button.click()

    # Need to add a couple of styles to the button because of overlap.
    csv_element = driver.find_element(By.XPATH, '//*[@title="Spreadsheet (CSV)"]')
    driver.execute_script(
        "arguments[0].setAttribute('style', 'margin-top: 10px !important;')",
        csv_element,
    )
    csv_element.click()
    driver.find_element(By.ID, "popup-continue-btn-downloadTxnHistoryModal").click()

    # Rename the download.
    download_filepath = wait_for_download_to_finish(
        download_filepath,
        ignore_pattern=[".gitkeep", HSBC_PREFIX],
        interval=0.25,
    )
    if not download_filepath:
        print("⏰ Timeout waiting for download to finish.")
        driver.quit()
        exit()
    new_name = os.path.join(
        download_filepath,
        f"{HSBC_PREFIX}__{re.sub(
           r"[^a-zA-Z0-9]",
           '-',
           account_name
       )}__{from_date.strftime("%d-%m-%Y")}__{to_date.strftime("%d-%m-%Y")}.csv".lower(),
    )
    print(f"Renaming {download_filepath} to: {new_name}")
    os.rename(download_filepath, new_name)

    # Go back to the accounts list and start over.
    try:
        WebDriverWait(driver, timeout=60).until(
            EC.element_to_be_clickable((By.ID, "back-to-accounts"))
        )
        print(
            f"✅ Back to accounts button appeared for account {account_id}! Continuing..."
        )
    except:
        print("⏰ Timeout waiting for back button to appear.")
        driver.quit()
        exit()
    driver.find_element(By.ID, "back-to-accounts").click()

driver.quit()
