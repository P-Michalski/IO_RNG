AWCG (Add-With-Carry Generator) is an extended version of the classical LCG generator that introduces an additional carry mechanism (_carry bit_). This simple addition significantly improves the generator's statistical properties, extends the period, and reduces correlations characteristic of simple LCG. AWCG represents an important step in the evolution of pseudorandom generators, combining implementation simplicity with better statistical quality.

### Mathematical Explanation

The AWCG generator extends the classical LCG with an additional state bit — carry (_carry_), which stores information about "overflow" from the previous iteration.

#### Basic Formula

The generator state consists of two components:

- $x_n$ – main state value (integer from range $[0, m-1]$)
- $\text{carry}_n$ – carry bit (usually 0 or 1, but can be larger)

State update proceeds as follows:

$$s = a \cdot x_n + c + \text{carry}_n$$

$$x_{n+1} = s \bmod m$$

$$\text{carry}_{n+1} = \lfloor s / m \rfloor$$

where:

- $a$ – multiplier
- $c$ – increment
- $m$ – modulus, defines the value range
- $s$ – intermediate value before applying modulo

#### Carry Mechanism

The key difference from LCG is that information about "overflow" (the integer part of $s/m$) is not lost but is carried over to the next iteration. This introduces a dependency between consecutive steps that goes beyond the simple first-order Markov scheme.

**Effects of the carry mechanism:**

- **Extended period**: Carry can significantly extend the generator's maximum period compared to pure LCG
- **Reduced correlations**: Nonlinear dependency between states reduces typical LCG correlations
- **Better distribution**: Values are more evenly distributed in multidimensional space

#### Variant with State Array

In the full AWCG implementation, a state array is often used instead of a single value. A popular variant uses two lag parameters (_lags_):

$$x_n = (x_{n-r} + x_{n-s} + \text{carry}_{n-1}) \bmod m$$

where $r > s > 0$ (typically $r=24$, $s=10$). This version is also called a **lagged Fibonacci generator with carry**.

#### Test Parameters

Standard parameters used in tests are an adaptation of GLIBC parameters:

- $a = 1103515245$
- $c = 12345$
- $m = 2^{32}$
- Seed: any initial value $x_0$
- Initial carry: $\text{carry}_0 = 0$

#### Bit Extraction

Similar to LCG, output bits are most often taken from the most significant (MSB) bits of value $x_n$:

- For $m = 2^{32}$: typically 32 bits are extracted
- Implementation: `(x >> (bits_total - bits_needed))` for MSB-first
- LSB-first is also available, though rarely used

### Popular Parameter Configurations

#### 1. AWCG-GLIBC (32-bit)

- $a = 1103515245$
- $c = 12345$
- $m = 2^{32}$
- Carry: standard binary carry
- Basis for many test implementations

#### 2. Lagged Fibonacci with Carry

- $r = 24$, $s = 10$
- $m = 2^{32}$
- Array of 24 state values
- Long period: approximately $2^{768}$

### Key Code Fragment

```python
def awcg_bit_stream(seed, n_bits, r=24, s=10, base=2**32,
                    bits_per_value=None, msb_first=True):
    """
    Generates bit stream using AWCG.

    Args:
        seed: initial value or state array
        n_bits: number of bits to generate
        r: main lag (state array length)
        s: smaller lag
        base: modulus (base)
        bits_per_value: how many bits to extract from each value
        msb_first: whether to take bits from most significant
    """
    # Initialize state array
    state = initialize_state(seed, r, base)
    carry = 0
    output = []
    p = 0  # position pointer in circular array

    while len(output) < n_bits:
        # Indices in circular array
        idx_r = p % r
        idx_n_minus_r = (p - r) % r
        idx_n_minus_s = (p - s) % r

        # AWCG step with carry
        val = state[idx_n_minus_r] + state[idx_n_minus_s] + carry

        # Calculate new value and carry
        if val >= base:
            carry = 1
            val -= base
        else:
            carry = 0

        state[idx_r] = val
        p = (p + 1) % r

        # Bit extraction
        bits = extract_bits(val, bits_per_value, msb_first)
        output.extend(bits[:n_bits - len(output)])

    return output
```

The Python implementation uses a circular array to store states and natural multiprecision arithmetic for computational safety.

### Applications

**Practical applications:**

- **Monte Carlo simulations** – when better quality than LCG is required, but without the need for highest-class generators
- **Stochastic modeling** – systems requiring moderate statistical properties
- **Educational materials** – demonstration of carry mechanism's impact on pseudorandom sequence quality
- **Scientific research** – analysis of generators with inter-state memory
- **Algorithm prototyping** – quick testing before production implementation

**Limitations:**

- **Cryptography**: Absolutely not recommended – predictable when parameters and several outputs are known
- **Security applications**: Linear structure enables analytical attacks
- **Simulations requiring highest quality**: Modern generators (PCG, xoshiro) offer better quality with similar or higher performance
- **Memory-constrained systems**: Variants with state arrays require more memory than simple LCG

### Statistical Quality and Issues

#### Advantages over LCG:

1. **Longer period**: Carry can extend maximum period well beyond $m$
2. **Better multidimensional distribution**: Reduction of "hyperplane" effect characteristic of LCG
3. **Weaker correlations**: Carry mechanism reduces correlations between consecutive values
4. **Passes most basic tests**: DIEHARD, some tests from TestU01

