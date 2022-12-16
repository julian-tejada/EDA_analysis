# EDA_analysis
Script to process EDA records from AcqKnowledge+Biopack system using Neurokit2+Biosppy

This script was adapted from the tutorials of the neurokit project https://neurokit.readthedocs.io/
Processes an AcqKnowledge format file from an EDA record in which there are two channels: EDA100C and 
Digital input. The triggers were recorded on the digital input. 
After the analysis, the frequency of peaks, amplitude and latency of each ER-SCR 
that occurred in the interval of each trigger will be recorded on a csv file. 

