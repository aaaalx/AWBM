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
# from datetime import date       
import datetime      
#import matplotlib.font_manager          
#import openpyxl
import hydroeval as he
    # https://pypi.org/project/hydroeval/
    # Hallouin, T. (XXXX). HydroEval: Streamflow Simulations Evaluator (Version X.X.X). Zenodo. https://doi.org/10.5281/zenodo.2591217
# from scripts_AWBM import AWBM_function
import time
from alive_progress import alive_it


# from AWBM_function import AWBM_function





tic_script = time.time() #starts the run time timer
# =============================================================================
#%% User Inputs
# =============================================================================
print('Loading user inputs...')
# File directories
# infile_SILO = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO_Gregors_1985-2020-pd.csv' # Either a single csv, or folder, containing the gridded SILO data
infile_SILO = "D:/OneDrive/Documents/Uni/Honours Thesis/Data/SILO_downloads/Compile/SILO_Gregors_1985-2020-pd.csv" 
    # Data source: SILO gridded data (.nc files processed with https://github.com/aaaalx/AWBM_data_processing)
    # has 1 header row
    # Date, P[mm], E[mm?] (need to check evap units again)
    # Date in the format 1985-01-01T00:00:00

# infile_gauge = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/AWBM/143009A BRISBANE RIVER AT GREGORS CREEK/143009A.csv' # csv containing observed streamflow data from gauge
    # 1/1/1985 is on (excel) row 8369, day 8369-4
    # 1/1/2021 is on (excel) row 21518, day 21518-4
# infile_gauge = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/Data/AWBM/143009A_20211216/143009A.csv'
infile_gauge = 'D:/OneDrive/Documents/Uni/Honours Thesis/Data/AWBM/143009A_20211216/143009A.csv'

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
# dir_plots = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/AWBM/Outputs/Plots/' # Directory where plots are saved
# dir_log = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/AWBM/Outputs/' # Directory of log file
# dir_results = 'C:/Users/Alex/OneDrive/Documents/Uni/Honours Thesis/AWBM/Outputs/Results/' # Directory to write results to

dir_plots = 'D:/OneDrive/Documents/Uni/Honours Thesis/AWBM/Outputs/Plots/' # Directory where plots are saved
dir_log = 'D:/OneDrive/Documents/Uni/Honours Thesis/AWBM/Outputs/' # Directory of log file
dir_results = 'D:/OneDrive/Documents/Uni/Honours Thesis/AWBM/Outputs/Results/' # Directory to write results to

# Dates (try to match (or convert to?) the date formats from .nc files)

    # Calibration period: Make sure the range selected matches with initial storage assumptions

date_start_cal = datetime.datetime(1985,1,1) 
date_end_cal = datetime.datetime(1985,3,1) 

    # Testing period
date_start_test = datetime.datetime(1985,1,1) 
date_end_test = datetime.datetime(2020,12,31)

###########

    
# C_i parameter ranges [min,(max+1)] (from ewater AWBM wiki)
bounds_C1 = range(0,51) # 7 -> 50
bounds_C2 = range(70,201) # 70 -> 200
bounds_C3 = range(150,501) # 150 -> 500
bounds_Cavg = range(70,75) # 70 -> 130
# for using the Average capacity calibration from (B,2004)
C1_Favg = float(0.075)
C2_Favg = float(0.762)
C3_Favg = float(1.524)

# A_i scenarios [A_1_i,A_2_i,A_3_i]
# e.g. Calling A_1_i2 with bounds_A[0][1]
bounds_A = ([0.134,0.433,0.433] #i1
            # ,[0.134,0.433,0.433] #i2
            # ,[0.134,0.433,0.433] #i3
            # ,[0.134,0.433,0.433] #i4
            # ,[0.134,0.433,0.433] #i5
            )

# Constants: Model params which aren't going to change between simulations
A = 3868.966716 # Catchment area in km^2
    #3868.96623 km^2 (3868966234.0000 m^2) from 'Catchment_combined_gregors' shapefile
    #7020 km^2 from: https://www.seqwater.com.au/dams/wivenhoe
    #5360 km^2 from: https://www.researchgate.net/publication/242172986_Maximising_Water_Storage_in_South_East_Queensland_Reservoirs_Evaluating_the_Impact_of_Runoff_Interception_by_Farm_Dams

S1_0 = float(0)         # Initial storage capacity storage 1 [mm]
S2_0 = float(0)         # Initial storage capacity storage 2 [mm]
S3_0 = float(0)         # Initial storage capacity storage 3 [mm] 
BS_0 = float(0)         # Initial storage capacity baseflow store [mm]
SS_0 = float(0)         # Initial storage capacity surface flow store [mm]

