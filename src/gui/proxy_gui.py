"""GUI 配置界面 - 类似 CC-Switch"""

import json
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, cast


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: str = "./config/proxy_config.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path, encoding="utf-8") as f:
                return cast(dict[str, Any], json.load(f))
        return self._default_config()

    def _default_config(self) -> dict[str, Any]:
        """默认配置"""
        return {
            "proxy": {
                "host": "127.0.0.1",
                "port": 8081,
                "enabled": False,
            },
            "providers": [
                {
                    "name": "OpenAI",
                    "url": "https://api.openai.com/v1",
                    "api_key": "",
                    "active": False,
                },
                {
                    "name": "Anthropic",
                    "url": "https://api.anthropic.com/v1",
                    "api_key": "",
                    "active": False,
                },
                {
                    "name": "Custom",
                    "url": "",
                    "api_key": "",
                    "active": False,
                },
            ],
        }

    def save(self) -> None:
        """保存配置"""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get_proxy_config(self) -> dict[str, Any]:
        """获取代理配置"""
        return cast(dict[str, Any], self.config.get("proxy", {}))

    def set_proxy_config(self, config: dict[str, Any]) -> None:
        """设置代理配置"""
        self.config["proxy"] = config
        self.save()

    def get_providers(self) -> list[dict[str, Any]]:
        """获取提供商列表"""
        return cast(list[dict[str, Any]], self.config.get("providers", []))

    def add_provider(self, provider: dict[str, Any]) -> None:
        """添加提供商"""
        self.config["providers"].append(provider)
        self.save()

    def remove_provider(self, index: int) -> None:
        """移除提供商"""
        if 0 <= index < len(self.config["providers"]):
            self.config["providers"].pop(index)
            self.save()

    def update_provider(self, index: int, provider: dict[str, Any]) -> None:
        """更新提供商"""
        if 0 <= index < len(self.config["providers"]):
            self.config["providers"][index] = provider
            self.save()


