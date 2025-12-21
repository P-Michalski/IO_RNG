LCG (Linear Congruential Generator) is a classical pseudorandom generator based on a simple recurrence relation: $x_{n+1} = (a x_n + c) \bmod m$. It is one of the oldest and most commonly used pseudorandom number generation algorithms due to its simplicity and computational efficiency. Despite its advantages, the generator is susceptible to statistical correlations and very sensitive to the selection of parameters $a$, $c$, and $m$.

### Mathematical Explanation

The LCG generator is based on an iterative linear function with modulo operation:

$$x_{n+1} = (a \cdot x_n + c) \bmod m$$

where:

- $x_n$ – current generator state (integer from range $[0, m-1]$)
- $x_0$ – initial value (seed), determines the entire sequence
- $a$ – multiplier, affects value dispersion
- $c$ – increment, can be 0 for so-called multiplicative generators
- $m$ – modulus, defines maximum period and value range

#### Full Period Conditions

For the generator to achieve maximum period equal to $m$, the following conditions must be met (Hull-Dobell theorem):

1. $\gcd(c, m) = 1$ – $c$ and $m$ are coprime
2. $a - 1$ is divisible by all prime divisors of $m$
3. If $m$ is divisible by 4, then $a - 1$ must also be divisible by 4

For multiplicative generators ($c = 0$), the conditions are more restrictive, and the maximum period is $m/4$ for $m = 2^k$.

#### Bit Extraction

Output bits are most often obtained from the most significant (MSB) bits of value $x_n$, because younger bits exhibit weaker statistical properties:

- For $m = 2^{31}$: typically 31 bits are extracted (excluding sign bit)
- For $m = 2^{32}$: all 32 bits can be extracted
- Implementation: `(x >> (bits_total - bits_needed))` for MSB-first

In practice, implementations allow choosing between MSB-first (most significant bits first) or LSB-first extraction, with the first option being the standard due to better statistical quality of higher bits.

### Popular Parameter Sets

#### 1. GLIBC (31-bit)

- $a = 1103515245$
- $c = 12345$
- $m = 2^{31}$
- Used in C standard library (glibc)
- Good balance between simplicity and quality

#### 2. Numerical Recipes (32-bit)

- $a = 1664525$
- $c = 1013904223$
- $m = 2^{32}$
- Popular in literature, though has some statistical flaws

#### 3. MSVC (Microsoft Visual C++)

- $a = 214013$
- $c = 2531011$
- $m = 2^{32}$
- Used in MSVC compiler

### Key Code Fragment

```python
def lcg_bit_stream(seed, a, c, m, n_bits, bits_per_value=None, msb_first=True):
    """
    Generates bit stream using LCG.

    Args:
        seed: initial value x_0
        a, c, m: LCG parameters
        n_bits: number of bits to generate
        bits_per_value: how many bits to extract from each value
        msb_first: whether to take bits from most significant
    """
    x = seed
    output = []

    while len(output) < n_bits:
        # LCG step - state update
        x = (a * x + c) % m

        # Bit extraction (default MSB-first)
        bits = extract_bits(x, bits_per_value, msb_first)
        output.extend(bits[:n_bits - len(output)])

    return output
```

### Applications

**Practical applications:**

- Educational and didactic materials – excellent PRNG example for learning
- Simple Monte Carlo simulations – when advanced statistical properties are not required
- Test data generation – quick creation of repeatable sequences
- Computer games (older) – generating maps, enemy positions
- Standard libraries of programming languages – e.g., rand() in C

**Limitations:**

- **Cryptography**: Absolutely not recommended for cryptographic applications due to complete predictability – knowing several consecutive values allows parameter recovery and entire sequence prediction
- **Simulations requiring high-quality randomness**: Correlations between values can lead to incorrect results
- **Security applications**: Linear structure enables easy cryptanalytic attacks

### Statistical Quality and Issues

#### Structural flaws:

1. **Linear correlations**: Values $x_n$ and $x_{n+1}$ are correlated
2. **Spectral test**: Points $(x_n, x_{n+1}, ..., x_{n+k})$ lie on hyperplanes in $k$-dimensional space
3. **Weakness of younger bits**: Least significant bits have very short periods (e.g., last bit has period 2)
4. **Predictability**: Completely deterministic – seed determines entire sequence

#### Statistical tests:

- Marsaglia's Spectral Test – reveals lattice structure
- Birthday Spacings Test – detects correlations
- DIEHARD Battery – LCG generators often fail many tests

### Historical Context and Trivia

**History:**

- LCG origins date back to **Derrick Henry Lehmer's** work from 1949, published in an article describing the method for the ENIAC machine
- In the 1950s-70s it was the de facto standard for pseudorandom generators
- First hardware implementations appeared in scientific calculators of the 1960s

**Trivia:**

- The rand() function in many C++ implementations still uses LCG (though newer standards recommend Mersenne Twister)
- The generator was used in IBM System/360 system (1964)
- Donald Knuth devoted an entire chapter to LCG in "The Art of Computer Programming" (Vol. 2)
- Spectral visualization test: when drawing pairs $(x_n, x_{n+1})$, parallel lines are visible instead of uniform point distribution

### Computational Complexity

- **Generation step**: $O(1)$ – one multiplication, one addition, one modulo
- **Memory**: $O(1)$ – only current state $x_n$ stored
- **Initialization**: $O(1)$ – setting seed

Due to extreme simplicity, LCG is one of the fastest generators, making it attractive for applications requiring enormous numbers of pseudorandom values with modest quality requirements.

### Computational Examples

#### Example 1: Small modulus

For $a=5$, $c=3$, $m=16$, $x_0=7$:

- $x_1 = (5 \cdot 7 + 3) \bmod 16 = 38 \bmod 16 = 6$
- $x_2 = (5 \cdot 6 + 3) \bmod 16 = 33 \bmod 16 = 1$
- $x_3 = (5 \cdot 1 + 3) \bmod 16 = 8 \bmod 16 = 8$
- $x_4 = (5 \cdot 8 + 3) \bmod 16 = 43 \bmod 16 = 11$

#### Example 2: MINSTD generator

For $a=16807$, $c=0$, $m=2^{31}-1=2147483647$, $x_0=1$:

- $x_1 = (16807 \cdot 1) \bmod 2147483647 = 16807$
- $x_2 = (16807 \cdot 16807) \bmod 2147483647 = 282475249$
- $x_3 = (16807 \cdot 282475249) \bmod 2147483647 = 1622650073$

This generator has full period $2^{31} - 2$ (all values except 0).

LCG remains useful primarily as a didactic generator and in applications where implementation simplicity and speed are more important than highest statistical quality.
