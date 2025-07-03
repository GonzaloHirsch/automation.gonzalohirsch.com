from typing import Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote import webelement

JS_SET_VALUE = """
var input = arguments[0];
var value = arguments[1];
input.value = value;
input.dispatchEvent(new Event('change', { bubbles: true }));
input.dispatchEvent(new Event('input', { bubbles: true }));
"""


class CustomDriver:
    def __init__(self, download_filepath, *args, **kwargs):
        # Set up Chrome
        options = webdriver.ChromeOptions()
        options.add_argument(
            "--start-maximized"
        )  # Do need to see it to be able to complete the security step.
        prefs = {
            "download.default_directory": download_filepath,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    def get_driver(self):
        return self.driver

    def set_element_value(self, element: webelement.WebElement, value: Any):
        self.driver.execute_script(JS_SET_VALUE, element, value)
