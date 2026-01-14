import sqlite3
import sys
import os

# Określ system operacyjny
is_windows = sys.platform == "win32"

# Połącz się z bazą danych
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Nowe ścieżki w zależności od systemu
if is_windows:
    paths = {
        23: "algorytmy/chacha20_rng/target/release/chacha20_rng.exe",
        24: "algorytmy/Xorshift256/bin/Xoshiro256.exe"
    }
else:  # Linux/macOS
    paths = {
        23: "algorytmy/chacha20_rng/target/release/chacha20_rng",
        24: "algorytmy/Xorshift256/bin/Release/net9.0/Xoshiro256"
    }

print(f"Detected OS: {'Windows' if is_windows else 'Linux/macOS'}")
print(f"Database: {db_path}\n")

# Zaktualizuj ścieżki dla obu algorytmów
for rng_id, new_path in paths.items():
    # Pobierz obecną ścieżkę
    cursor.execute("SELECT name, code_path FROM rngs WHERE id = ?", (rng_id,))
    result = cursor.fetchone()
    
    if result:
        old_name, old_path = result
        print(f"Updating ID {rng_id}: {old_name}")
        print(f"  Old path: {old_path}")
        print(f"  New path: {new_path}")
        
        # Zaktualizuj ścieżkę
        cursor.execute("""
            UPDATE rngs
            SET code_path = ? 
            WHERE id = ?
        """, (new_path, rng_id))
        
        # Sprawdź czy plik istnieje
        full_path = os.path.join(os.path.dirname(__file__), '..', new_path)
        if os.path.exists(full_path):
            print(f"  ✓ File exists: {full_path}")
        else:
            print(f"  ⚠ WARNING: File not found: {full_path}")
        
        print()
    else:
        print(f"⚠ WARNING: RNG with ID {rng_id} not found in database!\n")

# Zatwierdź zmiany
conn.commit()
print("Database updated successfully!")

# Pokaż finalne ścieżki
print("\nFinal paths in database:")
cursor.execute("SELECT id, name, code_path FROM rngs WHERE id IN (23, 24)")
for row in cursor.fetchall():
    print(f"  ID {row[0]}: {row[1]} -> {row[2]}")

# Zamknij połączenie
conn.close()