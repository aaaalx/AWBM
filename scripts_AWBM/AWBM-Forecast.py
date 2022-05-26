# -*- coding: utf-8 -*-
"""
Created on Thu May 26 16:28:48 2022

@author: alex.xynias

Script which uses AWBM_function.py to perform batches of AWBM simulations
    - Exports raw results without processing or analysis 


wdir='//fs07.watech.local/redirected folders$/alex.xynias/My Documents/GitHub/AWBM/scripts_AWBM'

"""

# =============================================================================
#%% Setup and Directories
# =============================================================================
import os     
import time                                
# import numpy as np                             
import pandas as pd                           
# import datetime as dt
# import glob  

from AWBM_function import AWBM_function 

tic_script = time.time() #starts the run time timer

# dir_out = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\output_AWBM-Forecast"
dir_out = r"C:\Users\Alex\OneDrive\Documents\Uni\Honours Thesis\output_AWBM-Forecast"
    # Parent folder for result files to be written to

dir_batch_input = r"C:\Users\Alex\OneDrive\Documents\Uni\Honours Thesis\input_AWBM_forecast.csv"
# dir_batch_input = r"C:\Users\alex.xynias\OneDrive - Water Technology Pty Ltd\UQ\Thesis\input_AWBM_forecast.csv"
    # The directory of the batch input file joins with the subdir_data column to locate the data
    
dir_in_data = dir_batch_input[:-len(dir_batch_input.split("\\")[-1])]



# =============================================================================
#%% Read batch input and set parameters 
# =============================================================================
# AWBM Parameters (from calibration)
    # Calibration start,warmup,end:  1/Jan/1985,30/Jun/1985,30/Jun/2017
    # Verification start,warmup,end: 1/Jul/2017,1/Jul/2017,30/Dec/2020
    # Calibration skill scores for the Gregor's creek gauge
        # NSE: 0.836
        # R^2: 0.89
        # Absolute dif: 593.528mm
        # Rel. dif: 33.002%
A = 7015 # Catchment area in km^2 
    # 7015km^2 derived from shapefile of catchment upstream of the wivenhoe dam outlet.

A1 = 0.134 # as a proportion (e.g. 0.134)
A2 = 0.433 # Such that  A1+A2+A3 == 1.0
A3 = A2

C1 = float(30.4)
C2 = float(145.9)
C3 = float(474.7)

BFI = float(0.769)       # Base flow index [0-1]
    #QLD average =0.17 (Boughton, 2009)
Kbase = float(0.027)     # Baseflow recession constant [0-1]
    #QLD average =0.95 (Boughton, 2009)
Ksurf = float(0.965)     # Surface flow recession constant [0-1]
    #13.4/43.3/43.3 = Default (Barret et al., 2008)

# AWBM initial storage conditions
S1_0 = float(0)         # Initial storage capacity storage 1 [mm]
S2_0 = float(0)         # Initial storage capacity storage 2 [mm]
S3_0 = float(0)         # Initial storage capacity storage 3 [mm] 
BS_0 = float(0)         # Initial storage capacity baseflow store [mm]
SS_0 = float(0)         # Initial storage capacity surface flow store [mm]


# Read batch input file
df_batch_input = pd.read_csv(dir_batch_input,skiprows=0,parse_dates=["date_start","date_end"])

nSims = len(df_batch_input)


for i_sim in range(0,nSims): # for each row in the batch input...
    tic_sim = time.time() # starts timer for simulation runtime    
    print(f'sim#{i_sim+1}/{nSims}...')    
    
    ID_scenario = df_batch_input.iloc[i_sim]['scenario_id']
    subdir_data = df_batch_input.iloc[i_sim]['subdir_data']
    CN_P = df_batch_input.iloc[i_sim]['CN_P']
    CN_E = df_batch_input.iloc[i_sim]['CN_E']
    CN_time = df_batch_input.iloc[i_sim]['CN_time']
    date_start = df_batch_input.iloc[i_sim]['date_start']
    date_end = df_batch_input.iloc[i_sim]['date_end']
    
    # Use the above input to prepare data (df_data) for AWBM_function
    dir_data_in_full = os.path.join(dir_in_data,subdir_data)
    
    print(f'   Loading input data for {ID_scenario}...')
    df_data = pd.read_csv(dir_data_in_full, parse_dates=[CN_time],usecols=[CN_time,CN_P,CN_E])    
        # Also drops input columns which aren't [CN_time,CN_P,CN_E]
    
    print('      Done!')
    
    print(f'   Preparing input data for {ID_scenario}...')
    # Calculate net change in stores (P-E)
    df_data['dS'] = df_data[CN_P]-df_data[CN_E]
    
    # Trim data to date_start:date_end
    df_data = df_data.loc[(df_data[CN_time] >= date_start) & (df_data[CN_time] <= date_end)]
    nTS = len(df_data) # number of timesteps (days) to be simulated
    
    # Reset integer index after trim
    df_data.reset_index(inplace=True,drop=True)
      
    print('      Done!')
      
    print(f'   Initialising df_AWBM_results...')
    headers_AWBM_results = ['Date'
                       ,'P','E'
                      ,'dS'
                      ,'S1','S2','S3'
                      ,'S1_E', 'S2_E', 'S3_E', 'Total_Excess'
                      , 'BFR', 'SFR' #Base Flow Recharge, Surface Flow Recharge
                      , 'BS', 'SS' #Baseflow Store, Surface runoff routing Store
                      , 'Qbase', 'Qsurf', 'Qtotal', 'Q'
                      ]
    
    
    df_AWBM_results = pd.DataFrame([], columns = headers_AWBM_results)
    
    # Populate first TS's data
    data_day0 = [date_start
                 ,df_data.loc[0,CN_P]
                 ,df_data.loc[0,CN_E]
                 ,df_data.loc[0,'dS']
                 ,S1_0,S2_0,S3_0
                 ,float(),float(),float(),float() # Si_E & Total_Excess
                 ,float(),float() # BFR & SFR
                 ,BS_0, SS_0
                 ,float(),float(),float(),float() # Qbase, Qsurf, Qtotal, Q
                ]
    
    df_AWBM_results.loc[0] = data_day0
    print('      Done!')
# =============================================================================
#%% Run the AWBM function for this sim
# =============================================================================
    print(f'   AWBM started at {time.asctime(time.localtime())}...')
    tic_sim_AWBM = time.time()
    for i_day in range(0,nTS):
        AWBM_function(i_day,df_AWBM_results,df_data,C1,C2,C3,A1,A2,A3,BFI,BS_0,Kbase,SS_0,Ksurf,A,CN_P,CN_E)
    
    
        # TODO: fancy progress bar?
        if i_day % 10000 == 0: # If the timestep is divisible by 1000....
            toc_sim_AWBM = time.time() - tic_sim_AWBM
            print(f'      {i_day}/{nTS} reached in {round(toc_sim_AWBM)}s')
            
    toc_sim_AWBM = time.time() - tic_sim_AWBM
    toc_sim = time.time() - tic_sim
    print(f'      Finished at {time.asctime(time.localtime())}...')
    print(f'         {toc_sim_AWBM}seconds')
    
    
    
    
    
# =============================================================================
# %% Save df_AWBM_results to dir_out
# =============================================================================
    print(f'Saving {ID_scenario} results to file..')
    
    i_fn_out = os.path.join(dir_out,f'RAWresultsAWBM_{ID_scenario}.csv')
    
    df_AWBM_results.to_csv(i_fn_out,index=False)
    
    input(f'   Done in {toc_sim}')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    