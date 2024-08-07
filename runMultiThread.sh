#!/bin/bash

# Function to run the Python script with an argument
run_script() {
    local arg=$1
    python3 MultiThreadTest.py "$arg"
}

# Start tasks in the background
run_script "1000BONKUSDT" &
run_script "1000PEPEUSDT" &

# Wait for all background tasks to complete
wait

echo "All tasks completed"

