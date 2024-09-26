import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
from rasterio.io import MemoryFile
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import os
from shapely.geometry import box
import geopandas as gpd
import cartopy.crs as ccrs
from cnmaps import get_adm_maps, draw_map

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 指定默认字体
plt.rcParams["axes.unicode_minus"] = False  # 解决保存图像时负号显示为方块的问题

# 1. 定义需要的经纬度范围
lat_min, lat_max = 32, 37
lon_min, lon_max = 110, 115

# 2. 生成需要的文件名列表
tif_files = []
for lat in range(lat_min, lat_max):
    for lon in range(lon_min, lon_max):
        filename = f"ALPSMLC30_N{str(lat).zfill(3)}E{str(lon).zfill(3)}_DSM.tif"
        if os.path.exists(filename):
            tif_files.append(filename)
        else:
            print(f"文件未找到：{filename}")

# 检查是否找到TIFF文件
if not tif_files:
    raise FileNotFoundError("未找到任何匹配的TIFF文件。请检查文件路径和名称。")

# 3. 读取并合并TIFF文件
src_files_to_mosaic = []
for fp in tif_files:
    src = rasterio.open(fp)
    src_files_to_mosaic.append(src)

mosaic, out_trans = merge(src_files_to_mosaic)

# 获取栅格数据的CRS（坐标参考系统）
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

# 4. 裁剪到指定区域
# 创建裁剪范围的多边形
bbox = box(lon_min, lat_min, lon_max, lat_max)
geo = gpd.GeoDataFrame({"geometry": [bbox]}, crs="EPSG:4326")
geo = geo.to_crs(crs=out_meta["crs"])

# 在内存中创建一个栅格数据集，以便进行裁剪
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

# 5. 创建自定义色标
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

# 6. 使用 cartopy 和 cnmaps 绘制行政区划和栅格数据
# 获取河南省和郑州市的行政边界
henan = get_adm_maps(province="河南省", only_polygon=True, record="first")
zhengzhou = get_adm_maps(city="郑州市", only_polygon=True, record="first")

# 创建带有 PlateCarree 投影的绘图区域
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection=ccrs.PlateCarree())

# 绘制裁剪后的栅格数据，使用正确的 extent 映射到经纬度范围
extent = [lon_min, lon_max, lat_min, lat_max]
im = ax.imshow(out_image[0], cmap=cmap, extent=extent, origin="upper")

# 设置 x 和 y 轴的经纬度范围
ax.set_xlim(110, 115)
ax.set_ylim(32, 37)

# 绘制河南省和郑州市的行政边界
draw_map(henan, ax=ax)
draw_map(zhengzhou, ax=ax, color="r")

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

# 添加颜色条
cbar = fig.colorbar(im, ax=ax)
cbar.set_label("Elevation")

# 设置标题和坐标轴标签
ax.set_title("分层设色地形图")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# 显示图像
plt.show()
