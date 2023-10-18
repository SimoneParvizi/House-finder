import sqlite3
from urllib.parse import urlparse

DATABASE_NAME = "listings.db"

def setup_db():
    create_table()

def create_table():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS listings (
        id INTEGER PRIMARY KEY,
        address TEXT,
        published_time TEXT,  -- Stored as 'DD-MM-YYYY'
        price REAL,
        size REAL,
        source_website TEXT
    )
    ''')

    conn.commit()
    conn.close()


def store_listing(address=None, published_time=None, price=None, size=None, source_website_url=None):
    
    # Replace missing values with 'NaN' or any other placeholder value
    address = address or "NaN"
    published_time = published_time or "NaN"
    price = price or "NaN"
    size = size or "NaN"
    source_website_url = source_website_url or "NaN"
    
    # Extract main part of domain from the URL
    if source_website_url != "NaN":
        parsed_url = urlparse(source_website_url)
        domain = parsed_url.netloc.split(".")
        if len(domain) > 2:
            # For domains like 'www.example.com', extract 'example'
            main_part = domain[-2]
        else:
            # For domains like 'example.com', extract 'example'
            main_part = domain[0]
    else:
        main_part = "NaN"

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO listings (address, published_time, price, size, source_website)
    VALUES (?, ?, ?, ?, ?)
    ''', (address, published_time, price, size, main_part))

    conn.commit()
    conn.close()


def get_all_listings():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT address, published_time, price, size, source_website FROM listings
    ''')

    listings = cursor.fetchall()
    conn.close()

    return listings


def clear_all_listings():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    DELETE FROM listings
    ''')

    conn.commit()
    conn.close()

def alter_table():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Add the published_time column
    cursor.execute('ALTER TABLE listings ADD COLUMN published_time TEXT')
    # Add the price column
    cursor.execute('ALTER TABLE listings ADD COLUMN price REAL')
    # Add the size column
    cursor.execute('ALTER TABLE listings ADD COLUMN size REAL')
    # Add the source_website column
    cursor.execute('ALTER TABLE listings ADD COLUMN source_website TEXT')

    conn.commit()
    conn.close()

