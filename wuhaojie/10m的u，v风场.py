import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
from datetime import datetime, timedelta
import cartopy.crs as ccrs
import cartopy.mpl.ticker as cticker
import imageio
from cnmaps import get_adm_maps, draw_maps

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

# 提取风场变量数据
try:
    u10 = dataset.variables['u10']
    v10 = dataset.variables['v10']
    time_var = dataset.variables['time']  # 时间变量
    print(f"u10 dimensions: {u10.dimensions}, shape: {u10.shape}")
    print(f"v10 dimensions: {v10.dimensions}, shape: {v10.shape}")
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
output_dir = r"D:\新建文件夹\10muv"
os.makedirs(output_dir, exist_ok=True)

# 准备动图绘制
fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})

# 设置经纬度网格线格式
ax.set_xticks(np.arange(110, 116, 1), crs=ccrs.PlateCarree())
ax.set_yticks(np.arange(32, 38, 1), crs=ccrs.PlateCarree())
lon_formatter = cticker.LongitudeFormatter()
lat_formatter = cticker.LatitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter)
ax.yaxis.set_major_formatter(lat_formatter)
ax.gridlines(draw_labels=True)

# 初始化风场图
u = u10[0, :, :]
v = v10[0, :, :]
speed = np.sqrt(u ** 2 + v ** 2)
quiver = ax.quiver(lon_grid, lat_grid, u, v, speed, transform=ccrs.PlateCarree(), scale=50, cmap='coolwarm')
ax.coastlines()
ax.set_extent([110, 115, 32, 37], crs=ccrs.PlateCarree())  # 设置经纬度范围
ax.set_title(f'10m处风场 {time_points[0].strftime("%Y-%m-%d %H:%M")}')
ax.set_xlabel('经度')
ax.set_ylabel('纬度')

# 添加颜色条
cbar = fig.colorbar(quiver, ax=ax, orientation='vertical', label='风速 (m/s)')

# 添加河南省省界和郑州市市界
henan = get_adm_maps(province='河南省')
zhengzhou = get_adm_maps(city='郑州市')
draw_maps(henan, ax=ax, linewidth=1.0, color='black')
draw_maps(zhengzhou, ax=ax, linewidth=1.0, color='red')  # 修改郑州市界颜色为红色


# 动画更新函数
def update(frame):
    current_time = time_points[frame]
    u = u10[frame, :, :]
    v = v10[frame, :, :]
    speed = np.sqrt(u ** 2 + v ** 2)

    quiver.set_UVC(u, v, speed)
    ax.set_title(f'10m处风场 {current_time.strftime("%Y-%m-%d %H:%M")}')

    # 保存图片
    fig.savefig(f'{output_dir}/wind_{current_time.strftime("%Y%m%d%H%M")}.png')
    return quiver,


# 生成动画
ani = animation.FuncAnimation(fig, update, frames=len(time_points), interval=200, repeat=False)

# 保存动画
output_file = r'D:\新建文件夹\10muv\wind_animation.gif'
ani.save(output_file, writer='pillow', fps=3)

# 提示保存完成
print(f"Saved wind field animation as {output_file}")

# 关闭NetCDF文件
dataset.close()
