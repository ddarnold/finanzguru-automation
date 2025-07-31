# config.py

import os

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
