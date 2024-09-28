import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

# 加载NetCDF文件
ds = xr.open_dataset("wind.nc")

# 提取需要的变量
u = ds["u"]
v = ds["v"]
w = ds["w"]
pressure_levels = [200.0, 500.0, 850.0, 925.0]

# 定义降采样因子，比如将经度和纬度都降采样为每隔4个点采样1个点
downsample_factor = 4

# 创建绘图网格
fig, axes = plt.subplots(2, 2, figsize=(16, 12), constrained_layout=True)

# 循环绘制每个气压层的风向和垂直速度填色图
for i, p_level in enumerate(pressure_levels):
    ax = axes[i // 2, i % 2]

    # 提取该气压层的数据，并进行降采样
    u_level = (
        u.sel(pressure_level=p_level)
        .coarsen(
            latitude=downsample_factor, longitude=downsample_factor, boundary="trim"
        )
        .mean()
    )
    v_level = (
        v.sel(pressure_level=p_level)
        .coarsen(
            latitude=downsample_factor, longitude=downsample_factor, boundary="trim"
        )
        .mean()
    )
    w_level = (
        w.sel(pressure_level=p_level)
        .coarsen(
            latitude=downsample_factor, longitude=downsample_factor, boundary="trim"
        )
        .mean()
    )

    # 创建经纬度网格
    lon, lat = np.meshgrid(u_level["longitude"], u_level["latitude"])

    # 绘制风向图
    ax.quiver(lon, lat, u_level.values, v_level.values, scale=500)

    # 绘制垂直速度的填色图
    contour = ax.contourf(lon, lat, w_level, cmap="RdBu_r", levels=20, alpha=0.6)

    # 设置标题和标签
    ax.set_title(f"{p_level} hPa Wind and Vertical Velocity")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

# 添加垂直速度的颜色条
fig.colorbar(
    contour,
    ax=axes.ravel().tolist(),
    orientation="vertical",
    label="Vertical Velocity (w)",
)

# 显示图像
plt.show()
