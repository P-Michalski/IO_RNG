import sqlite3

# Połącz się z bazą danych
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Nowy krótszy opis
new_description = "CSPRNG based on quadratic residues"

# Zaktualizuj opis dla algorytmu o id = 16
cursor.execute("""
    UPDATE rngs
    SET description = ? 
    WHERE id = 16
""", (new_description,))

# Zatwierdź zmiany
conn.commit()

# Sprawdź czy się udało
cursor.execute("SELECT name, description FROM rngs WHERE id = 16")
result = cursor.fetchone()
print(f"Updated: {result[0]}")
print(f"New description: {result[1]}")

# Zamknij połączenie
conn.close()