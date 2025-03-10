Using Contigs and Running RFdiffusion
Introduction to Contigs
In RFdiffusion, contigs are used to define the structure of proteins you want to generate or scaffold. They allow you to specify motifs from existing proteins and how these motifs should be connected by new sequences. Here's how you can use contigs:

Motif Specification: Use a letter prefix to indicate a motif from a specific chain in a PDB file. For example, A10-25 refers to residues 10 through 25 on chain A.

New Sequence Specification: Use a length range without a prefix to specify new sequences to be generated. For example, 5-15 means generate a sequence of length between 5 and 15 residues.

Chain Breaks: Use /0 to indicate a chain break. This is important for specifying separate chains in your output.

Running RFdiffusion with Contigs
To run RFdiffusion, you'll use the run_inference.py script. Here's a step-by-step guide:

Basic Script Usage
The basic command structure is as follows:

bash
./scripts/run_inference.py \
  'contigmap.contigs=[<contig_specifications>]' \
  inference.output_prefix=<output_folder> \
  inference.num_designs=<number_of_designs>
Example: Unconditional Monomer Generation
To generate a protein of length 150 residues without any motifs:

bash
./scripts/run_inference.py \
  'contigmap.contigs=[150-150]' \
  inference.output_prefix=test_outputs/test \
  inference.num_designs=10
Example: Motif Scaffolding
To scaffold a motif from residues 10-25 on chain A, with 5-15 residues before it and 30-40 residues after it:

bash
./scripts/run_inference.py \
  'contigmap.contigs=[5-15/A10-25/30-40]' \
  inference.input_pdb=path/to/your/pdb_file.pdb \
  inference.output_prefix=test_outputs/motif_scaffolding \
  inference.num_designs=10
Example: Chain Breaks
To scaffold two motifs from different chains with a chain break:

bash
./scripts/run_inference.py \
  'contigmap.contigs=[5-15/A10-25/30-40/0 B1-100]' \
  inference.input_pdb=path/to/your/pdb_file.pdb \
  inference.output_prefix=test_outputs/chain_break \
  inference.num_designs=10
Additional Options
Partial Diffusion: To diversify around an existing structure, use the diffuser.partial_T option. Ensure the contig length matches the input protein length.

bash
./scripts/run_inference.py \
  'contigmap.contigs=[100-100/0 B1-150]' \
  diffuser.partial_T=20 \
  inference.input_pdb=path/to/your/pdb_file.pdb \
  inference.output_prefix=test_outputs/partial_diffusion \
  inference.num_designs=10
Sequence Masking: Use contigmap.inpaint_seq to mask sequence identities and allow RFdiffusion to predict them.

bash
./scripts/run_inference.py \
  'contigmap.contigs=[5-15/A10-25/30-40]' \
  'contigmap.inpaint_seq=[A1/A30-40]' \
  inference.input_pdb=path/to/your/pdb_file.pdb \
  inference.output_prefix=test_outputs/inpaint_seq \
  inference.num_designs=10
