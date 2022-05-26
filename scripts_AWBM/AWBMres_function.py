# -*- coding: utf-8 -*-
"""
Created on Thu May 26 19:06:16 2022

@author: alex.xynias

This version of the function includes a conceptual simulation the volume of the wivenhoe-somerset reservoir

    - Uses a stage/storage curve to convert AWBM streamflow into a height and volume
    
    - Removes a static human demand from the system
        - After Rainfall & Evap, but before dam spill

    - If the reservoir volume exceeds 100% at the end of the timestep the excess volume is deleted
        - function assumes this can't occur in the first timestep 


"""
# =============================================================================
# Setup and Notes 
# =============================================================================

# import numpy as np  
# import datetime 
# import time
    
# Progress bar: https://github.com/rsalmei/alive-progress/blob/main/README.md
# To be used inside of a loop for each timestep


# *_t refers to a temp variable for the calculation
# indexing format: df.loc[row,col]

# =============================================================================
# The function
# =============================================================================


def AWBMres_function(i_day,df,df_SILO_data_cal,C1,C2,C3,A1,A2,A3,BFI,BS_0,Kbase,SS_0,Ksurf,A):
    threshold_resVolume = float(1354209000) # Aproximate max combined volume [m^3] of Wivenhoe and Somerset before water is released.
        # Operational volume of 1051460 ML at wivenhoe and 302749 ML at Somerset (1354209ML = 1354209000m^3)
            # Flood mitigation capacity of 1967000ML at wivenhoe
    outflow_human = float(750000) # Aproximate volume of outflows due to human demand.
        # a goal of 150 LPD is cited on the recent Water Security Status Report
            # but the reservoir also supplies industry (agriculture) water via 'Water Supply Schemes' ?
    
        # Using an aproximate 200LPD with the current population of SEQ being around 3.8E+6
            # Gives 720ML per day. I'll use 750ML (750000m^3) as a placeholder for now
        
    if i_day == 0: # set up condition for first timestep
  
       
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
        
        df.loc[i_day,'resVolume[m3]'] = df.loc[i_day,'Q'] # All streamflow enters the conceptual reservoir storage
        
        # print("...Done day 0")
        
    else: # for all subsequent timesteps
        # first, update the day column in df                
        df.loc[i_day,'dS'] = df_SILO_data_cal['dS'][i_day] # gets dS from silo calibration df
        df.loc[i_day,'E'] = df_SILO_data_cal['E[mm]'][i_day] 
        df.loc[i_day,'P'] = df_SILO_data_cal['P[mm]'][i_day] 
        
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

        df.loc[i_day,'resVolume[m3]'] = df.loc[i_day,'Q'] + df.loc[i_day-1,'resVolume[m3]'] # Adds new inflows into storage
            # TODO: remove evap*A_res from resVolume before spill and human outflow
            
        
        
















