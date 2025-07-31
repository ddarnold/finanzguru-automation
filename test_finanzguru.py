import logging
import unittest
import csv
import json
import os
import sys
import argparse  # Import the argparse module
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config import CAPABILITIES, APPIUM_SERVER_URL
from bot import FinanzguruBot

args = None
logger = logging.getLogger(__name__)

def parse_arguments():
    """
    Parses command-line arguments for the test script.
    """
    parser = argparse.ArgumentParser(
        description="Run Finanzguru booking tests with data from a specified file and configurable logging."
    )
    parser.add_argument(
        "-b",
        "--booking_file",
        type=str,
        help="Path to the JSON or CSV file containing booking data.",
        required=True
    )
    parser.add_argument(
        "-l",
        "--log_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is INFO."
    )
    return parser.parse_args()

class TestFinanzguru(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Remote(
            APPIUM_SERVER_URL,
            options=UiAutomator2Options().load_capabilities(CAPABILITIES),
        )
        self.bot = FinanzguruBot(self.driver)

    def tearDown(self):
        self.driver.quit()

    def _load_bookings(self, path: str):
        """Loads bookings from a given file path, supporting JSON and CSV."""
        _, file_extension = os.path.splitext(path)
        file_extension = file_extension.lower()

        with open(path, "r", encoding="utf-8") as f:
            if file_extension == ".json":
                return json.load(f)
            elif file_extension == ".csv":
                reader = csv.DictReader(f)
                return [row for row in reader]
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

    def test_add_multiple_bookings_from_file(self):  # Renamed to start with 'test_'
        """
        Tests adding multiple bookings from a file specified via command-line argument.
        """
        if not args.booking_file:
            self.fail("No booking file provided. Please use --booking_file argument.")

        booking_file = args.booking_file

        bookings = self._load_bookings(booking_file)
        total = len(bookings)
        logger.info(f"Loaded {total} bookings from {booking_file}")

        for i, booking in enumerate(bookings, start=1):
            logger.info(f"➡️ Adding booking {i}/{total}: {booking}")
            self.bot.add_booking(**booking)

if __name__ == "__main__":
    args = parse_arguments()
    
    log_level_numeric = getattr(logging, args.log_level.upper())
    logging.basicConfig(
        level=log_level_numeric,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Clean sys.argv for unittest.main()
    sys.argv = sys.argv[:1] # Keep only the script name

    unittest.main()