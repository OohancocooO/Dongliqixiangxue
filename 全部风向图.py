import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cnmaps import get_adm_maps, draw_map
from datetime import datetime, timedelta
import os

# 打开nc文件并加载数据
rd = xr.open_dataset("ERA5 hourly data on pressure levels from 1940 to present.nc")
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 设置时间范围
start_time = datetime(2021, 7, 17)
end_time = datetime(2021, 7, 20, 23)
pressure_level = 1000

# 获取地图数据
henan = get_adm_maps(province="河南省", only_polygon=True, record="first")
zhengzhou = get_adm_maps(city="郑州市", only_polygon=True, record="first")

# 限制绘图的经纬度范围
lon_min, lon_max = 110, 116
lat_min, lat_max = 32, 37
# 在主循环中修改保存图片的部分
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

    # 定义风速大于0和小于0的部分
    u_greater_than_0 = u_850.where((u_850 < 0) & (v_850 > 0))  # 东南风
    u_less_than_0 = u_850.where((u_850 > 0) & (v_850 < 0))  # 西北风

    # 创建经纬度网格
    lon_greater_than_0, lat_greater_than_0 = np.meshgrid(
        u_greater_than_0.longitude, u_greater_than_0.latitude
    )
    lon_less_than_0, lat_less_than_0 = np.meshgrid(
        u_less_than_0.longitude, u_less_than_0.latitude
    )

    # 创建图形
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection=ccrs.PlateCarree())

    # 填充风向区域
    ax.contourf(
        lon_greater_than_0,
        lat_greater_than_0,
        u_greater_than_0.squeeze(),
        colors="#FFFFCC",
        transform=ccrs.PlateCarree(),
    )
    ax.contourf(
        lon_less_than_0,
        lat_less_than_0,
        u_less_than_0.squeeze(),
        colors="#FFCCCC",
        transform=ccrs.PlateCarree(),
    )

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
        f"在{pressure_level}hPa气压下的风向图 时间：{time_selected}", fontsize=16
    )
    ax.set_xlim([lon_min, lon_max])
    ax.set_ylim([lat_min, lat_max])

    # 修改文件名格式
    safe_filename = time_selected.replace(":", "_")
    output_dir = r"D:\Study\Yunnan Uni\Dongliqixiangxue\wind_direction_images"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"wind_direction_{safe_filename}.png")
    
    # 保存图片
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    # 更新时间
    current_time += timedelta(hours=1)
    print(f"Processed: {time_selected}")

print("All images have been generated and saved.")
