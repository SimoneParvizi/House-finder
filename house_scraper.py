from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import smtplib
from twilio.rest import Client
import logging

# Set Chrome options for headless browsing
chrome_options = Options()
chrome_options.add_argument("--headless")
logging.basicConfig(level=logging.INFO)

driver = webdriver.Chrome(options=chrome_options)

def check_new_listings(previous_listings):
    driver.get('https://www.huurstunt.nl/studio/huren/amsterdam/+2km/0-1500/')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    current_listings = soup.select('.listing-item')
    
    new_listings = [listing for listing in current_listings if listing not in previous_listings]
    
    return new_listings, current_listings


def send_notification(new_listings):
    logging.info(f'New listings found: {new_listings}')
    # Twilio Credentials
    account_sid = 'your_account_sid'
    auth_token = 'your_auth_token'
    client = Client(account_sid, auth_token)

    whatsapp_message = f"New listings found: {new_listings}"
    message = client.messages.create(
                              from_='whatsapp:your_twilio_whatsapp_number',
                              body=whatsapp_message,
                              to='whatsapp:your_personal_whatsapp_number'
                          )

    print(f'Message sent with ID: {message.sid}')


    # Email via SMTP
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.login("simone.parvizi@outlook.it", "your_email_password")
        email_message = f"Subject: New Listings Found\n\n{whatsapp_message}"
        server.sendmail(
            "simone.parvizi@outlook.it",
            "simone.parvizi@outlook.it",
            email_message
        )


previous_listings = []

try:
    previous_listings = []
    while True:
        new_listings, previous_listings = check_new_listings(previous_listings)
        if new_listings:
            # Send notification
            send_notification(new_listings)
        else:
            logging.info(' No new listings found.')  
        time.sleep(5)  # Wait for 5 seconds before refreshing the page


except Exception as e:
    logging.error(f'An error occurred: {e}')

finally:
    driver.quit()  # This will close the browser and quit the driver
