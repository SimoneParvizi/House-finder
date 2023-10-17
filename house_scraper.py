#%%
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import smtplib
from twilio.rest import Client
import logging
import random
import requests
import os 


chrome_options = Options()
chrome_options.add_argument("--headless")
logging.basicConfig(level=logging.INFO)

driver = webdriver.Chrome(options=chrome_options)


# UPDATE WITH MORE WEBSITES
WEBSITES = [
    {
        'url': 'https://www.huurstunt.nl/studio/huren/amsterdam/+2km/0-1500/',
        'listing_selector': '.listing-item',
        'address_selector': '.address-class',  # Example, update with correct selector
        'email_selector': '.email-class'      # Example, update with correct selector
    },
    
    {
        'url': 'https://another-website.com/some-page/',
        'listing_selector': '.another-listing-item',
        'address_selector': '.address-class-for-another-website',  # This needs to be updated
        'email_selector': '.email-class-for-another-website'      # This needs to be updated
    }

]

EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
OUTLOOK_EMAIL = os.environ.get('OUTLOOK_EMAIL')
GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL')
PHONE_NUMBER = os.environ.get('PHONE_NUMBER')
IFTTT_WEBHOOKS_URL = os.environ.get('IFTTT_WEBHOOKS_URL')


def check_new_listings(url, listing_selector):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    current_listings = soup.select(listing_selector)
    return current_listings


def send_notification_to_owner(listing, address_selector, email_selector, url):
    address = listing.select_one(address_selector).text
    owner_email = listing.select_one(email_selector).text

    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={address.replace(' ', '+')}"

    # Customized email
    email_message_to_owner = f"""
    I am very interested in viewing the available studio ({address}) and would like to arrange a visit as soon as possible. 

    My gross monthly income is 4000 euros, I live alone, have no pets, and I am a non-smoker. I am currently employed as the Head of Product and Machine Learning Engineer at a health tech company based in Amsterdam.

    Reach me at {PHONE_NUMBER} or respond directly to this email ({OUTLOOK_EMAIL}) to confirm the appointment or to discuss any other details.

    Thank you for considering my application. I am looking forward to hearing back from you soon.

    Kindly,
    Simone Parvizi
    """


    # Send emails
    with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:
        server.starttls()  # Upgrade the connection to secure encrypted SSL/TLS connection ????????
        server.login(OUTLOOK_EMAIL, EMAIL_PASSWORD)


        # Custom message
        notification_email = f"You sent an email for the studio in {address} ({url}).\nHere's the location: {google_maps_url} "
        


        # For the owner email:
        headers = [
            "From: {}".format(OUTLOOK_EMAIL),
            "Subject: Studio in {}".format(address),
            "To: {}".format(owner_email),
            "MIME-Version: 1.0",
            "Content-Type: text/plain; charset=utf-8"
        ]
        full_email = "\r\n".join(headers) + "\r\n\r\n" + email_message_to_owner

        # Send the email to the owner
        server.sendmail(
            OUTLOOK_EMAIL,
            owner_email,
            full_email.encode("utf-8")
            )

        # Email to yourself:
        headers = [
            "From: {}".format(OUTLOOK_EMAIL),
            "Subject: FOUND A STUDIO at {}".format(address),
            "To: {}".format(OUTLOOK_EMAIL),
            "In-Reply-To: {}".format(owner_email),
            "References: {}".format(owner_email),
            "MIME-Version: 1.0",
            "Content-Type: text/plain; charset=utf-8"
            ]
        
        full_notification_email = "\r\n".join(headers) + "\r\n\r\n" + notification_email


        # Send the notification email to yourself
        server.sendmail(
            OUTLOOK_EMAIL,
            OUTLOOK_EMAIL,
            full_notification_email.encode("utf-8")
            )

# Twilio 
def send_whatsapp_notification(message_body):
    # Your Twilio account SID and Auth Token
    ACCOUNT_SID = 'YOUR_TWILIO_ACCOUNT_SID'
    AUTH_TOKEN = 'YOUR_TWILIO_AUTH_TOKEN'

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    # Your Twilio WhatsApp number (usually starts with "whatsapp:+1...")
    # and your personal WhatsApp number (make sure to include the country code, e.g., "+1234567890")
    from_whatsapp_number = 'whatsapp:YOUR_TWILIO_WHATSAPP_NUMBER'
    to_whatsapp_number = 'whatsapp:YOUR_PERSONAL_WHATSAPP_NUMBER'

    message = client.messages.create(
        body=message_body,
        from_=from_whatsapp_number,
        to=to_whatsapp_number
    )

    return message.sid

