import math
import matplotlib.pyplot as plt
import numpy as np

def heart_function(x, y):
    """心形函数"""
    return (x**2 + y**2 - 1)**3 - x**2 * y**3

def plot_heart():
    """绘制心形"""
    # 创建图形
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # 设置坐标范围
    x = np.linspace(-1.5, 1.5, 1000)
    y = np.linspace(-1.5, 1.5, 1000)
    X, Y = np.meshgrid(x, y)
    
    # 计算心形函数值
    Z = heart_function(X, Y)
    
    # 绘制等高线（心形轮廓）
    ax.contour(X, Y, Z, levels=[0], colors='red', linewidths=3)
    
    # 填充心形内部
    ax.contourf(X, Y, Z, levels=[-1000, 0], colors=['pink'], alpha=0.7)
    
    # 设置图形属性
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.set_title('Heart Shape', fontsize=16, fontweight='bold')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.grid(True, alpha=0.3)
    
    # 保存图形
    plt.savefig('heart.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("心形图形已生成并保存为 heart.png")

def print_ascii_heart():
    """打印ASCII心形"""
    heart = """
        ***     ***
      ******* *******
    ***************
    ***************
      ***********
        *******
          ***
           *
    """
    print(heart)

if __name__ == "__main__":
    print("=== 心形生成程序 ===")
    print("\n1. ASCII心形:")
    print_ascii_heart()
    
    print("\n2. 正在生成图形心形...")
    plot_heart()