import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cnmaps import get_adm_maps, draw_map

# 打开nc文件并加载数据
# 假设你的nc文件已加载为rd
rd = xr.open_dataset("ERA5 hourly data on pressure levels from 1940 to present.nc")

# 提取850 hPa时的风速数据
time_selected = "2021-07-19T01:00:00"
pressure_level = 1000

u_850 = rd["u"].sel(valid_time=time_selected, pressure_level=pressure_level)
v_850 = rd["v"].sel(valid_time=time_selected, pressure_level=pressure_level)

# 限制绘图的经纬度范围
lon_min, lon_max = 110, 116
lat_min, lat_max = 32, 38

u_850 = u_850.sel(
    longitude=slice(lon_min, lon_max), latitude=slice(lat_max, lat_min)
)  # 纬度是从大到小的
v_850 = v_850.sel(longitude=slice(lon_min, lon_max), latitude=slice(lat_max, lat_min))

# 定义风速大于0和小于0的部分
u_greater_than_0 = u_850.where((u_850 < 0) & (v_850 > 0))  # 东南风
u_less_than_0 = u_850.where((u_850 > 0) & (v_850 < 0))  # 西北风

# 创建经纬度网格
lon_greater_than_0, lat_greater_than_0 = np.meshgrid(
    u_greater_than_0.longitude, u_greater_than_0.latitude
)
lon_less_than_0, lat_less_than_0 = np.meshgrid(
    u_less_than_0.longitude, u_less_than_0.latitude
)

# 设置投影和绘图区域
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection=ccrs.PlateCarree())

# 使用contourf填充u和v同时大于0的部分
ax.contourf(
    lon_greater_than_0,
    lat_greater_than_0,
    u_greater_than_0.squeeze(),
    colors="#FFFFCC",
    transform=ccrs.PlateCarree(),
)

# 使用contourf填充u和v同时小于0的部分
ax.contourf(
    lon_less_than_0,
    lat_less_than_0,
    u_less_than_0.squeeze(),
    colors="#FFCCCC",
    transform=ccrs.PlateCarree(),
)

# 绘制风向箭头
step = 1  # 调整箭头的密度
ax.quiver(
    u_850.longitude[::step],
    u_850.latitude[::step],
    u_850[::step, ::step],
    v_850[::step, ::step],
    scale=100,
    transform=ccrs.PlateCarree(),
)

# 添加地图区域
henan = get_adm_maps(province="河南省", only_polygon=True, record="first")
zhengzhou = get_adm_maps(city="郑州市", only_polygon=True, record="first")

# 绘制区域边界
draw_map(henan, ax=ax, lw=1, color="black")  # 绘制河南省
draw_map(zhengzhou, ax=ax, lw=1.5, color="r")  # 绘制郑州市

# 设置标题和显示图像
ax.set_title(f"Wind Direction at {pressure_level}hPa on {time_selected}", fontsize=16)
ax.set_xlim([lon_min, lon_max])
ax.set_ylim([lat_min, lat_max])

plt.show()
