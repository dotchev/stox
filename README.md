Run some stats on stocks using historical price data from Yahoo finance API

## Setup

Install dependencies
```sh
pip install -r requirements.txt
```

## Temperature Levels

[temperature-levels.md](temperature-levels.md) tracks P25/P75 price levels
based on the % distance from the 200-day SMA, updated weekly by a GitHub
Actions job.

## 52-Week Returns

[stocks-52w.md](stocks-52w.md) tracks the geometric mean, std and Sharpe
ratio of rolling 52-week returns over the history common to all symbols
(max 5 years), updated weekly by a GitHub Actions job.
