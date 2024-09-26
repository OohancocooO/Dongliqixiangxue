import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
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
file_path = r"D:\pycharm\dongliqixiangxue\single levels.nc"

# 检查文件路径是否存在
if not os.path.exists(file_path):
    raise FileNotFoundError(f"文件未找到: {file_path}")

# 打开NetCDF文件
try:
    dataset = nc.Dataset(file_path)
except OSError as e:
    raise RuntimeError(f"无法打开文件: {e}")

# 提取对流降水和大尺度降水变量数据
try:
    cp = dataset.variables['cp'][:] * 100  # 转换为厘米
    lsp = dataset.variables['lsp'][:] * 100  # 转换为厘米
    valid_time_var = dataset.variables['valid_time']  # 时间变量
    print(f"cp shape: {cp.shape}")
    print(f"lsp shape: {lsp.shape}")
except KeyError as e:
    raise KeyError(f"变量未找到: {e}")

# 获取经纬度数据
lats = dataset.variables['latitude'][:]
lons = dataset.variables['longitude'][:]

# 创建网格
lon_grid, lat_grid = np.meshgrid(lons, lats)

# 获取时间单位并计算实际时间点
time_units = valid_time_var.units
time_calendar = valid_time_var.calendar if hasattr(valid_time_var, 'calendar') else 'standard'
time_points = nc.num2date(valid_time_var[:], units=time_units, calendar=time_calendar)

# 创建保存图片的文件夹
output_dir = r"D:\新建文件夹\duibi"
os.makedirs(output_dir, exist_ok=True)

# 准备动图绘制
fig, axs = plt.subplots(2, 1, figsize=(12, 16), subplot_kw={'projection': ccrs.PlateCarree()})

# 设置固定的颜色范围
vmin = min(cp.min(), lsp.min())
vmax = max(cp.max(), lsp.max())

# 初始化图像
initial_cp = cp[0, :, :]
initial_lsp = lsp[0, :, :]
smoothed_cp = gaussian_filter(initial_cp, sigma=1)
smoothed_lsp = gaussian_filter(initial_lsp, sigma=1)

# 插值
points = np.array([lon_grid.ravel(), lat_grid.ravel()]).T
cp_values = smoothed_cp.ravel()
lsp_values = smoothed_lsp.ravel()
grid_lon, grid_lat = np.meshgrid(np.linspace(110, 115, 100), np.linspace(32, 37, 100))
interpolated_cp = griddata(points, cp_values, (grid_lon, grid_lat), method='cubic')
interpolated_lsp = griddata(points, lsp_values, (grid_lon, grid_lat), method='cubic')

# 绘制对流降水图
mesh_cp = axs[0].pcolormesh(grid_lon, grid_lat, interpolated_cp, cmap='Blues', shading='auto', transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax)
colorbar_cp = fig.colorbar(mesh_cp, ax=axs[0], label='对流降水量 (cm)')
axs[0].set_title('对流降水量图')
axs[0].set_xlabel('经度')
axs[0].set_ylabel('纬度')

# 绘制大尺度降水图
mesh_lsp = axs[1].pcolormesh(grid_lon, grid_lat, interpolated_lsp, cmap='Blues', shading='auto', transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax)
colorbar_lsp = fig.colorbar(mesh_lsp, ax=axs[1], label='大尺度降水量 (cm)')
axs[1].set_title('大尺度降水量图')
axs[1].set_xlabel('经度')
axs[1].set_ylabel('纬度')

# 设置经纬度网格线格式
for ax in axs:
    ax.set_xticks(np.arange(110, 116, 1), crs=ccrs.PlateCarree())
    ax.set_yticks(np.arange(32, 38, 1), crs=ccrs.PlateCarree())
    lon_formatter = cticker.LongitudeFormatter()
    lat_formatter = cticker.LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.gridlines(draw_labels=True)
    ax.set_extent([110, 115, 32, 37], crs=ccrs.PlateCarree())  # 设置经纬度范围

    # 添加河南省省界
    henan = cnmaps.get_adm_maps(province='河南省')
    cnmaps.draw_maps(henan, ax=ax, linewidth=1.0, color='black')

    # 添加郑州市市界
    zhengzhou = cnmaps.get_adm_maps(city='郑州市')
    cnmaps.draw_maps(zhengzhou, ax=ax, linewidth=1.0, color='red')

# 动画更新函数
def update(frame):
    current_time = time_points[frame]
    cp_data = cp[frame, :, :]
    lsp_data = lsp[frame, :, :]
    smoothed_cp = gaussian_filter(cp_data, sigma=1)
    smoothed_lsp = gaussian_filter(lsp_data, sigma=1)

    # 插值
    cp_values = smoothed_cp.ravel()
    lsp_values = smoothed_lsp.ravel()
    interpolated_cp = griddata(points, cp_values, (grid_lon, grid_lat), method='cubic')
    interpolated_lsp = griddata(points, lsp_values, (grid_lon, grid_lat), method='cubic')

    mesh_cp.set_array(interpolated_cp.ravel())
    mesh_lsp.set_array(interpolated_lsp.ravel())
    axs[0].set_title(f'对流降水量图 {current_time.strftime("%Y-%m-%d %H:%M")}')
    axs[1].set_title(f'大尺度降水量图 {current_time.strftime("%Y-%m-%d %H:%M")}')

    # 保存每一帧的对比图
    frame_output_file = os.path.join(output_dir, f'precipitation_comparison_{current_time.strftime("%Y%m%d%H%M")}.png')
    plt.savefig(frame_output_file)

    return mesh_cp, mesh_lsp

# 生成动画
ani = animation.FuncAnimation(fig, update, frames=len(time_points), interval=200, repeat=False)

# 保存动画
output_file = r'D:\新建文件夹\duibi\precipitation_comparison_animation.gif'
ani.save(output_file, writer='pillow', fps=3)

# 提示保存完成
print(f"Saved precipitation comparison animation as {output_file}")

# 关闭NetCDF文件
dataset.close()
