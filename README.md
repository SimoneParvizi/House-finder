# Apartment Listings Notifier

This script automatically checks for new apartment listings on `https://www.huurstunt.nl/studio/huren/amsterdam/+2km/0-1500/` and sends notifications via WhatsApp and Email when new listings are found.

## Requirements:

- Python 3.x
- `selenium`
- `BeautifulSoup4`
- `twilio`
- Chrome WebDriver

## Setup:

1. Install the required Python packages:

   \```
   pip install selenium beautifulsoup4 twilio
   \```

2. Download the appropriate [Chrome WebDriver](https://sites.google.com/a/chromium.org/chromedriver/) for your version of Chrome and add it to your system's PATH.

3. Replace the placeholder credentials and information in the script:

   - Twilio `account_sid` and `auth_token`
   - `your_twilio_whatsapp_number` and `your_personal_whatsapp_number` for WhatsApp notifications
   - SMTP server details and email credentials for Email notifications

## Usage:

Run the script:

\```
python apartment_notifier.py
\```

The script will continuously monitor the website for new listings. If any new listings are found, it will send a notification via WhatsApp and an email to the specified recipients. The script will wait for 5 seconds before refreshing the page to check for new listings.

\## Note:

- It's essential to keep your credentials and tokens private. Never share them or commit them to public repositories.
- Continuously scraping a website can be against its terms of service. Please ensure you have the right to access and scrape the website. Adjust the script's sleep time if needed to prevent overwhelming the website's servers.

---

