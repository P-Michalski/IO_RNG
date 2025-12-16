"""
Weryfikacja czy wszystkie algorytmy z bazy danych istnieją w systemie plików
"""
import sqlite3
import os
from pathlib import Path

backend_dir = Path(__file__).parent
project_root = backend_dir.parent
db_path = backend_dir / 'db.sqlite3'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT id, name, code_path FROM rngs ORDER BY id')
rows = cursor.fetchall()

print("=== Weryfikacja plików algorytmów ===\n")

all_ok = True
for id, name, code_path in rows:
    full_path = project_root / code_path
    exists = full_path.exists()

    status = "✓" if exists else "✗"
    print(f"{status} ID {id:2d}: {name:20s} -> {code_path}")

    if not exists:
        print(f"         BRAK PLIKU: {full_path}")
        all_ok = False

conn.close()

if all_ok:
    print("\n✓ Wszystkie algorytmy są dostępne!")
else:
    print("\n✗ Niektóre pliki algorytmów nie istnieją")
