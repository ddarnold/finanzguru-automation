# bot.py

import logging
from datetime import datetime
import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import StaleElementReferenceException
from config import SCREENSHOT_DIR

logger = logging.getLogger(__name__)

class FinanzguruBot:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def click_booking_button(self):
        self._safe_action(
            "Clicking booking button",
            lambda: self._click_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().description("Buchung hinzufügen").instance(1)',
            ),
        )

    def enter_amount(self, amount: str):
        self._safe_action(
            "Entering amount",
            lambda: self._send_keys(AppiumBy.ACCESSIBILITY_ID, "Betrag", amount),
        )

    def switch_to_positive(self):
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
                AppiumBy.XPATH,
                '//android.widget.Button[@content-desc="Kategorie"]/com.horcrux.svg.SvgView',
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
        
    def select_date(self, date: str):
        target_date = datetime.strptime(date, "%Y-%m-%d")
        today = datetime.today()

        # Calculate month difference
        diff_months = (today.year - target_date.year) * 12 + (today.month - target_date.month)
        logger.debug(f"Months difference: {diff_months}")

        def click_day_with_instance_fallback(day_text: str):
            # Try instance(1)
            selector_instance_1 = f'new UiSelector().text("{day_text}").instance(1)'
            elements = self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, selector_instance_1)
            if elements:
                try:
                    logger.debug(f"Instance(1) found for day {day_text}, clicking it")
                    elements[0].click()
                    return
                except StaleElementReferenceException:
                    logger.debug("Stale element on instance(1), retrying find and click")
                    elements = self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, selector_instance_1)
                    if elements:
                        elements[0].click()
                        return
                    else:
                        logger.debug("No elements found after retry for instance(1)")

            # If instance(1) fails or no elements, try instance(0)
            selector_instance_0 = f'new UiSelector().text("{day_text}").instance(0)'
            elements = self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, selector_instance_0)
            if elements:
                try:
                    logger.debug(f"Instance(1) not found or stale, clicking instance(0) for day {day_text}")
                    elements[0].click()
                except StaleElementReferenceException:
                    logger.debug("Stale element on instance(0), retrying find and click")
                    elements = self.driver.find_elements(AppiumBy.ANDROID_UIAUTOMATOR, selector_instance_0)
                    if elements:
                        elements[0].click()
                    else:
                        raise Exception(f"No elements found with text {day_text} for instance(0) after retry")
            else:
                raise Exception(f"No elements found with text {day_text} for instance(0) or (1)")

        def action():
            self._click_element(AppiumBy.ACCESSIBILITY_ID, "Eigenes Datum")
            for i in range(diff_months):
                self._click_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().resourceId("undefined.header.leftArrow")')
                logger.debug(f'clicking left arrow {i+1}. time...')
            
            day_str = str(target_date.day)
            if target_date.day >= 26:
                click_day_with_instance_fallback(day_str)
            else:
                # For days < 26, just click instance(0)
                self._click_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{day_str}").instance(0)')
                logger.debug(f'clicking the day {day_str} with instance(0)')

            self._click_element(AppiumBy.ACCESSIBILITY_ID, "Übernehmen")
            logger.debug("✅ Entering the date successful.")

        self._safe_action("Selecting date...", action)


    def save_booking(self):
        def action():
            self._click_element(AppiumBy.ACCESSIBILITY_ID, "Speichern")
            logger.debug("⏳ Waiting to return to main screen...")
            self._wait_for_main_screen()

        self._safe_action("Saving booking", action)

    def _wait_for_main_screen(self):
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (
                        AppiumBy.ANDROID_UIAUTOMATOR,
                        'new UiSelector().text("Buchung hinzufügen").instance(0)',
                    )
                )
            )
            time.sleep(5)
            logger.debug("✅ Main screen ready for next booking.")
        except TimeoutException:
            logger.warning("Warning: Main screen did not appear in time; next booking may fail.")

    def add_booking(self, amount: str, name: str, category: str, date: str = None, type: str = "give"):
        self.click_booking_button()
        self.enter_amount(amount)
        if type.lower() == "get":
            self.switch_to_positive()
        self.enter_name(name)
        self.select_category(category)
        self.select_date(date)
        self.save_booking()

    def _click_element(self, by, value):
        el = self.wait.until(EC.element_to_be_clickable((by, value)))
        el.click()

    def _send_keys(self, by, value, text):
        el = self.wait.until(EC.presence_of_element_located((by, value)))
        el.send_keys(text)

    def _safe_action(self, action_name: str, func):
        try:
            func()
            logger.debug(f"✅ {action_name} successful")
        except Exception as e:
            screenshot_path = os.path.join(
                SCREENSHOT_DIR,
                f"{action_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            )
            self.driver.save_screenshot(screenshot_path)
            logger.error(f"❌ {action_name} failed! Screenshot saved: {screenshot_path}")
            raise e
