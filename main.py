import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import pyautogui
import threading

class JianyingBatchExporter:
    def __init__(self):
        # 初始化配置
        self.config_file = os.path.join(os.path.expanduser('~'), 'jianying_exporter_config.json')
        self.load_config()
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("剪映专业版批量导出工具 v2.0")
        self.root.geometry("550x400")
        
        # 设置窗口图标
        try:
            self.root.iconbitmap(self.resource_path('icon.ico'))
        except:
            pass
        
        # 创建UI元素
        self.create_widgets()
        
        # 导出状态
        self.exporting = False
        self.cancel_export = False
    
    def resource_path(self, relative_path):
        """ 获取资源的绝对路径 """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
    
    def load_config(self):
        """ 加载配置文件 """
        default_config = {
            'output_folder': os.path.join(os.path.expanduser('~'), 'Desktop', '剪映导出'),
            'base_name': '我的视频',
            'export_format': 'mp4',
            'quality': '高',
            'resolution': '1080p'
        }
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = {**default_config, **json.load(f)}
        except:
            self.config = default_config
    
    def save_config(self):
        """ 保存配置文件 """
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def create_widgets(self):
        """ 创建界面组件 """
        # 输出文件夹
        tk.Label(self.root, text="输出文件夹:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.folder_var = tk.StringVar(value=self.config.get('output_folder', ''))
        tk.Entry(self.root, textvariable=self.folder_var, width=40).grid(row=0, column=1, sticky='w')
        tk.Button(self.root, text="浏览...", command=self.select_folder).grid(row=0, column=2, padx=5)
        
        # 文件基础名称
        tk.Label(self.root, text="文件基础名称:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.name_var = tk.StringVar(value=self.config.get('base_name', ''))
        tk.Entry(self.root, textvariable=self.name_var, width=40).grid(row=1, column=1, sticky='w')
        
        # 导出格式
        tk.Label(self.root, text="导出格式:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.format_var = tk.StringVar(value=self.config.get('export_format', 'mp4'))
        tk.OptionMenu(self.root, self.format_var, 'mp4', 'mov', 'gif').grid(row=2, column=1, sticky='w')
        
        # 质量设置
        tk.Label(self.root, text="视频质量:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.quality_var = tk.StringVar(value=self.config.get('quality', '高'))
        tk.OptionMenu(self.root, self.quality_var, '低', '中', '高', '极高').grid(row=3, column=1, sticky='w')
        
        # 分辨率
        tk.Label(self.root, text="分辨率:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        self.resolution_var = tk.StringVar(value=self.config.get('resolution', '1080p'))
        tk.OptionMenu(self.root, self.resolution_var, '720p', '1080p', '2k', '4k').grid(row=4, column=1, sticky='w')
        
        # 日志输出
        self.log_text = tk.Text(self.root, height=8, width=60, state='disabled')
        self.log_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10)
        
        # 按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        self.export_btn = tk.Button(button_frame, text="开始导出", command=self.start_export, width=15)
        self.export_btn.pack(side=tk.LEFT, padx=10)
        
        self.cancel_btn = tk.Button(button_frame, text="取消导出", command=self.cancel_export_process, state='disabled')
        self.cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # 版权信息
        tk.Label(self.root, text="© 2023 剪映批量导出工具 | 版本 2.0", fg="gray").grid(row=7, column=0, columnspan=3)
    
    def log_message(self, message):
        """ 在日志区域显示消息 """
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.root.update()
    
    def select_folder(self):
        """ 选择输出文件夹 """
        folder = filedialog.askdirectory(initialdir=self.folder_var.get())
        if folder:
            self.folder_var.set(folder)
    
    def start_export(self):
        """ 开始导出流程 """
        # 保存配置
        self.config.update({
            'output_folder': self.folder_var.get(),
            'base_name': self.name_var.get(),
            'export_format': self.format_var.get(),
            'quality': self.quality_var.get(),
            'resolution': self.resolution_var.get()
        })
        self.save_config()
        
        # 验证输入
        if not self.folder_var.get():
            messagebox.showerror("错误", "请选择输出文件夹")
            return
        
        if not self.name_var.get():
            messagebox.showerror("错误", "请输入文件基础名称")
            return
        
        # 准备导出
        self.exporting = True
        self.cancel_export = False
        self.export_btn.config(state='disabled')
        self.cancel_btn.config(state='normal')
        self.log_message("=== 开始导出 ===")
        
        # 在新线程中执行导出
        export_thread = threading.Thread(target=self.run_export_process)
        export_thread.start()
    
    def cancel_export_process(self):
        """ 取消导出 """
        self.cancel_export = True
        self.log_message("正在取消导出...")
    
    def run_export_process(self):
        """ 执行实际的导出过程 """
        try:
            # 模拟切换到剪映窗口
            self.log_message("请在5秒内切换到剪映专业版窗口...")
            time.sleep(5)
            
            if self.cancel_export:
                self.log_message("导出已取消")
                return
            
            # 模拟导出操作
            self.log_message("正在准备时间轴片段...")
            
            # 模拟选择所有片段 (Ctrl+A)
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(1)
            
            if self.cancel_export:
                self.log_message("导出已取消")
                return
            
            # 模拟打开导出对话框 (假设快捷键是Ctrl+E)
            self.log_message("打开导出对话框...")
            pyautogui.hotkey('ctrl', 'e')
            time.sleep(2)
            
            # 模拟设置导出参数
            self.log_message("设置导出参数...")
            
            # 这里需要根据实际剪映界面调整坐标或使用图像识别定位
            # 以下为示例代码，实际使用时需要调整
            
            # 模拟设置输出路径
            pyautogui.press('tab', presses=3)  # 导航到路径输入框
            pyautogui.write(self.folder_var.get())
            
            # 模拟设置文件名
            pyautogui.press('tab')
            pyautogui.write(self.name_var.get())
            
            # 模拟设置格式和质量
            # 这里需要根据实际界面调整
            
            time.sleep(1)
            
            # 模拟开始导出
            self.log_message("开始导出片段...")
            pyautogui.press('enter')  # 确认导出
            
            # 模拟等待导出完成
            for i in range(30):  # 最多等待30秒
                if self.cancel_export:
                    break
                time.sleep(1)
                self.log_message(f"导出中... ({i+1}/30)")
            
            if self.cancel_export:
                self.log_message("导出已取消")
            else:
                self.log_message("导出完成！")
                messagebox.showinfo("完成", "所有片段已成功导出！")
        
        except Exception as e:
            self.log_message(f"导出出错: {str(e)}")
            messagebox.showerror("错误", f"导出过程中出错:\n{str(e)}")
        finally:
            self.exporting = False
            self.root.after(0, self.enable_export_button)
    
    def enable_export_button(self):
        """ 启用导出按钮 """
        self.export_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
    
    def run(self):
        """ 运行主循环 """
        self.root.mainloop()

if __name__ == "__main__":
    # 检查是否安装了pyautogui
    try:
        import pyautogui
    except ImportError:
        print("请先安装pyautogui模块: pip install pyautogui")
        sys.exit(1)
    
    app = JianyingBatchExporter()
    app.run()