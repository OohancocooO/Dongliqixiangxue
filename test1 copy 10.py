import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cnmaps import get_adm_maps, draw_map

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 加载数据
ds = xr.open_dataset("xiaochidu.nc")

# 获取河南省和郑州市的行政边界
henan = get_adm_maps(province="河南省", only_polygon=True, record="first")
zhengzhou = get_adm_maps(city="郑州市", only_polygon=True, record="first")

# 用户输入时间列表
time_list = [
    "2021-07-17T23:00:00",
    "2021-07-18T23:00:00",
    "2021-07-19T23:00:00",
    "2021-07-20T23:00:00",
]
selected_times = [np.datetime64(t) for t in time_list]

# 创建 2x2 网格图
fig, axs = plt.subplots(
    2, 2, subplot_kw={"projection": ccrs.PlateCarree()}, figsize=(12, 10)
)
axs = axs.flatten()

# 设定图像的经纬度范围
extent = [110, 115, 32, 37]

# 找到所有时间点的最接近的数据
time_indices = [np.argmin(np.abs(ds.time.values - t)) for t in selected_times]

# 统一颜色范围
vmin = ds.tp.sel(time=selected_times).min().values * 1000
vmax = ds.tp.sel(time=selected_times).max().values * 1000

# 循环绘制每个时间点的降水图
for i, ax in enumerate(axs):
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    # 绘制降水图
    precip = ax.pcolormesh(
        ds.longitude,
        ds.latitude,
        ds.tp[time_indices[i], :, :].values * 1000,
        cmap="Blues",
        shading="auto",
        vmin=vmin,
        vmax=vmax,
    )

    # 添加河南省和郑州市的行政边界
    draw_map(henan, ax=ax, lw=1, color="black")
    draw_map(zhengzhou, ax=ax, lw=1.5, color="r")

    # 添加自然特征
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=":")
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

    # 设置标题
    ax.set_title(f"{np.datetime_as_string(ds.time.values[time_indices[i]], unit='D')}")

# 添加统一的颜色条
cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  # 颜色条的位置
cbar = fig.colorbar(
    precip, cax=cbar_ax, orientation="vertical", label="Total Precipitation (mm)"
)

# 调整布局，增加左右间隙 (wspace)
plt.tight_layout(rect=[0, 0, 0.9, 1])  # wspace 控制左右间隙

# 显示图像
plt.show()
