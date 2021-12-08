
## All these parms will be in the larger script and input into the function
    # A = float(3869.6461797327);          # Catchment area [km^2]
    #     #3869.6461797327 km^2 from gregor's creek catchment crop
    #     #7020 km^2 from: https://www.seqwater.com.au/dams/wivenhoe
    #     #5360 km^2 from: https://www.researchgate.net/publication/242172986_Maximising_Water_Storage_in_South_East_Queensland_Reservoirs_Evaluating_the_Impact_of_Runoff_Interception_by_Farm_Dams
    #         #5360 +1490+333 aprox the 7020
    #             # 1340 and not 1490? https://www.seqwater.com.au/dams/somerset
    # A1 = float(0.134)       # Storage fraction [0-1]
    # A2 = float(0.433)       # Storage fraction [0-1]
    # A3 = float(0.433)       # Storage fraction [0-1]
    #     #13.4/43.3/43.3 = Default (Barret et al., 2008)
    # Acheck = A1 + A2 + A3   # Check to ensure A1+A2+A3 = 1
    # C1 = float(7)           # Storage capacity [mm]
    # C2 = float(70)         # Storage capacity [mm]
    # C3 = float(150)         # Storage capacity [mm]
    # BFI = float(0.35)       # Base flow index [0-1]
    #     #QLD average =0.17 (Boughton, 2009)
    # Kbase = float(0.95)     # Baseflow recession constant [0-1]
    #     #QLD average =0.95 (Boughton, 2009)
    # Ksurf = float(0.35)     # Surface flow recession constant [0-1]
    #     #13.4/43.3/43.3 = Default (Barret et al., 2008)
    # # Setting initial storage capacities
    # S1_0 = float(0)         # Initial storage capacity storage 1 [mm]
    # S2_0 = float(0)         # Initial storage capacity storage 2 [mm]
    # S3_0 = float(0)         # Initial storage capacity storage 3 [mm]wivenhoe 
    # BS_0 = float(0)         # Initial storage capacity baseflow store [mm]
    # SS_0 = float(0)         # Initial storage capacity surface flow store [mm]
    
import numpy as np  
# import datetime 
# import matplotlib.dates as mdates
sim = np.array([1,2,3,4,5])
sim.astype(np.float64)

def AWBM_function(sim_number,Date,P,E,A,A1,A2,A3,C1,C2,C3,BFI,Kbase,Ksurf,S1_0,S2_0,S3_0,BS_0,SS_0):

#TODO: update to variable[sim] format
        
    for sim in range(0, sim_number):
        # ===== 3.0 APPLYING MODEL ====================================================
        print(' ')
        print(' Applying the AWBM ...')
        
        Acheck = A1 + A2 + A3
        if Acheck != 1:
            print("Acheck failed, does not sum to 1")
          
        
        # Initialising variables for model run
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
        
        dS  = P[0]-E[0]
         
        S1_temp = max(S1_0[sim]+dS,0)
        S1_Excess = max(S1_temp-C1[sim],0)
        S1.append(min(S1_temp,C1[sim]))
        
        S2_temp = max(S2_0[sim]+dS,0)
        S2_Excess = max(S2_temp-C2[sim],0)
        S2.append(min(S2_temp,C2[sim]))
        
        S3_temp = max(S3_0[sim]+dS,0)
        S3_Excess = max(S3_temp-C3[sim],0)
        S3.append(min(S3_temp,C3[sim]))
        
        Total_Excess.append((S1_Excess*A1[sim])+(S2_Excess*A2[sim])+(S3_Excess*A3[sim]))
        
        BaseFlowRecharge = Total_Excess[0] * BFI[sim]
        SurfaceFlowRecharge = Total_Excess[0] * (1-BFI[sim])
        
        #BS_temp = (BaseFlowRecharge/2)+BS_0
        BS_temp = BaseFlowRecharge + BS_0
        Qbase.append((1-Kbase[sim])*BS_temp)
        BS.append(max((BS_0 + BaseFlowRecharge - Qbase[0]),0))
        
        #SS_temp = (SurfaceFlowRecharge/2)+SS_0[sim]
        SS_temp = SurfaceFlowRecharge + SS_0[sim]
        Qsurf.append((1-Ksurf)*SS_temp)
        SS.append(max((SS_0 + SurfaceFlowRecharge - Qsurf[0]),0))
        
        Qtotal.append(Qbase[0] + Qsurf[0])
        Q.append(((Qtotal[0]/1000)*(A*1000*1000))/24/60/60)
        
        for i in range(1,dims[0]):
            dS = P[i]-E[i] 
            
            S1_temp = max(S1[i-1]+dS,0)
            S1_Excess = max(S1_temp-C1,0)
            S1.append(min(S1_temp,C1))
            
            S2_temp = max(S2[i-1]+dS,0)
            S2_Excess = max(S2_temp-C2,0)
            S2.append(min(S2_temp,C2))
            
            S3_temp = max(S3[i-1]+dS,0)
            S3_Excess = max(S3_temp-C3,0)
            S3.append(min(S3_temp,C3))
            
            Total_Excess.append((S1_Excess*A1[sim])+(S2_Excess*A2[sim])+(S3_Excess*A3[sim]))
            
            BaseFlowRecharge = Total_Excess[i] * BFI[sim]
            SurfaceFlowRecharge = Total_Excess[i] * (1-BFI)
            
        #    BS_temp = (BaseFlowRecharge/2)+BS[i-1]
            BS_temp = BaseFlowRecharge + BS[i-1]
            Qbase.append((1-Kbase[sim])*BS_temp)
            BS.append(max((BS[i-1] + BaseFlowRecharge - Qbase[i]),0))
            
        #    SS_temp = (SurfaceFlowRecharge/2)+SS[i-1]
            SS_temp = SurfaceFlowRecharge + SS[i-1]
            Qsurf.append((1-Ksurf)*SS_temp)
            SS.append(max((SS[i-1] + SurfaceFlowRecharge - Qsurf[i]),0))
            
            Qtotal.append(Qbase[i] + Qsurf[i])
            Q.append(((Qtotal[i]/1000)*(A*1000*1000))/24/60/60)
                #double check the units here?
                
        print('  .....AWBM done for sim#' +str(sim))