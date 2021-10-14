#!/bin/bash

# Testing substitution with parameters from input_mordicus_data
echo "Generating data from ${mordicus_npy_data}\n"

# Testing substitution with parameters for the dataset
python "${mordicus_npy_data}"
