The Craps test simulates the craps dice game using bits as randomness source for die rolls. The game has well-defined win probabilities (~49.3%) that should be achieved by truly random generators.

## How it works
1. Converts bit triplets into die rolls (1-6)
2. Simulates craps games according to standard rules
3. Counts won and lost games
4. Compares win proportion with theoretical value (~0.493)
5. Uses Chi-square test for verification

## Craps Rules
```
First roll (sum of 2 dice):
- 7 or 11 → instant win
- 2, 3, or 12 → instant loss
- Other sums → "point", continue rolling:
  - If sum = point → win
  - If sum = 7 → loss
  - Otherwise → roll again
```

## Mathematical formula
```
Theoretical probabilities:
P(win) ≈ 0.493
P(loss) ≈ 0.507

Expected counts:
expected_wins = total_games × 0.493
expected_losses = total_games × 0.507

Chi-square test:
χ² = (wins - expected_wins)² / expected_wins +
     (losses - expected_losses)² / expected_losses

df = 1
p-value = erfc((χ² / 2)^0.5)
```

## Critical value
- **Threshold**: p-value ≥ 0.01
- Test **passed** when p-value ≥ 0.01

## Minimum requirements
- **Minimum**: 200,000 bits
- **Minimum games**: 100
- **Bits per roll**: 3 (with rejection of 6,7)

## Implementation
The test converts bit triplets into values 0-7 and rejects 6-7, using values 0-5 as rolls 1-6. Simulates complete craps games according to standard rules.

## API usage example
```bash
curl -X POST http://localhost:8000/api/rngs/1/run_test \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "diehard_craps",
    "samples_count": 200000,
    "seed": 42
  }'
```

## Result interpretation
- **score = 1.0**: Perfect win rate ~49.3%
- **score > 0.7**: Very good result
- **score < 0.5**: Weak generator, incorrect outcome distribution
- **passed = false**: Generator failed the test

## Test parameters
- **Data type**: Bits (binary)
- **Minimum samples**: 200,000 bits
- **Complexity**: Medium (game simulation)
- **Optimization**: Uses numpy for bit conversion
