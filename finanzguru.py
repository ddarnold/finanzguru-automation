from datetime import datetime
import locale
import time
import unittest
import csv
import json
import os
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# call:
# python your_script.py TestFinanzguru.test_multiple_bookings_from_json
# python your_script.py TestFinanzguru.test_multiple_bookings_from_csv


# --- Locale Setup ---
try:
    locale.setlocale(locale.LC_ALL, "de_DE.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, "German_Germany.1252")
    except locale.Error:
        print("Warning: Could not set German locale; month parsing might fail.")

# --- Appium Capabilities ---
CAPABILITIES = dict(
    platformName="Android",
    automationName="uiautomator2",
    deviceName="Android",
    appPackage="de.dwins.financeguru",
    noReset=True,
    printPageSourceOnFindFailure=True,
)
APPIUM_SERVER_URL = "http://localhost:4723"

# --- Screenshot Directory ---
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


class FinanzguruBot:
    """Helper class to interact with Finanzguru App"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def click_booking_button(self):
        self._safe_action(
            "Clicking booking button",
            lambda: self._click_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("Buchung hinzufügen").instance(0)',
            ),
        )

    def enter_amount(self, amount: str):
        self._safe_action(
            "Entering amount",
            lambda: self._send_keys(AppiumBy.ACCESSIBILITY_ID, "Betrag", amount),
        )
        
    def switch_to_positive(self):
        """Switches the transaction to positive (money received)."""
        self._safe_action(
            "Switching to positive transaction",
            lambda: self._click_element(AppiumBy.ACCESSIBILITY_ID, "Auf Positiv wechseln"),
        )

    def enter_name(self, name: str):
        self._safe_action(
            "Entering name",
            lambda: self._send_keys(AppiumBy.ACCESSIBILITY_ID, "Name", name),
        )

    def select_category(self, category: str):
        def action():
            self._click_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().className("com.horcrux.svg.SvgView").instance(3)',
            )
            self._send_keys(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("Kategorie suchen…")',
                category,
            )
            self._click_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().className("com.horcrux.svg.PathView").instance(2)',
            )

        self._safe_action(f"Selecting category '{category}'", action)

    def save_booking(self):
        def action():
            self._click_element(AppiumBy.ACCESSIBILITY_ID, "Speichern")
            print("⏳ Waiting to return to main screen...")
            self._wait_for_main_screen()

        self._safe_action("Saving booking", action)

    def _wait_for_main_screen(self):
        """Waits until the main booking screen is ready again."""
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (
                        AppiumBy.ANDROID_UIAUTOMATOR,
                        'new UiSelector().text("Buchung hinzufügen").instance(0)',
                    )
                )
            )
            time.sleep(5)  # Small pause to allow animations to finish
            print("✅ Main screen ready for next booking.")
        except TimeoutException:
            print("Warning: Main screen did not appear in time; next booking may fail.")

    # --- FUTURE FEATURE: Date Selection (Commented for Now) ---
    # def set_date(self, date_str: str):
    #     """
    #     Sets the booking date.
    #     date_str format: 'DD.MM.YYYY' (e.g., '15.06.2025')
    #     """
    #     self._safe_action("Setting date", lambda: self._set_custom_date(date_str))

    # def _set_custom_date(self, date_str: str):
    #     target_date = datetime.strptime(date_str, "%d.%m.%Y")
    #     # <<Insert clean date picker logic here – using the previous implementation>>

    def add_booking(self, amount: str, name: str, category: str, date: str = None, type: str = "give"):
        """Main flow to add a booking. Type can be 'give' (default, negative) or 'get' (positive)."""
        self.click_booking_button()
        self.enter_amount(amount)
        
        # If it's a positive transaction, switch after entering amount
        if type.lower() == "get":
            self.switch_to_positive()
        
        self.enter_name(name)
        self.select_category(category)
        # if date:
        #     self.set_date(date)
        self.save_booking()


    # --- Internal Helpers with Error Handling ---
    def _click_element(self, by, value):
        el = self.wait.until(EC.element_to_be_clickable((by, value)))
        el.click()

    def _send_keys(self, by, value, text):
        el = self.wait.until(EC.presence_of_element_located((by, value)))
        el.send_keys(text)

    def _safe_action(self, action_name: str, func):
        """Runs an action with error handling and screenshot on failure."""
        try:
            func()
            print(f"✅ {action_name} successful")
        except Exception as e:
            screenshot_path = os.path.join(
                SCREENSHOT_DIR,
                f"{action_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            )
            self.driver.save_screenshot(screenshot_path)
            print(f"❌ {action_name} failed! Screenshot saved: {screenshot_path}")
            raise e


class TestFinanzguru(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Remote(
            APPIUM_SERVER_URL,
            options=UiAutomator2Options().load_capabilities(CAPABILITIES),
        )
        self.bot = FinanzguruBot(self.driver)

    def tearDown(self):
        self.driver.quit()

    def test_multiple_bookings_from_json(self):
        """Runs multiple bookings from a JSON file."""
        bookings = self._load_bookings_from_json("bookings.json")
        for booking in bookings:
            print(f"➡️ Adding booking: {booking}")
            self.bot.add_booking(**booking)

    def test_multiple_bookings_from_csv(self):
        """Runs multiple bookings from a CSV file."""
        bookings = self._load_bookings_from_csv("bookings.csv")
        for booking in bookings:
            print(f"➡️ Adding booking: {booking}")
            self.bot.add_booking(**booking)

    # --- Loaders for CSV/JSON ---
    @staticmethod
    def _load_bookings_from_json(path: str):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _load_bookings_from_csv(path: str):
        bookings = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                bookings.append(row)
        return bookings


if __name__ == "__main__":
    unittest.main()
