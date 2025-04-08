import streamlit as st
import stmol
from main import run_workflow

# Set page config
st.set_page_config(
    page_title="Protein Design AI Lab",
    page_icon="🧬",
    layout="wide"
)

# Custom CSS for better styling
def local_css():
    st.markdown("""
    <style>
        .metric-card {
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            background: #f0f2f6;
            margin: 10px 0;
        }
        .stAlert {width: 100% !important;}
        .stCodeBlock {padding: 1rem !important;}
    </style>
    """, unsafe_allow_html=True)

local_css()

# Main app
def main():
    st.title("🧬 AI-Driven Protein Design Workbench")
    st.markdown("""
    **Multi-Agent System for Protein Engineering**  
    Leverage AI agents for automated protein design powered by UniProt, RF Diffusion, and Rosetta.
    """)
    
    # User input section
    with st.expander("🧪 Start New Protein Design", expanded=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            protein_function = st.text_input(
                "Describe desired protein function:",
                placeholder="e.g., 'Thermostable DNA polymerase for PCR applications'"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            run_button = st.button("🚀 Run Design Workflow")

    if run_button and protein_function:
        with st.spinner("🔬 AI Agents are working... This might take a few minutes"):
            try:
                results = run_workflow(protein_function)
                st.success("✅ Workflow Completed Successfully!")
            except Exception as e:
                st.error(f"⚠️ Error in workflow execution: {str(e)}")
                st.stop()

        # Display Results
        with st.container():
            st.subheader("📋 Workflow Results")
            
            # Workflow output
            with st.expander("📜 Full Workflow Output", expanded=True):
                st.code(results["result"], language="text")

            # Rosetta Analysis
            st.subheader("📊 Stability Analysis (Rosetta)")
            rosetta_data = results["rosetta_output"]
            
            cols = st.columns(3)
            with cols[0]:
                st.markdown("<div class='metric-card'>"
                            "<h3>Initial Stability</h3>"
                            f"<h1>{rosetta_data[0]:.2f} kcal/mol</h1>"
                            "</div>", unsafe_allow_html=True)
            
            with cols[2]:
                st.markdown("<div class='metric-card'>"
                            "<h3>Relaxed Stability</h3>"
                            f"<h1>{rosetta_data[2]:.2f} kcal/mol</h1>"
                            "</div>", unsafe_allow_html=True)

            # 3D Structure Visualization
            st.subheader("🔬 Relaxed Pose Visualization")
            if rosetta_data[1]:
                try:
                    # Assuming rosetta_data[1] contains PDB content as string
                    render_pdb(rosetta_data[1])
                    st.markdown("**Visualization Controls:**\n"
                                "- Right-click to rotate\n"
                                "- Scroll to zoom\n"
                                "- Left-click to move")
                except Exception as e:
                    st.error(f"Error rendering structure: {str(e)}")
            else:
                st.warning("No structure data available")

            # Download Section
            st.subheader("💾 Download Results")
            if rosetta_data[1]:
                st.download_button(
                    label="📥 Download Relaxed PDB",
                    data=rosetta_data[1],
                    file_name="relaxed_structure.pdb",
                    mime="chemical/x-pdb"
                )

# PDB visualization using stmol
def render_pdb(pdb_str):
    view = stmol.render_pdb(pdb_str)
    stmol.showmol(view, height=500, width=800)

if __name__ == "__main__":
    main()