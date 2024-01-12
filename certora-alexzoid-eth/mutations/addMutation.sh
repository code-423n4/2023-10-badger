#!/bin/bash

# Create a mutation for a specific contract, use second parameter as config file name
# Examples:
#    ./certora/mutations/addMutation.sh ActivePool ./packages/contracts/contracts/ActivePool.sol
#    ./certora/mutations/addMutation.sh CollSurplusPool ./packages/contracts/contracts/CollSurplusPool.sol
#    ./certora/mutations/addMutation.sh EBTCToken ./packages/contracts/contracts/EBTCToken.sol
#    ./certora/mutations/addMutation.sh SortedCdps ./packages/contracts/contracts/SortedCdps.sol

# Function to add diff block above modified code
add_diff_block() {
    local file="$1"
    local temp_file="./temp_${file##*/}"

    # Copy the original file to a temporary file
    cp "$file" "$temp_file"

    # Capture the entire git diff output
    git_diff_block=$(git diff "$file")

    # Extract the starting line number of the first change in the diff
    first_change_line_number=$(echo "$git_diff_block" | sed -n '/@@/,/@@/ { s/@@ -\([0-9]*\),[0-9]* .*/\1/p; q; }')

    # If a change is found, insert the diff block above it
    if [ ! -z "$first_change_line_number" ]; then
        # Adjust line number by subtracting 1 to insert above the block
        local adjusted_line_number=$((first_change_line_number - 1))

        # Insert the git diff block above the adjusted line number
        awk -v n="$adjusted_line_number" -v diff_block="$git_diff_block" 'NR==n {print "\n/**************************** Diff Block Start ****************************\n"diff_block"\n**************************** Diff Block End *****************************/\n"} 1' "$temp_file" > temp && mv temp "$temp_file"

    fi

    # Move the modified temp file back to original
    mv "$temp_file" "$file"
}

MUTATION_DIR_NAME="$1"
CONTRACT_FILENAME="$2"

if [ -z "$MUTATION_DIR_NAME" ] || [ -z "$CONTRACT_FILENAME" ]; then
    echo "usage:"
    echo "  ./addMutation.sh [MUTATION_DIR_NAME] [CONTRACT_FILENAME]"
    echo "Example:"
    echo "  ./certora/mutations/addMutation.sh ActivePool ./packages/contracts/contracts/ActivePool.sol"
    exit 0
fi

# Get the last mutation number
LAST_NUMBER=$(find certora/mutations/${MUTATION_DIR_NAME} -type f -name "*.sol" | awk -F '/' '{print $NF}' | awk -F '.sol' '{print $1}' | sort -n | tail -n 1)

# If LAST_NUMBER is empty, set it to 0
if [ -z "$LAST_NUMBER" ]; then
    LAST_NUMBER=0
fi

# Calculate the next mutation number
NEXT_NUMBER=$((LAST_NUMBER + 1))

# Add comments based on git diff
add_diff_block "$CONTRACT_FILENAME"

# Copy the mutated file
cp "$CONTRACT_FILENAME" "certora/mutations/${MUTATION_DIR_NAME}/${NEXT_NUMBER}.sol"

# Restore changes
git restore "$CONTRACT_FILENAME"