class ProxyGUI:
    """代理配置 GUI 界面"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("TCA Proxy - 本地代理配置")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # 配置管理器
        self.config_manager = ConfigManager()

        # 代理服务器进程
        self._proxy_process: subprocess.Popen[bytes] | None = None

        # 创建界面
        self._create_menu()
        self._create_proxy_frame()
        self._create_providers_frame()
        self._create_status_bar()

        # 加载配置
        self._load_config_to_ui()

    def _create_menu(self) -> None:
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="保存配置", command=self._save_config)
        file_menu.add_command(label="重置配置", command=self._reset_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)

        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="启动代理", command=self._start_proxy)
        tools_menu.add_command(label="停止代理", command=self._stop_proxy)
        tools_menu.add_command(label="测试连接", command=self._test_connection)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self._show_help)
        help_menu.add_command(label="关于", command=self._show_about)

    def _create_proxy_frame(self) -> None:
        """创建代理配置框架"""
        frame = ttk.LabelFrame(self.root, text="代理配置", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)

        # 启用代理
        self.proxy_enabled_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="启用代理", variable=self.proxy_enabled_var).grid(
            row=0, column=0, sticky=tk.W, pady=5
        )

        # 主机
        ttk.Label(frame, text="主机:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.proxy_host_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.proxy_host_var, width=30).grid(
            row=1, column=1, sticky=tk.W, padx=5, pady=5
        )

        # 端口
        ttk.Label(frame, text="端口:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.proxy_port_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.proxy_port_var, width=10).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=5
        )

        # 状态标签
        self.proxy_status_var = tk.StringVar(value="未启动")
        ttk.Label(frame, textvariable=self.proxy_status_var, foreground="gray").grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=5
        )

    def _create_providers_frame(self) -> None:
        """创建提供商配置框架"""
        frame = ttk.LabelFrame(self.root, text="LLM 提供商配置", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 树形视图
        columns = ("name", "url", "api_key", "active")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)

        # 设置列标题
        self.tree.heading("name", text="名称")
        self.tree.heading("url", text="API URL")
        self.tree.heading("api_key", text="API Key")
        self.tree.heading("active", text="激活")

        # 设置列宽度
        self.tree.column("name", width=100)
        self.tree.column("url", width=300)
        self.tree.column("api_key", width=200)
        self.tree.column("active", width=60)

        # 滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="添加", command=self._add_provider).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="编辑", command=self._edit_provider).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除", command=self._delete_provider).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="设为激活", command=self._set_active).pack(side=tk.LEFT, padx=5)

    def _create_status_bar(self) -> None:
        """创建状态栏"""
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _load_config_to_ui(self) -> None:
        """加载配置到 UI"""
        # 代理配置
        proxy_config = self.config_manager.get_proxy_config()
        self.proxy_enabled_var.set(proxy_config.get("enabled", False))
        self.proxy_host_var.set(proxy_config.get("host", "127.0.0.1"))
        self.proxy_port_var.set(str(proxy_config.get("port", 8080)))

        # 提供商配置
        for item in self.tree.get_children():
            self.tree.delete(item)

        providers = self.config_manager.get_providers()
        for provider in providers:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    provider.get("name", ""),
                    provider.get("url", ""),
                    "****" if provider.get("api_key") else "",
                    "✓" if provider.get("active") else "",
                ),
            )

    def _save_config(self) -> None:
        """保存配置"""
        # 保存代理配置
        proxy_config = {
            "enabled": self.proxy_enabled_var.get(),
            "host": self.proxy_host_var.get(),
            "port": int(self.proxy_port_var.get()),
        }
        self.config_manager.set_proxy_config(proxy_config)

        self.status_var.set("配置已保存")

    def _reset_config(self) -> None:
        """重置配置"""
        if messagebox.askyesno("确认", "确定要重置配置吗？"):
            self.config_manager.config = self.config_manager._default_config()
            self.config_manager.save()
            self._load_config_to_ui()
            self.status_var.set("配置已重置")

    def _start_proxy(self) -> None:
        """启动代理"""
        if self._proxy_process and self._proxy_process.poll() is None:
            messagebox.showwarning("警告", "代理服务器已在运行中")
            return

        # 获取配置
        proxy_config = self.config_manager.get_proxy_config()
        host = proxy_config.get("host", "127.0.0.1")
        port = proxy_config.get("port", 8080)

        # 检查是否有激活的提供商
        providers = self.config_manager.get_providers()
        active_provider = None
        for provider in providers:
            if provider.get("active"):
                active_provider = provider
                break

        if not active_provider:
            messagebox.showwarning("警告", "请先激活一个 LLM 提供商")
            return

        if not active_provider.get("api_key"):
            messagebox.showwarning("警告", f"请先配置 {active_provider.get('name')} 的 API Key")
            return

        try:
            # 启动代理服务器
            python_exe = sys.executable
            self._proxy_process = subprocess.Popen(
                [python_exe, "-m", "src.server.proxy"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.proxy_status_var.set(f"运行中 (http://{host}:{port})")
            self.status_var.set(f"代理已启动 - {active_provider.get('name')}")

            # 在新线程中检查进程状态
            threading.Thread(target=self._monitor_proxy, daemon=True).start()

        except Exception as e:
            messagebox.showerror("错误", f"启动代理失败: {str(e)}")
            self.status_var.set("启动代理失败")

    def _stop_proxy(self) -> None:
        """停止代理"""
        if not self._proxy_process:
            messagebox.showinfo("提示", "代理服务器未运行")
            return

        try:
            self._proxy_process.terminate()
            self._proxy_process.wait(timeout=5)
            self._proxy_process = None
            self.proxy_status_var.set("未启动")
            self.status_var.set("代理已停止")
        except Exception as e:
            messagebox.showerror("错误", f"停止代理失败: {str(e)}")
            self._proxy_process = None
            self.proxy_status_var.set("未启动")

    def _monitor_proxy(self) -> None:
        """监控代理进程状态"""
        if self._proxy_process:
            self._proxy_process.wait()
            if self._proxy_process.poll() is not None:
                self.root.after(0, self._on_proxy_stopped)

    def _on_proxy_stopped(self) -> None:
        """代理进程停止回调"""
        self._proxy_process = None
        self.proxy_status_var.set("未启动")
        self.status_var.set("代理已停止")

    def _test_connection(self) -> None:
        """测试连接"""
        import httpx

        proxy_config = self.config_manager.get_proxy_config()
        host = proxy_config.get("host", "127.0.0.1")
        port = proxy_config.get("port", 8080)

        url = f"http://{host}:{port}/health"

        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(url)
                if response.status_code == 200:
                    messagebox.showinfo("成功", f"连接成功!\n{response.json()}")
                    self.status_var.set("连接测试成功")
                else:
                    messagebox.showwarning("警告", f"连接失败: {response.status_code}")
                    self.status_var.set("连接测试失败")
        except httpx.ConnectError:
            messagebox.showwarning("警告", "无法连接到代理服务器\n请确保代理已启动")
            self.status_var.set("连接测试失败")
        except Exception as e:
            messagebox.showerror("错误", f"测试失败: {str(e)}")
            self.status_var.set("连接测试失败")

    def _add_provider(self) -> None:
        """添加提供商"""
        dialog = ProviderDialog(self.root, "添加提供商")
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            self.config_manager.add_provider(dialog.result)
            self._load_config_to_ui()
            self.status_var.set("提供商已添加")

    def _edit_provider(self) -> None:
        """编辑提供商"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要编辑的提供商")
            return

        index = self.tree.index(selection[0])
        provider = self.config_manager.get_providers()[index]

        dialog = ProviderDialog(self.root, "编辑提供商", provider)
        self.root.wait_window(dialog.dialog)

        if dialog.result:
            self.config_manager.update_provider(index, dialog.result)
            self._load_config_to_ui()
            self.status_var.set("提供商已更新")

    def _delete_provider(self) -> None:
        """删除提供商"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的提供商")
            return

        if messagebox.askyesno("确认", "确定要删除这个提供商吗？"):
            index = self.tree.index(selection[0])
            self.config_manager.remove_provider(index)
            self._load_config_to_ui()
            self.status_var.set("提供商已删除")

    def _set_active(self) -> None:
        """设为激活"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要激活的提供商")
            return

        index = self.tree.index(selection[0])
        providers = self.config_manager.get_providers()

        # 取消所有激活
        for _i, provider in enumerate(providers):
            provider["active"] = False

        # 激活选中的
        providers[index]["active"] = True
        self.config_manager.save()
        self._load_config_to_ui()
        self.status_var.set("提供商已激活")

    def _show_help(self) -> None:
        """显示帮助"""
        help_text = """
TCA Proxy - 本地代理配置工具

使用方法：
1. 配置代理主机和端口
2. 添加 LLM 提供商（OpenAI、Anthropic 等）
3. 设置 API Key
4. 激活要使用的提供商
5. 启动代理

配置完成后，可以在 Claude Code 中设置：
export ANTHROPIC_API_URL=http://127.0.0.1:8080
        """
        messagebox.showinfo("使用说明", help_text)

    def _show_about(self) -> None:
        """显示关于"""
        messagebox.showinfo(
            "关于",
            "TCA Proxy v0.1.0\n\n本地 LLM 代理配置工具\n类似 CC-Switch 的功能",
        )


