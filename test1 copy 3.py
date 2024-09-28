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

# 定义降采样步长
step = 10  # 可以根据数据分辨率调整这个值

# 创建绘图网格
fig, axes = plt.subplots(2, 2, figsize=(16, 12), constrained_layout=True)

# 循环绘制每个气压层的风向和垂直速度填色图
for i, p_level in enumerate(pressure_levels):
    ax = axes[i // 2, i % 2]

    # 提取该气压层的数据
    u_level = u.sel(pressure_level=p_level).squeeze()
    v_level = v.sel(pressure_level=p_level).squeeze()
    w_level = w.sel(pressure_level=p_level).squeeze()

    # 创建经纬度网格
    lon, lat = np.meshgrid(ds["longitude"], ds["latitude"])

    # 对经纬度和风场数据进行降采样
    lon_downsampled = lon[::step, ::step]
    lat_downsampled = lat[::step, ::step]
    u_downsampled = u_level[::step, ::step]
    v_downsampled = v_level[::step, ::step]

    # 绘制风向图（降采样后）
    ax.quiver(
        lon_downsampled,
        lat_downsampled,
        u_downsampled,
        v_downsampled,
        scale=500,
        color="black",
    )
    # 绘制垂直速度的填色图
    contour = ax.contourf(lon, lat, w_level, cmap="RdBu_r", levels=20, alpha=0.6)

    # 设置标题和标签
    ax.set_title(f"{p_level} hPa")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
fig.colorbar(
        contour,
        ax=axes.ravel().tolist(),
        orientation="vertical",
        label="Vertical Velocity (w)",
)

# 显示图像
plt.show()
