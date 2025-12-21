Park–Miller, also known as **MINSTD** (Minimal Standard), is a special case of a multiplicative LCG generator without an additive component. Proposed in 1988 as a response to problematic implementations of rand() in standard libraries, it became a reference point for evaluating the quality of simple pseudorandom generators. It uses careful selection of mathematical parameters ensuring maximum period and relatively good statistical properties.

### Mathematical Explanation

The Park-Miller generator is a multiplicative linear congruential generator, meaning it lacks an additive component:

$$x_{n+1} = (a \cdot x_n) \bmod m$$

where:

- $a = 16807 = 7^5$ – multiplier (primitive root modulo $m$)
- $m = 2^{31} - 1 = 2{,}147{,}483{,}647$ – modulus (Mersenne prime)
- $x_0$ – seed, initial value from range $[1, m-1]$

#### Why these specific parameters?

**Multiplier $a = 16807 = 7^5$:**

- Is a **primitive root** modulo $m$ – generates all elements of $\mathbb{Z}_m^*$
- Ensures full period $m-1 = 2{,}147{,}483{,}646$ (all values except 0)
- Power of 7 was chosen after extensive spectral tests

**Modulus $m = 2^{31} - 1$:**

- **Mersenne prime** – has special properties facilitating efficient modulo calculations
- Maximizes period for 31-bit integers
- Enables implementation without overflow on 32-bit architectures

#### Overflow Problem and Schrage's Arithmetic

Naive calculation of $(a \cdot x_n) \bmod m$ can lead to overflow because:

$$16807 \times 2{,}147{,}483{,}646 = 36{,}028{,}797{,}018{,}963{,}968 > 2^{31}$$

**Schrage's method** solves this problem through decomposition:

$$m = a \cdot q + r$$

where:

- $q = \lfloor m / a \rfloor = 127{,}773$
- $r = m \bmod a = 2{,}836$

Schrage's algorithm:

```
hi = x / q
lo = x % q
t = a * lo - r * hi
if t > 0:
    x = t
else:
    x = t + m
```

This ensures all intermediate calculations fit within 32 bits.

### Key Code Fragment

```python
def park_miller_bit_stream(seed, n_bits, bits_per_value=31):
    """
    Generates bit stream using Park-Miller MINSTD.
    """
    A = 16807
    M = 2147483647  # 2^31 - 1
    Q = M // A      # 127773
    R = M % A       # 2836

    x = seed % M
    if x <= 0:
        x = 1

    output = []

    while len(output) < n_bits:
        # Schrage's arithmetic
        hi = x // Q
        lo = x % Q
        t = A * lo - R * hi

        if t > 0:
            x = t
        else:
            x = t + M

        # Bit extraction
        bits = extract_bits(x, bits_per_value, msb_first=True)
        output.extend(bits[:n_bits - len(output)])

    return output
```

### Applications

**Practical applications:**

- **Educational materials** – simple, well-documented generator for learning
- **Scientific research** – reference point for quality comparisons
- **Statistical simulations** – when moderate quality requirements suffice
- **Reproduction of older research** – compatibility with publications from the 80s-90s
- **Embedded systems** – small memory footprint (4 bytes)

**Limitations:**

- **Cryptography**: Absolutely not recommended – predictable, easy to break
- **Demanding simulations**: Multidimensional correlations, failures in advanced tests
- **Modern applications**: PCG32, xoshiro offer better quality with similar speed

### Statistical Quality

#### Statistical tests:

- **DIEHARD**: Passes most tests (better than weak LCG)
- **TestU01 SmallCrush**: Passed
- **TestU01 Crush**: Partial failures
- **TestU01 BigCrush**: Failures in several tests
- **Spectral test**: Rank 3-4 (moderate for 31-bit generator)

### Historical Context and Trivia

**History:**

- Proposed by **Stephen K. Park** and **Keith W. Miller** in 1988 in the article "Random Number Generators: Good Ones Are Hard To Find"
- Response to proliferation of weak generators in standard libraries
- Title "Minimal Standard" aimed to raise the bar for library implementations

**Evolution:**

- **1988**: Original MINSTD ($a=16807$)
- **1993**: MINSTD Revised ($a=48271$) after additional tests
- **Currently**: Primarily historical and educational significance

**Trivia:**

- Park-Miller article was cited over 3000 times
- Multiplier $16807 = 7^5$ was chosen after testing hundreds of candidates
- Number $2^{31}-1$ is the 8th Mersenne prime
- Generator was used in MATLAB until version R2007b

### Computational Complexity

- **Generation step**: $O(1)$ – one multiplication, division, condition check
- **Memory**: $O(1)$ – 4 bytes (state $x_n$)
- **Initialization**: $O(1)$ – setting seed

### Computational Examples

#### Example 1: Basic sequence

For $x_0 = 1$:

- $x_1 = (16807 \cdot 1) \bmod (2^{31}-1) = 16{,}807$
- $x_2 = (16807 \cdot 16807) \bmod (2^{31}-1) = 282{,}475{,}249$
- $x_3 = (16807 \cdot 282475249) \bmod (2^{31}-1) = 1{,}622{,}650{,}073$
- $x_4 = (16807 \cdot 1622650073) \bmod (2^{31}-1) = 984{,}943{,}658$

Park-Miller remains an important reference point in the history of pseudorandom generators – representing the "minimally acceptable standard" from the late 1980s, now replaced by better algorithms (PCG, xoshiro), but still useful educationally and for replicating historical research.
