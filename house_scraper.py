#%%

import logging
import random
import os 
from dotenv import load_dotenv
import time
from database import setup_db #, store_listings, get_previous_listings
#%%

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

load_dotenv()

EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
OUTLOOK_EMAIL = os.environ.get('OUTLOOK_EMAIL')
GMAIL_EMAIL = os.environ.get('GMAIL_EMAIL')
PHONE_NUMBER = os.environ.get('PHONE_NUMBER')
IFTTT_WEBHOOKS_URL = os.environ.get('IFTTT_WEBHOOKS_URL')


if __name__ == '__main__':
    setup_db()

    # Log in to the website before starting the scraping loop
    if not login_to_huurstunt():
        logging.error("Failed to log in to the website. Exiting script.")
        exit(1)  # Exit the script with an error code

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
                
                # Fetch the previous listings from the database
                previous_listings_for_url = get_listings_from_db(url)  # Use this function
                
                try:
                    current_listings = check_new_listings(url, listing_selector)
                except Exception as e:
                    logging.error(f'Error checking listings for {url}: {e}')
                    continue  # Skip to the next website
                
                # Find new listings that aren't in the previous listings
                new_listings = [listing for listing in current_listings if listing not in previous_listings_for_url]
                
                for listing in new_listings:
                    try:
                        send_notification_to_owner(listing, address_selector, email_selector, url)
                        address = listing.select_one(address_selector).text
                        send_ifttt_notification(address)
                        logging.info(f'Sent email and IFTTT for new listing at {url}')
                    except Exception as e:
                        logging.error(f'Error sending notification for listing at {url}: {e}')

                # Store the current listings in the database
                store_listings(url, current_listings)

            sleep_duration = random.randint(40, 80)
            logging.info(f'Sleeping for {sleep_duration} seconds')
            time.sleep(sleep_duration)

    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')
