#!/bin/bash

# Path to the Python script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/launch_darkly_simulator.py"

# LaunchDarkly SDK key (placeholder - should be provided as environment variable or parameter)
SDK_KEY="${LD_SDK_KEY:-"your-sdk-key-here"}"

# Feature flag key (placeholder - should be provided as parameter)
FEATURE_FLAG="your-feature-flag-key"

# Default values
NUM_RECORDS=100
CONTROL_PROB=0.3
TREATMENT_PROB=0.35
DELAY=0.05
LOG_FILE="${SCRIPT_DIR}/simulator.log"
TARGET_ATTRIBUTE=""
TARGET_VALUE=""
ENABLE_TRACKING=""
METRIC_NAME=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --sdk-key)
            SDK_KEY="$2"
            shift 2
            ;;
        --feature-flag)
            FEATURE_FLAG="$2"
            shift 2
            ;;
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
        --user-type|--region|--age)
            TARGET_ATTRIBUTE="${1#--}"  # Remove the -- prefix
            TARGET_VALUE="$2"
            shift 2
            ;;
        --enable-tracking)
            ENABLE_TRACKING="true"
            shift
            ;;
        --metric-name)
            METRIC_NAME="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            echo "Usage: $0 [--sdk-key key] [--feature-flag flag-key] [--num-records N]"
            echo "          [--control-prob N] [--treatment-prob N] [--delay N] [--log-file file]"
            echo "          [--user-type|--region|--age value] [--enable-tracking]"
            echo "          [--metric-name name]"
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ "$SDK_KEY" = "your-sdk-key-here" ]; then
    echo "Error: SDK key must be provided either via LD_SDK_KEY environment variable or --sdk-key parameter"
    exit 1
fi

if [ "$FEATURE_FLAG" = "your-feature-flag-key" ]; then
    echo "Error: Feature flag key must be provided via --feature-flag parameter"
    exit 1
fi

# Build the command with base parameters
CMD="python3 \"$PYTHON_SCRIPT\" \
    --sdk-key \"$SDK_KEY\" \
    --feature-flag \"$FEATURE_FLAG\" \
    --num-records \"$NUM_RECORDS\" \
    --control-prob \"$CONTROL_PROB\" \
    --treatment-prob \"$TREATMENT_PROB\" \
    --delay \"$DELAY\" \
    --log-file \"$LOG_FILE\""

# Add target parameters if specified
if [ -n "$TARGET_ATTRIBUTE" ] && [ -n "$TARGET_VALUE" ]; then
    CMD="$CMD --target-attribute \"$TARGET_ATTRIBUTE\" --target-value \"$TARGET_VALUE\""
fi

# Add tracking parameters if specified
if [ "$ENABLE_TRACKING" = "true" ]; then
    CMD="$CMD --enable-tracking"
    if [ -n "$METRIC_NAME" ]; then
        CMD="$CMD --metric-name \"$METRIC_NAME\""
    fi
fi

# Print the command being executed (commented out by default)
# echo "Executing: $CMD"

# Execute the command
eval $CMD
