import sqlite3

# Połącz się z bazą danych
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Nowe opisy
descriptions = {
    16: "CSPRNG based on quadratic residues",
    23: "Stream-cipher-based CSPRNG (Rust)",
    24: "Fast Xoshiro RNG with good quality (C#/.NET)"
}

# Zaktualizuj opisy dla wszystkich algorytmów
for rng_id, new_description in descriptions.items():
    cursor.execute("""
        UPDATE rngs
        SET description = ? 
        WHERE id = ?
    """, (new_description, rng_id))
    
    # Sprawdź czy się udało
    cursor.execute("SELECT name, description FROM rngs WHERE id = ?", (rng_id,))
    result = cursor.fetchone()
    if result:
        print(f"Updated ID {rng_id}: {result[0]}")
        print(f"New description: {result[1]}\n")

# Zatwierdź wszystkie zmiany
conn.commit()

# Zamknij połączenie
conn.close()