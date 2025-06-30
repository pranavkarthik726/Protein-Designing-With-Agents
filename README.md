# Protein-Designing-With-Agents

## Description

A framework for protein design using agentic systems with RFDiffusion and web crawling technologies. This project provides an automated pipeline for designing novel proteins with specific binding functions.

## Overview

This project implements an agent-based system for protein design that combines:

- **Agentic Architecture**: Multiple specialized AI agents work together to handle different aspects of protein design
- **RFDiffusion**: Diffusion based protein scaffolding model to bind functional motiffs to proteins
- **Web Crawling**: Collection of relevant protein data and information from scientific databases

The system allows for the design of proteins with specific functions (like DNA binding) by searching, analyzing, and modifying existing protein structures.

## Features

- **Automated UniProt Query Generation**: Creates optimized queries to search for proteins with specific functions
- **Query Validation**: Verifies that search results match intended functionality
- **Protein Selection**: Intelligently selects the most suitable protein candidates 
- **Scaffolding Analysis**: Identifies functional motifs to preserve or modify
- **Diffusion-based Protein Generation**: Uses RF Diffusion to generate novel protein structures
- **PDB File Generation**: Creates standard Protein Data Bank files for the designed proteins

## Technology Stack

- **Python** and **Jupyter Notebooks** for implementation and experimentation
- **CrewAI** framework for managing multi-agent systems
- **UniProt API** for accessing protein databases
- **PyRosetta** for protein structure manipulation
- **RF Diffusion** for generative protein design
