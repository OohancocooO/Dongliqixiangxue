import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import metpy.calc as mpcalc
from metpy.units import units
from scipy.signal import convolve2d
import geopandas as gpd

# 设置matplotlib支持中文显示
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 'SimHei' 是一种支持中文的字体
plt.rcParams["axes.unicode_minus"] = False  # 正确显示负号

# 加载2月和3月的数据

g = 9.80665

# 合并2月和3月的数据
dataset = xr.open_dataset(r"D:\Download\presure level.nc")
dataset1 = xr.open_dataset(r"D:\Download\q.nc")


# 对数据进行时间平均
dataset_mean = dataset.mean(dim="valid_time")
dataset_mean1 = dataset1.mean(dim="valid_time")

# 获取各数据变量
u = dataset_mean["u"].values
v = dataset_mean["v"].values
q = dataset_mean["q"].values
sp = dataset_mean1["sp"].values
lev = dataset_mean["pressure_level"].values

# 获取经纬度
lon = dataset_mean["longitude"].values
lat = dataset_mean["latitude"].values

# 初始化整层积分水汽通量
qv_u = u * q
qv_v = v * q

# 处理地表以下气压层的数据
for i in range(len(lev)):
    qv_u[i, :, :] = xr.where(sp > lev[i], qv_u[i, :, :], 0.0)
    qv_v[i, :, :] = xr.where(sp > lev[i], qv_v[i, :, :], 0.0)

vint_qvu = -np.trapz(qv_u, lev, axis=0) / g
vint_qvv = -np.trapz(qv_v, lev, axis=0) / g

# 计算网格间距
dx, dy = mpcalc.lat_lon_grid_deltas(lon, lat)

# 计算散度
div = mpcalc.divergence(vint_qvu * units("m/s"), vint_qvv * units("m/s"), dx=dx, dy=dy)

# 对结果进行平滑处理
kernel = np.ones((9, 9)) / 81
div_smoothed = convolve2d(div, kernel, mode="same", boundary="fill", fillvalue=0)

# 绘制等值线图
plt.figure(figsize=(10, 8))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([lon.min(), lon.max(), lat.min(), lat.max()], crs=ccrs.PlateCarree())
ax.add_feature(cfeature.COASTLINE)

contour = ax.contourf(
    lon, lat, div_smoothed, cmap="coolwarm", transform=ccrs.PlateCarree()
)
plt.colorbar(
    contour,
    orientation="horizontal",
    pad=0.05,
    label="水汽通量散度 (kg m$^{-2}$ s$^{-1}$)",
)

plt.title("柱状积分水汽通量散度")

plt.show()
