import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cnmaps import get_adm_maps, draw_map
from datetime import datetime, timedelta
import os
from rasterio.merge import merge
from rasterio.mask import mask
from rasterio.io import MemoryFile
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from shapely.geometry import box
import geopandas as gpd
import rasterio

# 打开nc文件并加载数据
rd = xr.open_dataset("ERA5 hourly data on pressure levels from 1940 to present.nc")
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 设置时间范围
start_time = datetime(2021, 7, 17)
end_time = datetime(2021, 7, 20, 23)
pressure_level = 1000

# 经纬度范围
lat_min, lat_max = 32, 37
lon_min, lon_max = 110, 115

# 获取地图数据
henan = get_adm_maps(province="河南省", only_polygon=True, record="first")
zhengzhou = get_adm_maps(city="郑州市", only_polygon=True, record="first")

# 读取地形数据
tif_files = []
for lat in range(lat_min, lat_max):
    for lon in range(lon_min, lon_max):
        filename = f"D:\Study\Yunnan Uni\动力气象学\Map\ALPSMLC30_N{str(lat).zfill(3)}E{str(lon).zfill(3)}_DSM.tif"
        if os.path.exists(filename):
            tif_files.append(filename)
        else:
            print(f"文件未找到：{filename}")

if not tif_files:
    raise FileNotFoundError("未找到任何匹配的TIFF文件。请检查文件路径和名称。")

src_files_to_mosaic = []
for fp in tif_files:
    src = rasterio.open(fp)
    src_files_to_mosaic.append(src)

mosaic, out_trans = merge(src_files_to_mosaic)

out_meta = src.meta.copy()
out_meta.update(
    {
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_trans,
        "crs": src.crs,
    }
)

# 裁剪地形数据
bbox = box(lon_min, lat_min, lon_max, lat_max)
geo = gpd.GeoDataFrame({"geometry": [bbox]}, crs="EPSG:4326")
geo = geo.to_crs(crs=out_meta["crs"])

with MemoryFile() as memfile:
    with memfile.open(**out_meta) as dataset:
        dataset.write(mosaic)
        out_image, out_transform = mask(dataset=dataset, shapes=geo.geometry, crop=True)
        out_meta.update(
            {
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
            }
        )

# 创建自定义色标
colors = [
    (0 / 255, 201 / 255, 50 / 255),
    (30 / 255, 211 / 255, 104 / 255),
    (94 / 255, 224 / 255, 116 / 255),
    (162 / 255, 235 / 255, 130 / 255),
    (223 / 255, 248 / 255, 146 / 255),
    (246 / 255, 229 / 255, 149 / 255),
    (200 / 255, 178 / 255, 118 / 255),
    (162 / 255, 126 / 255, 94 / 255),
    (143 / 255, 97 / 255, 84 / 255),
]
cmap = ListedColormap(colors)

# 在主循环中合并风向图和地形图
current_time = start_time
while current_time <= end_time:
    time_selected = current_time.strftime("%Y-%m-%dT%H:%M:%S")

    # 提取风速数据
    u_850 = rd["u"].sel(valid_time=time_selected, pressure_level=pressure_level)
    v_850 = rd["v"].sel(valid_time=time_selected, pressure_level=pressure_level)

    u_850 = u_850.sel(
        longitude=slice(lon_min, lon_max), latitude=slice(lat_max, lat_min)
    )
    v_850 = v_850.sel(
        longitude=slice(lon_min, lon_max), latitude=slice(lat_max, lat_min)
    )

    # 创建图形
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection=ccrs.PlateCarree())

    # 绘制地形图
    extent = [lon_min, lon_max, lat_min, lat_max]
    ax.imshow(out_image[0], cmap=cmap, extent=extent, origin="upper")

    # 绘制风向箭头
    step = 1
    ax.quiver(
        u_850.longitude[::step],
        u_850.latitude[::step],
        u_850[::step, ::step],
        v_850[::step, ::step],
        scale=150,
        transform=ccrs.PlateCarree(),
    )

    # 绘制地图边界
    draw_map(henan, ax=ax, lw=1, color="black")
    draw_map(zhengzhou, ax=ax, lw=1.5, color="r")

    # 添加经纬度网格线和刻度标签
    gl = ax.gridlines(
        draw_labels=True,
        crs=ccrs.PlateCarree(),
        linewidth=1,
        color="gray",
        alpha=0,
        linestyle="--",
    )
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {"size": 10}
    gl.ylabel_style = {"size": 10}

    # 设置标题和显示范围
    ax.set_title(
        f"在{pressure_level}hPa气压下的风向图与地形图 时间：{time_selected}",
        fontsize=16,
    )
    ax.set_xlim([lon_min, lon_max])
    ax.set_ylim([lat_min, lat_max])

    # 保存图片
    safe_filename = time_selected.replace(":", "_")
    output_dir = r"D:\Study\Yunnan Uni\Dongliqixiangxue\wind_direction"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"wind_direction_{safe_filename}.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    # 更新时间
    current_time += timedelta(hours=1)
    print(f"Processed: {time_selected}")

print("All images have been generated and saved.")
