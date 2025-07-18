rm -f doa.txt

# Determine the highest log number
latest_log=$(ls /logs/log.* 2>/dev/null | awk -F. '{print $NF}' | sort -n | tail -1)
if [ -z "$latest_log" ]; then
    latest_log=0
fi
new_log_number=$((latest_log + 1))
echo "Starting new log file: log.$new_log_number"

# Append the current timestamp to the new log file
echo "Log start time: $(date)" >> /logs/log.$new_log_number

# Run the program and append to the new log file
python3 ./main.py 2>&1 | tee -a /logs/log.$new_log_number