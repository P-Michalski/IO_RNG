# Dokumentacja Testów Statystycznych RNG

## Spis treści
1. [Testy Podstawowe](#testy-podstawowe)
   - [Frequency Test (Chi-square)](#1-frequency-test-chi-square)
   - [Uniformity Test](#2-uniformity-test)
2. [NIST Test Suite](#nist-test-suite)
   - [Monobit Test](#3-nist-monobit-test)
   - [Block Frequency Test](#4-nist-block-frequency-test)
   - [Runs Test](#5-nist-runs-test)
   - [Longest Run of Ones Test](#6-nist-longest-run-of-ones-test)
   - [Cumulative Sums Test](#7-nist-cumulative-sums-test)
   - [Approximate Entropy Test](#8-nist-approximate-entropy-test)

---

## Testy Podstawowe

### 1. Frequency Test (Chi-square)

#### Opis
Test częstości Chi-kwadrat sprawdza, czy wygenerowane liczby są równomiernie rozłożone w zadanych przedziałach (binach). Jest to podstawowy test równomierności rozkładu.

#### Jak działa
1. Dzieli zakres [0, 1] na 10 równych przedziałów (binów)
2. Zlicza ile liczb wpadło do każdego przedziału
3. Porównuje obserwowane częstości z oczekiwanymi za pomocą statystyki Chi-kwadrat
4. Oblicza wynik testu na podstawie odchylenia od idealnego rozkładu

#### Wzór matematyczny
```
χ² = Σ ((Oi - Ei)² / Ei)

gdzie:
- Oi = obserwowana liczba w binie i
- Ei = oczekiwana liczba w binie i (n/10)
- n = całkowita liczba próbek
```

#### Wartość krytyczna
- **Próg**: χ² < 16.919 (dla α=0.05, df=9)
- Test **zaliczony** gdy χ² < wartość krytyczna

#### Implementacja
```python
def _frequency_test(self, numbers: List[float]) -> Dict[str, Any]:
    num_bins = 10
    bins = [0] * num_bins

    # Zlicz liczby w każdym binie
    for num in numbers:
        bin_idx = min(int(num * num_bins), num_bins - 1)
        bins[bin_idx] += 1

    # Chi-square test
    expected = len(numbers) / num_bins
    chi_square = sum(
        (observed - expected) ** 2 / expected
        for observed in bins
    )

    critical_value = 16.919
    passed = chi_square < critical_value
    score = max(0.0, min(1.0, 1 - (chi_square / critical_value)))

    return {
        'passed': passed,
        'score': round(score, 2),
        'statistics': {
            'chi_square': round(chi_square, 3),
            'critical_value': critical_value,
            'bins': bins,
            'expected_per_bin': expected
        }
    }
```

#### Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "frequency_test",
    "samples_count": 10000,
    "seed": 42
  }'
```

#### Interpretacja wyników
- **score = 1.0**: Idealny rozkład równomierny
- **score > 0.7**: Bardzo dobry wynik
- **score < 0.5**: Słaby generator, może nie być losowy
- **passed = false**: Generator nie przeszedł testu, rozkład niejednostajny

---

### 2. Uniformity Test

#### Opis
Test równomierności sprawdza, czy średnia i wariancja wygenerowanych liczb odpowiadają teoretycznym wartościom dla rozkładu jednostajnego U(0,1).

#### Jak działa
1. Oblicza średnią arytmetyczną wszystkich liczb
2. Oblicza wariancję próbki
3. Porównuje z wartościami oczekiwanymi:
   - Średnia powinna ≈ 0.5
   - Wariancja powinna ≈ 1/12 ≈ 0.0833

#### Wzory matematyczne
```
Średnia: μ = (1/n) × Σ xi
Wariancja: σ² = (1/n) × Σ (xi - μ)²

Dla U(0,1):
- Oczekiwana średnia: E[X] = 0.5
- Oczekiwana wariancja: Var[X] = 1/12 ≈ 0.0833
```

#### Kryteria zdania
- **|średnia - 0.5| < 0.05**
- **|wariancja - 0.0833| < 0.02**
- Obie warunki muszą być spełnione

#### Implementacja
```python
def _uniformity_test(self, numbers: List[float]) -> Dict[str, Any]:
    n = len(numbers)

    # Oblicz średnią
    mean = sum(numbers) / n

    # Oblicz wariancję
    variance = sum((x - mean) ** 2 for x in numbers) / n

    # Wartości oczekiwane dla rozkładu uniform [0,1]
    expected_mean = 0.5
    expected_variance = 1.0 / 12.0  # ≈ 0.083

    # Różnice
    mean_diff = abs(mean - expected_mean)
    var_diff = abs(variance - expected_variance)

    # Test przechodzi jeśli różnice są małe
    passed = mean_diff < 0.05 and var_diff < 0.02

    # Score bazujący na różnicach
    score = max(0.0, min(1.0, 1 - (mean_diff * 10 + var_diff * 5)))

    return {
        'passed': passed,
        'score': round(score, 2),
        'statistics': {
            'mean': round(mean, 6),
            'expected_mean': expected_mean,
            'variance': round(variance, 6),
            'expected_variance': round(expected_variance, 6),
            'mean_diff': round(mean_diff, 6),
            'var_diff': round(var_diff, 6)
        }
    }
```

#### Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "uniformity_test",
    "samples_count": 50000
  }'
```

#### Interpretacja wyników
- **mean ≈ 0.5**: Generator produkuje liczby symetrycznie wokół środka
- **variance ≈ 0.083**: Rozproszenie danych jest prawidłowe
- **mean_diff > 0.05**: Generator może mieć bias (skrzywienie)
- **var_diff > 0.02**: Liczby są zbyt skupione lub zbyt rozproszone

---

## NIST Test Suite

NIST (National Institute of Standards and Technology) opracował zestaw 15 testów statystycznych do oceny losowości sekwencji bitowych. Poniżej implementacja 6 kluczowych testów z tego zestawu.

### 3. NIST Monobit Test

#### Opis
Najprostszy test NIST. Sprawdza, czy liczba jedynek i zer w sekwencji bitowej jest w przybliżeniu równa. Jest to fundamentalny test równowagi bitów.

#### Jak działa
1. Konwertuje bity na wartości +1 (dla 1) i -1 (dla 0)
2. Sumuje wszystkie wartości
3. Im mniejsza suma bezwzględna, tym lepiej zbalansowana sekwencja
4. Oblicza p-value za pomocą funkcji komplementarnej błędu (erfc)

#### Wzory matematyczne
```
S = Σ (2×biti - 1)  gdzie bit ∈ {0,1}

Statystyka testowa:
s_obs = |S| / √n

P-value:
p = erfc(s_obs / √2)
```

#### Kryterium zdania
- **p-value ≥ 0.01**
- Test zaliczony gdy p-value jest wystarczająco duże

#### Implementacja
```python
def _nist_monobit_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)
    # S = suma bitów (jako +1/-1)
    s = sum(1 if bit == 1 else -1 for bit in bits)

    # Test statistic
    s_obs = abs(s) / math.sqrt(n)

    # P-value
    p_value = erfc(s_obs / math.sqrt(2))

    # Test passes if p-value >= 0.01
    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': round(score, 4),
        'statistics': {
            'p_value': round(p_value, 6),
            'test_statistic': round(s_obs, 6),
            'ones': sum(bits),
            'zeros': n - sum(bits),
            'threshold': 0.01
        }
    }
```

#### Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_monobit",
    "samples_count": 100000
  }'
```

#### Interpretacja wyników
- **p-value ≈ 1.0**: Idealna równowaga między 0 i 1
- **p-value > 0.5**: Bardzo dobra równowaga
- **p-value < 0.01**: Test niezaliczony, sekwencja nielosowa
- **ones ≈ zeros**: Dobry znak równowagi

#### Przykład wyniku
```json
{
  "passed": true,
  "score": 0.8234,
  "statistics": {
    "p_value": 0.823412,
    "test_statistic": 0.224,
    "ones": 50112,
    "zeros": 49888,
    "threshold": 0.01
  },
  "generated_bits": [0, 1, 1, 0, ...]
}
```

---

### 4. NIST Block Frequency Test

#### Opis
Test sprawdza, czy proporcja jedynek w poszczególnych blokach (podciągach) jest bliska 0.5. Jest to bardziej lokalna wersja testu Monobit.

#### Jak działa
1. Dzieli sekwencję bitów na bloki o wielkości M (domyślnie 128 bitów)
2. Dla każdego bloku oblicza proporcję jedynek
3. Sprawdza, czy proporcje są bliskie 0.5 za pomocą statystyki Chi-kwadrat
4. Oblicza p-value

#### Wzory matematyczne
```
Dla każdego bloku i:
πi = (liczba jedynek w bloku i) / M

Statystyka Chi-kwadrat:
χ² = 4M × Σ (πi - 0.5)²

P-value:
p = erfc(√(χ²/2))
```

#### Parametry
- **Domyślny rozmiar bloku**: M = 128 bitów
- **Minimalny rozmiar sekwencji**: 128 bitów
- **Kryterium**: p-value ≥ 0.01

#### Implementacja
```python
def _nist_block_frequency_test(self, bits: List[int], block_size: int = 128):
    import math
    from math import erfc

    n = len(bits)
    num_blocks = n // block_size

    if num_blocks == 0:
        return {
            'passed': False,
            'score': 0.0,
            'statistics': {'error': 'Not enough bits for block test'}
        }

    # Chi-square statistic
    chi_square = 0.0
    proportions = []

    for i in range(num_blocks):
        block = bits[i * block_size:(i + 1) * block_size]
        proportion = sum(block) / block_size
        proportions.append(proportion)
        chi_square += (proportion - 0.5) ** 2

    chi_square *= 4 * block_size

    # P-value
    p_value = erfc(math.sqrt(chi_square / 2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': round(score, 4),
        'statistics': {
            'p_value': round(p_value, 6),
            'chi_square': round(chi_square, 6),
            'num_blocks': num_blocks,
            'block_size': block_size,
            'threshold': 0.01
        }
    }
```

#### Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_block_frequency",
    "samples_count": 128000
  }'
```

#### Interpretacja wyników
- **p-value > 0.5**: Wszystkie bloki mają dobrą równowagę
- **p-value ≈ 0.01**: Graniczny wynik, niektóre bloki mogą być niezbalansowane
- **num_blocks**: Im więcej bloków, tym bardziej wiarygodny test
- **chi_square**: Im mniejsza wartość, tym lepiej

---

### 5. NIST Runs Test

#### Opis
Test sprawdza, czy liczba przejść (runs) między 0 a 1 jest prawidłowa. Run to nieprzerwany ciąg identycznych bitów. Test wykrywa czy sekwencja nie jest zbyt "gładka" lub zbyt "zmienna".

#### Jak działa
1. Sprawdza pre-test: proporcja jedynek musi być bliska 0.5
2. Zlicza liczbę runs (przejść z 0→1 lub 1→0)
3. Porównuje z oczekiwaną liczbą runs
4. Oblicza p-value

#### Wzory matematyczne
```
π = liczba jedynek / n

Pre-test: |π - 0.5| < 2/√n

Liczba runs: V_n (obs) = liczenie przejść

Oczekiwana liczba runs:
E[V_n] = 2nπ(1-π)

Statystyka testowa:
T = |V_n(obs) - E[V_n]| / (2√(2n)π(1-π))

P-value:
p = erfc(T/√2)
```

#### Przykład runs
```
Sekwencja: 1 1 0 0 0 1 1 1 0 1
Runs:      [11][000][111][0][1]
Liczba runs: 5
```

#### Implementacja
```python
def _nist_runs_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)
    ones = sum(bits)
    pi = ones / n

    # Pre-test: proporcja jedynek musi być bliska 0.5
    if abs(pi - 0.5) >= 2 / math.sqrt(n):
        return {
            'passed': False,
            'score': 0.0,
            'statistics': {
                'error': 'Pre-test failed: proportion of ones not close to 0.5',
                'proportion': round(pi, 6)
            }
        }

    # Zlicz runs
    runs = 1
    for i in range(1, n):
        if bits[i] != bits[i - 1]:
            runs += 1

    # Expected value
    expected_runs = 2 * n * pi * (1 - pi)

    # Test statistic
    numerator = abs(runs - expected_runs)
    denominator = 2 * math.sqrt(2 * n) * pi * (1 - pi)
    test_stat = numerator / denominator if denominator != 0 else 0

    # P-value
    p_value = erfc(test_stat / math.sqrt(2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': round(score, 4),
        'statistics': {
            'p_value': round(p_value, 6),
            'runs': runs,
            'expected_runs': round(expected_runs, 2),
            'threshold': 0.01
        }
    }
```

#### Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_runs",
    "samples_count": 100000
  }'
```

#### Interpretacja wyników
- **runs ≈ expected_runs**: Prawidłowa liczba przejść
- **runs << expected_runs**: Sekwencja zbyt "gładka", długie serie tych samych bitów
- **runs >> expected_runs**: Sekwencja zbyt "zmienna", za dużo przełączeń
- **Pre-test failed**: Sekwencja nie jest zbalansowana (użyj najpierw Monobit)

---

### 6. NIST Longest Run of Ones Test

#### Opis
Test sprawdza długość najdłuższego ciągu jedynek w sekwencji. Zbyt krótkie lub zbyt długie maksymalne serie mogą wskazywać na niełosowość.

#### Jak działa
1. Dzieli sekwencję na bloki
2. W każdym bloku znajduje najdłuższy ciąg jedynek
3. Klasyfikuje bloki według długości najdłuższego run
4. Porównuje rozkład z oczekiwanym za pomocą Chi-kwadrat

#### Parametry zależne od długości
```
n < 6,272:
  - M = 8 (rozmiar bloku)
  - K = 3 (liczba kategorii)
  - Kategorie długości: ≤1, 2, 3, ≥4

6,272 ≤ n < 750,000:
  - M = 128
  - K = 5
  - Kategorie: ≤4, 5, 6, 7, 8, ≥9

n ≥ 750,000:
  - M = 10,000
  - K = 6
  - Kategorie: ≤10, 11, 12, 13, 14, 15, ≥16
```

#### Implementacja
```python
def _nist_longest_run_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)

    if n < 128:
        return {'passed': False, 'score': 0.0,
                'statistics': {'error': 'Minimum 128 bits required'}}

    # Parametry dla różnych długości
    if n < 6272:
        K, M = 3, 8
        v_values = [1, 2, 3, 4]
        pi_values = [0.2148, 0.3672, 0.2305, 0.1875]
    elif n < 750000:
        K, M = 5, 128
        v_values = [4, 5, 6, 7, 8, 9]
        pi_values = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
    else:
        K, M = 6, 10000
        v_values = [10, 11, 12, 13, 14, 15, 16]
        pi_values = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]

    num_blocks = n // M
    frequencies = [0] * (K + 1)

    # Dla każdego bloku znajdź najdłuższy run jedynek
    for i in range(num_blocks):
        block = bits[i * M:(i + 1) * M]
        max_run = 0
        current_run = 0

        for bit in block:
            if bit == 1:
                current_run += 1
                max_run = max(max_run, current_run)
            else:
                current_run = 0

        # Przypisz do kategorii
        if max_run <= v_values[0]:
            frequencies[0] += 1
        elif max_run >= v_values[-1]:
            frequencies[K] += 1
        else:
            for j in range(len(v_values) - 1):
                if v_values[j] < max_run <= v_values[j + 1]:
                    frequencies[j + 1] += 1
                    break

    # Chi-square
    chi_square = sum(
        (frequencies[i] - num_blocks * pi_values[i]) ** 2 /
        (num_blocks * pi_values[i])
        for i in range(K + 1)
    )

    # P-value
    p_value = erfc(math.sqrt(chi_square / 2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': round(score, 4),
        'statistics': {
            'p_value': round(p_value, 6),
            'chi_square': round(chi_square, 6),
            'frequencies': frequencies,
            'num_blocks': num_blocks,
            'threshold': 0.01
        }
    }
```

#### Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_longest_run",
    "samples_count": 128000
  }'
```

#### Interpretacja wyników
- **p-value > 0.1**: Rozkład długości runs jest prawidłowy
- **frequencies**: Pokazuje rozkład najdłuższych runs w blokach
- **chi_square**: Im mniejsza wartość, tym lepsze dopasowanie do oczekiwanego rozkładu

---

### 7. NIST Cumulative Sums Test

#### Opis
Test sum kumulatywnych (CUSUM) wykrywa odchylenia od losowości poprzez śledzenie maksymalnego odchylenia skumulowanej sumy od zera.

#### Jak działa
1. Konwertuje bity na +1/-1
2. Oblicza sumę kumulatywną w każdym punkcie
3. Znajduje maksymalne odchylenie (forward mode)
4. Oblicza p-value na podstawie tego odchylenia

#### Wzory matematyczne
```
Dla każdego biti ∈ {0,1}:
Xi = 2×biti - 1  (konwersja do ±1)

Suma kumulatywna:
Sk = Σ(i=1 do k) Xi

Maksymalne odchylenie:
z = max|Sk|

P-value: złożony wzór z funkcją erfc
```

#### Interpretacja geometryczna
Test obserwuje "random walk" - jeśli sekwencja jest losowa, suma kumulatywna powinna oscylować wokół zera bez zbyt dużych odchyleń.

#### Implementacja
```python
def _nist_cumulative_sums_test(self, bits: List[int]) -> Dict[str, Any]:
    import math
    from math import erfc

    n = len(bits)

    # Forward cumulative sum
    s = [0]
    for bit in bits:
        s.append(s[-1] + (1 if bit == 1 else -1))

    z_forward = max(abs(val) for val in s)

    # Test statistic (uproszczony wzór)
    sum_val = 0.0
    for k in range(int((-n / z_forward + 1) / 4),
                   int((n / z_forward - 1) / 4) + 1):
        term1 = erfc((4 * k + 1) * z_forward / math.sqrt(n) / math.sqrt(2))
        term2 = erfc((4 * k - 1) * z_forward / math.sqrt(n) / math.sqrt(2))
        sum_val += term1 - term2

    p_value = 1 - sum_val

    passed = p_value >= 0.01
    score = min(1.0, max(0.0, p_value))

    return {
        'passed': passed,
        'score': round(score, 4),
        'statistics': {
            'p_value': round(p_value, 6),
            'max_excursion': z_forward,
            'threshold': 0.01
        }
    }
```

#### Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_cumulative_sums",
    "samples_count": 100000
  }'
```

#### Interpretacja wyników
- **max_excursion**: Maksymalne odchylenie od zera
  - Im mniejsze, tym lepiej zbalansowana sekwencja
  - Duże wartości wskazują na bias
- **p-value > 0.5**: Bardzo dobra równowaga
- **p-value < 0.01**: Wykryto systematyczny bias

#### Wizualizacja
```
Dobra sekwencja (losowa):
  Suma  |     /\    /\
        |    /  \  /  \
      0 |___/____\/____\___
        |

Zła sekwencja (bias):
  Suma  |          /
        |         /
      0 |________/
        |
```

---

### 8. NIST Approximate Entropy Test

#### Opis
Test entropii aproksymacyjnej mierzy częstotliwość wszystkich możliwych nakładających się wzorców (patternów) długości m w sekwencji. Wykrywa, czy sekwencja jest zbyt regularna lub przewidywalna.

#### Jak działa
1. Wybiera długość wzorca m (domyślnie 10, dostosowywane do długości sekwencji)
2. Liczy wszystkie możliwe wzorce długości m
3. Oblicza entropię dla wzorców długości m i m+1
4. Porównuje te entropie - dla losowej sekwencji powinny być podobne

#### Wzory matematyczne
```
Dla wzorca długości m:
Φ(m) = Σ (pi × log(pi))

gdzie pi = częstość wzorca i

Approximate Entropy:
ApEn(m) = Φ(m) - Φ(m+1)

Statystyka Chi-kwadrat:
χ² = 2n(log(2) - ApEn)

P-value:
p = erfc(√(χ²/2))
```

#### Parametry adaptacyjne
```python
# Dopasowanie m do rozmiaru sekwencji
m = min(m_requested, int(log2(n)) - 5)
if m < 2:
    m = 2
```

#### Implementacja
```python
def _nist_approximate_entropy_test(self, bits: List[int], m: int = 10):
    import math
    from math import erfc

    n = len(bits)

    if n < 100:
        return {'passed': False, 'score': 0.0,
                'statistics': {'error': 'Minimum 100 bits required'}}

    # Dopasuj m jeśli n jest za małe
    m = min(m, int(math.log2(n)) - 5)
    if m < 2:
        m = 2

    def compute_phi(m_local):
        patterns = {}
        for i in range(n):
            pattern = tuple(bits[(i + j) % n] for j in range(m_local))
            patterns[pattern] = patterns.get(pattern, 0) + 1

        phi = sum((count / n) * math.log((count / n))
                  for count in patterns.values())
        return phi

    phi_m = compute_phi(m)
    phi_m_plus_1 = compute_phi(m + 1)

    apen = phi_m - phi_m_plus_1

    # Chi-square approximation
    chi_square = 2 * n * (math.log(2) - apen)

    # P-value
    p_value = erfc(math.sqrt(chi_square / 2))

    passed = p_value >= 0.01
    score = min(1.0, p_value)

    return {
        'passed': passed,
        'score': round(score, 4),
        'statistics': {
            'p_value': round(p_value, 6),
            'approximate_entropy': round(apen, 6),
            'chi_square': round(chi_square, 6),
            'm': m,
            'threshold': 0.01
        }
    }
```

#### Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_approximate_entropy",
    "samples_count": 100000
  }'
```

#### Interpretacja wyników
- **approximate_entropy**: Wartość ApEn
  - Im bliżej 0, tym bardziej losowa sekwencja
  - Duże wartości sugerują regularność
- **m**: Długość wzorca użyta w teście
  - Większe m = dokładniejszy test (wymaga więcej danych)
- **p-value > 0.1**: Brak wykrywalnych wzorców, dobra losowość
- **p-value < 0.01**: Wykryto regularność we wzorcach

#### Co wykrywa
- Powtarzające się sekwencje
- Cykliczne wzorce
- Zbyt przewidywalną strukturę
- Brak entropii w danych

---

### 9. NIST Binary Matrix Rank Test

#### Opis
Test analizuje rangę macierzy binarnych utworzonych z sekwencji bitowej. Sprawdza czy ranga macierzy odpowiada oczekiwanej dla losowych danych. Niska ranga wskazuje na zależności liniowe między bitami.

#### Jak działa
1. Dzieli sekwencję na macierze 32×32 bity
2. Oblicza rangę każdej macierzy metodą eliminacji Gaussa
3. Klasyfikuje macierze według rangi (32, 31, lub mniej)
4. Porównuje rozkład z oczekiwanym za pomocą Chi-kwadrat

#### Wzory matematyczne
```
Dla macierzy M×M binarnej:
Ranga = liczba liniowo niezależnych wierszy/kolumn

Prawdopodobieństwa dla M=32:
P(rank=32) = 0.2888
P(rank=31) = 0.5776
P(rank≤30) = 0.1336

Chi-square: χ² = Σ (Oi - Ei)² / Ei
```

#### Parametry
- **Rozmiar macierzy**: 32×32
- **Minimum bitów**: 1024
- **Kryterium**: p-value ≥ 0.01

#### Implementacja
```python
def _nist_matrix_rank_test(self, bits: List[int]):
    M = Q = 32
    num_matrices = n // (M * Q)

    rank_counts = {M: 0, M-1: 0, 'other': 0}

    for każdej macierzy:
        rank = compute_rank(matrix)  # Eliminacja Gaussa
        klasyfikuj według rangi

    chi_square = suma[(Oi - Ei)² / Ei]
    p_value = erfc(√(chi²/2))
```

#### Przykład użycia API
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "nist_matrix_rank",
    "samples_count": 100000
  }'
```

---

### 10. NIST Discrete Fourier Transform (Spectral) Test

#### Opis
Test DFT wykrywa okresowe wzorce w sekwencji bitowej używając transformaty Fouriera. Losowa sekwencja nie powinna mieć wyraźnych pików w spektrum częstotliwości.

#### Jak działa
1. Konwertuje bity do wartości +1/-1
2. Oblicza dyskretną transformatę Fouriera (DFT)
3. Liczy piki przekraczające próg
4. Porównuje z oczekiwaną liczbą pików

#### Wzory matematyczne
```
DFT: S(k) = Σ X(n)×e^(-2πikn/N)

Próg: T = √(ln(1/0.05)×n)

Oczekiwana liczba pików poniżej T:
N0 = 0.95×n/2

Statystyka: d = (N1 - N0) / √(n×0.95×0.05/4)
```

#### Implementacja
```python
def _nist_dft_test(self, bits: List[int]):
    X = [2*bit - 1 for bit in bits]  # Konwersja do ±1

    S = dft(X)  # Oblicz DFT

    T = √(ln(1/0.05)×n)
    N1 = zlicz(s < T for s in S)

    d = (N1 - N0) / √(n×0.95×0.05/4)
    p_value = erfc(|d|/√2)
```

#### Przykład użycia
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -d '{"test_name": "nist_dft", "samples_count": 10000}'
```

#### Interpretacja
- **Wykrywa**: Okresowe wzorce, cykliczność
- **p-value > 0.5**: Brak wykrywalnych okresowości
- **peaks_below_threshold ≈ expected**: Prawidłowe spektrum

---

### 11. NIST Non-Overlapping Template Matching Test

#### Opis
Test szuka określonego wzorca (template) w sekwencji, gdzie wystąpienia nie nakładają się na siebie. Sprawdza czy liczba wystąpień jest zgodna z oczekiwaniami dla losowej sekwencji.

#### Jak działa
1. Wybiera m-bitowy wzorzec (domyślnie 000000001)
2. Dzieli sekwencję na bloki wielkości M
3. W każdym bloku zlicza wystąpienia wzorca (non-overlapping)
4. Porównuje rozkład z oczekiwanym

#### Wzory
```
Oczekiwana liczba wystąpień w bloku:
μ = (M - m + 1) / 2^m

Wariancja:
σ² = M × [(1/2^m) - (2m-1)/2^(2m)]

Chi-square: χ² = Σ(Wi - μ)² / σ²
```

#### Parametry
- **Domyślny template**: [0,0,0,0,0,0,0,0,1]
- **Rozmiar bloku**: M = 1000
- **Minimum bitów**: 1000

#### Implementacja
```python
def _nist_non_overlapping_template_test(self, bits, template=None):
    if template is None:
        template = [0,0,0,0,0,0,0,0,1]

    for każdego bloku:
        count = 0
        i = 0
        while i <= len(block) - m:
            if block[i:i+m] == template:
                count += 1
                i += m  # Przeskocz (non-overlapping)
            else:
                i += 1

    chi_square = Σ(count - μ)² / σ²
```

---

### 12. NIST Overlapping Template Matching Test

#### Opis
Podobny do poprzedniego, ale wystąpienia wzorca mogą się nakładać. Używa specyficznego wzorca 111111111 (9 jedynek).

#### Jak działa
1. Używa stałego wzorca: 9 jedynek
2. W każdym bloku zlicza nakładające się wystąpienia
3. Kategoryzuje bloki według liczby wystąpień (0,1,2,3,4,5+)
4. Test Chi-kwadrat na rozkładzie

#### Wzory
```
λ = (M - m + 1) / 2^m
η = λ / 2

Prawdopodobieństwa teoretyczne:
π = [0.364091, 0.185659, 0.139381,
     0.100571, 0.0704323, 0.139865]
```

#### Parametry
- **Wzorzec**: [1,1,1,1,1,1,1,1,1]
- **Rozmiar bloku**: M = 1032
- **Kategorie**: 0, 1, 2, 3, 4, ≥5

---

### 13. NIST Maurer's Universal Statistical Test

#### Opis
Test uniwersalny Maurera mierzy kompresowność sekwencji. Losowa sekwencja powinna być trudna do skompresowania. Test mierzy dystans między powtórzeniami L-bitowych wzorców.

#### Jak działa
1. Dzieli sekwencję na L-bitowe bloki
2. Faza inicjalizacji: Q pierwszych bloków buduje tabelę
3. Faza testowa: K kolejnych bloków testuje dystanse
4. Oblicza średni logarytm dystansu

#### Wzory matematyczne
```
fn = (1/K) × Σ log2(i - T[blocki])

gdzie T[block] = ostatnia pozycja bloku

Parametry adaptacyjne:
L=6, Q=640   dla n < 387840
L=7, Q=1280  dla n < 904960
L=8, Q=2560  dla n ≥ 904960
```

#### Implementacja
```python
def _nist_universal_test(self, bits):
    # Wybierz parametry L, Q

    T = {}  # Tabela pozycji bloków

    # Faza inicjalizacji
    for i in range(1, Q+1):
        block = tuple(bits[(i-1)*L:i*L])
        T[block] = i

    # Faza testowa
    sum_log = 0
    for i in range(Q+1, Q+K+1):
        block = tuple(bits[(i-1)*L:i*L])
        distance = i - T[block]
        sum_log += log2(distance)
        T[block] = i

    fn = sum_log / K
```

#### Interpretacja
- **fn ≈ expected**: Dobra kompresowność (wysoka entropia)
- **fn znacznie różne**: Sekwencja zbyt regularna lub zbyt chaotyczna

---

### 14. NIST Linear Complexity Test

#### Opis
Test mierzy długość najkrótszego rejestru przesuwnego ze sprzężeniem zwrotnym liniowym (LFSR), który może wygenerować daną sekwencję. Używa algorytmu Berlekamp-Massey.

#### Jak działa
1. Dzieli sekwencję na bloki długości M
2. Dla każdego bloku oblicza złożoność liniową (algorytm Berlekamp-Massey)
3. Kategoryzuje odstępstwa od oczekiwanej złożoności
4. Test Chi-kwadrat na rozkładzie

#### Wzory matematyczne
```
Oczekiwana złożoność:
μ = M/2 + (9+(-1)^(M+1))/36 - (M/3+2/9)/2^M

Kategorie Ti:
[-∞,-2.5], (-2.5,-1.5], ..., (2.5,+∞]

Prawdopodobieństwa:
π = [0.010417, 0.03125, 0.125, 0.5,
     0.25, 0.0625, 0.020833]
```

#### Algorytm Berlekamp-Massey
```python
def berlekamp_massey(bits):
    c = [0] * n  # Wielomian połączenia
    b = [0] * n  # Wielomian pomocniczy
    L = 0        # Złożoność liniowa

    for każdego bitu:
        oblicz dyskrepancję d
        if d == 1:
            zaktualizuj c
            if warunek:
                zaktualizuj L

    return L
```

#### Parametry
- **M**: 500 (domyślnie)
- **Minimum bloków**: 200 (minimum 100000 bitów)

---

### 15. NIST Serial Test

#### Opis
Test sprawdza częstość wszystkich możliwych nakładających się m-bitowych wzorców. Jest rozszerzeniem testu Approximate Entropy, oblicza dwie statystyki testowe.

#### Jak działa
1. Oblicza funkcję ψ² dla m, m-1 i m-2
2. Oblicza delta1 i delta2
3. Dla każdej delty oblicza p-value
4. Test przechodzi gdy obie p-values ≥ 0.01

#### Wzory matematyczne
```
ψ²(m) = (2^m/n)×Σvi² - n

gdzie vi = liczba wystąpień wzorca i

Δ1 = ψ²(m) - ψ²(m-1)
Δ2 = ψ²(m) - 2ψ²(m-1) + ψ²(m-2)

p-value1 = erfc(√(|Δ1|/2))
p-value2 = erfc(√(|Δ2|/2))
```

#### Implementacja
```python
def _nist_serial_test(self, bits, m=16):
    m = min(m, int(log2(n)) - 2)  # Dostosuj m

    psi2_m = psi_sq(m, bits)
    psi2_m1 = psi_sq(m-1, bits)
    psi2_m2 = psi_sq(m-2, bits)

    delta1 = psi2_m - psi2_m1
    delta2 = psi2_m - 2*psi2_m1 + psi2_m2

    p_value1 = erfc(√(|delta1|/2))
    p_value2 = erfc(√(|delta2|/2))

    passed = (p_value1 >= 0.01) and (p_value2 >= 0.01)
```

---

### 16. NIST Random Excursions Test

#### Opis
Test analizuje liczbę cykli w "random walk" - spacerze losowym utworzonym z sekwencji. Sprawdza czy liczba wizyt w każdym stanie random walk jest prawidłowa.

#### Jak działa
1. Konwertuje bity do +1/-1
2. Oblicza sumy cząstkowe (random walk)
3. Zlicza cykle (powroty do zera)
4. Dla każdego stanu (-4 do +4) zlicza wizyty
5. Porównuje z oczekiwanymi wartościami

#### Wzory matematyczne
```
Xi = 2×biti - 1  (konwersja do ±1)

Suma cząstkowa:
Sk = Σ(i=1 do k) Xi

Cykl: powrót Sk do 0

Stany testowane: ±1, ±2, ±3, ±4

Dla każdego stanu x:
χ²(x) = (wizyt - oczekiwane)² / oczekiwane
```

#### Wymagania
- **Minimum cykli**: 500
- Jeśli < 500 cykli, test nie może być wykonany

#### Interpretacja geometryczna
```
Random walk:
  +4 |      *
  +2 |   *     *
   0 |--*---*----*--  (cykle)
  -2 |     *
  -4 |
```

---

### 17. NIST Random Excursions Variant Test

#### Opis
Wariant testu Random Excursions, który testuje więcej stanów (±1 do ±9) i używa innej statystyki testowej. Każdy stan ma osobną p-value.

#### Jak działa
1. Podobnie jak Random Excursions: tworzy random walk
2. Testuje stany: ±1, ±2, ..., ±9 (18 stanów)
3. Dla każdego stanu oblicza osobną p-value
4. Test przechodzi gdy wszystkie p-values ≥ 0.01

#### Wzory matematyczne
```
Dla stanu x:
statystyka = |wizyt - cykle| / √(2×cykle×(4|x|-2))

p-value(x) = erfc(statystyka/√2)

Test passed = wszystkie p-values ≥ 0.01
```

#### Różnice od Random Excursions
- Więcej stanów (18 vs 8)
- Inna statystyka testowa
- Każdy stan testowany oddzielnie
- Bardziej rygorystyczny (wszystkie p-values muszą przejść)

#### Implementacja
```python
def _nist_random_excursions_variant_test(self, bits):
    # Oblicz random walk i cykle

    states = [-9,-8,...,-1,1,2,...,9]

    for każdego stanu x:
        visits = zlicz(S == x)

        stat = |visits - cycles| / √(2×cycles×(4|x|-2))
        p_value = erfc(stat/√2)

        zapisz p_value

    passed = all(p >= 0.01 for p in p_values)
```

---

## Porównanie testów

| Test | Typ danych | Min. próbek | Co wykrywa | Złożoność |
|------|-----------|-------------|------------|-----------|
| Frequency | Floats | 100 | Nierównomierny rozkład | Niska |
| Uniformity | Floats | 100 | Nieprawidłowa średnia/wariancja | Niska |
| **NIST Suite (15 testów)** |
| 1. Monobit | Bits | 100 | Niezbalansowanie 0/1 | Niska |
| 2. Block Frequency | Bits | 128 | Lokalne niezbalansowanie | Średnia |
| 3. Runs | Bits | 100 | Nieprawidłowe przejścia | Średnia |
| 4. Longest Run | Bits | 128 | Zbyt długie/krótkie serie | Średnia |
| 5. Matrix Rank | Bits | 1024 | Zależności liniowe | Wysoka |
| 6. DFT (Spectral) | Bits | 100 | Okresowe wzorce | Wysoka |
| 7. Non-Overlap Template | Bits | 1000 | Specyficzne wzorce | Średnia |
| 8. Overlap Template | Bits | 1032 | Seryjne wzorce (111...1) | Średnia |
| 9. Universal | Bits | 387840 | Kompresowność | Wysoka |
| 10. Linear Complexity | Bits | 100000 | Złożoność LFSR | Bardzo wysoka |
| 11. Serial | Bits | 100 | Częstość m-bitowych wzorców | Wysoka |
| 12. Approximate Entropy | Bits | 100 | Regularność wzorców | Wysoka |
| 13. Cumulative Sums | Bits | 100 | Systematyczny bias | Wysoka |
| 14. Random Excursions | Bits | ~10000* | Właściwości random walk | Bardzo wysoka |
| 15. Random Excursions Var | Bits | ~10000* | Random walk (więcej stanów) | Bardzo wysoka |

\* Wymaga min. 500 cykli (powrotów do zera), co zazwyczaj wymaga ~10000+ bitów

## Rekomendacje użycia

### Dla szybkiego testowania (< 10,000 próbek)
1. NIST Monobit
2. NIST Block Frequency
3. NIST Runs
4. Frequency Test

### Dla dokładnego testowania (100,000 - 1,000,000 próbek)
1. **Podstawowe (zawsze)**:
   - NIST Monobit
   - NIST Block Frequency
   - NIST Runs
   - NIST Longest Run

2. **Zaawansowane**:
   - NIST Matrix Rank
   - NIST DFT
   - NIST Serial
   - NIST Cumulative Sums
   - NIST Approximate Entropy

3. **Specjalistyczne**:
   - NIST Linear Complexity
   - NIST Random Excursions
   - NIST Random Excursions Variant

### Dla generatorów kryptograficznych (> 1,000,000 próbek)
**Priorytet 1 (krytyczne)**:
1. NIST Linear Complexity - wykrywa prostotę algorytmu
2. NIST Approximate Entropy - mierzy nieprzewidywalność
3. NIST Serial - sprawdza zależności między wzorcami
4. NIST Universal - testuje kompresowność

**Priorytet 2 (ważne)**:
5. NIST DFT - wykrywa ukryte periodiczhości
6. NIST Matrix Rank - sprawdza niezależność liniową
7. NIST Random Excursions - analizuje random walk
8. NIST Cumulative Sums - wykrywa bias

**Priorytet 3 (uzupełniające)**:
9-15. Pozostałe testy NIST

### Dla szybkich generatorów pseudolosowych (gaming, symulacje)
- NIST Monobit
- NIST Runs
- Frequency Test
- Uniformity Test
- NIST DFT

### Dla generatorów sprzętowych (TRNG)
Wszystkie 15 testów NIST + Frequency + Uniformity

## Interpretacja p-value

| p-value | Interpretacja |
|---------|---------------|
| > 0.5 | Bardzo dobry wynik |
| 0.1 - 0.5 | Dobry wynik |
| 0.01 - 0.1 | Akceptowalny |
| < 0.01 | **Test niezaliczony** |

## Przykład pełnego testu generatora

### Test podstawowy (szybki - ~5 minut)
```bash
# 1. Test równowagi
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -d '{"test_name": "nist_monobit", "samples_count": 100000}'

# 2. Test bloków
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -d '{"test_name": "nist_block_frequency", "samples_count": 100000}'

# 3. Test przebiegów
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -d '{"test_name": "nist_runs", "samples_count": 100000}'

# 4. Test serii
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -d '{"test_name": "nist_longest_run", "samples_count": 100000}'
```

### Test rozszerzony (pełny NIST - ~30 minut)
```bash
# Uruchom wszystkie 15 testów NIST
for test in nist_monobit nist_block_frequency nist_runs nist_longest_run \
            nist_matrix_rank nist_dft nist_serial nist_approximate_entropy \
            nist_cumulative_sums nist_non_overlapping_template \
            nist_overlapping_template nist_universal nist_linear_complexity \
            nist_random_excursions nist_random_excursions_variant; do
  curl -X POST http://localhost:8000/api/rngs/1/run_test \
    -H "Content-Type: application/json" \
    -d "{\"test_name\": \"$test\", \"samples_count\": 1000000}"
  sleep 2
done

# Pobierz wszystkie wyniki
curl http://localhost:8000/api/rngs/1/test_results
```

### Test kryptograficzny (maksymalna dokładność)
```bash
# Kluczowe testy dla generatorów kryptograficznych
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -d '{"test_name": "nist_linear_complexity", "samples_count": 5000000}'

curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -d '{"test_name": "nist_approximate_entropy", "samples_count": 5000000}'

curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -d '{"test_name": "nist_serial", "samples_count": 5000000}'

curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -d '{"test_name": "nist_universal", "samples_count": 5000000}'
```

## Bibliografia

- NIST Special Publication 800-22: A Statistical Test Suite for Random and Pseudorandom Number Generators for Cryptographic Applications
- https://csrc.nist.gov/publications/detail/sp/800-22/rev-1a/final

---

*Dokumentacja wygenerowana dla projektu IO_RNG Backend*
