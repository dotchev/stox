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
