"""
Dodaje domyślne parametry dla algorytmów parametrycznych w bazie danych
"""
import sqlite3
import json

backend_dir = __file__.rsplit('/', 1)[0]
db_path = f"{backend_dir}/db.sqlite3"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== Dodawanie domyślnych parametrów ===\n")

# Parametry dla LCG (GLIBC-like)
lcg_params = {
    'a': 1103515245,
    'c': 12345,
    'm': 2**31,
    'bits_per_value': 31
}

# Parametry dla AWCG (Standard)
awcg_params = {
    'r': 24,
    's': 10,
    'base': 2**32,
    'bits_per_value': 32
}

# Aktualizuj LCG
cursor.execute('''
    UPDATE rngs
    SET parameters = ?
    WHERE (name = 'LCG' OR name = 'LCG GLIBC')
''', (json.dumps(lcg_params),))
print(f"Zaktualizowano {cursor.rowcount} rekord(ów) LCG")
print(f"  Parametry: {lcg_params}\n")

# Aktualizuj AWCG
cursor.execute('''
    UPDATE rngs
    SET parameters = ?
    WHERE name LIKE 'AWCG%'
''', (json.dumps(awcg_params),))
print(f"Zaktualizowano {cursor.rowcount} rekord(ów) AWCG")
print(f"  Parametry: {awcg_params}\n")

conn.commit()

# Pokaż zaktualizowane rekordy
cursor.execute('SELECT id, name, parameters FROM rngs WHERE parameters IS NOT NULL AND parameters != ""')
rows = cursor.fetchall()

print("=== Algorytmy z parametrami ===")
for id, name, params in rows:
    params_dict = json.loads(params) if params else {}
    print(f"ID {id:2d}: {name:20s} -> {params_dict}")

conn.close()
print("\n✓ Parametry dodane!")
