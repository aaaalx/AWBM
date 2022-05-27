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


def AWBMres_function(i_day,df,df_data,C1,C2,C3,A1,A2,A3,BFI,BS_0,Kbase,SS_0,Ksurf,A,CN_P,CN_E,threshold_resVolume,outflow_human,A_res):
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
        df.loc[i_day,'dS'] = df_data['dS'][i_day] # gets dS from silo calibration df
        df.loc[i_day,'E'] = df_data[CN_E][i_day] 
        df.loc[i_day,'P'] = df_data[CN_P][i_day] 
        
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

        df.loc[i_day,'resVolume[m3]'] = df.loc[i_day,'Q'] + df.loc[i_day-1,'resVolume[m3]'] # Adds new inflows into the "lake" storage var
        
            
        # Add the reservoir area to the results output for later checking if needed. 
        df.loc[i_day,'A_res'] = A_res 
            # From the QGIS layer; the reservoir storage area is aprox 45.7+113.8km^2

        # Because the AWBM catchment area already includes the surface area of the lakes,
        #   There is already direct rainfall being introduced into the system.
        #   This step will use E (rather than) dS to avoid accounting for that rainfall twice.        

        df.loc[i_day,'resEvapLoss[m3]'] = (df.loc[i_day,CN_E]/1000) * (df.loc[i_day,'A_res']*10000)
        df.loc[i_day,'resVolume[m3]'] = df.loc[i_day,'resVolume[m3]'] - df.loc[i_day,'resEvapLoss[m3]']
            # A_res is given in Ha, convert this to m^2 with *10000
            # Evap is in mm, and needs to be converted ( into m in order to match 

        # Remove outflows from human demand and agriculture from the resVolume
        df.loc[i_day,'resVolume[m3]'] = df.loc[i_day,'resVolume[m3]'] - outflow_human


        # Spill condition
        if df.loc[i_day,'resVolume[m3]'] >= threshold_resVolume:
            # Record the water being spilt during the timestep
            df.loc[i_day,'resSpill[m3]'] = threshold_resVolume - df.loc[i_day,'resVolume[m3]']
            # Remove the excess water from the res
            df.loc[i_day,'resVolume[m3]'] = threshold_resVolume
            












