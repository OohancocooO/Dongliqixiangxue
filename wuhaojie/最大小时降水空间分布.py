import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.ndimage import gaussian_filter
from scipy.interpolate import griddata
import cnmaps
import cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker

# 设置matplotlib支持中文显示
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'

# 使用正确的文件路径
file_path = r"D:\pycharm\dongliqixiangxue\xiaochidu.nc"

# 检查文件路径是否存在
if not os.path.exists(file_path):
    raise FileNotFoundError(f"文件未找到: {file_path}")

# 打开NetCDF文件
try:
    dataset = nc.Dataset(file_path)
except OSError as e:
    raise RuntimeError(f"无法打开文件: {e}")

# 提取降水变量数据
try:
    tp = dataset.variables['tp']
    time_var = dataset.variables['time']  # 时间变量
    print(f"tp dimensions: {tp.dimensions}, shape: {tp.shape}")
except KeyError as e:
    raise KeyError(f"变量未找到: {e}")

# 获取经纬度数据
lats = dataset.variables['latitude'][:]
lons = dataset.variables['longitude'][:]

# 创建网格
lon_grid, lat_grid = np.meshgrid(lons, lats)

# 找到每个网格点的最大小时降水量
max_hourly_precipitation = np.max(tp[:], axis=0)

# 平滑数据
smoothed_data = gaussian_filter(max_hourly_precipitation, sigma=1)

# 插值
points = np.array([lon_grid.ravel(), lat_grid.ravel()]).T
values = smoothed_data.ravel()
grid_lon, grid_lat = np.meshgrid(np.linspace(lons.min(), lons.max(), 500), np.linspace(lats.min(), lats.max(), 500))
interpolated_data = griddata(points, values, (grid_lon, grid_lat), method='cubic')

# 创建保存图片的文件夹
output_dir = r"D:\新建文件夹\最大小时空间分布"
os.makedirs(output_dir, exist_ok=True)

# 绘制最大小时降水量图
fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})

vmin = max_hourly_precipitation.min()
vmax = max_hourly_precipitation.max()

mesh = ax.pcolormesh(grid_lon, grid_lat, interpolated_data, cmap='Blues', shading='auto', transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax)
colorbar = fig.colorbar(mesh, ax=ax, label='最大小时降水量 (mm)')
ax.set_title('最大小时降水量图')
ax.set_xlabel('经度')
ax.set_ylabel('纬度')

# 设置经纬度网格线格式
ax.set_xticks(np.arange(110, 116, 1), crs=ccrs.PlateCarree())
ax.set_yticks(np.arange(32, 38, 1), crs=ccrs.PlateCarree())
lon_formatter = cticker.LongitudeFormatter()
lat_formatter = cticker.LatitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter)
ax.yaxis.set_major_formatter(lat_formatter)
ax.gridlines(draw_labels=True)

# 添加河南省省界
henan = cnmaps.get_adm_maps(province='河南省')
cnmaps.draw_maps(henan, ax=ax, linewidth=1.0, color='black')

# 添加郑州市市界
zhengzhou = cnmaps.get_adm_maps(city='郑州市')
cnmaps.draw_maps(zhengzhou, ax=ax, linewidth=1.0, color='red')

# 设置经纬度范围
ax.set_extent([110, 115, 32, 37], crs=ccrs.PlateCarree())

# 保存图像
output_file = os.path.join(output_dir, 'max_hourly_precipitation.png')
fig.savefig(output_file)

# 提示保存完成
print(f"Saved max hourly precipitation map as {output_file}")

# 关闭NetCDF文件
dataset.close()
