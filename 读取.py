import numpy as np
import matplotlib.pyplot as plt
import xarray as xr


dataset = xr.open_dataset("single levels.nc")

print(dataset)
# print(dataset.data_vars)
