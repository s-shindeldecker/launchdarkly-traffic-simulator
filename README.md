# LaunchDarkly Traffic Simulator

A configurable traffic simulator for LaunchDarkly feature flags that generates synthetic user data and events with customizable targeting.

## Features

- Generate synthetic user traffic with configurable attributes:
  - Brand (Admiral, Diamond, Elephant, Toothbrush, Biscuit)
  - Product (Car, Home, Motorcycle, Renters)
  - Tier (Bronze, Silver, Gold, Platinum)
  - Price (Various preset values)
- Target specific user segments with boosted probability
- Configurable simulation parameters:
  - Number of records
  - Control/Treatment probabilities
  - Delay between events
  - Targeting attributes and values
- Detailed logging with rotation

## Requirements

- Python 3.x
- LaunchDarkly SDK
- Faker library

## Installation

1. Clone the repository:
```bash
git clone https://github.com/s-shindeldecker/launchdarkly-traffic-simulator.git
cd launchdarkly-traffic-simulator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The simulator can be run using the provided shell script:

```bash
# Basic usage (generates 100 records)
./run_simulator.sh

# Custom number of records
./run_simulator.sh --num-records 1000

# Target specific attributes (1.5x probability boost)
./run_simulator.sh --brand Toothbrush
./run_simulator.sh --product Car
./run_simulator.sh --tier Gold
./run_simulator.sh --price 93.84

# Combine parameters
./run_simulator.sh --num-records 500 --product Car --control-prob 0.4 --treatment-prob 0.45
```

### Parameters

- `--num-records`: Number of records to generate (default: 100)
- `--control-prob`: Base probability for control group (default: 0.3)
- `--treatment-prob`: Base probability for treatment group (default: 0.35)
- `--delay`: Delay between records in seconds (default: 0.05)
- `--log-file`: Custom log file path
- Targeting parameters:
  - `--brand`: Target specific brand
  - `--product`: Target specific product
  - `--tier`: Target specific tier
  - `--price`: Target specific price

### Available Values

- Brands: Admiral, Diamond, Elephant, Toothbrush, Biscuit
- Products: Car, Home, Motorcycle, Renters
- Tiers: Bronze, Silver, Gold, Platinum
- Prices: 93.84, 143.73, 101.35, 86.02, 46.91, 125.62, 77.85, 99.68, 73.99, 148.79

## CRON Usage

To schedule regular simulations, add entries to your crontab:

```bash
# Run every day at 2 AM
0 2 * * * /path/to/run_simulator.sh

# Run every 6 hours with targeting
0 */6 * * * /path/to/run_simulator.sh --product Car --num-records 1000
```

## Logging

The simulator creates detailed logs including:
- User context attributes
- Flag evaluation results
- Tracking probabilities
- Event details

Logs are automatically rotated to prevent excessive file size.

## License

MIT License - See LICENSE file for details