class ProviderDialog:
    """提供商配置对话框"""

    def __init__(self, parent: tk.Tk, title: str, provider: dict[str, Any] | None = None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.result: dict[str, Any] | None = None

        # 创建界面
        ttk.Label(self.dialog, text="名称:").pack(anchor=tk.W, padx=20, pady=5)
        self.name_var = tk.StringVar(value=provider.get("name", "") if provider else "")
        ttk.Entry(self.dialog, textvariable=self.name_var, width=40).pack(padx=20, pady=5)

        ttk.Label(self.dialog, text="API URL:").pack(anchor=tk.W, padx=20, pady=5)
        self.url_var = tk.StringVar(value=provider.get("url", "") if provider else "")
        ttk.Entry(self.dialog, textvariable=self.url_var, width=40).pack(padx=20, pady=5)

        ttk.Label(self.dialog, text="API Key:").pack(anchor=tk.W, padx=20, pady=5)
        self.api_key_var = tk.StringVar(value=provider.get("api_key", "") if provider else "")
        ttk.Entry(self.dialog, textvariable=self.api_key_var, width=40, show="*").pack(
            padx=20, pady=5
        )

        # 按钮
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="确定", command=self._ok).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=self.dialog.destroy).pack(side=tk.LEFT, padx=10)

    def _ok(self) -> None:
        """确定"""
        name = self.name_var.get().strip()
        url = self.url_var.get().strip()
        api_key = self.api_key_var.get().strip()

        if not name:
            messagebox.showwarning("警告", "名称不能为空")
            return

        if not url:
            messagebox.showwarning("警告", "API URL 不能为空")
            return

        self.result = {
            "name": name,
            "url": url,
            "api_key": api_key,
            "active": False,
        }
        self.dialog.destroy()


def main() -> None:
    """主函数"""
    root = tk.Tk()
    ProxyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
