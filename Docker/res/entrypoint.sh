#!/usr/bin/env sh

# Exit immediately if any command fails
set -e

# Interactive shell handling
if [ -t 0 ]; then
  # If no arguments are provided, show README
  if [ "$#" -lt 1 ]; then
    if [ -f README.md ]; then
      cat README.md
    else
      echo "Welcome to the EDHOC-PSK analysis container."
      echo "Available commands: tamarin-prover, proverif"
    fi
  else
    # Execute the provided command
    exec "$@"
  fi
else
  # Non-interactive mode: default to Tamarin as a service
  cat <<'ENDOFINFO'
--------- EDHOC-PSK Docker Image ---------

Running Tamarin Prover as a service.
To use CLI tools, run interactively:
  docker run --tty --interactive <image> <command>

---------------------------------------------------
ENDOFINFO

  # Default Tamarin server launch
  exec /usr/local/bin/tamarin-prover \
    interactive \
    --port=3001 \
    --interface='*4' \
    "."
fi
