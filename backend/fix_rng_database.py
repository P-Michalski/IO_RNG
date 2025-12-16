"""
Skrypt do uporządkowania bazy danych RNG:
1. Usuwa duplikaty
2. Aktualizuje ścieżki na algorytmy/*.py
3. Dodaje brakujące algorytmy
"""
import sqlite3
import os

# Katalog backend
backend_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(backend_dir, 'db.sqlite3')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Stan początkowy ===")
cursor.execute('SELECT id, name, language, code_path FROM rngs ORDER BY id')
rows = cursor.fetchall()
for row in rows:
    print(f"ID: {row[0]:2d}, Name: {row[1]:20s}, Language: {row[2]:10s}, Path: {row[3]}")
print()

# Krok 1: Usuń duplikaty - zostaw tylko pierwszy wpis każdego typu
print("=== Usuwanie duplikatów ===")
# Znajdź duplikaty
cursor.execute('''
    SELECT name, code_path, MIN(id) as keep_id
    FROM rngs
    GROUP BY name, code_path
    HAVING COUNT(*) > 1
''')
duplicates = cursor.fetchall()

for name, path, keep_id in duplicates:
    cursor.execute('''
        DELETE FROM rngs
        WHERE name = ? AND code_path = ? AND id != ?
    ''', (name, path, keep_id))
    deleted = cursor.rowcount
    if deleted > 0:
        print(f"Usunięto {deleted} duplikat(ów): {name}")

conn.commit()
print()

# Krok 2: Aktualizuj ścieżki na algorytmy/*.py
print("=== Aktualizacja ścieżek ===")
cursor.execute('SELECT id, name, code_path FROM rngs')
rows = cursor.fetchall()

for id, name, old_path in rows:
    filename = os.path.basename(old_path)
    new_path = f"algorytmy/{filename}"
    if new_path != old_path:
        cursor.execute('UPDATE rngs SET code_path = ? WHERE id = ?', (new_path, id))
        print(f"ID {id:2d}: {old_path} -> {new_path}")

conn.commit()
print()

# Krok 3: Dodaj brakujące algorytmy
print("=== Dodawanie brakujących algorytmów ===")

# Sprawdź jakie algorytmy już są
cursor.execute('SELECT name, code_path FROM rngs')
existing = [(name, path) for name, path in cursor.fetchall()]
existing_paths = [path for _, path in existing]

# Lista wszystkich algorytmów Python
algorithms = [
    {
        'name': 'Blum Blum Shub',
        'language': 'python',
        'algorithm': 'Blum Blum Shub',
        'description': 'Kryptograficznie bezpieczny generator oparty na problemie kwadratowych residuów',
        'code_path': 'algorytmy/BlumBlumShub.py',
        'is_active': 1,
        'parameters': None
    }
]

for algo in algorithms:
    if algo['code_path'] not in existing_paths:
        cursor.execute('''
            INSERT INTO rngs (name, language, algorithm, description, code_path, is_active, parameters, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (
            algo['name'],
            algo['language'],
            algo['algorithm'],
            algo['description'],
            algo['code_path'],
            algo['is_active'],
            algo['parameters']
        ))
        print(f"Dodano: {algo['name']} ({algo['code_path']})")
    else:
        print(f"Już istnieje: {algo['name']}")

conn.commit()
print()

# Pokaż końcowy stan
print("=== Stan końcowy ===")
cursor.execute('SELECT id, name, language, code_path FROM rngs ORDER BY id')
rows = cursor.fetchall()
for row in rows:
    print(f"ID: {row[0]:2d}, Name: {row[1]:20s}, Language: {row[2]:10s}, Path: {row[3]}")

conn.close()
print("\n✓ Baza danych zaktualizowana!")
