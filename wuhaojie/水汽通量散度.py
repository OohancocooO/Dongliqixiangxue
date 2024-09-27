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

def extract_variables(dataset):
    try:
        u10 = dataset.variables['u10'][:]  # 10m u-风分量
        v10 = dataset.variables['v10'][:]  # 10m v-风分量
        tcwv = dataset.variables['tcwv'][:]  # 总柱水汽
        time_var = dataset.variables['valid_time'][:]  # 时间变量
        lats = dataset.variables['latitude'][:]
        lons = dataset.variables['longitude'][:]
    except KeyError as e:
        raise KeyError(f"变量未找到: {e}")
    return u10, v10, tcwv, time_var, lats, lons

def save_frames(lon_grid, lat_grid, u10, v10, tcwv, time_points, output_dir, vmin, vmax):
    henan = cnmaps.get_adm_maps(province='河南省')
    zhengzhou = cnmaps.get_adm_maps(city='郑州市')

    for frame in range(len(time_points)):
        current_time = time_points[frame]
        qu = u10[frame, :, :] * tcwv[frame, :, :]  # 东向水汽通量
        qv = v10[frame, :, :] * tcwv[frame, :, :]  # 北向水汽通量

        # 计算水汽通量散度
        divQ = np.gradient(qu, axis=-1) + np.gradient(qv, axis=-2)

        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([110, 115, 32, 37], crs=ccrs.PlateCarree())  # 设置经纬度范围
        contour = ax.contourf(lon_grid, lat_grid, divQ, cmap='coolwarm', transform=ccrs.PlateCarree(), vmin=vmin, vmax=vmax)
        plt.colorbar(contour, ax=ax, orientation='horizontal', pad=0.05, label='水汽通量散度')
        ax.set_title(f'水汽通量散度的空间分布 {current_time.strftime("%Y-%m-%d %H:%M")}')
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
    file_path = r"D:\pycharm\dongliqixiangxue\single levels.nc"
    output_dir = r"D:\新建文件夹\850hpa"
    output_file = os.path.join(output_dir, '850hpa_divergence_animation.gif')

    os.makedirs(output_dir, exist_ok=True)

    dataset = load_dataset(file_path)
    u10, v10, tcwv, time_var, lats, lons = extract_variables(dataset)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    # 使用pandas处理时间变量
    time_points = pd.to_datetime(time_var)

    # 计算水汽通量散度的全局最小值和最大值
    qu = u10 * tcwv
    qv = v10 * tcwv
    divQ = np.gradient(qu, axis=-1) + np.gradient(qv, axis=-2)
    vmin = divQ.min()
    vmax = divQ.max()

    save_frames(lon_grid, lat_grid, u10, v10, tcwv, time_points, output_dir, vmin, vmax)
    create_animation_from_images(output_dir, output_file)

    dataset.close()
    print(f"Saved divergence animation as {output_file}")

if __name__ == "__main__":
    main()
