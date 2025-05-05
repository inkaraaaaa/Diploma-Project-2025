#!/bin/bash

# Find process using port 8000
echo "Finding processes on port 8000..."
pid=$(lsof -ti:8000)

if [ -z "$pid" ]; then
  echo "No process found running on port 8000"
  exit 0
else
  echo "Found process with PID $pid running on port 8000"
  
  # Kill the process
  echo "Stopping process..."
  kill -9 $pid
  
  # Verify process was killed
  if lsof -ti:8000 > /dev/null; then
    echo "Failed to stop process on port 8000"
    exit 1
  else
    echo "Successfully stopped process on port 8000"
  fi
fi