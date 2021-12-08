# =============================================================================
# Clears all variables from workspace.
%reset -f 


# ===== 0.0 IMPORTING PACKAGES / MODULES ======================================
print(' ')
print(' Importing python modules ...')

#import os                                     # Operating system function
import numpy as np                             # Basic mathematics library
#import pandas as pd                           # Data analysis module
#import matplotlib
import matplotlib.pyplot as plt                # Imports plotting library
import matplotlib.dates as mdates
import matplotlib.font_manager as font_manager
#from datetime import datetime                 # Imports module to convert dates
import datetime                          # Imports module to convert dates
#import matplotlib.font_manager          # Imports font libarary for plotting
import csv                                     #Imports csv module
#import openpyxl

print('      ... python modules imported.')

# ===== 1.0 LOADING INPUT DATA ================================================
print(' ')
print(' Loading input data ...')

infile_name = 'SILO_1985-2021_-27.35_152.60_trim.csv'     # This input data used for calibartion.
#infile_name = 'MetData-Jan-Mar-2011.csv'     # This input data used for testing.

# Establishing variables
Date_in = []
Day_in = []
P_in = []
# Add another variable for streamflow (from SS dam)?
E_in = []

with open(infile_name) as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    next(csvReader)         # This skips the 1st row (header information)
    next(csvReader)         # This skips the 2nd row (header information)
    for row in csvReader:
        Day_in.append(row[0])
        Date_in.append(row[1])
        P_in.append(row[2])
        E_in.append(row[3])
                
del infile_name, row

# Converting dates from string to datetime for plotting
dims = np.shape(Date_in)
Date = []
for i in range(0,dims[0]):
    temp_str = Date_in[i]
    temp_PD = datetime.datetime.strptime(temp_str, '%d/%m/%Y')
    Date.append(temp_PD)
del temp_str
del temp_PD    
del i
del dims

# Converting missing data to zero values 
# (only one case on day 18 of 1974 input for P_in - included as example only)
Day = np.array(Day_in)
Day[Day==''] = 0
#Day[Day==''] = np.nan               # Alternative scripting to convert to NaN
Day=[float(x) for x in Day]

P = np.array(P_in)
P[P==''] = 0               
#P[P==''] = np.nan                   # Alternative scripting to convert to NaN
P=[float(x) for x in P]

E = np.array(E_in)
E[E==''] = 0               
#E[E==''] = np.nan                   # Alternative scripting to convert to NaN
E=[float(x) for x in E]

del Date_in, Day_in, P_in, E_in

print('     ... input data loaded.')
  
# ===== 2.0 MODEL PARAMETERS ==================================================
print(' ')
print(' Setting up model parameters ...')

A = float(3869.6461797327);          # Catchment area [km^2]
    #3869.6461797327 km^2 from gregor's creek catchment crop
    #7020 km^2 from: https://www.seqwater.com.au/dams/wivenhoe
    #5360 km^2 from: https://www.researchgate.net/publication/242172986_Maximising_Water_Storage_in_South_East_Queensland_Reservoirs_Evaluating_the_Impact_of_Runoff_Interception_by_Farm_Dams
        #5360 +1490+333 aprox the 7020
            # 1340 and not 1490? https://www.seqwater.com.au/dams/somerset
A1 = float(0.134)       # Storage fraction [0-1]
A2 = float(0.433)       # Storage fraction [0-1]
A3 = float(0.433)       # Storage fraction [0-1]
    #13.4/43.3/43.3 = Default (Barret et al., 2008)
Acheck = A1 + A2 + A3   # Check to ensure A1+A2+A3 = 1
C1 = float(7)           # Storage capacity [mm]
C2 = float(70)         # Storage capacity [mm]
C3 = float(150)         # Storage capacity [mm]
BFI = float(0.35)       # Base flow index [0-1]
    #QLD average =0.17 (Boughton, 2009)
Kbase = float(0.95)     # Baseflow recession constant [0-1]
    #QLD average =0.95 (Boughton, 2009)
Ksurf = float(0.35)     # Surface flow recession constant [0-1]
    #13.4/43.3/43.3 = Default (Barret et al., 2008)
# Setting initial storage capacities
S1_0 = float(0)         # Initial storage capacity storage 1 [mm]
S2_0 = float(0)         # Initial storage capacity storage 2 [mm]
S3_0 = float(0)         # Initial storage capacity storage 3 [mm]wivenhoe 
BS_0 = float(0)         # Initial storage capacity baseflow store [mm]
SS_0 = float(0)         # Initial storage capacity surface flow store [mm]

print('      ... model parameters set-up.')

# ===== 3.0 APPLYING MODEL ====================================================
print(' ')
print(' Applying the AWBM ...')

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
 
S1_temp = max(S1_0+dS,0)
S1_Excess = max(S1_temp-C1,0)
S1.append(min(S1_temp,C1))

S2_temp = max(S2_0+dS,0)
S2_Excess = max(S2_temp-C2,0)
S2.append(min(S2_temp,C2))

S3_temp = max(S3_0+dS,0)
S3_Excess = max(S3_temp-C3,0)
S3.append(min(S3_temp,C3))

Total_Excess.append((S1_Excess*A1)+(S2_Excess*A2)+(S3_Excess*A3))

BaseFlowRecharge = Total_Excess[0] * BFI
SurfaceFlowRecharge = Total_Excess[0] * (1-BFI)

