import numpy as np
import matplotlib.pyplot as plt
import xarray as xr


# dataset = xr.open_dataset("ERA5 hourly data on pressure levels from 1940 to present.nc")
# dataset = xr.open_dataset(r"D:\Study\Yunnan Uni\hourly data china.nc")
# dataset = xr.open_dataset(r"D:\Study\Yunnan Uni\pressure levels china.nc")
dataset = xr.open_dataset(r"D:\Study\Yunnan Uni\data_stream-oper.nc")

print(dataset)
# print(dataset.data_vars)
