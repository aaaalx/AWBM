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
import os                                     
import numpy as np                             
import pandas as pd                           
#import matplotlib
# import matplotlib.pyplot as plt               
# import matplotlib.dates as mdates
# import matplotlib.font_manager as font_manager
from datetime import date             
#import matplotlib.font_manager          
#import openpyxl
# import hydroeval as he
    # https://pypi.org/project/hydroeval/
    # Hallouin, T. (XXXX). HydroEval: Streamflow Simulations Evaluator (Version X.X.X). Zenodo. https://doi.org/10.5281/zenodo.2591217
# from scripts_AWBM import AWBM_function
import time
import csv

tic_script = time.time() #starts the run time timer
# =============================================================================
#%% User Inputs
# =============================================================================
print('Loading user inputs...')
# File directories
infile_SILO = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO_Gregors_1985-2020-pd.csv' # Either a single csv, or folder, containing the gridded SILO data
    # Data source: SILO gridded data (.nc files processed with https://github.com/aaaalx/AWBM_data_processing)
    # has 1 header row
    # Date, P[mm], E[mm?] (need to check evap units again)
    # Date in the format 1985-01-01T00:00:00

# infile_gauge = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/AWBM/143009A BRISBANE RIVER AT GREGORS CREEK/143009A.csv' # csv containing observed streamflow data from gauge
    # 1/1/1985 is on (excel) row 8369, day 8369-4
    # 1/1/2021 is on (excel) row 21518, day 21518-4
infile_gauge = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/AWBM/143009A_20211216/143009A.csv'
    # Data source: https://water-monitoring.information.qld.gov.au/
        # Custom Outputs: all selected
        # Custom period: "00:00_01/01/1985" to "00:00_15/12/2021" at daily timesteps
        # Interactive tools / alternative source: http://www.bom.gov.au/waterdata/
    # Mean Discharge (ML/day) on (excel) col 16 (P)
    # Volume (ML) on (excel) col 22 (V)
    # has 4 header rows
    # Date in the format 30/1/1985 0:00

    # Data quality data always on col+1
        # 1 - Good (actual)
        # 9 - CITEC - Normal Reading
        # 10 - Good
        # 20 - Fair
        # 30 - Poor
        # 59 - CITEC - Derived Height
        # 60 - Estimate
        # 69 - CITEC - Derived Discharge
        # 83 - Non standard rainfall
        # 130 - Not coded value
        # 150 - Unknown
        # 151 - Data not yet available
        # 160 - Suspect
        # 200 - Water level below threshold
        # 255 - No data exists
    # Mean Discharge (Cumecs) on (excel) col 8 (H)
    # Discharge (ML/day) on (excel) col 
    # 1/1/1985 is on (excel) row 8369, day 8369-4
    # 1/1/2021 is on (excel) row 21518, day 21518-4

# Folder dirs, must end with "/"
dir_plots = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/AWBM/Outputs/Plots/' # Directory where plots are saved
dir_log = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/AWBM/Outputs/' # Directory of log file
dir_results = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/AWBM/Outputs/Results/' # Directory to write results to

# Dates (try to match (or convert to?) the date formats from .nc files)

    # Calibration period: Make sure the range selected matches with initial storage assumptions

date_start_cal = date(1985,1,1) 
date_end_cal = date(1985,1,5) 

    # Testing period
date_start_test = date(1985,1,1) 
date_end_test = date(2020,12,31)

###########
# Constants: Model params which aren't going to change between simulations
A = 3868.966716 # Catchment area in km^2
    #3868.96623 km^2 (3868966234.0000 m^2) from 'Catchment_combined_gregors' shapefile
    #7020 km^2 from: https://www.seqwater.com.au/dams/wivenhoe
    #5360 km^2 from: https://www.researchgate.net/publication/242172986_Maximising_Water_Storage_in_South_East_Queensland_Reservoirs_Evaluating_the_Impact_of_Runoff_Interception_by_Farm_Dams

S1_0 = float(0)         # Initial storage capacity storage 1 [mm]
S2_0 = float(0)         # Initial storage capacity storage 2 [mm]
S3_0 = float(0)         # Initial storage capacity storage 3 [mm]wivenhoe 
BS_0 = float(0)         # Initial storage capacity baseflow store [mm]
SS_0 = float(0)         # Initial storage capacity surface flow store [mm]

