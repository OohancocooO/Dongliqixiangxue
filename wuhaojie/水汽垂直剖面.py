import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
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
        q = dataset['q'][:]  # 水汽混合比
        pressure = dataset['pressure_level'][:]  # 气压层
        time_var = dataset['valid_time'][:]  # 时间变量
        lats = dataset['latitude'][:]  # 直接使用 xarray 数据结构
        lons = dataset['longitude'][:]  # 直接使用 xarray 数据结构
    except KeyError as e:
        raise KeyError(f"变量未找到: {e}")
    return q, pressure, time_var, lats, lons

def save_vertical_profile_frames(lon, pressure, q, time_points, output_dir):
    for frame in range(len(time_points)):
        current_time = pd.to_datetime(time_points[frame])
        q_frame = q[frame, :, :]  # 当前时间帧的水汽混合比

        fig, ax1 = plt.subplots(figsize=(10, 8))

        # 绘制水汽混合比剖面
        q_contour = ax1.contourf(lon, pressure, q_frame, cmap='Blues', alpha=0.6)
        plt.colorbar(q_contour, ax=ax1, orientation='horizontal', pad=0.05, label='水汽混合比 (kg/kg)')
        ax1.set_title(f'水汽混合比垂直剖面 {current_time.strftime("%Y-%m-%d %H:%M")}')
        ax1.set_xlabel('经度')
        ax1.set_ylabel('气压 (hPa)')
        ax1.invert_yaxis()  # 翻转y轴，使气压从大到小

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
    file_path = r"D:\pycharm\dongliqixiangxue\ERA5 hourly data on pressure levels from 1940 to present.nc"
    output_dir = r"D:\新建文件夹\vertical_profile"
    output_file = os.path.join(output_dir, 'vertical_profile_animation.gif')

    os.makedirs(output_dir, exist_ok=True)

    dataset = load_dataset(file_path)
    q, pressure, time_var, lats, lons = extract_variables(dataset)

    # 选择北纬35度的剖面
    q_profile = q.sel(latitude=35, method='nearest')

    # 使用pandas处理时间变量
    time_points = pd.to_datetime(time_var)

    save_vertical_profile_frames(lons, pressure, q_profile, time_points, output_dir)
    create_animation_from_images(output_dir, output_file)

    dataset.close()
    print(f"Saved vertical profile animation as {output_file}")

if __name__ == "__main__":
    main()
