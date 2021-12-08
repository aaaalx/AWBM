
# =============================================================================
# #%%setup for testing
# =============================================================================
# #https://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html
# infile_name = "Data/AWBM/wivenhoe_storage_curve.csv" # Specify CSV file with data
#     # Surface Area,Volume,Elevation
#     # [Ha],[ML],[M AHD]
# volume = 9480

# =============================================================================
# #%% Storage interpolation function
# =============================================================================
# Takes a volume in [m^3] and returns the surface area [km^2] with 
# linear interpolation from given data (SEQwater)

def storage_interp(infile_name,volume):
    #Import Libraries
    import numpy as np
    from scipy.interpolate import interp1d
    
    # volume = volume * 0.001 # [m^3 to ML conversion]
    
    #Import data
    wivenhoe_storage_curve = np.loadtxt(infile_name,delimiter=',',skiprows=2) 
        
    y_data = wivenhoe_storage_curve[:,0] #selects the surface area values
    x_data = wivenhoe_storage_curve[:,1] #selects the storage values
    # z_data = wivenhoe_storage_curve[:,2] #selects the elevation [m AHD] values
    
    y_f = interp1d(x_data,y_data, 'linear')
        #linear interpolates between the given data points.
    
    surface_area = int(y_f(volume)) * 0.01 # converts from Ha to km^2
        
    return surface_area
    

# =============================================================================
# # %% test outputs
# =============================================================================
# print(storage_interp("wivenhoe_storage_curve.csv",volume))