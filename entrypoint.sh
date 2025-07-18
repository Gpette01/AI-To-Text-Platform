#!/bin/bash

# # Start the D-Bus service
# dbus-daemon --system
# sleep 2

# # Start the Avahi daemon
# avahi-daemon --no-drop-root -D --no-chroot
# sleep 2

# aplay -l

# mkdir -p /root/.gnuradio/prefs
# echo "gr_vmcircbuf_factory = file" > /root/.gnuradio/prefs/vmcircbuf_default_factory

# python3 produce.py


#python3 ./record.py
# python3 speechToText.py

# rm *.wav

# timeout 30s python3 ./record.py --frequency 102.3e6
# timeout 10s sh -c 'python3 ./record.py --frequency 102.3e6'

# python3 speechToText.py

# Serial number to search for
TARGET_SN="00000001"

# Run rtl_test with a short timeout (e.g., 1 second) to capture device info
RTL_TEST_OUTPUT=$(rtl_test -t 1 2>&1)

# Extract the device index and serial number using grep and awk
DEVICE_INDEX=$(echo "$RTL_TEST_OUTPUT" | grep -oP '\d+:.*SN: \K\d+' | grep -n "$TARGET_SN" | cut -d: -f1)

# Check if the device was found and set the environment variable
if [ -n "$DEVICE_INDEX" ]; then
    RTL_DEVICE_INDEX=$((DEVICE_INDEX - 1))  # Adjusting index to 0-based
    echo "Device with SN $TARGET_SN found at index: $RTL_DEVICE_INDEX"
else
    echo "Device with SN $TARGET_SN not found."
    RTL_DEVICE_INDEX="0"
fi

echo "export RTL_DEVICE_INDEX=$RTL_DEVICE_INDEX" >> /etc/profile.d/rtl_device_index.sh


# Debug: Print the environment variable to verify export
echo "RTL_DEVICE_INDEX in script:"
echo "$RTL_DEVICE_INDEX"


tail -f /dev/null