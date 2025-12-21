PCG32 (Permuted Congruential Generator) is a modern pseudorandom generator combining the simplicity and speed of classical LCG with an advanced output permutation function. Designed by Melissa O'Neill around 2014, PCG quickly gained popularity as the "successor" to Mersenne Twister, offering better statistical quality with significantly lower memory usage and higher performance.

### Mathematical Explanation

The PCG32 generator consists of two main components: a simple state generator (LCG) and an advanced output permutation function.

#### State Update (LCG)

The internal state is a 64-bit integer updated according to the classical LCG formula:

$$\text{state}_{n+1} = (a \cdot \text{state}_n + c) \bmod 2^{64}$$

where:

- $a = 6364136223846793005$ – carefully chosen multiplier ensuring maximum period
- $c = \text{inc}$ – increment, odd value chosen during initialization
- Modulus $2^{64}$ ensures full period $2^{64}$ (all 64-bit values)

**Increment $c$ (inc):**
The increment value is calculated from the parameterized sequence (_sequence_):

$$\text{inc} = (\text{seq} << 1) | 1$$

Operation `<< 1` shifts bits left, and `| 1` ensures oddness. Different sequences generate independent pseudorandom streams.

#### Permutation Function: XSH RR (xorshift high, random rotate)

PCG's key innovation is the advanced permutation function transforming 64-bit state into 32-bit output:

1. **Xorshift of high bits**:
   $$\text{xorshifted} = ((\text{state} >> 18) \oplus \text{state}) >> 27$$

   This operation:

   - Shifts state 18 bits right
   - XORs with original state (mixes bits)
   - Shifts result 27 bits (selects upper 32 bits)

2. **Random rotation**:
   $$\text{rot} = \text{state} >> 59$$

   Upper 5 bits of state determine rotation amount (0-31).

3. **Right rotation**:
   $$\text{output} = (\text{xorshifted} >> \text{rot}) | (\text{xorshifted} << (32 - \text{rot}))$$

   Bitwise rotation right by `rot` positions.

**Why does this work?**

- **Xorshift**: Mixes correlated bits from LCG, reducing linear dependencies
- **State-dependent rotation**: Adds nonlinearity – different states have different permutations
- **Selection of upper bits**: Upper bits of LCG have better statistical properties than lower
- **32-bit output from 64-bit state**: Provides additional protection against state reconstruction

#### Initialization

PCG32 initialization is a two-stage process:

```python
state = 0
inc = (seq << 1) | 1  # Ensure oddness

# Step 1: Generator "warm-up"
state = (state * a + inc) % 2**64

# Step 2: Add initstate
state = (state + initstate) % 2**64
state = (state * a + inc) % 2**64
```

This ensures different seeds lead to uncorrelated sequences.

### PCG Variants

The PCG family offers many variants adapted to different needs:

#### 1. **PCG32** (implemented here)

- State: 64 bits
- Output: 32 bits
- Permutation: XSH RR
- Most popular, good balance

#### 2. **PCG64**

- State: 128 bits
- Output: 64 bits
- Longer period, better properties for 64-bit applications

#### 3. **PCG32-fast**

- Simplified permutation (XSH RS)
- Faster, but slightly worse statistically

#### 4. **PCG-unique**

- Each instance has unique inc generated from object address
- Provides independent streams without manual configuration

### Key Code Fragment

```python
def pcg32_bit_stream(seed, n_bits, bits_per_value=32, msb_first=True):
    """
    Generates bit stream using PCG32.

    Args:
        seed: int (initstate) or (initstate, seq)
        n_bits: number of bits to generate
        bits_per_value: how many bits to extract (default 32)
        msb_first: whether to take bits from most significant
    """
    # PCG constants
    MULT = 6364136223846793005
    MASK64 = (1 << 64) - 1

    # Parse seed
    if isinstance(seed, int):
        initstate, seq = seed, 1
    else:
        initstate, seq = seed[0], seed[1]

    # Calculate inc (must be odd)
    inc = ((seq << 1) | 1) & MASK64

    # State initialization
    state = 0
    state = (state * MULT + inc) & MASK64
    state = (state + initstate) & MASK64
    state = (state * MULT + inc) & MASK64

    output = []

    while len(output) < n_bits:
        # Step 1: State update (LCG)
        state = (state * MULT + inc) & MASK64

        # Step 2: XSH RR permutation
        xorshifted = (((state >> 18) ^ state) >> 27) & 0xFFFFFFFF
        rot = (state >> 59) & 0x1F
        output_val = ((xorshifted >> rot) |
                      (xorshifted << ((-rot) & 31))) & 0xFFFFFFFF

        # Bit extraction
        bits = extract_bits(output_val, bits_per_value, msb_first)
        output.extend(bits[:n_bits - len(output)])

    return output
```

The implementation uses 64-bit arithmetic available in modern Python, with masking ensuring correct behavior modulo $2^{64}$.

### Applications

**Practical applications:**

- **Computer games** – procedural world generation, AI, particle systems, animations
- **Monte Carlo simulations** – scientific research, financial modeling, physics
- **Unit testing** – deterministic test data generation
- **Procedural content generation** – textures, sounds, game levels
- **Scientific libraries** – numpy (from version 1.17+ as default generator PCG64)
- **Animations and visual effects** – Perlin noise, particle systems

