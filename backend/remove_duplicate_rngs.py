import sqlite3
import os

# Połącz się z bazą danych
db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Database: {db_path}\n")

# IDs do usunięcia
ids_to_remove = [1, 10]

# Pokaż informacje o algorytmach przed usunięciem
print("Algorithms to be removed:")
for rng_id in ids_to_remove:
    cursor.execute("SELECT id, name, description FROM rngs WHERE id = ?", (rng_id,))
    result = cursor.fetchone()
    if result:
        print(f"  ID {result[0]}: {result[1]}")
        print(f"    Description: {result[2]}")
    else:
        print(f"  ID {rng_id}: Not found in database")
print()

# Sprawdź czy są jakieś powiązane wyniki testów
print("Checking for related test results...")
for rng_id in ids_to_remove:
    cursor.execute("SELECT COUNT(*) FROM test_results WHERE rng_id = ?", (rng_id,))
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"  ⚠ Warning: Found {count} test result(s) for RNG ID {rng_id}")
    else:
        print(f"  ✓ No test results found for RNG ID {rng_id}")
print()

# Potwierdź usunięcie
confirm = input("Do you want to proceed with deletion? (yes/no): ")
if confirm.lower() not in ['yes', 'y']:
    print("Deletion cancelled.")
    conn.close()
    exit()

# Usuń powiązane wyniki testów (jeśli istnieją)
print("\nDeleting related test results...")
for rng_id in ids_to_remove:
    cursor.execute("DELETE FROM test_results WHERE rng_id = ?", (rng_id,))
    deleted = cursor.rowcount
    if deleted > 0:
        print(f"  Deleted {deleted} test result(s) for RNG ID {rng_id}")

# Usuń algorytmy
print("\nDeleting RNG algorithms...")
for rng_id in ids_to_remove:
    cursor.execute("DELETE FROM rngs WHERE id = ?", (rng_id,))
    if cursor.rowcount > 0:
        print(f"  ✓ Deleted RNG ID {rng_id}")
    else:
        print(f"  ⚠ RNG ID {rng_id} not found")

# Zatwierdź zmiany
conn.commit()
print("\n✓ Database updated successfully!")

# Pokaż pozostałe algorytmy
print("\nRemaining RNG algorithms:")
cursor.execute("SELECT id, name FROM rngs ORDER BY id")
for row in cursor.fetchall():
    print(f"  ID {row[0]}: {row[1]}")

# Zamknij połączenie
conn.close()