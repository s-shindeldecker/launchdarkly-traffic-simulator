#!/bin/bash

# Path to the Python script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/launch_darkly_simulator.py"

# LaunchDarkly SDK key
SDK_KEY="sdk-c6b1251d-06e7-4efd-9486-2c51570cc5d3"

# Default values
NUM_RECORDS=100
CONTROL_PROB=0.3
TREATMENT_PROB=0.35
DELAY=0.05
LOG_FILE="${SCRIPT_DIR}/simulator.log"
TARGET_ATTRIBUTE=""
TARGET_VALUE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --num-records)
            NUM_RECORDS="$2"
            shift 2
            ;;
        --control-prob)
            CONTROL_PROB="$2"
            shift 2
            ;;
        --treatment-prob)
            TREATMENT_PROB="$2"
            shift 2
            ;;
        --delay)
            DELAY="$2"
            shift 2
            ;;
        --log-file)
            LOG_FILE="$2"
            shift 2
            ;;
        --brand|--product|--tier|--price)
            TARGET_ATTRIBUTE="${1#--}"  # Remove the -- prefix
            TARGET_VALUE="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 [--num-records N] [--control-prob N] [--treatment-prob N] [--delay N] [--log-file file] [--brand|--product|--tier|--price value]"
            exit 1
            ;;
    esac
done

# Build the command with base parameters
CMD="python3 \"$PYTHON_SCRIPT\" \
    --sdk-key \"$SDK_KEY\" \
    --num-records \"$NUM_RECORDS\" \
    --control-prob \"$CONTROL_PROB\" \
    --treatment-prob \"$TREATMENT_PROB\" \
    --delay \"$DELAY\" \
    --log-file \"$LOG_FILE\""

# Add target parameters if specified
if [ -n "$TARGET_ATTRIBUTE" ] && [ -n "$TARGET_VALUE" ]; then
    CMD="$CMD --target-attribute \"$TARGET_ATTRIBUTE\" --target-value \"$TARGET_VALUE\""
fi

# Execute the command
eval $CMD
