import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cnmaps

# 设置matplotlib支持中文显示
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'


def load_dataset(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件未找到: {file_path}")
    try:
        dataset = nc.Dataset(file_path)
    except OSError as e:
        raise RuntimeError(f"无法打开文件: {e}")
    return dataset


def extract_variables(dataset):
    try:
        viwvn = dataset.variables['viwvn'][:]  # 东向水汽通量垂直积分
        viwve = dataset.variables['viwve'][:]  # 北向水汽通量垂直积分
        time_var = dataset.variables['valid_time'][:]  # 时间变量
        lats = dataset.variables['latitude'][:]
        lons = dataset.variables['longitude'][:]
    except KeyError as e:
        raise KeyError(f"变量未找到: {e}")
    return viwvn, viwve, time_var, lats, lons


def save_frames(lon_grid, lat_grid, viwvn, viwve, time_points, output_dir):
    henan = cnmaps.get_adm_maps(province='河南省')
    zhengzhou = cnmaps.get_adm_maps(city='郑州市')

    for frame in range(len(time_points)):
        current_time = time_points[frame]
        u = viwvn[frame, :, :]  # 东向水汽通量
        v = viwve[frame, :, :]  # 北向水汽通量

        fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
        ax.set_extent([110, 115, 32, 37], crs=ccrs.PlateCarree())  # 设置经纬度范围
        ax.quiver(lon_grid, lat_grid, u, v, transform=ccrs.PlateCarree())
        ax.set_title(f'整层水汽通量矢量场 {current_time.strftime("%Y-%m-%d %H:%M")}')
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
    output_file = os.path.join(output_dir, '850hpa_vector_field_animation.gif')

    os.makedirs(output_dir, exist_ok=True)

    dataset = load_dataset(file_path)
    viwvn, viwve, time_var, lats, lons = extract_variables(dataset)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    time_units = dataset.variables['valid_time'].units
    time_calendar = dataset.variables['valid_time'].calendar if hasattr(dataset.variables['valid_time'],
                                                                        'calendar') else 'standard'
    time_points = nc.num2date(time_var, units=time_units, calendar=time_calendar)

    save_frames(lon_grid, lat_grid, viwvn, viwve, time_points, output_dir)
    create_animation_from_images(output_dir, output_file)

    dataset.close()
    print(f"Saved vector field animation as {output_file}")


if __name__ == "__main__":
    main()
