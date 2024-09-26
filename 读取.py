import numpy as np
import matplotlib.pyplot as plt
import xarray as xr


dataset = xr.open_dataset("ERA5 hourly data on pressure levels from 1940 to present.nc")

#print(dataset)
print(dataset.data_vars)
