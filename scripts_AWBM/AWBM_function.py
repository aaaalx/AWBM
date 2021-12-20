# =============================================================================
# Setup and Notes 
# =============================================================================

import numpy as np  
import datetime 

import time



# # Input data headers (for ref only)
# df_run_headers_f = ['Date'
#                   , 'Day'
#                   , 'dS'
#                   ,'S1','S2','S3'
#                   ,'S1_E', 'S2_E', 'S3_E', 'Total_Excess'
#                   , 'BFR', 'SFR' #Base Flow Recharge, Surface Flow Recharge
#                   , 'BS', 'SS' #Baseflow Store, Surface runoff routing Store
#                   , 'Qbase', 'Qsurf', 'Qtotal', 'Q'
#                   ]


# # other variables:
# C1 = Cavg_i * C1_Favg
# C2 = Cavg_i * C2_Favg
# C3 = Cavg_i * C3_Favg
# A1 = bounds_A[0]
# A2 = bounds_A[1]
# A3 = bounds_A[2]
# A = 3868.966716 # Catchment area in km^2
# S1_0 = float(0.1)         # Initial storage capacity storage 1 [mm]
# S2_0 = float(0.1)         # Initial storage capacity storage 2 [mm]
# S3_0 = float(0.1)         # Initial storage capacity storage 3 [mm] 
# BS_0 = float(0)         # Initial storage capacity baseflow store [mm]
# SS_0 = float(0)         # Initial storage capacity surface flow store [mm]
# BFI = float(0.35)       # Base flow index [0-1]
# Kbase = float(0.95)     # Baseflow recession constant [0-1]
# Ksurf = float(0.35)     # Surface flow recession constant [0-1]
    
# Progress bar: https://github.com/rsalmei/alive-progress/blob/main/README.md

# =============================================================================
# The function
# =============================================================================
# To be used inside of a loop for each timestep
# *_t refers to a temp variable for the calc

def AWBM_function(i_day,df,df_SILO_data_cal,C1,C2,C3,A1,A2,A3,BFI,BS_0,Kbase,SS_0,Ksurf,A):
    
    if i_day == 0: # set up condition for first timestep
        print(f'Setting up first timestep... {C1},{C2},{C3}')
        
        
        # Calculating storage levels and overflows 
        S1_t = max(df['S1'][i_day]+df['dS'][i_day],0) # calculates Soil store + (P-E) > 0 
        df['S1_E'][i_day] = max(S1_t - C1,0) # calculates the excess
        df['S1'][i_day] = min(S1_t,C1) # writes the new storage to df
        
        S2_t = max(df['S2'][i_day]+df['dS'][i_day],0)
        df['S2_E'][i_day] = max(S2_t - C1,0)
        df['S2'][i_day] = min(S2_t,C1)      
        
        S3_t = max(df['S3'][i_day]+df['dS'][i_day],0)
        df['S3_E'][i_day] = max(S3_t - C1,0)
        df['S3'][i_day] = min(S3_t,C1)       
        
        df['Total_Excess'][i_day] = ( # Calculates sum of A_i*S_i_E 
            A1*df['S1_E'][i_day] +
            A2*df['S2_E'][i_day] +
            A3*df['S3_E'][i_day] )      
        
        df['BFR'][i_day] = df['Total_Excess'][i_day] * BFI # calc base flow recharge
        df['SFR'][i_day] = df['Total_Excess'][i_day] * (1-BFI) # calc surface flow recharge
        
        BS_t = df['BFR'][i_day] + BS_0 # calc new Baseflow storage level
        df['Qbase'][i_day] = (1-Kbase)*BS_t
        df['BS'][i_day] = max(BS_t - df['Qbase'][i_day],0) # calc baseflow
        
        SS_t = df['SFR'][i_day] + SS_0 # calc new surface storage level
        df['Qsurf'][i_day] = (1-Ksurf)*SS_t
        df['SS'][i_day] = max(SS_t - df['Qsurf'][i_day],0) # calc surf flow
        
        df['Qtotal'][i_day] = df['Qsurf'][i_day] + df['Qbase'][i_day] # calc total outflow in [mm]/[catchment size]
        # calc total outflow in m^3 per timestep (i.e. day)
        df['Q'][i_day] = (df['Qtotal'][i_day]*1e-3) * (A*1e6) # calc total m^3 outflow for the timestep
            # 1e6 to convert catchment size from km^2 to m^2
            # 1e-3 to convert Qtotal from mm to m            
        
        print(f"...Done day0 Q = {df['Q'][i_day]} [m^3]")
    else: # for all subsequent timesteps
        
        df['dS'][i_day] = df_SILO_data_cal['dS'][i_day] # gets dS from silo calibration df
        
        # Calculating storage levels and overflows 
        S1_t = max(df['S1'][i_day-1]+df['dS'][i_day],0) # calculates Soil store + (P-E) > 0 
        df['S1_E'][i_day] = max(S1_t - C1,0) # calculates the excess
        df['S1'][i_day] = min(S1_t,C1) # writes the new storage to df
        
        S2_t = max(df['S2'][i_day-1]+df['dS'][i_day],0)
        df['S2_E'][i_day] = max(S2_t - C1,0)
        df['S2'][i_day] = min(S2_t,C1)      
        
        S3_t = max(df['S3'][i_day-1]+df['dS'][i_day],0)
        df['S3_E'][i_day] = max(S3_t - C1,0)
        df['S3'][i_day] = min(S3_t,C1)       
        
        df['Total_Excess'][i_day] = ( # Calculates sum of A_i*S_i_E 
            A1*df['S1_E'][i_day] +
            A2*df['S2_E'][i_day] +
            A3*df['S3_E'][i_day] )      
        
        df['BFR'][i_day] = df['Total_Excess'][i_day] * BFI # calc base flow recharge
        df['SFR'][i_day] = df['Total_Excess'][i_day] * (1-BFI) # calc surface flow recharge
        
        BS_t = df['BFR'][i_day] + df['BS'][i_day-1] # calc new Baseflow storage level
        df['Qbase'][i_day] = (1-Kbase)*BS_t
        df['BS'][i_day] = max(BS_t - df['Qbase'][i_day],0) # calc baseflow
        
        SS_t = df['SFR'][i_day] + df['SS'][i_day-1] # calc new surface storage level
        df['Qsurf'][i_day] = (1-Ksurf)*SS_t
        df['SS'][i_day] = max(SS_t - df['Qsurf'][i_day],0) # calc surf flow
        
        df['Qtotal'][i_day] = df['Qsurf'][i_day] + df['Qbase'][i_day] # calc total outflow in [mm]/[catchment size]
        # calc total outflow in m^3 per timestep (i.e. day)
        df['Q'][i_day] = (df['Qtotal'][i_day]*1e-3) * (A*1e6) # calc total m^3 outflow for the timestep
            # 1e6 to convert catchment size from km^2 to m^2
            # 1e-3 to convert Qtotal from mm to m   
        
        


            
    
    

