SystemRNG (System Random Number Generator) is an interface to cryptographically secure randomness sources provided by the operating system. Unlike deterministic pseudorandom generators, SystemRNG draws entropy from real physical sources and system events, ensuring the highest cryptographic quality. It is the **gold standard** for all applications requiring unpredictability and security.

### Operating Principle

SystemRNG is not an algorithm in the traditional sense – it is an abstraction over entropy collection and delivery mechanisms implemented by the operating system kernel.

#### System Entropy Sources

Operating systems collect entropy from many sources:

**Hardware events:**

- Interrupt timing – moment of hardware interrupt occurrence
- Thermal noise from devices – voltage fluctuations in electronic components
- Disk operation timing – micro-delays in I/O operations
- Mouse movement and clicks – timing and positions
- Keystroke timing
- Network packets – arrival timing, jitter

**System events:**

- Process IDs of new processes
- Thread IDs
- CPU performance counters
- High-resolution timestamp (TSC, RDTSC)
- Kernel object identifiers

**Dedicated hardware sources:**

- **RDRAND** (Intel/AMD) – CPU instruction generating randomness from DRNG (Digital Random Number Generator)
- **RDSEED** – CPU instruction drawing from ENRNG (Enhanced NRBG)
- **TPM** (Trusted Platform Module) – dedicated cryptographic chip
- **Hardware RNG** – dedicated devices (e.g., /dev/hwrng on Linux)

#### System Implementations

**Linux/Unix (/dev/urandom, /dev/random):**

Linux kernel maintains an **entropy pool** – buffer of entropy collected from various sources.

**/dev/random** (blocking):

- Blocks when entropy pool is "exhausted"
- Historically used for critical operations
- From Linux 5.6+ behavior changed

**/dev/urandom** (non-blocking):

- **Never blocks** – always returns data
- After initialization: cryptographically secure CSPRNG (ChaCha20 from 5.17+)
- **Recommended for all applications** (including keys)

**Windows (CryptGenRandom, BCryptGenRandom):**

Windows uses **Cryptographic Service Provider (CSP)** / **Cryptography API: Next Generation (CNG)**.

**CryptGenRandom** (old API):

- Part of CryptoAPI
- Uses AES-CTR with seed from entropy pool

**BCryptGenRandom** (modern API):

- Part of CNG (Cryptography Next Generation)
- Faster, more secure
- By default uses `BCRYPT_USE_SYSTEM_PREFERRED_RNG`

**Windows entropy sources:**

- Performance counters (QueryPerformanceCounter)
- System timestamp
- Process/Thread IDs
- Memory allocations
- CPU thermal noise (if available)
- TPM (if available)

#### Interface in Python

Python provides os.urandom() as a cross-platform interface:

```python
import os

# Get n bytes cryptographically secure
random_bytes = os.urandom(32)  # 256 bits
```

**Mapping per platform:**

- Linux: `/dev/urandom` or `getrandom()` syscall
- Windows: `BCryptGenRandom()`
- macOS: `/dev/urandom`

### Key Code Fragment

```python
def system_random_bit_stream(seed, n_bits, bits_per_value=32):
    """
    Generates bit stream using system CSPRNG.
    'seed' parameter is ignored (for compatibility).
    """
    import os

    # Calculate required number of bytes
    num_bytes = (bits_per_value + 7) // 8
    output = []

    while len(output) < n_bits:
        # Get bytes from system source
        if sys.platform.startswith('win'):
            # Windows: BCryptGenRandom (through ctypes)
            raw = bcrypt_gen_random(num_bytes)
        else:
            # Linux/macOS: /dev/urandom
            raw = os.urandom(num_bytes)

        # Convert bytes to number
        val = int.from_bytes(raw, 'big')
        val &= (1 << bits_per_value) - 1

        # Bit extraction
        bits = extract_bits(val, bits_per_value, msb_first=True)
        output.extend(bits[:n_bits - len(output)])

    return output
```

### secrets Module – High-level API

Python 3.6+ offers `secrets` module – **recommended interface for security applications**:

```python
import secrets

# Token generation
token_hex = secrets.token_hex(16)      # 32-character hex
token_urlsafe = secrets.token_urlsafe(32)  # Base64 URL-safe

# Random numbers
rand_int = secrets.randbelow(100)       # [0, 100)
rand_bits = secrets.randbits(256)       # 256-bit number

# Sequence selection
choice = secrets.choice(['a', 'b', 'c'])
```

Everything based on `os.urandom()` – cryptographic guarantee.

### Applications

**Cryptographic applications:**

- **Key generation** – AES, RSA, ECDSA, ChaCha20 keys
- **Initialization vectors (IV)** – for block ciphers (AES-CBC, AES-GCM)
- **Nonce generation** – one-time values for protocols (TLS, IPsec)
- **Password salts** – bcrypt, scrypt, Argon2, PBKDF2
- **Session tokens** – web applications, authentication tokens
- **CSRF tokens** – cross-site request forgery protection
- **API keys** – generating unique identifiers

**Other applications:**

- **Gambling/online casinos** – drawing where regulations require "true randomness"
- **Live drawing** – contests, lotteries
- **Seeding other generators** – initializing PCG, xoshiro for deterministic simulations

