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

def extract_variable(dataset, level):
    try:
        rh = dataset.sel(pressure_level=level).variables['r'][:]  # 指定层次的相对湿度
        time_var = dataset.variables['valid_time'][:]  # 时间变量
        lats = dataset.variables['latitude'][:]
        lons = dataset.variables['longitude'][:]
    except KeyError as e:
        raise KeyError(f"变量未找到: {e}")
    return rh, time_var, lats, lons

def save_humidity_frames(lon_grid, lat_grid, rh, time_points, output_dir, level):
    henan = cnmaps.get_adm_maps(province='河南省')
    zhengzhou = cnmaps.get_adm_maps(city='郑州市')

    for frame in range(len(time_points)):
        current_time = pd.to_datetime(time_points[frame])
        rh_frame = rh[frame, :, :]  # 当前时间帧的相对湿度

        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([110, 115, 32, 37], crs=ccrs.PlateCarree())  # 设置经纬度范围
        rh_contour = ax.contourf(lon_grid, lat_grid, rh_frame, cmap='viridis', alpha=0.6, transform=ccrs.PlateCarree())
        plt.colorbar(rh_contour, ax=ax, orientation='horizontal', pad=0.05, label='相对湿度 (%)')
        ax.set_title(f'{level} hPa 相对湿度 {current_time.strftime("%Y-%m-%d %H:%M")}')
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
    rh_output_dir = r"D:\新建文件夹\500hpa_rh"
    rh_output_file = os.path.join(rh_output_dir, '500hpa_rh_animation.gif')

    os.makedirs(rh_output_dir, exist_ok=True)

    dataset = load_dataset(file_path)
    rh, time_var, lats, lons = extract_variable(dataset, level=500)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # 使用pandas处理时间变量
    time_points = pd.to_datetime(time_var)

    save_humidity_frames(lon_grid, lat_grid, rh, time_points, rh_output_dir, level='500')
    create_animation_from_images(rh_output_dir, rh_output_file)

    dataset.close()
    print(f"Saved 500 hPa relative humidity animation as {rh_output_file}")

if __name__ == "__main__":
    main()
