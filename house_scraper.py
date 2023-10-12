from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import smtplib
from twilio.rest import Client
import logging
import random
#%%

##############################################################################
#############                                                 ################
#                                                                            #   
# Make sure to handle the privacy and terms of service of each website you   #
# scrape, as web scraping may be prohibited or restricted by some websites   # 
# Always read and respect the website's robots.txt file and terms of service #
#                                                                            #
#############                                                 ################
##############################################################################

# Set Chrome options for headless browsing
chrome_options = Options()
chrome_options.add_argument("--headless")
logging.basicConfig(level=logging.INFO)

driver = webdriver.Chrome(options=chrome_options)

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

def check_new_listings(url, listing_selector):
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    current_listings = soup.select(listing_selector)
    return current_listings

def send_notification_to_owner(listing, address_selector, email_selector, url):
    address = listing.select_one(address_selector).text
    owner_email = listing.select_one(email_selector).text

    # Customize the message based on the house address
    email_message_to_owner = f"Subject: Interested in your listing at {address}\n\nI am interested in the house at {address}. Please contact me for further details."

    # Send email to owner
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()  # Upgrade the connection to secure encrypted SSL/TLS connection
        server.login("youremail@gmail.com", "your_password_or_app_specific_password")

        # Send email to the owner
        server.sendmail(
            "youremail@gmail.com",
            owner_email,
            email_message_to_owner
        )

        # Send a notification email to yourself with the URL of the house
        notification_email = f"Subject: Sent an email about {address}\n\nYou sent an email expressing interest in the house at {address}. Here's the URL for reference: {url}"
        
        # Sending the notification to yourself by replying to the email you sent to the owner
        server.sendmail(
            "youremail@gmail.com",
            "youremail@gmail.com",
            notification_email,
            headers={"In-Reply-To": owner_email, "References": owner_email}  # These headers make the email appear as a reply in email clients
        )

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
                    logging.info(f'Sent notification for new listing at {url}')
                except Exception as e:
                    logging.error(f'Error sending notification for listing at {url}: {e}')

            previous_listings[url] = current_listings[:MAX_PREVIOUS_LISTINGS]
        
        sleep_duration = random.randint(40, 80)
        logging.info(f'Sleeping for {sleep_duration} seconds')
        time.sleep(sleep_duration)

except Exception as e:
    logging.error(f'An unexpected error occurred: {e}')