**When to ALWAYS use SystemRNG:**

- Any cryptographic application
- Generating secret values (keys, passwords)
- Web application security (tokens, sessions)
- When unpredictability is critical

**When PRNG can be used (PCG, MT):**

- Scientific simulations (Monte Carlo)
- Games (non-gambling)
- Procedural content generation
- Statistical tests

### Quality and Security

#### Advantages:

1. **Cryptographically secure** – unpredictable even for attacker with system knowledge
2. **Non-deterministic seed** – uses real entropy sources
3. **Forward secrecy** – old values don't allow predicting new ones
4. **Backward secrecy** – new values don't allow reconstructing old ones
5. **FIPS 140-2/3 standards** – system implementations often certified

#### Security guarantees:

**Unpredictability:**

- Attacker knowing CSPRNG algorithm + all previous outputs **cannot** predict next bit with probability > 50%
- Requires breaking cryptography (e.g., ChaCha20, AES)

**Attack resistance:**

- **State compromise resilience**: Even if attacker obtains full CSPRNG state, new entropy from system "fixes" generator
- **Backtracking resistance**: State compromise doesn't reveal past outputs

**Certifications:**

- Linux /dev/urandom: Compliant with FIPS 140-2 requirements
- Windows BCryptGenRandom: FIPS 140-2 Level 1 certified
- Apple SecRandomCopyBytes: Meets Common Criteria EAL4+

### Performance

SystemRNG is **slower** than dedicated PRNGs, but **fast enough** for most applications.

**Why slower?**

- Syscall overhead – user→kernel space transition
- Entropy pool operations
- Multithreading synchronization
- Initialization state checking

**Optimizations:**

- Fetching larger buffers (e.g., 1024 bytes) instead of 4 bytes at a time
- Userspace buffering for frequent small requests
- For simulations: using SystemRNG for seed, then PRNG

### Historical Context and Trivia

**Linux /dev/random evolution:**

- **1994**: Theodore Ts'o introduces /dev/random to Linux 1.3.30
- **2006**: Yarrow algorithm (Bruce Schneier) replaced by custom design
- **2016**: Controversies about /dev/random "blocking" vs /dev/urandom
- **2017-2020**: Series of improvements, migration to ChaCha20
- **2022**: Linux 5.17 – fully rewritten implementation, ChaCha20-based

**/dev/random vs /dev/urandom controversy:**

- **Myth**: "/dev/random is more secure"
- **Truth**: From ~2013 /dev/urandom is equally secure after initialization
- **Consensus (2016+)**: **Use /dev/urandom for everything**
- Linus Torvalds personally recommended /dev/urandom

**Windows CryptoAPI history:**

- **1996**: CryptoAPI (CryptGenRandom) in Windows NT 4.0
- **2007**: CNG (BCryptGenRandom) in Windows Vista
- **2015**: NSA backdoor in Dual_EC_DRBG (not used in Windows, but raised concerns)
- **2018**: Windows 10 RS5 – BCryptGenRandom performance improvements

**Trivia:**

- FreeBSD uses **Fortuna** (Ferguson & Schneier, 2003) – theoretically perfect CSPRNG
- OpenBSD pioneered **pledge() + unveil()** – restricting /dev/urandom access
- Android uses /dev/urandom + additional entropy from sensors
- iPhone collects entropy from **Secure Enclave** – dedicated cryptographic coprocessor
- Some servers have **hardware RNG PCI cards** for additional entropy

**Security incidents:**

- **2006**: Debian OpenSSL bug – weak entropy due to code error (CVE-2008-0166)
- **2012**: Android Bitcoin wallets – weak randomness on some devices, bitcoin theft
- **2013**: Snowden reveals – NSA interference in DRBG standards (Dual_EC_DRBG)

**Lessons learned:**

- Never implement your own CSPRNG
- Always use system API
- Check initialization (especially in early boot / embedded)

### Usage Examples

#### Example 1: AES key generation

```python
import secrets

# 256-bit AES key
aes_key = secrets.token_bytes(32)
print(aes_key.hex())  # e.g., '3f7a...'
```

#### Example 2: Session token

```python
import secrets

# 256-bit token (base64 URL-safe)
session_token = secrets.token_urlsafe(32)
print(session_token)  # e.g., 'dGhlIHNhb...'
```

#### Example 3: Password salt

```python
import secrets
import hashlib

password = "user_password"
salt = secrets.token_bytes(16)  # 128-bit salt

# PBKDF2 with salt
hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
```

#### Example 4: Seed for PRNG (deterministic simulations)

```python
import secrets
import random

# Use SystemRNG to generate seed
seed = secrets.randbits(64)

# Feed deterministic PRNG
rng = random.Random(seed)
# Now simulation is reproducible with this seed
```

#### Example 5: List selection (cryptographic)

```python
import secrets

# Element selection (uniform, cryptographically secure)
items = ['option1', 'option2', 'option3']
chosen = secrets.choice(items)
```

SystemRNG represents the highest level of randomness quality available in computer systems – it combines physical entropy sources with cryptographically secure algorithms. It is absolutely essential for all security-related applications and should be the default choice when unpredictability is critical. It is recommended to avoid custom PRNG implementations in favor of proven, system-based solutions.
