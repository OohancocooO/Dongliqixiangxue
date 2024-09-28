import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cnmaps import get_adm_maps
import numpy as np

# 读取数据集文件（假设文件名为 'data.nc'）
ds = xr.open_dataset("single levels.nc")

# 获取时间变量
times = ds["valid_time"].values

# 获取河南省和郑州市的行政边界
henan = get_adm_maps(province="河南省", only_polygon=True, record="first")
zhengzhou = get_adm_maps(city="郑州市", only_polygon=True, record="first")

# 设置投影为Mercator投影
projection = ccrs.PlateCarree()

# 绘制每小时的降水数据
for t in times:
    plt.figure(figsize=(10, 8))

    # 创建一个带投影的图形
    ax = plt.axes(projection=projection)

    # 绘制栅格数据
    ds["tp"].sel(time=t).plot(
        ax=ax,
        cmap="Blues",
        cbar_kwargs={"label": "Total Precipitation (mm)"},
        transform=projection,
    )

    # 绘制中国和河南省的行政区划
    ax.add_geometries(
        henan["geometry"],
        crs=projection,
        edgecolor="black",
        facecolor="none",
        linewidth=1,
        label="河南省",
    )
    ax.add_geometries(
        zhengzhou["geometry"],
        crs=projection,
        edgecolor="red",
        facecolor="none",
        linewidth=1,
        label="郑州市",
    )

    # 添加一些地图特征
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=":")

    # 设置图的标题
    plt.title(f"Total Precipitation at {str(t)}")

    plt.show()
