import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
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
        hgt = dataset.sel(pressure_level=level).variables['z'][:]  # 指定层次的高度场
        lats = dataset.variables['latitude'][:]
        lons = dataset.variables['longitude'][:]
    except KeyError as e:
        raise KeyError(f"变量未找到: {e}")
    return hgt, lats, lons

def plot_height_field(lon_grid, lat_grid, hgt, output_file, level):
    henan = cnmaps.get_adm_maps(province='河南省')
    zhengzhou = cnmaps.get_adm_maps(city='郑州市')

    # 计算时间平均高度场
    hgt_mean = hgt.mean(axis=0)

    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent([110, 115, 32, 37], crs=ccrs.PlateCarree())  # 设置经纬度范围
    height_contour = ax.contourf(lon_grid, lat_grid, hgt_mean, cmap='viridis', alpha=0.6, transform=ccrs.PlateCarree())
    plt.colorbar(height_contour, ax=ax, orientation='horizontal', pad=0.05, label='高度 (m)')
    ax.set_title(f'{level} hPa 高度场')
    ax.set_xlabel('经度')
    ax.set_ylabel('纬度')
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.gridlines(draw_labels=True)

    # 添加河南省和郑州市边界
    cnmaps.draw_maps(henan, ax=ax, linewidth=1.0, color='black')
    cnmaps.draw_maps(zhengzhou, ax=ax, linewidth=1.0, color='red')

    # 保存图像
    plt.savefig(output_file)
    plt.close(fig)

def main():
    file_path = r"D:\Git desktop\dongliqixiang\ERA5 hourly data on pressure levels from 1940 to present.nc"
    output_file = r"D:\新建文件夹\500hpa_height_field.png"

    dataset = load_dataset(file_path)
    hgt, lats, lons = extract_variable(dataset, level=500)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    plot_height_field(lon_grid, lat_grid, hgt, output_file, level='500')

    dataset.close()
    print(f"Saved 500 hPa height field as {output_file}")

if __name__ == "__main__":
    main()
