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


def store_listing(address, price=None, size=None, source_website_url=None):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Extract until .com or .nl
    main_part = source_website_url.split(".com")[0] + ".com" if ".com" in source_website_url else source_website_url.split(".nl")[0] + ".nl"

    # Listing with the same specific_url already exists or not
    cursor.execute('SELECT * FROM listings WHERE specific_url = ?', (source_website_url,))
    existing_listing = cursor.fetchone()

    if not existing_listing:
        cursor.execute('''
        INSERT INTO listings (address, price, source_website, specific_url)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (address, price or "NaN", size or "NaN", main_part, source_website_url))

        conn.commit()

    conn.close()


def get_all_listings():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT address, price, size, source_website, specific_url FROM listings
    ''')

    listings = cursor.fetchall()
    conn.close()

    return listings


def get_columns_of_table(table_name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()

    conn.close()
    return [column[1] for column in columns]  # column[1] is the column name in the result


def get_all_tables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    conn.close()
    return [table[0] for table in tables]


def clear_all_listings():
    
    confirmation = input("Are you sure you want to clear all listings? This action cannot be undone. (yes/no): ")
    confirmation
    if confirmation.lower() != 'yes':
        print("Action cancelled.")
        return

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    DELETE FROM listings
    ''')

    conn.commit()
    conn.close()
    print("All listings cleared.")


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


