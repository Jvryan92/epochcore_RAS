#!/bin/bash

# Create a temporary file to simulate GITHUB_OUTPUT
GITHUB_OUTPUT=$(mktemp)
export GITHUB_OUTPUT

echo "Testing the fixed workflow step..."
echo "GITHUB_OUTPUT file: $GITHUB_OUTPUT"

# Simulate the fixed workflow step
echo "Initializing EpochCore RAS recursive improvement system..."
python integration.py init-recursive > /dev/null

echo "Getting system status..."
STATUS=$(python integration.py recursive-status)
echo "status=$STATUS" >> $GITHUB_OUTPUT

echo ""
echo "Contents of GITHUB_OUTPUT:"
cat $GITHUB_OUTPUT

echo ""
echo "Validating GITHUB_OUTPUT format..."
while IFS= read -r line; do
    if [[ "$line" =~ ^[a-zA-Z_][a-zA-Z0-9_]*=.*$ ]]; then
        echo "✓ Valid: $line"
    else
        echo "✗ Invalid: $line"
    fi
done < $GITHUB_OUTPUT

rm $GITHUB_OUTPUT