BFI = float(0.35)       # Base flow index [0-1]
    #QLD average =0.17 (Boughton, 2009)
Kbase = float(0.95)     # Baseflow recession constant [0-1]
    #QLD average =0.95 (Boughton, 2009)
Ksurf = float(0.35)     # Surface flow recession constant [0-1]
    #13.4/43.3/43.3 = Default (Barret et al., 2008)


time_scriptstart = time.ctime()
        
with open(dir_log + 'setup_log.csv', 'a') as log: 
    log.write('[Date],[km^2],[mm],[mm],[mm],[mm],[mm],[-],[-],[-],[%],[mm],[mm],[mm],[mm] \n')
    log.write('Start_time,A,S1_0,S2_0,S3_0,BS_0,SS_0,BFI,Kbase,Ksurf,A_i,C1,C2,C3,Cavg \n')
    log.write(f'{time_scriptstart},{A},{S1_0},{S2_0},{S3_0},{BS_0},{SS_0},{BFI},{Kbase},{Ksurf},"{bounds_A}","{bounds_C1[0]}-{bounds_C1[-1]}","{bounds_C2[0]}-{bounds_C2[-1]}","{bounds_C3[0]}-{bounds_C3[-1]}","{bounds_Cavg[0]}-{bounds_Cavg[-1]}" \n')
    log.write('================ \n')
print(f'Finished log saved to: {dir_log}')

# =============================================================================
#%% Load Input Data & Establish Variables
# =============================================================================
print('Loading input data...')

# Loading df_SILO_data
#Pandas.read_csv() (no chunks)
tic = time.time()
df_SILO_data_in = pd.read_csv(infile_SILO)
df_SILO_data_in['Date'] = df_SILO_data_in['Date'].apply(pd.to_datetime) #convert Date column to datetime format(https://stackoverflow.com/questions/13654699/reindexing-pandas-timeseries-from-object-dtype-to-datetime-dtype)
df_SILO_data_in = df_SILO_data_in.set_index('Date') # sets the date column as the index
df_SILO_data_in['dS'] = df_SILO_data_in['P[mm]'] - df_SILO_data_in['E[mm?]']
toc = time.time() - tic
print(f'Loaded SILO data from: {infile_SILO}')

# Loading df_Gauge_data
tic = time.time()
df_Gauge_data_in = pd.read_csv(infile_gauge)
    # 3 rows of header to skip
    # 'Time', '143009A.10' (discharge total ML/day)
    
col_keep = ['Time','143009A.10','Unnamed: 20'] 
df_Gauge_data = df_Gauge_data_in[col_keep]

df_Gauge_data.columns = df_Gauge_data.iloc[1] # Renames the df headers
df_Gauge_data = df_Gauge_data.iloc[3:-3] # removes first and last 3 rows (header info etc)
df_Gauge_data['Date'] = pd.to_datetime(df_Gauge_data['Date'], dayfirst=True)    
df_Gauge_data = df_Gauge_data.set_index('Date') # sets the date column as the index
df_Gauge_data = df_Gauge_data.rename(columns = {np.nan: "Quality"}) # update the label for the quality column
df_Gauge_data['Volume ML'] = df_Gauge_data['Volume ML'].astype(float)
df_Gauge_data['Volume m^3'] = df_Gauge_data['Volume ML'].apply(lambda x: x*1000) # Volume ML to Volume M^3 # https://towardsdatascience.com/apply-and-lambda-usage-in-pandas-b13a1ea037f7
del col_keep
toc = time.time() - tic
print(f'Loaded Gauge data from: {infile_gauge}')


tic = time.time()
df_SILO_data_cal = df_SILO_data_in[date_start_cal:date_end_cal]
df_Gauge_data_cal = df_Gauge_data[date_start_cal:date_end_cal]
toc = time.time() - tic
print(f'Input data cropped to calibration period {str(date_start_cal)[:-9]}:{str(date_end_cal)[:-9]}')

# remove the input datasets from memory
# del df_SILO_data_in
# del df_Gauge_data_in, df_Gauge_data
# =============================================================================
#%% Running AWBM + Skill Scores + Saving  
# =============================================================================
print(' ')
print(' Running the AWBM ...')

# Initialise variables
dS = df_SILO_data_cal['dS']
dS = dS.reset_index()
days = np.shape(df_SILO_data_cal)[0] # number of days in cal period


