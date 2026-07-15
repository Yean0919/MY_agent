import numpy as np
import matplotlib.pyplot as plt

# 设置图形大小
plt.figure(figsize=(8, 8))

# 计算五角星的顶点坐标
n_points = 5
# 从顶部开始，顺时针排列
angles = np.linspace(np.pi/2, np.pi/2 + 2*np.pi, n_points, endpoint=False)

# 外圈和内圈半径
outer_radius = 10
inner_radius = 4

# 生成五角星的顶点（交替使用外圈和内圈）
star_x = []
star_y = []

for i in range(n_points):
    # 外圈顶点
    star_x.append(outer_radius * np.cos(angles[i]))
    star_y.append(outer_radius * np.sin(angles[i]))
    # 内圈顶点（在外圈顶点之间）
    inner_angle = angles[i] + np.pi / n_points
    star_x.append(inner_radius * np.cos(inner_angle))
    star_y.append(inner_radius * np.sin(inner_angle))

# 闭合星星
star_x.append(star_x[0])
star_y.append(star_y[0])

# 绘制星星
plt.plot(star_x, star_y, 'gold', linewidth=3, label='Star')
plt.fill(star_x, star_y, 'gold', alpha=0.6)

# 设置图形属性
plt.title('Star Shape', fontsize=16, fontweight='bold')
plt.xlabel('X', fontsize=12)
plt.ylabel('Y', fontsize=12)
plt.axis('equal')
plt.grid(True, alpha=0.3)
plt.legend()

# 保存并显示
plt.tight_layout()
plt.savefig('star.png', dpi=150, bbox_inches='tight')
plt.show()

print("星星已生成并保存为 star.png")