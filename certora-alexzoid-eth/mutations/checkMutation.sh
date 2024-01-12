#!/bin/bash

# Apply a mutation, run prover and restore original file
# Run from the root git directory. Run without mutation's number parameter to not apply any patches
#
# Examples:
# 
# Run ActivePool.conf:
#    ./certora/mutations/checkMutation.sh ActivePool
#
# Run ActivePool.conf for a `rule_name` rule:
#    ./certora/mutations/checkMutation.sh ActivePool --rule rule_name
#
# Prove ActivePool/15.sol patch for ActivePool.conf:
#    ./certora/mutations/checkMutation.sh ActivePool ./packages/contracts/contracts/ActivePool.sol 15
#
# Prove 15.sol patch for a `rule_name` rule:
#    ./certora/mutations/checkMutation.sh ActivePool ./packages/contracts/contracts/ActivePool.sol 15 --rule rule_name
#
# Prove ActivePool_gambit/3.sol patch for ActivePool.conf:
#    ./certora/mutations/checkMutation.sh ActivePool_gambit ./packages/contracts/contracts/ActivePool.sol 3
#

if [ "$#" -lt 1 ]; then
    echo "Please provide the configuration name as the first argument (e.g., 'ActivePool')."
    exit 1
fi

MUTATION_DIRECTORY_NAME="$1"
# If name contains several parts divided by `_`, use first part as a config name
CONFIG_NAME=$(echo "$MUTATION_DIRECTORY_NAME" | cut -d '_' -f 1)
shift

# Check if next argument not a mutation number or option
CONTRACT_PATH=""
if [[ -n "$1" && ! $1 =~ ^[0-9]+$ && ! $1 =~ ^-- ]]; then
    CONTRACT_PATH="$1"
    shift
fi

MSG="[run ${CONFIG_NAME}] $@"

# Check if the next argument is a mutation number
if [[ $1 =~ ^[0-9]+$ ]]; then
  FILE_NAME="$1.sol"
  shift 1 
  MSG="[prove ${MUTATION_DIRECTORY_NAME}/$FILE_NAME] $@"
fi

PATCH_PATH="./certora/mutations/${MUTATION_DIRECTORY_NAME}/${FILE_NAME}"
if [ -f "$PATCH_PATH" ]; then
  # If the patch file exists then apply and restore a mutation
  cp "$PATCH_PATH" "$CONTRACT_PATH"
  certoraRun certora/confs/${CONFIG_NAME}_verified.conf --msg "${MSG}" "$@"
  git restore "$CONTRACT_PATH"
else
  # Run without patching 
  certoraRun certora/confs/${CONFIG_NAME}_verified.conf --msg "${MSG}" "$@" 
fi