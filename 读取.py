import numpy as np
import matplotlib.pyplot as plt
import xarray as xr


dataset = xr.open_dataset("ERA5 hourly data on pressure levels from 1940 to present.nc")
dataset2 = xr.open_dataset('single levels.nc')
dataset3 = xr.open_dataset(r"D:\Study\Yunnan Uni\data_stream-oper.nc")
dataset3 = xr.open_dataset(r"D:\Study\Yunnan Uni\data_stream-wave.nc")
dataset4 = xr.open_dataset(r"D:\Download\presure level.nc")

# print(dataset)
print(dataset)

print(dataset.data_vars)
