#!/bin/bash
set -e

# Function to check if containers are running
check_containers() {
  echo "Checking containers..."
  
  if ! docker-compose ps -q web &>/dev/null || [ -z "$(docker-compose ps -q web)" ]; then
    echo "Web container is not running!"
    return 1
  fi
  
  if ! docker-compose ps -q db &>/dev/null || [ -z "$(docker-compose ps -q db)" ]; then
    echo "Database container is not running!"
    return 1
  fi
  
  if ! docker-compose ps -q nginx &>/dev/null || [ -z "$(docker-compose ps -q nginx)" ]; then
    echo "Nginx container is not running!"
    return 1
  fi
  
  echo "All containers are running."
  return 0
}

# Function to check logs for issues
check_logs() {
  echo "Checking for errors in logs..."
  
  if docker-compose logs web | grep -i "error\|exception" | grep -v "INFO" > /dev/null; then
    echo "Found errors in web container logs."
    return 1
  fi
  
  echo "No significant errors found in logs."
  return 0
}

# Restart containers if needed
restart_containers() {
  echo "Restarting containers..."
  docker-compose down
  docker-compose up -d --build
  echo "Containers restarted."
}

# Main function
main() {
  if ! check_containers; then
    echo "Some containers are not running. Restarting..."
    restart_containers
  elif ! check_logs; then
    echo "Found errors in logs. Restarting..."
    restart_containers
  else
    echo "All checks passed. System is healthy."
  fi
}

# Run main function
main