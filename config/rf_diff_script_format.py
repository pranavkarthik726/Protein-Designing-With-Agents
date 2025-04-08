from pydantic import BaseModel, Field
from typing import Optional

class RFDiffusionScriptConfig(BaseModel):
    """
    Data model for configuring an RF Diffusion script for protein motif scaffolding.
    
    Attributes:
        output_prefix: The directory and filename prefix where design outputs will be saved.
        input_pdb: File path to the input PDB containing the protein complex structure.
        contigmap_contigs: A string defining the fixed/flexible design regions (contigs). 
                           For example, "[A25-109/0 0-70/B17-29/0-70]" or "[10-40/A163-181/10-40]".
        num_designs: Number of design variants to generate.
        contigmap_length: (Optional) Constraint for total design length (e.g., "70-120").
        contigmap_inpaint_seq: (Optional) Specifies residues within a contig to allow inpainting 
                               (i.e., to be redesigned), e.g., "[A163-168/A170-171/A179]".
        ckpt_override_path: (Optional) File path to a model checkpoint to override the default.
    """
    
    output_prefix: str = Field(
        ...,
        description="Output directory and file prefix for design results (e.g., 'example_outputs/design_motifscaffolding_with_target')."
    )
    input_pdb: str = Field(
        ...,
        description="provide only the ID of protein complex whose structure is to be used for design (e.g., '1YCR')."
    )
    contigmap_contigs: str = Field(
        ...,
        description="Defines the fixed and flexible regions for design, such as '[A25-109/0 0-70/B17-29/0-70]' for p53-Mdm2 or '[10-40/A163-181/10-40]' for RSV-F."
    )
    num_designs: int = Field(
        ...,
        description="Number of design variants to generate."
    )
    contigmap_length: Optional[str] = Field(
        None,
        description="Optional total length constraints for the design (e.g., '70-120')."
    )
    contigmap_inpaint_seq: Optional[str] = Field(
        None,
        description="Optional flag specifying which residues within a contig should be redesigned (inpainted), such as '[A163-168/A170-171/A179]'."
    )
    ckpt_override_path: Optional[str] = Field(
        None,
        description="Optional path to a model checkpoint to override the default (e.g., '../models/Complex_base_ckpt.pt')."
    )
    
    def get_script(self) -> str:
        """
        Constructs and returns the complete bash command string for the RF Diffusion inference.
        
        Returns:
            A string containing the command that runs the inference with the configuration parameters.
        """
        # Base command with essential parameters
        cmd_parts = [
            "../scripts/run_inference.py",
            f"inference.output_prefix={example_outputs/design_motifscaffolding_with_target}",
            f"inference.input_pdb={self.input_pdb}",
            f"'contigmap.contigs={self.contigmap_contigs}'",
            f"inference.num_designs={self.num_designs}",
        ]
        
        # Insert contigmap length if provided (positioned after input PDB)
        if self.contigmap_length:
            cmd_parts.insert(3, f"contigmap.length={self.contigmap_length}")
        
        # Append inpaint sequence if provided
        if self.contigmap_inpaint_seq:
            cmd_parts.append(f"'contigmap.inpaint_seq={self.contigmap_inpaint_seq}'")
        
        # Append checkpoint override if provided
        if self.ckpt_override_path:
            cmd_parts.append(f"inference.ckpt_override_path={self.ckpt_override_path}")
        
        # Combine all command parts into a single string
        return " ".join(cmd_parts)
    def get_script_with_dict(params: dict[str, Optional[str]],dir) -> str:
        """
        Constructs and returns the bash command string for the RF Diffusion inference
        using a dictionary of parameters.

        Args:
            params: A dictionary of RF diffusion parameters.

        Returns:
            A string containing the full command to run the RF Diffusion script.
        """
        cmd_parts = ["../scripts/run_inference.py "]

        # Required fields
        cmd_parts.append(f"inference.output_prefix={dir}/output")
        cmd_parts.append(f"inference.input_pdb=input_pdbs/{params['input_pdb']}")
        cmd_parts.append(f"'contigmap.contigs={params['contigmap_contigs']}'")
        cmd_parts.append(f"inference.num_designs={1}")

        # Optional fields
        if "contigmap_length" in params and params["contigmap_length"]:
            cmd_parts.insert(3, f"contigmap.length={params['contigmap_length']}")
        if "contigmap_inpaint_seq" in params and params["contigmap_inpaint_seq"]:
            cmd_parts.append(f"'contigmap.inpaint_seq={params['contigmap_inpaint_seq']}'")
        if "ckpt_override_path" in params and params["ckpt_override_path"]:
            cmd_parts.append(f"inference.ckpt_override_path={params['ckpt_override_path']}")

        return " ".join(cmd_parts)


