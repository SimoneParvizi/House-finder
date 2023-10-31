import shutil

original_db = 'listings.db'
backup_db = 'listings_backup.db'


shutil.copy2(original_db, backup_db)

