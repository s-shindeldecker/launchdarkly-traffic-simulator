# LaunchDarkly Traffic Simulator

A configurable traffic simulator for LaunchDarkly feature flags that generates synthetic user data and events with customizable targeting rules.

## Features

- Generate synthetic user traffic with configurable attributes:
  - User Type (new, returning, premium, basic)
  - Region (north, south, east, west)
  - Age (random between 18-80)
- Target specific user segments with boosted probability
- Configurable simulation parameters:
  - Number of records
  - Control/Treatment probabilities
  - Delay between events
  - Event tracking options
  - Custom metric names
- Detailed logging with rotation
- Data analysis and visualization capabilities

## Requirements

- Python 3.x
- Required Python packages (install via requirements.txt):
  - ldclient-py (LaunchDarkly SDK)
  - faker (Synthetic data generation)
  - pandas (Data manipulation)
  - numpy (Numerical operations)
  - matplotlib (Basic plotting)
  - seaborn (Statistical visualizations)
  - plotly (Interactive visualizations)
  - ipywidgets (Jupyter notebook widgets)
  - nbformat (Notebook format support)

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

3. Set up your LaunchDarkly SDK key:
```bash
# For bash/zsh
export LAUNCHDARKLY_SDK_KEY='your-sdk-key'

# For Windows Command Prompt
set LAUNCHDARKLY_SDK_KEY=your-sdk-key

# For Windows PowerShell
$env:LAUNCHDARKLY_SDK_KEY='your-sdk-key'
```

You can also add this to your shell's profile file (.bashrc, .zshrc, etc.) to make it permanent.

## Usage

The simulator is run using Python with various command-line arguments. The SDK key can be provided either via the LAUNCHDARKLY_SDK_KEY environment variable (recommended) or the --sdk-key parameter.

```bash
# Basic usage with SDK key from environment variable
python launch_darkly_simulator.py --feature-flag YOUR_FLAG_KEY

# Custom number of records with event tracking
python launch_darkly_simulator.py --feature-flag YOUR_FLAG_KEY \
    --num-records 1000 --enable-tracking

# Target specific attributes (1.5x probability boost)
python launch_darkly_simulator.py --feature-flag YOUR_FLAG_KEY \
    --target-attribute user_type --target-value premium

# Custom event tracking with specific probabilities
python launch_darkly_simulator.py --feature-flag YOUR_FLAG_KEY \
    --enable-tracking --metric-name "custom-metric" \
    --control-prob 0.4 --treatment-prob 0.45
```

### Required Parameters

- `--feature-flag`: The feature flag key to evaluate

### Optional Parameters

- `--sdk-key`: LaunchDarkly SDK key (recommended to use LAUNCHDARKLY_SDK_KEY environment variable instead)
- `--num-records`: Number of records to generate (default: 100)
- `--control-prob`: Base probability for control group (default: 0.3)
- `--treatment-prob`: Base probability for treatment group (default: 0.35)
- `--delay`: Delay between records in seconds (default: 0.05)
- `--log-file`: Custom log file path (default: simulator.log)
- `--enable-tracking`: Enable event tracking (flag)
- `--metric-name`: Custom metric name for tracking events
- Targeting parameters (must be used together):
  - `--target-attribute`: Attribute to target (user_type, region, or age)
  - `--target-value`: Value to target for the specified attribute

### Available Values

- User Types: new, returning, premium, basic
- Regions: north, south, east, west
- Age: Random integer between 18 and 80

## Data Analysis

The project includes a Jupyter notebook (`Simulate_Percent_Rollout.ipynb`) for analyzing and visualizing the simulation results. The notebook provides:
- Data loading and preprocessing
- Statistical analysis of flag evaluations
- Distribution visualizations
- Targeting effectiveness analysis
- Interactive plots and widgets

To use the notebook:
```bash
jupyter notebook Simulate_Percent_Rollout.ipynb
```

## Logging

The simulator creates detailed logs including:
- User context attributes (user type, region, age)
- Flag evaluation results
- Event tracking details
- Targeting probabilities
- Processing status

Logs are automatically rotated (1MB per file, maximum 5 backup files) to prevent excessive disk usage.

Example log entry:
```
2023-XX-XX XX:XX:XX - LaunchDarklySimulator - INFO - Tracked event 'flag-example-evaluation' for user abc-123 - Type: premium, Region: north, Age: 35 (Flag Value: true, Probability: 0.45)
```

## Error Handling

The simulator includes robust error handling for:
- LaunchDarkly client initialization failures
- Invalid targeting configurations
- Record processing errors
- Network connectivity issues

All errors are logged with detailed information for troubleshooting.

## License

MIT License - See LICENSE file for details
