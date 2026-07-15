import numpy as np
import matplotlib.pyplot as plt

# 心形线参数方程
# x = 16 * sin³(t)
# y = 13 * cos(t) - 5 * cos(2t) - 2 * cos(3t) - cos(4t)

def draw_heart():
    # 生成参数 t，从 0 到 2π
    t = np.linspace(0, 2 * np.pi, 1000)
    
    # 计算心形线上的点
    x = 16 * np.sin(t) ** 3
    y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
    
    # 创建图形
    plt.figure(figsize=(8, 8))
    
    # 绘制心形
    plt.plot(x, y, color='red', linewidth=2)
    
    # 填充心形内部
    plt.fill(x, y, color='red', alpha=0.3)
    
    # 设置图形属性
    plt.title('Heart Shape', fontsize=16, fontweight='bold')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.axis('equal')  # 保持纵横比
    plt.grid(True, alpha=0.3)
    
    # 显示图形
    plt.show()

if __name__ == '__main__':
    draw_heart()
