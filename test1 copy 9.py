import xarray as xr

# 打开 NetCDF 文件
dataset = xr.open_dataset(r"D:\Download\presure level.nc")
dataset1 = xr.open_dataset(r"D:\Download\q.nc")

# 定义时间范围，提取7月19日的数据
start_date = "2021-07-19T00:00:00"
end_date = "2021-07-19T23:59:59"

# 筛选出7月19日的数据
dataset_19th = dataset.sel(valid_time=slice(start_date, end_date))
dataset1_19th = dataset1.sel(valid_time=slice(start_date, end_date))

# 输出筛选后的数据，或保存到新的文件
print(dataset_19th)
print(dataset1_19th)
