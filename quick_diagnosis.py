import os
import sqlite3
from pathlib import Path


current_dir = os.getcwd()
print(f"Current directory: {current_dir}")


db_paths = [
    "/home/amina/development/code/phase-5/jiseti/jiseti.db",  
    os.path.join(current_dir, "jiseti.db"),  
    os.path.join(current_dir, "instance", "jiseti.db"),  
]

print("\n--- Checking all possible database locations ---")
for db_path in db_paths:
    print(f"\nChecking: {db_path}")
    print(f"Exists: {os.path.exists(db_path)}")
    
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        print(f"Size: {file_size} bytes")
        
        if file_size > 0:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"Tables: {[table[0] for table in tables]}")
                
                
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"  - {table_name}: {count} records")
                
                conn.close()
                
            except Exception as e:
                print(f"Error reading database: {e}")
        else:
            print("Database file is empty")

print(f"\n--- All .db files in {current_dir} ---")
for file in os.listdir(current_dir):
    if file.endswith('.db'):
        full_path = os.path.join(current_dir, file)
        size = os.path.getsize(full_path)
        print(f"Found: {file} (size: {size} bytes)")

instance_dir = os.path.join(current_dir, "instance")
if os.path.exists(instance_dir):
    print(f"\n--- Files in instance directory ---")
    for file in os.listdir(instance_dir):
        if file.endswith('.db'):
            full_path = os.path.join(instance_dir, file)
            size = os.path.getsize(full_path)
            print(f"Found: {file} (size: {size} bytes)")