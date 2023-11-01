
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import smtplib
from twilio.rest import Client
import requests
import time
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import StaleElementReferenceException

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
    # Twilio account SID and Auth Token
    ACCOUNT_SID = 'YOUR_TWILIO_ACCOUNT_SID'
    AUTH_TOKEN = 'YOUR_TWILIO_AUTH_TOKEN'

    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    # Twilio WhatsApp number (usually starts with "whatsapp:+1...")
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


# Huurstunt
def login_to_huurstunt(driver, email, password):
    print(f"Email: {email}")
    print(f"Password: {password}")

    
    try:
        driver.get("https://www.huurstunt.nl/")

        # Handle the cookie consent bar
        try:
            cookie_allow_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/a[@aria-label='allow cookies']"))
            )
            cookie_allow_button.click()
        except Exception as e:
            logging.error(f"Error handling cookie consent: {e}")

        # Click the "Account" button to open the login modal
        account_button = driver.find_element(By.XPATH, "/html/body/nav/ul/li[2]/a")
        driver.execute_script("arguments[0].scrollIntoView(true);", account_button)
        account_button.click()

        # Wait for and fill in the email and password fields in the login modal
        email_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "login_form_userName"))
        )
        for char in email:
            email_input.send_keys(char)
            time.sleep(0.1)
        time.sleep(2)

        
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='login_form_userPass']"))
        )
        for char in password:
            password_input.send_keys(char)
            time.sleep(0.1)
        #password_input.send_keys(password)
        time.sleep(2)

        # Wait for and click the 'Inloggen' button in the login modal
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div/div[1]/form/div[2]/div[1]/button"))
        )
        submit_button.click()
        print('correclty logged in')

        # numerical_price = 1500
        # price_mapping = {
        #     0: '0',
        #     100: '100',
        #     200: '200',
        #     300: '300',
        #     400: '400',
        #     500: '500',
        #     600: '600',
        #     700: '700',
        #     800: '800',
        #     900: '900',
        #     1000: '1000',
        #     1250: '1250',
        #     1500: '1500',
        #     1750: '1750',
        #     2000: '2000',
        #     2500: '2500',
        #     3000: '3000',
        #     3500: '3500',
        #     4000: '4000',
        #     5000: '5000',
        #     6000: '6000',
        #     10000: 'geen maximum'
        # }

        # # Find the closest price option
        # closest_price = min(price_mapping.keys(), key=lambda x: abs(x - numerical_price))
        # selected_option = price_mapping[closest_price]

        # # Locate the price dropdown element and select the option
        # price_dropdown = driver.find_element(By.XPATH, '//*[@id="price_till"]')
        # print('clicked trial')
        # price_dropdown.click()
        # print(f"Selected option max_price: {selected_option}")
        # option_xpath = f'//option[text()="{selected_option}"]'
        # option = driver.find_element(By.XPATH, option_xpath)
        # option.click()
        # print("Clicked option for max_price")

    except Exception as e:
            print(f"An error occurred during the login process: {e}")

# v2 also doesn't work
def login_to_huurstunt_2(driver, email, password, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            driver.get("https://www.huurstunt.nl/")

            # Handle the cookie consent bar
            try:
                cookie_allow_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/a[@aria-label='allow cookies']"))
                )
                cookie_allow_button.click()
            except Exception as e:
                logging.error(f"Error handling cookie consent: {e}")

            # Click the "Account" button to open the login modal
            account_button = driver.find_element(By.XPATH, "/html/body/nav/ul/li[2]/a")
            driver.execute_script("arguments[0].scrollIntoView(true);", account_button)
            account_button.click()

            # Wait for and fill in the email and password fields in the login modal
            email_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "login_form_userName"))
            )
            email_input.clear()  # Clear the field
            email_input.send_keys(email)

            password_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='login_form_userPass']"))
            )
            password_input.clear()  # Clear the field
            password_input.send_keys(password)

            # Wait for and click the 'Inloggen' button in the login modal
            submit_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div/div[1]/form/div[2]/div[1]/button"))
            ) 
            submit_button.click()
            
            # Assume a successful login if we reach this point without exceptions
            print('Successfully logged in')
            return True

        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < max_attempts - 1:
                print("Retrying...")
                driver.refresh()  # Refresh the page to get back to the initial state
            else:
                print("Max attempts reached.")
                
    # If we exit the loop without a successful login
    return False


def set_max_price_huurstunt(driver, numerical_price):
    price_mapping = {
        0: '0',
        100: '100',
        200: '200',
        300: '300',
        400: '400',
        500: '500',
        600: '600',
        700: '700',
        800: '800',
        900: '900',
        1000: '1000',
        1250: '1250',
        1500: '1500',
        1750: '1750',
        2000: '2000',
        2500: '2500',
        3000: '3000',
        3500: '3500',
        4000: '4000',
        5000: '5000',
        6000: '6000',
        10000: 'geen maximum'
    }

    closest_price = min(price_mapping.keys(), key=lambda x: abs(x - numerical_price))
    selected_option = price_mapping[closest_price]
    
    # Locate the price dropdown for MAX price and select the option
    select = Select(driver.find_element(By.ID, 'price_till'))
    select.select_by_visible_text(selected_option)


def set_min_price_huurstunt(driver, numerical_price):
    
    price_mapping = {
        0: '0',
        100: '100',
        200: '200',
        300: '300',
        400: '400',
        500: '500',
        600: '600',
        700: '700',
        800: '800',
        900: '900',
        1000: '1000',
        1250: '1250',
        1500: '1500',
        1750: '1750',
        2000: '2000',
        2500: '2500',
        3000: '3000',
        3500: '3500',
        4000: '4000',
        5000: '5000',
        6000: '6000',
        10000: 'geen minimum'
    }

    closest_price = min(price_mapping.keys(), key=lambda x: abs(x - numerical_price))
    selected_option = price_mapping[closest_price]


    try:
        # Find and click the min price dropdown
        price_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="price_from"]'))
        )
        price_dropdown.click()
    except StaleElementReferenceException:
        # If a StaleElementReferenceException occurs, re-locate the element
        price_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="price_from"]'))
        )
        price_dropdown.click()
        
    selected_option = str(numerical_price)
    option_xpath = f'//option[text()="{selected_option}"]'
    option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, option_xpath))
    )
    option.click()


def set_filters_huurstunt(driver, min_price, max_price, location):

    set_min_price_huurstunt(driver, min_price)
    set_max_price_huurstunt(driver, max_price)

    time.sleep(2)
    # Location
    location_field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'location'))
    )
    location_field.send_keys(location)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".suggestion.tt-suggestion"))
    )

    location_field.send_keys(Keys.ARROW_DOWN)
    location_field.send_keys(Keys.RETURN)

    # Search
    time.sleep(2)
    search_button = driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div/div/div/div/form/div[2]/button')
    search_button.click()

    # Studio option
    time.sleep(2)
    studio_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//label[@class='form-check-label' and contains(text(), 'Studio')]"))
    )
    
    driver.execute_script("arguments[0].scrollIntoView(true);", studio_button)
    time.sleep(2)
    driver.execute_script("arguments[0].click();", studio_button)








# To finish
def authenticate_google_account():
    # Check if the user has already authenticated and stored their credentials
    creds = None
    if os.path.exists('token.json'):
        creds = service_account.Credentials.from_authorized_user_file('token.json', SCOPES)

    # If not, initiate the OAuth flow to obtain credentials
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for future use
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())

    # Build a service object using the obtained credentials
    service = build('drive', 'v3', credentials=creds)

    return service

