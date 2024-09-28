import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import xarray as xr
from cnmaps import get_adm_maps, draw_map

# 加载数据
ds = xr.open_dataset("xiaochidu.nc")

# 获取河南省和郑州市的行政边界
henan = get_adm_maps(province="河南省", only_polygon=True, record="first")
zhengzhou = get_adm_maps(city="郑州市", only_polygon=True, record="first")

# 用户输入时间
user_input_time = (
    "2021-07-18T00:00:00"
)
selected_time = np.datetime64(user_input_time)

# 找到最接近输入时间的数据
time_index = np.argmin(np.abs(ds.time.values - selected_time))

# 创建绘图
fig, ax = plt.subplots(subplot_kw={"projection": ccrs.PlateCarree()})
ax.set_extent([110, 117, 31, 37], crs=ccrs.PlateCarree())

# 绘制表面气压的等气压线，每100 hPa绘制一条等压线
pressure = ds.sp[time_index, :, :].values / 100  # 将单位转为 hPa
lon, lat = np.meshgrid(ds.longitude, ds.latitude)

# 绘制等压线，每 100 hPa 显示一条
cs = ax.contour(
    lon,
    lat,
    pressure,
    levels=np.arange(np.min(pressure), np.max(pressure), 50),
    colors="black",
    transform=ccrs.PlateCarree(),
)
ax.clabel(cs, inline=1, fontsize=10, fmt="%1.0f hPa")

# 添加河南省和郑州市的行政边界
draw_map(henan, ax=ax, lw=1, color="black")
draw_map(zhengzhou, ax=ax, lw=1.5, color="r")

# 添加海岸线和其他自然特征
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=":")

# 标题
ax.set_title(
    f"Surface Pressure - {np.datetime_as_string(ds.time.values[time_index], unit='h')}"
)

# 显示图像
plt.show()
