import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd  # 新增的库，用于加载和绘制shapefile
from cnmaps import get_adm_maps, draw_map

# 设置matplotlib支持中文显示
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 'SimHei' 是一种支持中文的字体
plt.rcParams["axes.unicode_minus"] = False  # 正确显示负号

# 合并2月和3月的数据
dataset = xr.open_dataset(r"D:\Download\presure level.nc")
dataset1 = xr.open_dataset(r"D:\Download\q.nc")

dataset = xr.open_dataset(r"D:\Download\presure level.nc")
dataset1 = xr.open_dataset(r"D:\Download\q.nc")

g = 9.80665

# 定义时间范围，提取7月19日的数据
start_date = "2021-07-19T08:00:00"
end_date = "2021-07-20T04:00:00"

# 筛选出7月19日的数据
dataset = dataset.sel(valid_time=slice(start_date, end_date))
dataset1 = dataset1.sel(valid_time=slice(start_date, end_date))

# 对数据进行时间平均
# 获取各数据变量
u = dataset["u"].values
v = dataset["v"].values
q = dataset["q"].values
sp = dataset1["sp"].values
lev = dataset["pressure_level"].values
# 获取经纬度
lon = dataset["longitude"].values
lat = dataset["latitude"].values

# 初始化整层积分水汽通量
qv_u = u * q
qv_v = v * q

# 处理地表以下气压层的数据
for i in range(len(lev)):
    qv_u[:, i, :, :] = xr.where(sp > lev[i], qv_u[:, i, :, :], 0.0)
    qv_v[:, i, :, :] = xr.where(sp > lev[i], qv_v[:, i, :, :], 0.0)

vint_qvu = -np.trapz(qv_u, lev, axis=1) / g
vint_qvv = -np.trapz(qv_v, lev, axis=1) / g

# 创建一个PlateCarree投影的地图
fig = plt.figure(figsize=(10, 8))
ax = plt.axes(projection=ccrs.PlateCarree())

# 限定地图范围
ax.set_extent([80, 160, 9, 51], crs=ccrs.PlateCarree())

# 添加海岸线
ax.coastlines()

# 添加经纬度网格
gl = ax.gridlines(
    draw_labels=True, linewidth=1, color="white", alpha=0.5, linestyle="--"
)
gl.top_labels = False

# 计算整层水汽通量的大小
qv_magnitude = np.sqrt(vint_qvu**2 + vint_qvv**2)

# 降采样风向箭头
stride = (7, 7)  # 每隔7个格点绘制一个箭头

# 绘制整层水汽通量矢量箭头
q = ax.quiver(
    lon[:: stride[1]],
    lat[:: stride[0]],
    vint_qvu[0, :: stride[0], :: stride[1]],
    vint_qvv[0, :: stride[0], :: stride[1]],
    angles="xy",
    scale=240,
    width=0.0030,
    transform=ccrs.PlateCarree(),
    color="black",  # 使用单一颜色表示方向
)

ax.quiverkey(q, 0.95, 1.025, 20, "1000", labelpos="E", color="b", labelcolor="b")

# 6. 使用 cartopy 和 cnmaps 绘制行政区划和栅格数据
# 获取河南省和郑州市的行政边界
henan = get_adm_maps(province="河南省", only_polygon=True, record="first")
zhengzhou = get_adm_maps(city="郑州市", only_polygon=True, record="first")

draw_map(henan, ax=ax, color="r", linewidth=1.5)

# 设置标题
ax.set_title("XXXXXXXXX整层水汽通量")

plt.show()
