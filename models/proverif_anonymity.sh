#!/usr/bin/env bash

label="$1"
file="$2"
out_log="out-${label}.log"
time_log="time-${label}.log"
csv_file="results.csv"

[[ ! -f "$csv_file" ]] && echo "label,status,time_real,time_user,time_sys" > "$csv_file"

# Start ProVerif in background, redirect stdout+stderr
/usr/bin/time -f "%e %U %S" -o "$time_log" proverif "$file" &> "$out_log" &
PV_PID=$!

# Monitor the output file in a loop
status="UNKNOWN"
while sleep 1; do
    if grep -q "A trace has been found" "$out_log"; then
        echo "[*] ATTACK detected! Killing ProVerif..."
        kill "$PV_PID"
        status="ATTACK"
        break
    fi
    # check if ProVerif finished
    if ! kill -0 "$PV_PID" 2>/dev/null; then
        break
    fi
done

wait "$PV_PID" 2>/dev/null || true  # wait for cleanup

# Parse time
read real user sys < "$time_log"

# If no attack detected, parse result
if [[ "$status" == "UNKNOWN" ]]; then
    if grep -q "RESULT Observational equivalence is true" "$out_log"; then
        status="PASSED"
    else
        status="FAILED"
    fi
fi

# Append CSV
printf "%s,%s,%s,%s,%s\n" "$label" "$status" "$real" "$user" "$sys" >> "$csv_file"
echo "[*] $label -> $status"

# Clean up temporary logs
rm -f "$out_log" "$time_log"