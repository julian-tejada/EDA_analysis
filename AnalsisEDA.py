# -*- coding: utf-8 -*-
# This script was adapted from the tutorials of the neurokit project https://neurokit.readthedocs.io/
# Processes an AcqKnowledge format file from an EDA record in which there are two channels: EDA100C and 
# Digital input. The triggers were recorded on the digital input. 
# After the analysis, the frequency of peaks, amplitude and latency of each ER-SCR 
# that occurred in the interval of each trigger will be recorded on a csv file. 


__author__ = "Julian Tejada"



import neurokit2 as nk
import pandas as pd
import numpy as np
import math
import sys
# import seaborn as sns
import biosppy


###############################
# import data from acq
df, sampling_rate = nk.read_acqknowledge(str(sys.argv[1]))
# df, sampling_rate = nk.read_acqknowledge('Subject1.acq')

# first filter 
bio = biosppy.signals.eda.eda(df["EDA100C"],  show=False, min_amplitude=0.01)

# Create a ts vector with the time
length = len(df["EDA100C"])
T = (length - 1) / sampling_rate
ts = np.linspace(0, T, length, endpoint=False)
# Extract SCRs using Gamboa method
SCRs = biosppy.signals.eda.basic_scr(bio["filtered"], sampling_rate=2000)
#bio = biosppy.signals.eda.eda(df["EDA100C"], sampling_rate=2000)

#SCRs = biosppy.signals.eda.basic_scr(bio["filtered"], sampling_rate=2000)
#SCRs2 = biosppy.signals.eda.eda(bio["filtered"], sampling_rate=2000)
# Show onsets, peaks and amplitudes from Gamboa analysis

biosppy.plotting.plot_eda(ts=ts, raw=df["Digital input"], filtered=bio["filtered"], onsets=SCRs["onsets"], peaks=SCRs["peaks"], amplitudes=SCRs["amplitudes"], show=True)

boifiltered = pd.DataFrame(list(zip(bio['filtered'])), columns=['filtered'])
#
SCRs_df = pd.DataFrame(list(zip(*bio)),  columns=['ts','filtered','onsets','peaks','amplitudes'])
# convert SCRs tuple into pandas DataFrame
# SCRs_df = pd.DataFrame(list(zip(*SCRs)), columns=['onsets','peaks','amplitudes'])
SCRs_df["Artefacts"] = ""
# Detection of artefacts related with movement: signal jump, a threshold of 0.1 uS between signals 
for Detector in range(len(SCRs_df['onsets'])-2):
    if ((SCRs_df['amplitudes'][Detector+1]-SCRs_df['amplitudes'][Detector])>0.1):
        SCRs_df['Artefacts'][Detector+1] = 1
    else:
        SCRs_df['Artefacts'][Detector+1] = 0
# Detection of artefacts related with time: onset and offset greather than duration threshold (500 ms)
for Detector2 in range(len(SCRs_df['onsets'])-2):
    if ((ts[SCRs_df['peaks'][Detector2+1]]-ts[SCRs_df['onsets'][Detector2]])>500):
        SCRs_df['Artefacts'][Detector2+1] = 1
    else:
        SCRs_df['Artefacts'][Detector2+1] = 0

# Identification of onset and duration of the triggers
events = nk.events_find(df["Digital input"])
# Definition of the dataframe of the results
Results = pd.DataFrame(np.zeros(((len(events['onset'])), 5)), columns=['Trigger','peaks','amplitudes', 'latency', 'artefacts'])

for trialnr in range(len(events['onset'])):
    Temporal = SCRs_df[(SCRs_df['onsets']>(events['onset'][trialnr]-500)) & (SCRs_df['peaks']<(events['onset'][trialnr]+events['duration'][trialnr]+500))]
    Results['Trigger'][trialnr] =  trialnr
    Results['peaks'][trialnr] =  len(Temporal['peaks'])
    Results['amplitudes'][trialnr] =  Temporal['amplitudes'].max()
    #Results['amplitudes'][trialnr] =  Temporal['amplitudes'].mean()
    Results['artefacts'][trialnr] = Temporal['Artefacts'].max()
    if (math.isnan(Temporal['onsets'].min()) == False):
        Results['latency'][trialnr] =  ts[Temporal['onsets'].min()]-ts[events['onset'][trialnr]]

#saved_df=pd.DataFrame(Results)
#with open_file('yourcsv.csv','r') as infile:
#      saved_df.to_csv('yourcsv.csv',mode='a',header=False)
export_csv = Results.to_csv (r'export_dataframe_%s.csv' % str(sys.argv[1]), index = None, header=True) #Don't forget to add '.csv' at the end of the path

