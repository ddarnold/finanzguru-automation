# Finanzguru Automation Bot 🤖

Automated booking bot for the **Finanzguru** Android app using Python and Appium. This bot allows you to add multiple financial bookings (expenses and income) from JSON or CSV files by simulating user interactions in the app.

-----

## Features

  * Add bookings with amount, name, category, and optional transaction type (expense/income)
  * Supports positive (income) and negative (expense) transactions
  * Load bookings from JSON or CSV files
  * Robust error handling with screenshots on failure
  * Easy to customize and extend

-----

## Getting Started

Follow these instructions to set up and run the Finanzguru Automation Bot.

### Prerequisites

Before you begin, ensure you have the following installed:

  * **Python 3.x**
  * **Java Development Kit (JDK)**: Required for Appium.
  * **Android SDK**: Essential for Android device communication and `uiautomator2`.
  * **Appium Server**: The core of mobile automation.

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/finanzguru-bot.git
    cd finanzguru-bot
    ```

2.  **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    The `requirements.txt` file includes:

      * `Appium-Python-Client`: For interacting with the Appium server.
      * `python-dateutil`: For robust date parsing.
      * `python-dotenv`: For managing environment variables (though not explicitly used in the provided `config.py`, it's good practice for sensitive info).

3.  **Set up Appium:**

      * Install Appium Server globally or run it via command line.
      * Ensure your Android device (emulator or physical) is connected and recognized by ADB (`adb devices`).

-----

## Usage

This bot is designed to be run from the command line, allowing you to specify the booking data file and logging level.

### Booking Data Format

The bot supports both **JSON** and **CSV** file formats for your booking data.

#### JSON Format (`bookings.json`)

Your JSON file should be an array of objects, each representing a booking.

```json
[
  {
    "amount": "2448",
    "name": "Souvenir Valencia",
    "category": "Sonstige Ausgaben",
    "type": "give",
    "date": "2025-05-31"
  },
  {
    "amount": "333",
    "name": "T-Mobile Hotspot",
    "category": "Internet & Telefon",
    "type": "give",
    "date": "2025-05-31"
  }
]
```

#### CSV Format

If using CSV, ensure your columns match the keys in the JSON format (`amount`, `name`, `category`, `type`, `date`).

#### Data Formatting Instructions (from `input_prompt.txt`)

When preparing your `bookings.json` or CSV file, adhere to the following rules:

1.  💰 **Amount Formatting**:

      * Multiply the decimal amount by 100 and **remove the decimal point**.
      * **Example**: `"123.45"` ➝ `"12345"`, `"10.00"` ➝ `"1000"`

2.  🏷️ **Name Extraction**:

      * Extract a **clear, human-readable label** for the `"name"` field.
      * For **card transactions**: Use the merchant name (e.g., `"Lidl"`).
      * For **bank transfers**: Use the sender name and purpose (e.g., `"Udruženje Građana DIPLOCENTAR • Neoporeziva primanja"`).
      * **Omit irrelevant or technical data** such as card numbers, exchange rates, internal codes, account numbers, etc.

3.  ➡️⬅️ **Transaction Type**:

      * Use `"give"` for expenses (money out).
      * Use `"get"` for income (money in).

4.  🗂️ **Category Assignment**:

      * Assign a `"category"` only if you are **reasonably certain**.
      * Otherwise, use the default:
          * `"Sonstige Ausgaben"` for `"give"`
          * `"Sonstige Einnahmen"` for `"get"`
      * Categories must come from the following approved list:
        ```
        Drogerie, Elterngeld, Kapitalerträge, Kindergeld, Leistung der Bundesagentur für Arbeit,
        Lohn / Gehalt, Mieteinnahmen, Rente/Pension, Sonstige Einnahmen, Lebensmittel,
        Lieferservice, Mittagsessen, Restaurants, Supplements, Ausleihe, Bankgebühren, FinanzApp,
        Kredit, Sonstige Finanzausgaben, Spende, Steuern, Bücher & Zeitungen, Gaming,
        In-App-Käufe, Kino, Mitgliedschaft, Musik & Podcasts, Serien & Filme,
        Sonstige Freizeitausgaben, Sport, Urlaub, Veranstaltungen, Apotheke,
        Sonstige Gesundheitsausgaben, Ärztliche Behandlung, Futter & Tierbedarf,
        Tierärztliche Behandlung, Kinderbetreuung, Schule & Förderung,
        Sonstige Kinderausgaben, Taschengeld, Bekleidung, Cloud-Dienste, Elektrohandel,
        Friseur, Geschenke, Mobilfunk, Prime-Mitgliedschaft, Shopping,
        Sonstiger Lifestyle, Auto, Bus & Bahn, Fahrrad, Flüge, Laden,
        Sharing / Gemietet, Tanken, Taxi, Bargeld, Kreditkartenabrechnung, Mama,
        Sonstige Ausgaben, BTC, Bausparvertrag, Kapitalanlage, Sparen,
        Anhängerversicherung, Bauherrenhaftpflichtversicherung, Berufsunfähigkeitsversicherung,
        Betriebliche Altersvorsorge, Bootshaftpflichtversicherung, Brillenversicherung,
        Drohnenhaftpflichtversicherung, Geräteversicherung, Gesetzliche Krankenversicherung,
        Gesetzliche Rentenversicherung, Gewässerschadenhaftpflichtversicherung,
        Haftpflichtversicherung, Hausratversicherung, Jagdhaftpflichtversicherung,
        KFZ-Versicherung, Kapitallebensversicherung, Kombi-Sachversicherung,
        Krankenzusatzversicherung, Lebensversicherung, Motorradversicherung,
        Pflegeversicherung, Photovoltaikhaftpflichtversicherung, Private Krankenversicherung,
        Rechtsschutzversicherung, Reisekrankenversicherung, Rentenversicherung,
        Risikolebensversicherung, Sonstige Sachversicherung, Sonstige Versicherung,
        Tierhaftpflichtversicherung, Tierkrankenversicherung, Unfallversicherung,
        Wohngebäudeversicherung, Wohnwagenversicherung, Zahnzusatzversicherung,
        Bauen / Renovieren, Baufinanzierung, Einrichtung, Gas, Internet & Telefon,
        Miete, Rundfunkgebühren, Sonstiges Wohnen, Strom
        ```

### Running the Bot

1.  **Start the Appium Server.**

2.  **Run the script from your terminal:**

    ```bash
    python test_finanzguru.py -b <path_to_your_booking_file> [-l <log_level>]
    ```

      * Replace `<path_to_your_booking_file>` with the actual path to your JSON or CSV booking file (e.g., `bookings.json`).
      * `[-l <log_level>]` is optional. You can set the logging level to `DEBUG`, `INFO` (default), `WARNING`, `ERROR`, or `CRITICAL`.

    **Example:**

    ```bash
    python test_finanzguru.py -b bookings.json -l DEBUG
    ```

    This command will load bookings from `bookings.json` and display detailed debug logs during execution.

-----

## Project Structure

  * `bot.py`: Contains the `FinanzguruBot` class, which encapsulates all the Appium interactions and logic for adding bookings.
  * `config.py`: Stores configuration variables for Appium capabilities and screenshot directory.
  * `test_finanzguru.py`: The main script that parses command-line arguments, loads booking data, and runs the automation using the `FinanzguruBot`. It uses `unittest` for structuring the test.
  * `bookings.json`: An example JSON file demonstrating the expected format for booking data.
  * `requirements.txt`: Lists the Python dependencies required for the project.
  * `input_prompt.txt`: Provides detailed instructions for formatting booking data, useful for generating new booking files.
  * `screenshots/`: (Created automatically) This directory will store screenshots taken when an error occurs during automation.

-----

## Troubleshooting

  * **Appium Server Not Running**: Ensure the Appium server is started before running the script.
  * **Android Device/Emulator Not Found**: Verify your device is connected and recognized by ADB (`adb devices`).
  * **Element Not Found Errors**: These often indicate changes in the app's UI elements. You may need to update the `AppiumBy` locators in `bot.py`. The bot captures screenshots on failure to help diagnose these issues.
  * **Stale Element Reference Exception**: This can occur when the UI changes after an element is found. The `select_date` method in `bot.py` includes a fallback mechanism for common cases.

-----

## Contributing

Feel free to fork this repository, open issues, or submit pull requests to improve the bot's functionality or robustness.