BFI = float(0.35)       # Base flow index [0-1]
    #QLD average =0.17 (Boughton, 2009)
Kbase = float(0.95)     # Baseflow recession constant [0-1]
    #QLD average =0.95 (Boughton, 2009)
Ksurf = float(0.35)     # Surface flow recession constant [0-1]
    #13.4/43.3/43.3 = Default (Barret et al., 2008)
    
# C_i parameter ranges [min,(max+1)]
bounds_C1 = range(0,81)
bounds_C2 = range(50,401)
bounds_C3 = range(100,401)

# A_i scenarios [A_1_i,A_2_i,A_3_i]
# e.g. Calling A_1_i2 with bounds_A[0][1]
bounds_A = ([0.134,0.433,0.433]
            ,[0.134,0.433,0.433]
            ,[0.134,0.433,0.433]
            ,[0.134,0.433,0.433]
            )



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
        
with open(dir_log + 'setup_log.csv', 'a') as log: 
    log.write('[Date],[km^2],[mm],[mm],[mm],[mm],[mm],[-],[-],[-],[%],[mm],[mm],[mm] \n')
    log.write('Start_time,A,S1_0,S2_0,S3_0,BS_0,SS_0,BFI,Kbase,Ksurf,A_i,C1,C2,C3 \n')
    log.write(f'{time.ctime()},{A},{S1_0},{S2_0},{S3_0},{BS_0},{SS_0},{BFI},{Kbase},{Ksurf},"{bounds_A}","{bounds_C1[0]}-{bounds_C1[-1]}","{bounds_C2[0]}-{bounds_C2[-1]}","{bounds_C3[0]}-{bounds_C3[-1]}" \n')
    log.write('================ \n')
print(f'Finished log saved to: {dir_log}')

# =============================================================================
#%% Load Input Data & Establish Variables
# =============================================================================
print('Loading input data...')

#%% Loading df_SILO_data
#Pandas.read_csv() (no chunks)
tic = time.time()
df_SILO_data_in = pd.read_csv(infile_SILO)
toc_pd = time.time() - tic

#daskDF.read_csv() (use if running out of mem)
# import dask.dataframe as daskDF # https://docs.dask.org/en/stable/dataframe.html
# tic = time.time()
# df_SILO_data_in = daskDF.read_csv(infile_SILO)
# toc_dask = time.time() - tic


# TODO: find the best way to index and crop df_SILO_data_in based on some 
# kind of user input that doesn't rely on row numbers
 
row_start_cal = []
row_end_cal = []


df_SILO_data_cal = df_SILO_data_in[row_start_cal:row_end_cal]
del df_SILO_data_in # might not need to delete if I use it again to pull data for testing period

print(f'Input data cropped to calibration period {date_start_cal}:{date_end_cal}')


print(f'Loaded SILO data from: {infile_SILO}')

print(f'Loaded Gauge data from: {infile_gauge}')




# =============================================================================
#%% Simulation Loop, Save Data
# =============================================================================


# # Initialise and clear variables from previous simulations
# dims = np.shape(Date)
# dS = []
# S1 = []; S2 = []; S3 = []
# S1_Excess =[]; S2_Excess =[]; S3_Excess =[]
# Total_Excess = []
# BaseFlowRecharge = []
# SurfaceFlowRecharge = []
# BS = []
# SS = []
# Qbase = []
# Qsurf = []
# Qtotal = []
# Q = []

# # Apply the AWBM
# tic_AWBM = time.time()

# AWBM_function(sim_number,Date,P,E,A,A1,A2,A3,C1,C2,C3,BFI,Kbase,Ksurf,S1_0,S2_0,S3_0,BS_0,SS_0)

# toc_AWBM = tic_AWBM - time.time() # Measures sim duration (seconds)

# print(f'Simulation {sim} of {nSims} complete...')

# # Save simulation data to named file
#     # TODO: See if globbing from prev scripts may be useful here?

# print(f'Simulation {sim} data saved to file...')
    

    
    
    
