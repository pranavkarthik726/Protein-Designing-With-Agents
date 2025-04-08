#!/bin/bash

# RFDiffusion script for protein design

# Required parameters:
# --pdb: Input PDB file (UniProt ID)
# --output_dir: Output directory for results
# --contigmap: Defines the connectivity and length of the designed protein.

# Task-specific settings based on the analysis:
# - Preserve DNA-binding domain (residues 1-231).
# - Replace disordered regions (363-434, 469-506) and compositional bias regions (377-388, 389-401, 402-417) with a scaffold.
# - Design a contigmap to connect the DNA-binding domain and the scaffold, and fill the gaps.
# - Using "mask" to exclude the disordered regions and compositional bias regions.

# Define variables
PROTEIN_ID="Q86WS4"
OUTPUT_DIR="./output"

# Construct the contigmap string. Since we are replacing multiple regions, we will design a contigmap with fixed regions and variable loops.
# Example: 1-231,X[scaffold_length],363-434,X[loop_length],469-506
# For simplicity, let's assume a contigmap that keeps 1-231 fixed and designs the rest. A more refined approach would be to divide the remaining sequence into smaller chunks, separated by "X".
# Since the exact length of scaffold is unknown at this stage, we can use a flexible length by defining it as "X[min-max]", e.g., X[50-100].
# Here, a simplified contigmap is used. In reality, it would be necessary to determine more appropriate ranges for the 'X' spans or divide these up into smaller chunks.

CONTIGMAP="1-231,X[50-150]" # Keep DNA binding domain (1-231) and design the rest.

# Construct the command
COMMAND="python ./run_rf_diffusion.py --pdb $PROTEIN_ID --output_dir $OUTPUT_DIR --contigmap $CONTIGMAP"

# Add masking. Create a mask string based on the disordered and compositional bias regions. RFDiffusion uses a comma-separated list of ranges for masking.
MASK_RANGES="363-434,469-506,377-388,389-401,402-417"
COMMAND="$COMMAND --mask $MASK_RANGES"

# Add other optional parameters (example)
#COMMAND="$COMMAND --num_designs 10" # Generate 10 designs
#COMMAND="$COMMAND --design_cycles 50" # Number of design cycles

# Print the command (optional)
echo "Running RFDiffusion with the following command:"
echo $COMMAND

# Execute the command
eval $COMMAND