#BS_temp = (BaseFlowRecharge/2)+BS_0
BS_temp = BaseFlowRecharge + BS_0
Qbase.append((1-Kbase)*BS_temp)
BS.append(max((BS_0 + BaseFlowRecharge - Qbase[0]),0))

#SS_temp = (SurfaceFlowRecharge/2)+SS_0
SS_temp = SurfaceFlowRecharge + SS_0
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
    
    Total_Excess.append((S1_Excess*A1)+(S2_Excess*A2)+(S3_Excess*A3))
    
    BaseFlowRecharge = Total_Excess[i] * BFI
    SurfaceFlowRecharge = Total_Excess[i] * (1-BFI)
    
#    BS_temp = (BaseFlowRecharge/2)+BS[i-1]
    BS_temp = BaseFlowRecharge + BS[i-1]
    Qbase.append((1-Kbase)*BS_temp)
    BS.append(max((BS[i-1] + BaseFlowRecharge - Qbase[i]),0))
    
#    SS_temp = (SurfaceFlowRecharge/2)+SS[i-1]
    SS_temp = SurfaceFlowRecharge + SS[i-1]
    Qsurf.append((1-Ksurf)*SS_temp)
    SS.append(max((SS[i-1] + SurfaceFlowRecharge - Qsurf[i]),0))
    
    Qtotal.append(Qbase[i] + Qsurf[i])
    Q.append(((Qtotal[i]/1000)*(A*1000*1000))/24/60/60)

print('      ... AWBM run complete.')

# ===== 4.0 EXPORTING DATA ====================================================
print(' ')
print(' Exporting data to csv file ...')

outFileName = 'Ouput-AWBM.csv'
header1 = ['Date', 'Day', 'P', 'E', 'Qbase', 'Qsurf', 'Qtotal', 'Q']
header2 = ['[dd-mm-yyy]', '[-]', '[mm]', '[mm]', '[mm]', '[mm]',
           '[mm]', '[m^3/s]']
# Using "zip" funciton to combine variables
outData = zip(Date, Day, P, E, Qbase, Qsurf, Qtotal, Q)
#outData = zip(Date, Day, P, E, S1, S2, S3, BS, SS, Qbase, Qsurf, Qtotal, Q)
with open(outFileName,'w') as f:
    writer = csv.writer(f,lineterminator='\n')
    writer.writerow(header1)
    writer.writerow(header2)
    for row in outData:
        writer.writerow(row)

print('      ... data exported to csv file.')

# ===== 5.0 PLOTING DATA (Quick Plots) ========================================
# A reference source to get started: 
# https://realpython.com/python-matplotlib-guide/
# https://matplotlib.org/api/axes_api.html?highlight=axes%20class#plotting
#
# Need to run the line below once in each session to adjust setting to plot
# in separate window - not at command line.
# %matplotlib qt

# To return to inline plot at command line use %matplotlib inline 

print(' ')
print(' Plotting data ...')

# ===== Setting plot formatting (global settings - applies to all plots)
mS = 18 # Used to set marker size
lW = 5 # Used to set linewidth
fS = 28 # Used to set font size
plt.rcParams['font.family'] = 'Times New Roman' # Globally sets the font type
plt.rc('font',size=fS)
plt.rc('axes',titlesize=fS)
plt.rc('axes',labelsize=fS)
plt.rc('xtick',labelsize=fS)
plt.rc('ytick',labelsize=fS)
plt.rc('legend',fontsize=fS)
plt.rc('figure',titlesize=fS)
#date_formatter = mdates.DateFormatter('%d-%m')

months = mdates.MonthLocator()
monthsFmt = mdates.DateFormatter('%m')
days = mdates.DayLocator()


stDate = datetime.datetime.strptime('1974-1-1', '%Y-%m-%d')
enDate = datetime.datetime.strptime('1974-4-1', '%Y-%m-%d')

# ===== Single plot example =====
fig, ax1 = plt.subplots() #Establishes figure handle
#fig, ax1 = plt.subplots(figsize=(5,3),dpi=50) #Establishes figure handles of size
ax2 = ax1.twinx()


tle = 'AWBM - Model Output'

# Plotting using different plot types in single figure
#ax1.semilogy(Date,Q, '-', c='b',label='Simulated flow',
#         markersize=mS,linewidth=lW)
ax1.plot(Date,Q, '-o', c='b',label='Simulated flow',
         markersize=mS,linewidth=lW)
ax2.bar(Date,P,color='k',label='Rainfall')
#ax1.xaxis.set_major_formatter(date_formatter)
#ax1.grid()
ax1.set_xlim(stDate, enDate)
ax1.xaxis.set_major_locator(months)
ax1.xaxis.set_major_formatter(monthsFmt)
ax1.xaxis.set_minor_locator(days)
#ax1.set_ylim(-0.1,1)
#ax2.set_ylim(-30,300)
#ax1.set_xticks([0, 10, 20, 30, 40, 50, 60])
#ax1.set_yticks([0, 200, 400, 600])
ax1.set_xlabel('Date [Month in 1974]')
ax1.set_ylabel('Avg Daily Flow [m$^3$ $s^{-1}$]')
ax2.set_ylabel('Rainfall [mm]')
ax1.set_title(tle)
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

fig.tight_layout()

# =============================================================================
# ========= END OF SCRIPT ======= END OF SCRIPT ======= END OF SCRIPT =========
# =============================================================================