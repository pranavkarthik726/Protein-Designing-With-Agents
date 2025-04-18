import os
import json
from pydantic import BaseModel
from crewai.tools.structured_tool import CrewStructuredTool
from crewai import Agent, Task, Crew, LLM
import requests
import urllib.parse
from pydantic import BaseModel, Field
from typing import List, Literal
from pathlib import Path
from crewai.tools import tool
from rosseta.rosseta_run import PyRosettaWrapper
from storage_manager import StorageManager
from tools.uniprot_extended_tool import toolset
from tools.rossetta_tool import PyRosettaWrapper
from tools.rf_dif_tool import run_rf_diffusion
from config.rf_diff_script_format import RFDiffusionScriptConfig
def run_workflow(user_input: str):

    os.environ["GEMINI_API_KEY"] = "AIzaSyCwso6IHHj7BNIOOv1PbveHd5E8pjqqUoU"
    gemini_llm = LLM(
        model="gemini/gemini-2.0-flash",
        temperature=0.7,
    )

    rf_diff_context_path = r"config/RF_diff_context.txt"
    with open(rf_diff_context_path, 'r') as f:
        RF_Dif_manual = f.read()

    storage = StorageManager()
    current_path = os.path.join(os.getcwd(), str(storage.get_session_path()))
    print(current_path)

    crewtool = toolset(current_path)
    Rosettatool = PyRosettaWrapper(current_path)

    @tool("fetchUniProt")
    def fetchUniProt(query: str) -> str:
        """This tool provides an acces to fetch data from UniProtKB using the UniProt REST API.
        the input has to be strictly a string """
        return crewtool.uniprot_fetch_tool(query=query)

    @tool("getSiteInfo")
    def getSiteInfo(protein_id: str) -> str:
        """Fetches the protein site information from cache."""
        return crewtool.get_protein__site_info(protein_id=protein_id)

    @tool("getFuncInfo")
    def getFuncInfo(protein_id: str) -> str:
        """Fetches the protein function information from cache."""
        return crewtool.get_all_function()

    @tool("rfDiffTool")
    def rfDiffTool(script:dict,protein_id: str,) -> str:
        """This tool provides an access to fetch data from RF_diff
        the input has to be strictly a RFDiffusionScriptConfig first is the script and the second is the protein_id, the tool will automatically access the pdb file """
        print(RFDiffusionScriptConfig.get_script_with_dict(script,dir=current_path))
        return run_rf_diffusion(script_str=RFDiffusionScriptConfig.get_script_with_dict(script,dir=current_path), pdb_file_path= current_path+"/pdb/"+protein_id+".pdb")

    @tool("rossetaTool")
    def rossetaTool(pdb_id: str) -> str:
        """This tool provides an access to fetch data from Rosetta
        the input has to be strictly a string first is the script and the second is the protein_id, the tool will automatically access the pdb file """
        return Rosettatool.run(pdb_file=pdb_id)

    queryGen = Agent(
        role="queryGen",
        goal="Generates a UniProt query from a given protein function: {userinput}. Ensure the query retrieves relevant proteins",
        backstory="Designed as a highly specialized bioinformatics assistant to construct precise UniProt queries.",
        verbose=True,
        llm=gemini_llm,
    )

    queryValidator = Agent(
        role="queryValidator",
        goal="Ensures the generated UniProt query is accurate and relevant to the protein function: {userinput}. Verify that the query retrieves the correct proteins and aligns with the intended function."
            "RUN the uniprot_fetch_tool, if it doesn't work then the query is suboptimal, provide suggestions to improve it."
            "uniprot_fetch_tool only works with a parathesis query in string format"
            "Query rules:"
            "-the query has to be string with paranthesis and semicolon and characters no other special characters allowed"
            "-avoid metioning \"query\" as it is unnecessary",
        backstory="This agent acts as a quality control specialist for bioinformatics queries, ensuring that the query targets the right proteins.",
        tools=[fetchUniProt],
        verbose=True,
        llm=gemini_llm,
    )
    proteinPicker = Agent(
        role="Protein Selection Expert",
        goal="Select the best protein that matches the given function requirement from a provided list. Access the list of proteins from the tool.",
        backstory="You are an expert in protein biochemistry and bioinformatics, with a keen ability to match protein functions to desired roles.",
        verbose=True,
        llm=gemini_llm,
        tools=[getFuncInfo]
    )

    scaffoldPlanner = Agent(
        role="Protein Scaffolding Specialist",
        goal="Assist in creating protein scaffolds by identifying which motifs should be masked or preserved based on UniProt features.",
        backstory="Expert in computational protein design with experience in analyzing protein structural and functional data.",
        llm=gemini_llm,
        tools=[getSiteInfo],
        tools_verbose=True,
        verbose=True
    )
    rfDiffuser = Agent(
        role="RF Diffusion Expert",
        goal=("Translate the protein scaffolding requirements into specific RF Diffusion implementation strategies, "
            "specifying which motifs to mask versus preserve and providing technical details."),
        backstory="Expert in diffusion-based generative modeling for protein design. Manual context: {RF_Dif_manual}",
        llm=gemini_llm,
        verbose=True
    )
    rfDiffVerifier = Agent(
        role="RF Diffusion Script Verifier",
        goal=(
            "Verify the generated RF Diffusion configuration script for correctness, "
            "remove any unnecessary or redundant lines, ensure all parameters and file paths "
            "are valid, then execute the script via the RF Diffusion tool. STOP IMMEDIATELY AFTER PDB FILE GENERATION."
        ),
        backstory="Expert in RF Diffusion process scripts, code review, and pipeline execution. Manual context: {RF_Dif_manual}",
        llm=gemini_llm,
        tools=[rfDiffTool],
        verbose=True,
    )
    ConclusionAgent = Agent(
        role="Conclusion Agent",
        goal="Summarize the results of the workflow, including the generated PDB file and any relevant analysis.",
        backstory="This agent provides a concise summary of the workflow results, including the generated PDB file and any relevant analysis.",
        llm=gemini_llm,
        verbose=True,
    )

    generateQuery = Task(
        description=(
            "1. Extract key biological terms from the protein function description: {userinput}.\n"
            "2. Map these terms to UniProt search fields and controlled vocabularies.\n"
            "3. Generate a string within paranthesis UniProt query optimized for accuracy and recall.\n"
            "4. Validate and refine the query to ensure relevant search results."
        ),
        expected_output="UniProt query for the given protein function description",
        agent=queryGen,
    )

    validateQuery = Task(
        description="Review the UniProt query generated by the uniprot_query_generator agent.",
        expected_input="A UniProt query string generated from a protein function description, along with the original user input.",
        expected_output=(
                        "If the query is suboptimal, provide suggestions to improve it."
                        "After a successful query return the protein ID"),
        steps=[
            "Receive the generated UniProt query and the original protein function description.",
            "Submit the query to the UniProt database using uniprot_tool.",
            "Analyze the retrieved proteins and compare their functions to the intended protein function.",
            "resolve the query using the uniprot_fetch_tool unitil the problem is fixed",
            "Approve the query if it runs successfully and retrieves relevant proteins.",
        ],
        acceptance_criteria=[
            "The query retrieves proteins that strongly match the intended function.",
            "The query does not produce irrelevant or overly broad results.",
            "Suggestions for improvement are practical and enhance query precision.",
            "The validation report clearly explains the decision."
        ],
        agent=queryValidator,
    )
    pickProtein = Task(
        description="Choose the best protein from the provided list that performs the target function:{function}. try to choose only limited proteins",
        expected_output="A JSON object detailing the selected protein and its function.",
        agent=proteinPicker,
    )
    analyzeMotifs = Task(
        description=("Analyze the provided UniProt features in JSON format, identifying all functional sites (active sites, binding sites, metal-binding sites, etc.). "
                    "Interpret the user's desired protein function described in natural language and determine which motifs should be preserved as anchors and which regions masked for redesign. "
                    "Identify the most appropriate scaffolding approach and provide clear reasoning for your decisions, including motif positions. "
                    "unction to be preserved: {function}. use the protein id from previous task"),
        expected_output=("A detailed JSON report containing an analysis of UniProt features, the identified motifs to be preserved or masked with justification, "
                        "and the recommended scaffolding approach."),
        agent=scaffoldPlanner,
        context=[pickProtein]
        #context=[protein_analysis_task],
    )

    # Task for generating the RF Diffusion configuration script based on the protein analysis
    createDiffConfig = Task(
        description=("Using the analysis from the previous task, generate a configuration script for running the RF Diffusion process. "
                    "Include model settings, diffusion parameters, input file paths, output directory locations, and any optional parameters (such as contigmap)."),
        expected_output="A valid terminal script containing the RF Diffusion configuration with all necessary parameters."
        "You should make sure sure that the pdb file should be the uniprot ID which will be given from the previous task",
        agent=rfDiffuser,
        context=[analyzeMotifs],
        output_pydantic=RFDiffusionScriptConfig,
    )

    rfDiffVerification = Task(
        description=(
            "1) Take the output configuration script from the previous task.  "
            "2) Check syntax and parameter correctness, remove any unnecessary or redundant lines.  "
            "3) Run the cleaned script using rf_diffusion_tool.run(script_path).  "
            "4) IMMEDIATELY STOP PROCESSING ONCE PDB FILE IS GENERATED IN THE OUTPUT DIRECTORY."
            "5) Do NOT perform any additional verification steps beyond PDB file creation."
        ),
        expected_output=(
            "— A cleaned and validated RF Diffusion configuration script  \n"
            "— Confirmation of PDB file generation in the output directory"
        ),
        agent=rfDiffVerifier,
        context=[createDiffConfig],
        output_pydantic=RFDiffusionScriptConfig
    )
    ConclusionTask = Task(
        description="Summarize the results of the workflow, including the generated PDB file and any relevant analysis.",
        expected_output="A summary of the workflow results, including the generated PDB file and any relevant analysis.",
        agent=ConclusionAgent,
        context = [pickProtein,analyzeMotifs,rfDiffVerification],
    )

    combined_crew = Crew(
        agents=[queryGen, queryValidator, proteinPicker, scaffoldPlanner, rfDiffuser, rfDiffVerifier,ConclusionAgent],
        tasks=[generateQuery, validateQuery, pickProtein, analyzeMotifs, createDiffConfig, rfDiffVerification,ConclusionTask],
        verbose=True,
    )

    combined_inputs = {
        "userinput": user_input,
        "function": user_input,
        "RF_Dif_manual": RF_Dif_manual,
    }
    
    result = combined_crew.kickoff(inputs=combined_inputs)
    #print(result)
    

    ros_obj = PyRosettaWrapper(current_path)
    ros_obj.run(pdb_file="pdb/output_0.pdb")
    return {"result":result,"rosetta_output":ros_obj}