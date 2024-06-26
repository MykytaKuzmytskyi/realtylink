# Scrapy Real Estate Spider

## Overview

This Scrapy project is designed to scrape real estate information
from [RealtyLink](https://realtylink.org/en/properties~for-rent) for rental properties. The spider navigates through
pages, extracts property details, and saves the data in a structured format (e.g., JSON file).

## Usage

1. **Clone the repository:**
    ```bash
    git clone https://github.com/MykytaKuzmytskyi/realtylink.git
    cd realtylink
    ```
2. Install modules and dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate (on Windows)
   source venv/bin/activate (on macOS)
   pip install -r requirements.txt
   ```
3. **Run the Scrapy spider:**
    ```bash
    scrapy crawl houses -O data.json
    ```
   This command will execute the `housese` and save the scraped data in a JSON file named `data.json`.

4. **Wait for the spider to complete the scraping process.** Once finished, you'll find the output JSON file in the
   project directory (`data.json`).

## Data Fields

The spider extracts the following information for each property:

- Link
- Title
- Region
- Address
- Description
- Photo URLs
- Price
- Number of Rooms
- Area

## Closing the Spider

The spider uses Selenium and Chrome for dynamic content handling. It's important to close the browser instance properly.
The `closed` method in the spider ensures that the browser is quit when the spider finishes.
