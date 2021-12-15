# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 09:51:39 2021

@author: Alex.Xynias

Automatically solve AWBM parameters given calibration data, and specified
testing period

"""

# =============================================================================
# Setup
# =============================================================================
# conda install -c anaconda git
#import os                                     
import numpy as np                             
# import pandas as pd                           
#import matplotlib
# import matplotlib.pyplot as plt               
# import matplotlib.dates as mdates
# import matplotlib.font_manager as font_manager
# import datetime                          
#import matplotlib.font_manager          
# import csv
#import openpyxl
# import hydroeval as he
    # https://pypi.org/project/hydroeval/
    # Hallouin, T. (XXXX). HydroEval: Streamflow Simulations Evaluator (Version X.X.X). Zenodo. https://doi.org/10.5281/zenodo.2591217
from scripts_AWBM import AWBM_function
import time

tic_script = time.time() #starts the run time timer
# =============================================================================
#%% User Inputs
# =============================================================================

# File directories
infile_SILO = '' # Either a single csv, or folder, containing the gridded SILO data
    # If folder, use the pattern+globbing method to sort through
infile_gauge = '' # csv containing observed streamflow data from gauge
infile_QGIS = '' # csv containing data on each grid's

dir_plots = '' # Directory where plots are saved
dir_log = '' # Directory of log file
dir_results = '' # Directory to write results to

# Dates (try to match (or convert to?) the date formats from .nc files)
    # Calibration period: Make sure the range selected works with initial storage assumptions
date_start_cal = ''
date_end_cal = ''

    # Testing period
date_start_test = ''
date_end_test = ''



# Constants: Model params which aren't going to change between simulations
A = 3868.966 # Catchment area in km^2
    #3868.96623 km^2 (3868966234.0000 m^2) from 'Catchment_combined_gregors' shapefile
    #7020 km^2 from: https://www.seqwater.com.au/dams/wivenhoe
    #5360 km^2 from: https://www.researchgate.net/publication/242172986_Maximising_Water_Storage_in_South_East_Queensland_Reservoirs_Evaluating_the_Impact_of_Runoff_Interception_by_Farm_Dams

S1_0 = float(0)         # Initial storage capacity storage 1 [mm]
S2_0 = float(0)         # Initial storage capacity storage 2 [mm]
S3_0 = float(0)         # Initial storage capacity storage 3 [mm]wivenhoe 
BS_0 = float(0)         # Initial storage capacity baseflow store [mm]
SS_0 = float(0)         # Initial storage capacity surface flow store [mm]

Ksurf = float(0.35)     # Surface flow recession constant [0-1]
BFI = float(0.35)       # Base flow index [0-1]
    #QLD average =0.17 (Boughton, 2009)
Kbase = float(0.95)     # Baseflow recession constant [0-1]
    #QLD average =0.95 (Boughton, 2009)
Ksurf = float(0.35)     # Surface flow recession constant [0-1]
    #13.4/43.3/43.3 = Default (Barret et al., 2008)


# TODO: Copy log file set up from the TERN_download script
    # Include col:
        # Time of simulation
        # "sim X of nSim"
        # Start/End of calibration period
        # R^2
        # NSE
        # Any other skill score
        # C_i and A_i
        # Initial values
        # All other model parameters



print(f'Log set up in: {dir_log}')

# =============================================================================
#%% Load Input Data & Establish Variables
# =============================================================================
print('Loading input data...')

Date_in = []
Day_in = []
P_in = []
# Add another variable for streamflow (from SS dam)?
E_in = []

# TODO: Review the most efficient methods for loading & processing the input arrays?
    # csv vs pandas vs numpy




print(f'Input data cropped to {date_start_cal},{date_end_cal}')

print(f'Loaded SILO data from: {infile_SILO}')

print(f'Loaded Gauge data from: {infile_gauge}')





# =============================================================================
#%% Simulation Loop, Save Data
# =============================================================================


# Initialise and clear variables from previous simulations
dims = np.shape(Date)
dS = []
S1 = []; S2 = []; S3 = []
S1_Excess =[]; S2_Excess =[]; S3_Excess =[]
Total_Excess = []
BaseFlowRecharge = []
SurfaceFlowRecharge = []
BS = []
SS = []
Qbase = []
Qsurf = []
Qtotal = []
Q = []

# Apply the AWBM
tic_AWBM = time.time()

AWBM_function(sim_number,Date,P,E,A,A1,A2,A3,C1,C2,C3,BFI,Kbase,Ksurf,S1_0,S2_0,S3_0,BS_0,SS_0)

toc_AWBM = tic_AWBM - time.time() # Measures sim duration (seconds)

print(f'Simulation {sim} of {nSims} complete...')

# Save simulation data to named file
    # TODO: See if globbing from prev scripts may be useful here?

print(f'Simulation {sim} data saved to file...')
    

    
    
    
