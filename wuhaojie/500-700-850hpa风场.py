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

def extract_variables(dataset, level):
    try:
        u = dataset.sel(pressure_level=level).variables['u'][:]  # 指定层次的u-风分量
        v = dataset.sel(pressure_level=level).variables['v'][:]  # 指定层次的v-风分量
        time_var = dataset.variables['valid_time'][:]  # 时间变量
        lats = dataset.variables['latitude'][:]
        lons = dataset.variables['longitude'][:]
    except KeyError as e:
        raise KeyError(f"变量未找到: {e}")
    return u, v, time_var, lats, lons

def save_wind_frames(lon_grid, lat_grid, u, v, time_points, output_dir, level):
    henan = cnmaps.get_adm_maps(province='河南省')
    zhengzhou = cnmaps.get_adm_maps(city='郑州市')

    for frame in range(len(time_points)):
        current_time = pd.to_datetime(time_points[frame])
        u_frame = u[frame, :, :]  # u-风分量
        v_frame = v[frame, :, :]  # v-风分量

        # 计算风速
        wind_speed = np.sqrt(u_frame**2 + v_frame**2)

        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([110, 115, 32, 37], crs=ccrs.PlateCarree())  # 设置经纬度范围
        wind_contour = ax.contourf(lon_grid, lat_grid, wind_speed, cmap='viridis', alpha=0.6, transform=ccrs.PlateCarree())
        plt.colorbar(wind_contour, ax=ax, orientation='horizontal', pad=0.05, label='风速 (m/s)')
        ax.quiver(lon_grid, lat_grid, u_frame, v_frame, transform=ccrs.PlateCarree(), scale=100, width=0.002)  # 调整箭头大小
        ax.set_title(f'{level} hPa 风场 {current_time.strftime("%Y-%m-%d %H:%M")}')
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
    file_path = r"D:\Git desktop\dongliqixiang\ERA5 hourly data on pressure levels from 1940 to present.nc"
    wind_500_output_dir = r"D:\新建文件夹\500hpa_wind"
    wind_700_output_dir = r"D:\新建文件夹\700hpa_wind"
    wind_850_output_dir = r"D:\新建文件夹\850hpa_wind"
    wind_500_output_file = os.path.join(wind_500_output_dir, '500hpa_wind_animation.gif')
    wind_700_output_file = os.path.join(wind_700_output_dir, '700hpa_wind_animation.gif')
    wind_850_output_file = os.path.join(wind_850_output_dir, '850hpa_wind_animation.gif')

    os.makedirs(wind_500_output_dir, exist_ok=True)
    os.makedirs(wind_700_output_dir, exist_ok=True)
    os.makedirs(wind_850_output_dir, exist_ok=True)

    dataset = load_dataset(file_path)
    u500, v500, time_var, lats, lons = extract_variables(dataset, level=500)
    u700, v700, _, _, _ = extract_variables(dataset, level=700)
    u850, v850, _, _, _ = extract_variables(dataset, level=850)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # 使用pandas处理时间变量
    time_points = pd.to_datetime(time_var)

    save_wind_frames(lon_grid, lat_grid, u500, v500, time_points, wind_500_output_dir, level='500')
    save_wind_frames(lon_grid, lat_grid, u700, v700, time_points, wind_700_output_dir, level='700')
    save_wind_frames(lon_grid, lat_grid, u850, v850, time_points, wind_850_output_dir, level='850')
    create_animation_from_images(wind_500_output_dir, wind_500_output_file)
    create_animation_from_images(wind_700_output_dir, wind_700_output_file)
    create_animation_from_images(wind_850_output_dir, wind_850_output_file)

    dataset.close()
    print(f"Saved 500 hPa wind animation as {wind_500_output_file}")
    print(f"Saved 700 hPa wind animation as {wind_700_output_file}")
    print(f"Saved 850 hPa wind animation as {wind_850_output_file}")

if __name__ == "__main__":
    main()