**Advantages over Mersenne Twister:**

- **Faster initialization**: Instant vs hundreds of CPU cycles
- **Lower memory usage**: 8 bytes vs 2.5 KB
- **Better quality in low dimensions**: Passes more statistical tests
- **Many independent streams**: Easy parallelization through different sequences
- **Predictable performance**: No "warming up" like MT

**Limitations:**

- **Not for cryptography**: State can be reconstructed from several outputs (64 output bits < 64 state bits)
- **Not CSPRNG**: Lacks cryptographic properties

### Statistical Quality

#### Statistical tests:

**TestU01 (L'Ecuyer and Simard):**

- **SmallCrush**: 100% passed
- **Crush**: 100% passed
- **BigCrush**: 100% passed (all 160 tests)

**PractRand (Doty-Humphrey):**

- Passes tests up to at least 32 TB of data
- No detected anomalies for standard parameters

**DIEHARD Battery:**

- All tests passed
- Much better result than LCG, Park-Miller

#### Quality advantages:

1. **No lattice structure**: Eliminates hyperplane problem characteristic of LCG
2. **Uniform distribution**: Values evenly distributed in multidimensional space
3. **Long sequences**: Passes tests on terabytes of data without detected patterns
4. **Low correlation**: Consecutive and distant values are statistically independent

### Historical Context and Trivia

**History:**

- Designed by **Melissa O'Neill** at Harvey Mudd College (~2014)
- First publication: article "PCG: A Family of Simple Fast Space-Efficient Statistically Good Algorithms for Random Number Generation" (2014)
- Official website: www.pcg-random.org with full documentation and implementations

**Motivation for creation:**

- Response to Mersenne Twister weaknesses (large memory, weak in low dimensions)
- Need for fast, quality generator for games and simulations
- Desire to create generator "better than MT in everything except period"

**Industry adoption:**

- **NumPy** (Python): PCG64 as default from version 1.17 (2019)
- **Rust**: rand_pcg crate widely used
- **C++**: Implementations in libraries such as pcg-cpp
- **Games**: Used in Unity, Unreal Engine (through integrations)

**Trivia:**

- Name "Permuted Congruential Generator" emphasizes key innovation – LCG output permutation
- Melissa O'Neill wrote a **256-page technical report** documenting all PCG aspects
- PCG has over 20 variants (different state sizes, permutation functions)
- Generator was tested on **petabytes** of data in PractRand tests
- PCG-unique uses memory address to generate unique inc – each instance has different stream

### Computational Complexity

- **Generation step**: $O(1)$ – constant number of operations (multiplication, addition, xor, shifts, rotation)
- **Memory**: $O(1)$ – 8 bytes state + 8 bytes inc (16 bytes total)
- **Initialization**: $O(1)$ – two LCG steps

**Detailed operation analysis per step:**

- 1× 64-bit multiplication
- 2× 64-bit addition
- 3× bit shifts
- 1× XOR
- 1× bit rotation (2 shifts + OR)

**Total**: ~8-10 CPU instructions per 32 output bits (≈0.3 instructions/bit)

**Practical performance:**

- Python (CPython): ~50-100 MB/s
- C/C++ (optimized): ~400-800 MB/s
- Rust: ~500-1000 MB/s
- SIMD (AVX2): ~2-4 GB/s (parallel streams)

### Computational Examples

#### Example 1: Basic initialization

For `initstate = 42`, `seq = 54`:

**Initialization step:**

```
inc = (54 << 1) | 1 = 109 (binary: 1101101, odd ✓)

state = 0
state = (0 * 6364136223846793005 + 109) % 2^64 = 109
state = (109 + 42) % 2^64 = 151
state = (151 * 6364136223846793005 + 109) % 2^64
      = 960784502091959864
```

Initial state: `960784502091959864`

#### Example 2: First iteration

State: `state = 960784502091959864`

**State update:**

```
state_new = (960784502091959864 * 6364136223846793005 + 109) % 2^64
          = 15295219558163128549 % 2^64
          = 15295219558163128549  (already in 64-bit range)
```

**XSH RR permutation:**

```
xorshifted = ((state >> 18) ^ state) >> 27
state >> 18 = 3653889584...
(state >> 18) ^ state = ...
xorshifted = ... (32 bits)

rot = state >> 59 = 0 (upper 5 bits)

output = (xorshifted >> 0) | (xorshifted << 32)
       = xorshifted  (no rotation for rot=0)
```

Result: 32-bit pseudorandom value.

#### Example 3: State space and periods

- **Full period**: $2^{64} = 18{,}446{,}744{,}073{,}709{,}551{,}616$ state values
- **Number of independent streams**: $2^{63}$ (different seq values)
- **Total space**: $2^{64} \times 2^{63} = 2^{127}$ unique sequences

This means $2^{63}$ parallel streams can be generated, each with period $2^{64}$.

#### Example 4: Comparison with LCG (2D visualization)

If drawing points $(x_n, x_{n+1})$:

- **LCG**: Visible parallel lines (lattice structure)
- **PCG32**: Uniform distribution without visible structure

XSH RR permutation effectively destroys LCG linear structure.

PCG32 represents a modern approach to PRNG generator design: use of simple, well-understood components (LCG) with intelligent permutation giving excellent statistical properties at minimal cost. It is an ideal choice for most applications not requiring cryptographic guarantees.
