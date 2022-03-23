#!/bin/bash

# Testing substitution with parameters from input_mordicus_data
echo "Generating data from inputInstructionFile\n"

# Testing substitution with parameters for the dataset
python $(dirname ${BASH_SOURCE[0]})/inputInstructionFile

mv snapshot.npy $(dirname ${BASH_SOURCE[0]})/snapshot.npy