#### Disadvantages:

1. **Still predictable**: Linear nature (with nonlinear carry) allows state reconstruction
2. **Slower than LCG**: Additional operations (carry checking) reduce performance
3. **Doesn't pass advanced tests**: BigCrush from TestU01 reveals weaknesses
4. **Implementation complexity**: More difficult to implement than simple LCG, especially lag variants

#### Statistical tests:

- **DIEHARD Battery**: Most tests pass successfully (better than LCG)
- **TestU01 SmallCrush**: Passes
- **TestU01 Crush**: Partially passes
- **TestU01 BigCrush**: Detects statistical anomalies
- **PractRand**: Reveals problems with long sequences (> 1TB)

### Historical Context and Trivia

**History:**

- AWCG is part of the **with-carry** generator family designed by **George Marsaglia and Arima Zaman** in the 1990s
- The first publication describing Multiply-With-Carry (MWC) appeared in 1991
- AWCG emerged as an additive variant of MWC, simpler in theoretical analysis

**Variants and development:**

- **MWC (Multiply-With-Carry)**: $x_n = (a \cdot x_{n-1} + \text{carry}_{n-1}) \bmod b$
- **CMWC (Complementary MWC)**: $x_n = (a \cdot x_{n-r} + \text{carry}_{n-1}) \bmod b$, where carry is large
- **Lagged Fibonacci with carry**: uses two lag parameters

**Historical significance:**

- Bridge between simple LCG and advanced generators of the 90s/2000s
- Inspiration for later constructions combining simplicity with better quality
- Proof of concept that a simple mechanism (carry) can significantly improve statistical properties

**Trivia:**

- Marsaglia called with-carry generators the "mother of all RNGs"
- The carry mechanism is analogous to digital carry in arithmetic
- AWCG with good parameters can achieve a period on the order of $2^{1000}$ and more
- Some hardware implementations use AWCG variants due to circuit simplicity

### Computational Complexity

- **Generation step**: $O(1)$ – addition, carry check, modulo (simpler than multiplication in LCG)
- **Memory**:
  - Basic version: $O(1)$ – state + carry
  - Version with lags: $O(r)$ – array of $r$ values + carry
- **Initialization**: $O(r)$ – state array initialization (if used)

For the basic AWCG variant, it is slightly slower than LCG (additional carry check), but still very fast. Variants with lags are slower and require more memory.

### Computational Examples

#### Example 1: Simple AWCG with small modulus

For $a=5$, $c=3$, $m=16$, $x_0=1$, $\text{carry}_0=0$:

- **Step 1**:

  - $s = 5 \cdot 1 + 3 + 0 = 8$
  - $x_1 = 8 \bmod 16 = 8$
  - $\text{carry}_1 = \lfloor 8/16 \rfloor = 0$

- **Step 2**:

  - $s = 5 \cdot 8 + 3 + 0 = 43$
  - $x_2 = 43 \bmod 16 = 11$
  - $\text{carry}_2 = \lfloor 43/16 \rfloor = 2$

- **Step 3**:

  - $s = 5 \cdot 11 + 3 + 2 = 60$
  - $x_3 = 60 \bmod 16 = 12$
  - $\text{carry}_3 = \lfloor 60/16 \rfloor = 3$

- **Step 4**:
  - $s = 5 \cdot 12 + 3 + 3 = 66$
  - $x_4 = 66 \bmod 16 = 2$
  - $\text{carry}_4 = \lfloor 66/16 \rfloor = 4$

Note that carry grows, which extends the period compared to pure LCG.

#### Example 2: AWCG-GLIBC

For $a=1103515245$, $c=12345$, $m=2^{32}$, $x_0=1$, $\text{carry}_0=0$:

- **Step 1**:

  - $s = 1103515245 \cdot 1 + 12345 + 0 = 1103527590$
  - $x_1 = 1103527590$
  - $\text{carry}_1 = 0$ (no overflow)

- **Step 2**:
  - $s = 1103515245 \cdot 1103527590 + 12345 + 0 = 1217656738076457950$
  - $x_2 = 1217656738076457950 \bmod 2^{32} = 2524885598$
  - $\text{carry}_2 = \lfloor 1217656738076457950 / 2^{32} \rfloor = 283473826$

In this case, large carry affects subsequent iterations, increasing sequence complexity.

#### Example 3: Lagged Fibonacci with Carry

For $r=5$, $s=2$, $m=10$, initial state $[1,2,3,4,5]$, $\text{carry}_0=0$:

- **Step 1** ($n=5$):

  - $x_5 = (x_0 + x_3 + 0) \bmod 10 = (1 + 4 + 0) \bmod 10 = 5$
  - $\text{carry} = 0$

- **Step 2** ($n=6$):

  - $x_6 = (x_1 + x_4 + 0) \bmod 10 = (2 + 5 + 0) \bmod 10 = 7$
  - $\text{carry} = 0$

- **Step 3** ($n=7$):
  - $x_7 = (x_2 + x_5 + 0) \bmod 10 = (3 + 5 + 0) \bmod 10 = 8$
  - $\text{carry} = 0$

AWCG remains useful mainly in educational contexts and as a moderate quality generator for simple simulations. It is a good compromise between LCG simplicity and quality requirements, though modern generators (PCG32, xoshiro256\*\*) offer better properties with similar or higher performance.