# IFTTT
def send_ifttt_notification(value1):

    data = {"value1": value1}
    response = requests.post(IFTTT_WEBHOOKS_URL, data=data)
    print(f"Sending to URL: {IFTTT_WEBHOOKS_URL}")
    print(f"Payload: {data}")
    return response.status_code

#%%
if __name__ == '__main__':


    previous_listings = {}
    MAX_PREVIOUS_LISTINGS = 100 

    try:
        while True:
            for website in WEBSITES:
                url = website['url']
                listing_selector = website['listing_selector']
                address_selector = website['address_selector']
                email_selector = website['email_selector']

                logging.info(f'Checking new listings for {url}')
                
                try:
                    current_listings = check_new_listings(url, listing_selector)
                except Exception as e:
                    logging.error(f'Error checking listings for {url}: {e}')
                    continue  # Skip to the next website
                
                if url not in previous_listings:
                    previous_listings[url] = []
                
                new_listings = [listing for listing in current_listings if listing not in previous_listings[url]]
                
                for listing in new_listings:
                    try:
                        send_notification_to_owner(listing, address_selector, email_selector, url)
                        address = listing.select_one(address_selector).text
                        send_ifttt_notification(address)
                        logging.info(f'Sent email and IFTTT for new listing at {url}')
                    except Exception as e:
                        logging.error(f'Error sending notification for listing at {url}: {e}')

                previous_listings[url] = current_listings[:MAX_PREVIOUS_LISTINGS]
            
            sleep_duration = random.randint(40, 80)
            logging.info(f'Sleeping for {sleep_duration} seconds')
            time.sleep(sleep_duration)

    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')

#%%

def send_notification_to_owner(listing, address_selector, email_selector, url):
    address = listing.select_one(address_selector).text
    owner_email = listing.select_one(email_selector).text

    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={address.replace(' ', '+')}"

    # Customized email
    email_message_to_owner = f"""
    I am very interested in viewing the available studio ({address}) and would like to arrange a visit as soon as possible. 

    My gross monthly income is 4000 euros, I live alone, have no pets, and I am a non-smoker. I am currently employed as the Head of Product and Machine Learning Engineer at a health tech company based in Amsterdam.

    Reach me at {PHONE_NUMBER} or respond directly to this email ({OUTLOOK_EMAIL}) to confirm the appointment or to discuss any other details.

    Thank you for considering my application. I am looking forward to hearing back from you soon.

    Kindly,
    Simone Parvizi
    """


    # Send emails
    with smtplib.SMTP('smtp-mail.outlook.com', 587) as server:
        server.starttls()  # Upgrade the connection to secure encrypted SSL/TLS connection ????????
        server.login(OUTLOOK_EMAIL, EMAIL_PASSWORD)


        # Custom message
        notification_email = f"You sent an email for the studio in {address} ({url}).\nHere's the location: {google_maps_url} "
        


        # For the owner email:
        headers = [
            "From: {}".format(OUTLOOK_EMAIL),
            "Subject: Studio in {}".format(address),
            "To: {}".format(owner_email),
            "MIME-Version: 1.0",
            "Content-Type: text/plain; charset=utf-8"
        ]
        full_email = "\r\n".join(headers) + "\r\n\r\n" + email_message_to_owner

        # Send the email to the owner
        server.sendmail(
            OUTLOOK_EMAIL,
            owner_email,
            full_email.encode("utf-8")
            )

        # Email to yourself:
        headers = [
            "From: {}".format(OUTLOOK_EMAIL),
            "Subject: FOUND A STUDIO at {}".format(address),
            "To: {}".format(OUTLOOK_EMAIL),
            "In-Reply-To: {}".format(owner_email),
            "References: {}".format(owner_email),
            "MIME-Version: 1.0",
            "Content-Type: text/plain; charset=utf-8"
            ]
        
        full_notification_email = "\r\n".join(headers) + "\r\n\r\n" + notification_email


        # Send the notification email to yourself
        server.sendmail(
            OUTLOOK_EMAIL,
            OUTLOOK_EMAIL,
            full_notification_email.encode("utf-8")
            )

html = """
<div class="listing">
    <div class="address">123 Test Street</div>
    <div class="email">parvizi.simone@gmail.com</div>
</div>
"""
soup = BeautifulSoup(html, 'html.parser')
listing = soup.select_one('.listing')

# Dummy website
url = "https://example.com/test-listing"
address_selector = ".address"
email_selector = ".email"

send_notification_to_owner(listing, address_selector, email_selector, url)

# %%
