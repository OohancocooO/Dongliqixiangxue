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

# 获取时间单位并计算实际时间点
time_units = time_var.units
time_calendar = time_var.calendar if hasattr(time_var, 'calendar') else 'standard'
time_points = nc.num2date(time_var[:], units=time_units, calendar=time_calendar)

# 创建保存图片的文件夹
output_dir = r"D:\新建文件夹\jieguo"
os.makedirs(output_dir, exist_ok=True)

# 准备动图绘制
fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})

# 初始数据处理和平滑
initial_data = tp[0, :, :]
smoothed_data = gaussian_filter(initial_data, sigma=1)

# 插值
points = np.array([lon_grid.ravel(), lat_grid.ravel()]).T
values = smoothed_data.ravel()
grid_lon, grid_lat = np.meshgrid(np.linspace(110, 115, 100), np.linspace(32, 37, 100))
interpolated_data = griddata(points, values, (grid_lon, grid_lat), method='cubic')

# 设置固定的颜色范围
vmin = tp[:].min()
vmax = tp[:].max()

mesh = ax.pcolormesh(grid_lon, grid_lat, interpolated_data, cmap='Blues', shading='auto', transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax)
colorbar = fig.colorbar(mesh, ax=ax, label='降水量 (mm)')
ax.set_title('降水量图')
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

# 动画更新函数
def update(frame):
    current_time = time_points[frame]
    data = tp[frame, :, :]
    smoothed_data = gaussian_filter(data, sigma=1)

    # 插值
    values = smoothed_data.ravel()
    interpolated_data = griddata(points, values, (grid_lon, grid_lat), method='cubic')

    mesh.set_array(interpolated_data.ravel())
    ax.set_title(f'降水量图 {current_time.strftime("%Y-%m-%d %H:%M")}')

    # 保存未插值的原始降水图
    fig_orig, ax_orig = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    ax_orig.pcolormesh(lon_grid, lat_grid, data, cmap='Blues', shading='auto', transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax)
    ax_orig.coastlines()
    cnmaps.draw_maps(henan, ax=ax_orig, linewidth=1.0, color='black')
    cnmaps.draw_maps(zhengzhou, ax=ax_orig, linewidth=1.0, color='red')
    ax_orig.set_extent([110, 115, 32, 37], crs=ccrs.PlateCarree())  # 设置经纬度范围
    ax_orig.set_title(f'原始降水量图 {current_time.strftime("%Y-%m-%d %H:%M")}')
    ax_orig.set_xlabel('经度')
    ax_orig.set_ylabel('纬度')
    ax_orig.set_xticks(np.arange(110, 116, 1), crs=ccrs.PlateCarree())
    ax_orig.set_yticks(np.arange(32, 38, 1), crs=ccrs.PlateCarree())
    ax_orig.xaxis.set_major_formatter(lon_formatter)
    ax_orig.yaxis.set_major_formatter(lat_formatter)
    ax_orig.gridlines(draw_labels=True)
    fig_orig.colorbar(
        ax_orig.pcolormesh(lon_grid, lat_grid, data, cmap='Blues', shading='auto', transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax),
        ax=ax_orig, label='降水量 (mm)')
    fig_orig.savefig(f'{output_dir}/original_precipitation_{current_time.strftime("%Y%m%d%H%M")}.png')
    plt.close(fig_orig)

    return mesh,


# 生成动画
ani = animation.FuncAnimation(fig, update, frames=len(time_points), interval=200, repeat=False)

# 保存动画
output_file = r'D:\新建文件夹\jieguo\precipitation_animation.gif'
ani.save(output_file, writer='pillow', fps=3)

# 提示保存完成
print(f"Saved precipitation animation as {output_file}")

# 关闭NetCDF文件
dataset.close()
