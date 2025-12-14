# AWCG (Add-With-Carry Generator)

## Skrót

AWCG to modyfikacja LCG dodająca bit przeniesienia (*carry*), co poprawia statystyczne własności. Wzór: \( x_{n+1} = (a x_n + c + \text{carry}_n) \bmod m \).

## Wersja długa

### Wyjaśnienie matematyczne
- Stan generatora: wartość \(x_n\) oraz bit przeniesienia \(\text{carry}_n\).
- Aktualizacja: \( s = a x_n + c + \text{carry}_n \)
- Nowe \(x_{n+1} = s \bmod m\)
- Nowe \(\text{carry}_{n+1} = \lfloor s / m \rfloor\) (bit przeniesienia)
- Parametry testowe: \(a=1103515245\), \(c=12345\), \(m=2^{32}\)
- Bit carry wprowadza zależność międzyokresową, wydłużając okres i poprawiając jakość statystyczną względem prostego LCG.

### Kluczowy fragment kodu
```python
# Krok AWCG
s = a * x + c + carry
x = s % m
carry = s // m

# Ekstrakcja bitów
output_bits = extract_bits(x, bits_per_value, msb_first)
```

### Zastosowania
- **Symulacje**: Monte Carlo, modelowanie stochastyczne o wyższych wymaganiach niż LCG.
- **Edukacja**: demonstracja wpływu mechanizmu carry na jakość sekwencji.
- **Badania**: analiza generatorów z pamięcią międzystanową.
- Nie zalecany do kryptografii (przewidywalny przy znajomości parametrów).

### Kontekst i ciekawostki
- Wariant rodziny generatorów *with-carry* (Marsaglia i Zaman, lata 90.).
- Mechanizm carry wprowadza nieliniowość, co znacząco poprawia wyniki w testach statystycznych względem LCG.
- Multiply-With-Carry (MWC) i Complementary-MWC (CMWC) to pokrewne konstrukcje oferujące jeszcze lepszą jakość.
- AWCG z dobrymi parametrami zdaje podstawowe testy statystyczne, ale jest wolniejszy od nowoczesnych generatorów (PCG, xoshiro).
- Historycznie ważny jako most między prostymi LCG a zaawansowanymi generatorami lat 90./2000.

### Krótki przykład obliczeniowy
Dla \(a=5, c=3, m=16\), \(x_0=1, \text{carry}_0=0\):
- \(s = 5 \cdot 1 + 3 + 0 = 8\)
- \(x_1 = 8 \bmod 16 = 8\), \(\text{carry}_1 = \lfloor 8/16 \rfloor = 0\)
- \(s = 5 \cdot 8 + 3 + 0 = 43\)
- \(x_2 = 43 \bmod 16 = 11\), \(\text{carry}_2 = \lfloor 43/16 \rfloor = 2\)
- \(s = 5 \cdot 11 + 3 + 2 = 60\)
- \(x_3 = 60 \bmod 16 = 12\), \(\text{carry}_3 = \lfloor 60/16 \rfloor = 3\)
