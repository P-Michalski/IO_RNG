Test 3D Spheres losuje punkty w przestrzeni 3D w sześcianie [0,1]³ i zlicza punkty wewnątrz sfery o promieniu r = 0.5 z centrum w (0.5, 0.5, 0.5). Liczba punktów wewnątrz powinna odpowiadać stosunkowi objętości sfery do objętości sześcianu.

## Jak działa

1. Konwertuje bity na punkty 3D w sześcianie [0,1]³
2. Dla każdego punktu oblicza odległość od centrum (0.5, 0.5, 0.5)
3. Zlicza punkty, których odległość ≤ 0.5 (wewnątrz sfery)
4. Porównuje proporcję z teoretyczną wartością (objętość sfery/sześcianu)
5. Używa testu z-score do weryfikacji

## Wzór matematyczny

```
Odległość od centrum:
dist = √((x-0.5)² + (y-0.5)² + (z-0.5)²)

Punkt wewnątrz sfery jeśli: dist ≤ 0.5

Teoretyczna proporcja:
V_sphere / V_cube = (4/3 × π × 0.5³) / 1 ≈ 0.5236

Z-score:
z = |inside_count - expected_inside| /
    √(expected_inside × (1 - expected_ratio))

p-value = erfc(z / √2)
```

## Wartość krytyczna

- **Próg**: p-value ≥ 0.01
- Test **zaliczony** gdy p-value ≥ 0.01

## Minimalne wymagania

- **Minimum**: 150,000 bitów
- **Minimum punktów**: 100
- **Bity na współrzędną**: 10
- **Promień sfery**: 0.5

## Implementacja

Test wykorzystuje numpy do konwersji bitów na współrzędne 3D i obliczania odległości od centrum sfery. Sprawdza czy punkty mieszczą się w sferze wpisanej w sześcian jednostkowy.

## Przykład użycia API

```bash
curl -X POST http://localhost:8000/api/rngs/24/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_3dspheres",
    "samples_count": 150000,
    "parameters": {bits_per_value: 32, msb_first: 1}
  }'
```

## Interpretacja wyników

- **score = 1.0**: Idealny stosunek punktów wewnątrz/na zewnątrz
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, nieprawidłowy rozkład 3D
- **passed = false**: Generator nie przeszedł testu

## Parametry testu

- **Typ danych**: Bity (binary)
- **Minimalna liczba próbek**: 150,000 bitów
- **Złożoność**: Średnia (obliczanie odległości 3D)
- **Optymalizacja**: Wykorzystuje numpy dla obliczeń wektorowych
