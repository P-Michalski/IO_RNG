SplitMix64 is a fast, modern 64-bit generator using a sequence of simple mixing operations to transform a linearly growing state into high-quality pseudorandom output. Designed by Sebastiano Vigna around 2015, SplitMix64 has found wide application mainly as an **initialization generator** (_splitter_) for more advanced generators requiring multiple initial values, such as xoshiro and xoroshiro.

### Mathematical Explanation

The SplitMix64 generator consists of two simple components: simple state update and an advanced mixing function.

#### State Update

The generator state is a single 64-bit integer $x$, updated by adding a constant:

$$x_{n+1} = x_n + \gamma$$

where $\gamma = \text{0x9E3779B97F4A7C15}$ is a carefully chosen constant representing the **golden angle in 64-bit representation**.

**Why this constant?**

The constant $\gamma$ comes from the **golden ratio** $\phi = \frac{1 + \sqrt{5}}{2} \approx 1.618033988749$:

$$\gamma = \lfloor 2^{64} / \phi \rfloor = 11400714819323198485_{10} = \text{0x9E3779B97F4A7C15}_{16}$$

The golden angle property ensures that consecutive values $x_n$ are "maximally spread" in 64-bit space.

#### Mixing Function

SplitMix64's key innovation is the mixing function transforming linearly growing state into pseudorandom output. It is an adaptation of the **MurmurHash3 finalizer**:

```
z ← x
z ← (z ⊕ (z >> 30)) × 0xBF58476D1CE4E5B9
z ← (z ⊕ (z >> 27)) × 0x94D049BB133111EB
output ← z ⊕ (z >> 31)
```

**Step analysis:**

1. Xorshift + multiplication (first diffusion layer)
2. Xorshift + multiplication (second diffusion layer)
3. Final xorshift (uniform distribution)

### Key Code Fragment

```python
def splitmix64_bit_stream(seed, n_bits, bits_per_value=64):
    """
    Generates bit stream using SplitMix64.
    """
    GAMMA = 0x9E3779B97F4A7C15
    MASK64 = (1 << 64) - 1

    state = seed & MASK64
    output = []

    while len(output) < n_bits:
        # State update
        state = (state + GAMMA) & MASK64

        # Mixing function
        z = state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        output_val = (z ^ (z >> 31)) & MASK64

        # Bit extraction
        bits = extract_bits(output_val, bits_per_value, msb_first=True)
        output.extend(bits[:n_bits - len(output)])

    return output
```

### Applications

**Practical applications:**

- **Generator initialization** – main use: creating states for xoshiro, xoroshiro, xorshift
- **Hash functions** – as component of hash functions
- **Fast generation** – applications requiring simple, fast generator
- **Seeding** – converting single seed to multiple independent values

**Why popular as splitter?**

- **Simplicity**: Only a few lines of code
- **Speed**: One of the fastest mixing functions (~5-10 CPU cycles per 64 bits)
- **Golden angle**: Ensures good independence of consecutive values

**Limitations:**

- **Not for long sequences**: Doesn't pass all PractRand tests for very long streams (> 256 GB)
- **Not for cryptography**: State easy to reconstruct
- **Medium quality**: Good as splitter, worse than xoshiro/PCG as standalone generator

### Statistical Quality

#### Statistical tests:

- **TestU01 SmallCrush**: Passed
- **TestU01 Crush**: Partial failures
- **TestU01 BigCrush**: Failures in several tests
- **PractRand**: Passes up to ~256 GB, then anomalies
- **As splitter**: Excellent – generated states pass all tests

### Historical Context and Trivia

**History:**

- Designed by **Sebastiano Vigna** (Università degli Studi di Milano) around 2015
- Inspiration: Java 8: SplittableRandom (Guy Steele, Doug Lea)
- Published as part of research on xoshiro/xoroshiro generators

**Trivia:**

- Golden angle ($\gamma$) ensures **uniform Weyl distribution** – sequence $x \bmod 1$ is uniformly distributed in $[0,1]$
- SplitMix64 is used internally in xoshiro implementations in Rust (rand crate)
- Mixing function is so good it's also used in non-cryptographic hash functions

### Computational Complexity

- **Generation step**: $O(1)$ – 1 addition + 3 xor + 3 shifts + 2 multiplications (~5-10 CPU cycles)
- **Memory**: $O(1)$ – 8 bytes (64-bit state)
- **Initialization**: $O(1)$ – setting seed

### Computational Example

For $x_0 = 0$, $\gamma = \text{0x9E3779B97F4A7C15}$:

```
x_1 = 0 + 0x9E3779B97F4A7C15 = 0x9E3779B97F4A7C15
(apply mixing function)
output_1 = ... (64-bit pseudorandom value)

x_2 = 0x9E3779B97F4A7C15 + 0x9E3779B97F4A7C15 = 0x3C6EF372FE94F82A
(apply mixing function)
output_2 = ... (another pseudorandom value)
```

SplitMix64 proves that a simple concept (counter + good mixing function) can yield a useful generator, especially in the role of seed generator for more advanced generators.
