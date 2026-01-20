import sqlite3
import os

def update_algorithm_paths():
    """
    Aktualizuje ścieżki code_path dla algorytmów o id 23 i 24 w bazie danych.
    """
    # Ścieżka do bazy danych
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    
    if not os.path.exists(db_path):
        print(f"Błąd: Nie znaleziono bazy danych pod ścieżką: {db_path}")
        return
    
    try:
        # Połączenie z bazą danych
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Aktualizacja algorytmu id=24 (Xorshift256)
        new_path_24 = 'algorytmy/Xorshift256/bin/Xoshiro256.exe'
        cursor.execute(
            "UPDATE rngs SET code_path = ? WHERE id = ?",
            (new_path_24, 24)
        )
        
        # Aktualizacja algorytmu id=23 (ChaCha20)
        new_path_23 = 'algorytmy/chacha20_rng/target/release/chacha20_rng.exe'
        cursor.execute(
            "UPDATE rngs SET code_path = ? WHERE id = ?",
            (new_path_23, 23)
        )
        
        # Zatwierdzenie zmian
        conn.commit()
        
        # Sprawdzenie czy aktualizacja się powiodła
        cursor.execute("SELECT id, name, code_path FROM rngs WHERE id IN (23, 24)")
        results = cursor.fetchall()
        
        print("✓ Pomyślnie zaktualizowano ścieżki algorytmów:")
        print("-" * 80)
        for row in results:
            print(f"ID: {row[0]}")
            print(f"Nazwa: {row[1]}")
            print(f"Nowa ścieżka: {row[2]}")
            print("-" * 80)
        
    except sqlite3.Error as e:
        print(f"Błąd bazy danych: {e}")
    
    finally:
        if conn:
            conn.close()
            print("\n✓ Połączenie z bazą danych zamknięte")

if __name__ == "__main__":
    print("=== Aktualizacja ścieżek algorytmów ===\n")
    update_algorithm_paths()