import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
from datetime import datetime, timedelta
from scipy.ndimage import gaussian_filter
from scipy.interpolate import griddata
import cnmaps
import cartopy.crs as ccrs

# 设置matplotlib支持中文显示
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'

# 使用正确的文件路径
file_path = r"D:\ERA5 hourly data on pressure levels from 1940 to present.nc"

# 检查文件路径是否存在
if not os.path.exists(file_path):
    raise FileNotFoundError(f"文件未找到: {file_path}")

# 打开NetCDF文件
try:
    dataset = nc.Dataset(file_path)
except OSError as e:
    raise RuntimeError(f"无法打开文件: {e}")

# 提取crwc变量数据
try:
    crwc = dataset.variables['crwc']
    time_var = dataset.variables['valid_time']  # 时间变量，假设是valid_time
    print(f"crwc dimensions: {crwc.dimensions}, shape: {crwc.shape}")
except KeyError as e:
    raise KeyError(f"变量未找到: {e}")

# 获取经纬度数据
lats = dataset.variables['latitude'][:]
lons = dataset.variables['longitude'][:]

# 创建网格
lon_grid, lat_grid = np.meshgrid(lons, lats)

# 获取时间维度长度
num_times = crwc.shape[0]  # 时间维度的长度

# 设置初始时间
start_time = datetime.strptime("2021:7月17日:00:00", "%Y:%m月%d日:%H:%M")

# 过滤掉7月17日的数据
filtered_indices = [i for i in range(num_times) if (start_time + timedelta(hours=i)).day != 17]
filtered_num_times = len(filtered_indices)

# 郑州市的经纬度
zhengzhou_lat = 34.76
zhengzhou_lon = 113.65

# 准备动图绘制
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': ccrs.PlateCarree()})

# 初始数据处理和平滑
initial_data = crwc[filtered_indices[0], :, :, :].sum(axis=0)
smoothed_data = gaussian_filter(initial_data, sigma=1)

# 插值
points = np.array([lon_grid.ravel(), lat_grid.ravel()]).T
values = smoothed_data.ravel()
grid_lon, grid_lat = np.meshgrid(np.linspace(lons.min(), lons.max(), 100), np.linspace(lats.min(), lats.max(), 100))
interpolated_data = griddata(points, values, (grid_lon, grid_lat), method='cubic')

mesh = ax.pcolormesh(grid_lon, grid_lat, interpolated_data, cmap='Blues', shading='auto', transform=ccrs.PlateCarree())
colorbar = fig.colorbar(mesh, ax=ax, label='降水量 (kg/m^2)')
ax.set_title('ERA5 降水量图')
ax.set_xlabel('经度')
ax.set_ylabel('纬度')

# 标注郑州市位置
zhengzhou_marker, = ax.plot(zhengzhou_lon, zhengzhou_lat, 'ro', label='郑州市', transform=ccrs.PlateCarree())  # 红色的点

# 添加河南省省界
henan = cnmaps.get_adm_maps(province='河南省')
cnmaps.draw_maps(henan, ax=ax, linewidth=1.0, color='black')

# 添加郑州市边界
zhengzhou = cnmaps.get_adm_maps(city='郑州市')
cnmaps.draw_maps(zhengzhou, ax=ax, linewidth=1.0, color='red')

# 添加图例
ax.legend(loc='upper right')


# 动画更新函数
def update(frame):
    current_time = start_time + timedelta(hours=filtered_indices[frame])
    data = crwc[filtered_indices[frame], :, :, :].sum(axis=0)
    smoothed_data = gaussian_filter(data, sigma=1)

    # 插值
    values = smoothed_data.ravel()
    interpolated_data = griddata(points, values, (grid_lon, grid_lat), method='cubic')

    mesh.set_array(interpolated_data.ravel())
    ax.set_title(f'ERA5 降水量图 {current_time.strftime("%Y:%m月%d日:%H:%M")}')
    return mesh,


# 生成动画
ani = animation.FuncAnimation(fig, update, frames=filtered_num_times, interval=200, repeat=False)

# 保存动画
output_file = 'precipitation_animation.gif'
ani.save(output_file, writer='pillow', fps=3)

# 提示保存完成
print(f"Saved precipitation animation as {output_file}")

# 关闭NetCDF文件
dataset.close()
