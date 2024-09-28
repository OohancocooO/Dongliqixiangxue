import numpy as np
import matplotlib.pyplot as plt
import xarray as xr


dataset = xr.open_dataset("xiaochidu.nc")
dataset2 = xr.open_dataset(r"D:\Study\Yunnan Uni\pressure levels china.nc")
dataset3 = xr.open_dataset(r"D:\Study\Yunnan Uni\data_stream-oper.nc")
# dataset3 = xr.open_dataset(r"D:\Study\Yunnan Uni\data_stream-wave.nc")
dataset4 = xr.open_dataset("xiaochidu.nc")

# print(dataset)
print(dataset.time)

# print(dataset.data_vars)
