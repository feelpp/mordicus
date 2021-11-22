#!/bin/bash

# Testing substitution with parameters from input_mordicus_data
echo "Generating data from input_instruction_file\n"

# Testing substitution with parameters for the dataset
python $(dirname ${BASH_SOURCE[0]})/input_instruction_file_resolution.py

mv snapshot.npy $(dirname ${BASH_SOURCE[0]})/snapshot.npy
