#!/bin/bash

# 1. Create mutations with Gambit. Start from git root directory. Example:
# rm -rf ./gambit_out && gambit mutate -f packages/contracts/contracts/SortedCdps.sol

# 2. Copy mutations from gambit directory to mutations directory. Start from git root directory. Example:
# ./certora/mutations/gambitToMutations.sh packages/contracts/contracts/SortedCdps.sol SortedCdps_gambit292

# 3. Prove all mutations with certoraMutate
# certoraMutate --prover_conf certora/confs/SortedCdps_verified.conf --mutation_conf certora/confs/gambit/SortedCdps_gambit292.conf 

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <target_sol_path> <bugs_directory_name>"
  exit 1
fi

sol_path="$1"
bugs="$2"

# Create the destination directory for the patch file
dest_dir="certora/mutations/${bugs}"
mkdir -p "${dest_dir}"

# Determine the maximum mutant number
max_num=$(ls ./gambit_out/mutants/ | sort -n | tail -1)

# Iterate over each directory number from 1 to max_num
for ((mutant_number=1; mutant_number<=max_num; mutant_number++)); do
    
  dir="./gambit_out/mutants/${mutant_number}/${sol_path}"
  cp "${dir}" "${dest_dir}/${mutant_number}.sol"

done