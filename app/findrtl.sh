#!/bin/bash

# Serial number to search for
TARGET_SN="00000001"

# Run rtl_test with a short timeout (e.g., 1 second) to capture device info
RTL_TEST_OUTPUT=$(rtl_test -t 1 2>&1)

# Extract the device index and serial number using grep and awk
DEVICE_INDEX=$(echo "$RTL_TEST_OUTPUT" | grep -oP '\d+:.*SN: \K\d+' | grep -n "$TARGET_SN" | cut -d: -f1)

# Check if the device was found and set the environment variable
if [ -n "$DEVICE_INDEX" ]; then
    export RTL_DEVICE_INDEX=$((DEVICE_INDEX - 1))  # Adjusting index to 0-based
    echo "Device with SN $TARGET_SN found at index: $RTL_DEVICE_INDEX"
else
    echo "Device with SN $TARGET_SN not found."
fi
