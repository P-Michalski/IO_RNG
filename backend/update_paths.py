"""
Script to update RNG file paths in database to relative paths (universal across systems)
"""
import sqlite3
import os

# Get the absolute path to the backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))

print(f"Backend directory: {backend_dir}")
print()

# Connect to database
db_path = os.path.join(backend_dir, 'db.sqlite3')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get current paths
cursor.execute('SELECT id, name, code_path FROM rngs')
rows = cursor.fetchall()

print("Current paths:")
for row in rows:
    print(f"  ID: {row[0]}, Name: {row[1]}, Path: {row[2]}")
print()

# Update paths to relative (just filename, will be resolved at runtime)
updates = []

for row in rows:
    id, name, old_path = row
    # Extract just the filename
    filename = os.path.basename(old_path)
    updates.append((filename, id))
    print(f"Updating ID {id}: {old_path} -> {filename}")

# Execute updates
for new_path, id in updates:
    cursor.execute('UPDATE rngs SET code_path = ? WHERE id = ?', (new_path, id))

conn.commit()

# Verify updates
cursor.execute('SELECT id, name, code_path FROM rngs')
updated_rows = cursor.fetchall()

print("\nUpdated paths (now just filenames):")
for row in updated_rows:
    print(f"  ID: {row[0]}, Name: {row[1]}, Path: {row[2]}")

conn.close()
print("\nDatabase updated successfully!")
print("Note: Paths are now relative filenames. The backend code will resolve them at runtime.")
