#Test script for storage curve interpolation.
#https://docs.scipy.org/doc/scipy/reference/tutorial/interpolate.html

# #Import Libraries
# import numpy as np
# from scipy.interpolate import interp1d

# volume = 1000

# #Import data
# infile_name = "wivenhoe_storage_curve.csv" # Specify CSV file with data
# wivenhoe_storage_curve = np.loadtxt(infile_name,delimiter=',',skiprows=2) 


# y_data = wivenhoe_storage_curve[:,0] #selects the surface area values
# x_data = wivenhoe_storage_curve[:,1] #selects the storage values
# # z_data = wivenhoe_storage_curve[:,2] #selects the elevation [m AHD] values

# y_f = interp1d(x_data,y_data, 'linear')
#     #linear interpolates between the given data points.


# #e.g. returns the surface area when the volume is 1000 ML
# surface_area = int(y_f(volume)) * 0.01
# print(surface_area)


#%%
from storage_interp import storage_interp

infile_name = "wivenhoe_storage_curve.csv" # Specify CSV file with data
volume = 1000


x = storage_interp(infile_name,volume)