# Set up results DF
df_run_headers = ['Date'
                  , 'dS'
                  ,'S1','S2','S3'
                  ,'S1_E', 'S2_E', 'S3_E', 'Total_Excess'
                  , 'BFR', 'SFR' #Base Flow Recharge, Surface Flow Recharge
                  , 'BS', 'SS' #Baseflow Store, Surface runoff routing Store
                  , 'Qbase', 'Qsurf', 'Qtotal', 'Q'
                  ]


    
# TODO: Remove the \n and set up the log file to be able to write the skill
#       Scores to the end of each sim so that it's all in the one location.
with open(dir_log + 'sim_log.csv', 'a') as log: 
    log.write('[Date],[km^2],[mm],[mm],[mm],[mm],[mm],[-],[-],[-],[%],[mm],[mm],[mm],[mm] \n')
    log.write('Start_time,A,S1_0,S2_0,S3_0,BS_0,SS_0,BFI,Kbase,Ksurf,A_i,C1,C2,C3,Cavg \n')

total_sims = (len(bounds_Cavg)-1)*(days) # Calculates the total # of days to be simulated



#%% Simulation Loop
# for Cavg_i in alive_it(bounds_Cavg): #alive_it() for total progress bar
for Cavg_i in bounds_Cavg:
    # update variables for sim run
    # TODO: round C values to x decimal places?
    C1 = Cavg_i * C1_Favg
    C2 = Cavg_i * C2_Favg
    C3 = Cavg_i * C3_Favg
    A1 = bounds_A[0]
    A2 = bounds_A[1]
    A3 = bounds_A[2]    

    
    with open(dir_log + 'sim_log.csv', 'a') as log: 
        log.write(f'{time_scriptstart},{A},{S1_0},{S2_0},{S3_0},{BS_0},{SS_0},{BFI},{Kbase},{Ksurf},"{bounds_A}",{C1},{C2},{C3},{Cavg_i} \n')
            
    # reset the data between sims & set formatting    
    day0_data = [date_start_cal
               , dS['dS'][0] # dS
               , S1_0, S2_0,S3_0
               ,float(),float(),float(),float() # Si_E & Total_Excess
               ,float(),float() # BFR & SFR
               , BS_0, SS_0
               , float(),float(),float(),float() # Qbase, Qsurf, Qtotal, Q
               ]
    
    df = pd.DataFrame([], columns = df_run_headers) # creates the df
    df.loc[0] = day0_data # sets the first day's data
    # gives df the full dS from the SILO data
    df = df.append(dS[1:])
    df = df.reset_index()
    df = df.rename(columns= {'index': 'Day'}) # sets the day index with the right formatting
    
    
    
    for i_day in range(0,days): # loops through each day in a simulation
        if i_day == 0: # set up condition for first timestep
            print(f'Setting up first timestep... {C1},{C2},{C3}')
            
            #df.loc[row,col]
            # df.loc[i_day, ]
            
            # Calculating storage levels and overflows 
            S1_t = max(df.loc[i_day,'S1']+df.loc[i_day,'dS'],0) # calculates Soil store + (P-E) > 0 
            df.loc[i_day,'S1_E'] = max(S1_t - C1,0) # calculates the excess
            df.loc[i_day, 'S1'] = min(S1_t,C1) # writes the new storage to df
            
            S2_t = max(df.loc[i_day,'S2']+df.loc[i_day,'dS'],0) 
            df.loc[i_day,'S2_E'] = max(S2_t - C1,0) 
            df.loc[i_day, 'S2'] = min(S2_t,C1) 
            
            S3_t = max(df.loc[i_day,'S3']+df.loc[i_day,'dS'],0) 
            df.loc[i_day,'S3_E'] = max(S3_t - C1,0) 
            df.loc[i_day, 'S3'] = min(S3_t,C1) 
            
            df.loc[i_day,'Total_Excess'] =( # Calculates sum of A_i*S_i_E 
                A1*df.loc[i_day,'S1_E'] +
                A2*df.loc[i_day,'S2_E'] +
                A3*df.loc[i_day,'S3_E'] )
            
            df.loc[i_day,'BFR'] = df.loc[i_day,'Total_Excess'] * BFI # calc base flow recharge
            df.loc[i_day,'SFR'] = df.loc[i_day,'Total_Excess'] * (1-BFI)# calc surface flow recharge
  
            BS_t = df.loc[i_day,'BFR'] + BS_0 # calc new Baseflow storage level
            df.loc[i_day,'Qbase'] = (1-Kbase)*BS_t
            df.loc[i_day,'BS'] = max(BS_t - df.loc[i_day,'Qbase'],0) # calc baseflow
            
            SS_t = df.loc[i_day,'SFR'] + SS_0 # calc new Baseflow storage level
            df.loc[i_day,'Qsurf'] = (1-Kbase)*BS_t
            df.loc[i_day,'SS'] = max(SS_t - df.loc[i_day,'Qsurf'],0) # calc baseflow   
       
            df.loc[i_day,'Qtotal'] = df.loc[i_day,'Qsurf'] + df.loc[i_day,'Qsurf'] # calc total outflow in [mm]/[catchment size]
            # calc total outflow in m^3 per timestep (i.e. day)
            df.loc[i_day,'Q'] = (df.loc[i_day,'Qtotal']*1e-3) * (A*1e6) # calc total m^3 outflow for the timestep
                # 1e6 to convert catchment size from km^2 to m^2
                # 1e-3 to convert Qtotal from mm to m             
            
            print(f"...Done day0 Q = {df.loc[i_day,'Q']} [m^3]")
            
            
            
        else: # for all subsequent timesteps
            # first, update the day column in df                             
            df.loc[i_day,'dS'] = df_SILO_data_cal['dS'][i_day] # gets dS from silo calibration df
                        
            
            # Calculating storage levels and overflows 
            S1_t = max(df.loc[i_day-1,'S1']+df.loc[i_day,'dS'],0) # calculates Soil store + (P-E) > 0 
            df.loc[i_day,'S1_E'] = max(S1_t - C1,0) # calculates the excess
            df.loc[i_day, 'S1'] = min(S1_t,C1) # writes the new storage to df
            
            S2_t = max(df.loc[i_day-1,'S2']+df.loc[i_day,'dS'],0) 
            df.loc[i_day,'S2_E'] = max(S2_t - C1,0) 
            df.loc[i_day, 'S2'] = min(S2_t,C1) 
            
            S3_t = max(df.loc[i_day-1,'S3']+df.loc[i_day,'dS'],0) 
            df.loc[i_day,'S3_E'] = max(S3_t - C1,0) 
            df.loc[i_day, 'S3'] = min(S3_t,C1) 
            
            df.loc[i_day,'Total_Excess'] =( # Calculates sum of A_i*S_i_E 
                A1*df.loc[i_day,'S1_E'] +
                A2*df.loc[i_day,'S2_E'] +
                A3*df.loc[i_day,'S3_E'] )
            
            df.loc[i_day,'BFR'] = df.loc[i_day,'Total_Excess'] * BFI # calc base flow recharge
            df.loc[i_day,'SFR'] = df.loc[i_day,'Total_Excess'] * (1-BFI)# calc surface flow recharge
  
            BS_t = df.loc[i_day,'BFR'] + df.loc[i_day-1,'BS'] # calc new Baseflow storage level
            df.loc[i_day,'Qbase'] = (1-Kbase)*BS_t
            df.loc[i_day,'BS'] = max(BS_t - df.loc[i_day,'Qbase'],0) # calc baseflow
            
            SS_t = df.loc[i_day,'SFR'] + df.loc[i_day-1,'SS'] # calc new Baseflow storage level
            df.loc[i_day,'Qsurf'] = (1-Kbase)*BS_t
            df.loc[i_day,'SS'] = max(SS_t - df.loc[i_day,'Qsurf'],0) # calc baseflow   
       
            df.loc[i_day,'Qtotal'] = df.loc[i_day,'Qsurf'] + df.loc[i_day,'Qsurf'] # calc total outflow in [mm]/[catchment size]
            # calc total outflow in m^3 per timestep (i.e. day)
            df.loc[i_day,'Q'] = (df.loc[i_day,'Qtotal']*1e-3) * (A*1e6) # calc total m^3 outflow for the timestep
                # 1e6 to convert catchment size from km^2 to m^2
                # 1e-3 to convert Qtotal from mm to m  
                
    ###### TODO:  test, then move back to the function file          

    print('Model run complete')    
    #%%Calculate skill scores
    sim_Q = df['Q']
    obs_Q = df_Gauge_data_cal['Volume m^3']
    
    correlation_matrix = np.corrcoef(sim_Q,obs_Q)
    correlation_xy = correlation_matrix[0,1]
    ss_r2_Q = correlation_xy**2
    
    ss_nse_Q = float(he.evaluator(he.nse, sim_Q, obs_Q))
    ss_rmse_Q = float(he.evaluator(he.rmse, sim_Q, obs_Q))
    ss_pbias_Q = float(he.evaluator(he.pbias, sim_Q, obs_Q))
    
    # save SS to sim_log.csv or memory
    
    
    
print('fin')
