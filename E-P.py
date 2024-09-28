import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# 假设你的数据已经加载为 ds
ds = xr.open_dataset(r"D:\Study\Yunnan Uni\data_stream-oper.nc")

# 选择特定时间 2021-07-19T01:00:00
time_selected = np.datetime64("2021-07-18T01:00:00")
ds_selected = ds.sel(valid_time=time_selected)

# 计算 e - tp
diff = -ds_selected["e"] * ds_selected["e"] - ds_selected["tp"]

# 创建图形和投影
fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={"projection": ccrs.PlateCarree()})

# 设置正负颜色渐变：红色到蓝色
cmap = plt.get_cmap("RdBu")

# 绘制 e - tp 的值
im = ax.pcolormesh(
    ds_selected["longitude"],
    ds_selected["latitude"],
    diff,
    cmap=cmap,
    transform=ccrs.PlateCarree(),
)

# 添加海岸线
ax.coastlines()

# 添加颜色条
cbar = plt.colorbar(im, ax=ax, orientation="horizontal")
cbar.set_label("e")

# 显示图像
plt.title("Difference between e and tp at")
plt.show()
