import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cnmaps
import pandas as pd  # 导入pandas库

# 设置matplotlib支持中文显示
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'

def load_dataset(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件未找到: {file_path}")
    try:
        dataset = xr.open_dataset(file_path)
    except OSError as e:
        raise RuntimeError(f"无法打开文件: {e}")
    return dataset

def calculate_temperature_difference(t2m, d2m):
    # 计算2米温度和露点温度的差值
    temp_diff = t2m - d2m
    return temp_diff

def extract_variables(dataset):
    try:
        t2m = dataset.variables['t2m'][:]  # 2米温度
        d2m = dataset.variables['d2m'][:]  # 露点温度
        time_var = dataset.variables['time'][:]  # 时间变量
        lats = dataset.variables['latitude'][:]
        lons = dataset.variables['longitude'][:]
    except KeyError as e:
        raise KeyError(f"变量未找到: {e}")
    return t2m, d2m, time_var, lats, lons

def save_temp_diff_frames(lon_grid, lat_grid, temp_diff, time_points, output_dir):
    henan = cnmaps.get_adm_maps(province='河南省')
    zhengzhou = cnmaps.get_adm_maps(city='郑州市')

    for frame in range(len(time_points)):
        current_time = pd.to_datetime(time_points[frame])
        temp_diff_frame = temp_diff[frame, :, :]  # 当前时间帧的温度差

        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([110, 115, 32, 37], crs=ccrs.PlateCarree())  # 设置经纬度范围
        temp_diff_contour = ax.contourf(lon_grid, lat_grid, temp_diff_frame, cmap='coolwarm', alpha=0.6, transform=ccrs.PlateCarree())
        plt.colorbar(temp_diff_contour, ax=ax, orientation='horizontal', pad=0.05, label='温度差 (°C)')
        ax.set_title(f'2米温度和露点温度差 {current_time.strftime("%Y-%m-%d %H:%M")}')
        ax.set_xlabel('经度')
        ax.set_ylabel('纬度')
        ax.coastlines()
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.gridlines(draw_labels=True)

        # 添加河南省和郑州市边界
        cnmaps.draw_maps(henan, ax=ax, linewidth=1.0, color='black')
        cnmaps.draw_maps(zhengzhou, ax=ax, linewidth=1.0, color='red')

        # 保存图像
        output_file = os.path.join(output_dir, f'frame_{frame:03d}.png')
        plt.savefig(output_file)
        plt.close(fig)

def create_animation_from_images(output_dir, output_file):
    fig, ax = plt.subplots(figsize=(12, 8))
    images = []

    for frame in sorted(os.listdir(output_dir)):
        if frame.endswith('.png'):
            img = plt.imread(os.path.join(output_dir, frame))
            images.append([plt.imshow(img, animated=True)])

    ani = animation.ArtistAnimation(fig, images, interval=200, repeat=False)
    ani.save(output_file, writer='pillow', fps=3)
    plt.close(fig)

def main():
    file_path = r"D:\Git desktop\dongliqixiang\Dongliqixiangxue\xiaochidu.nc"
    temp_diff_output_dir = r"D:\新建文件夹\temp_diff"
    temp_diff_output_file = os.path.join(temp_diff_output_dir, 'temp_diff_animation.gif')

    os.makedirs(temp_diff_output_dir, exist_ok=True)

    dataset = load_dataset(file_path)
    t2m, d2m, time_var, lats, lons = extract_variables(dataset)
    temp_diff = calculate_temperature_difference(t2m, d2m)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # 使用pandas处理时间变量
    time_points = pd.to_datetime(time_var)

    save_temp_diff_frames(lon_grid, lat_grid, temp_diff, time_points, temp_diff_output_dir)
    create_animation_from_images(temp_diff_output_dir, temp_diff_output_file)

    dataset.close()
    print(f"Saved temperature difference animation as {temp_diff_output_file}")

if __name__ == "__main__":
    main()
