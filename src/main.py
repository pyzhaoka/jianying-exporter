#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import logging
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab

class JianyingBatchExporter:
    def __init__(self):
        # 初始化配置
        self.config = self.load_config()
        self.setup_logging()
        self.setup_ui()
        self.running = False

    def setup_logging(self):
        """配置日志系统"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='jianying_export.log',
            filemode='w'
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        default_config = {
            "output_dir": os.path.join(os.path.expanduser('~'), "Desktop", "剪映导出"),
            "shortcuts": {
                "select_all": ["ctrl", "a"],
                "export": ["ctrl", "e"]
            },
            "timeline_region": {"x": 100, "y": 800, "width": 800, "height": 50}
        }
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return {**default_config, **json.load(f)}
        except Exception as e:
            self.logger.warning(f"加载配置失败: {str(e)}")
            return default_config

    def setup_ui(self):
        """初始化用户界面"""
        self.root = tk.Tk()
        self.root.title("剪映专业版批量导出工具 v3.1")
        self.root.geometry("600x450")
        
        # 图标设置
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
            self.root.iconbitmap(icon_path)
        except Exception as e:
            self.logger.error(f"图标加载失败: {str(e)}")

        # 控件布局
        self.create_widgets()
        self.setup_style()

    def setup_style(self):
        """设置UI样式"""
        style = ttk.Style()
        style.configure('TButton', padding=6)
        style.configure('TLabel', padding=5)

    def create_widgets(self):
        """创建界面组件"""
        # 输出目录选择
        ttk.Label(self.root, text="输出目录:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.output_dir_var = tk.StringVar(value=self.config["output_dir"])
        ttk.Entry(self.root, textvariable=self.output_dir_var, width=40).grid(row=0, column=1, sticky='we')
        ttk.Button(self.root, text="浏览...", command=self.select_directory).grid(row=0, column=2, padx=5)

        # 导出设置
        ttk.Label(self.root, text="文件前缀:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.file_prefix_var = tk.StringVar(value="导出视频")
        ttk.Entry(self.root, textvariable=self.file_prefix_var, width=40).grid(row=1, column=1, sticky='we')

        # 日志输出
        self.log_text = tk.Text(self.root, height=10, width=70, state='disabled')
        self.log_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        # 操作按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="开始导出", command=self.start_export)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = ttk.Button(btn_frame, text="停止", state='disabled', command=self.stop_export)
        self.stop_btn.pack(side=tk.LEFT)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN).grid(
            row=4, column=0, columnspan=3, sticky='we', padx=10, pady=5)

    def log_message(self, message, level="info"):
        """记录日志"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
        if level == "error":
            self.logger.error(message)
        else:
            self.logger.info(message)

    def select_directory(self):
        """选择输出目录"""
        dir_path = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if dir_path:
            self.output_dir_var.set(dir_path)
            self.config["output_dir"] = dir_path

    def start_export(self):
        """开始导出流程"""
        if self.running:
            return

        self.running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_var.set("运行中...")

        # 在新线程中运行导出
        export_thread = threading.Thread(target=self.run_export, daemon=True)
        export_thread.start()

    def stop_export(self):
        """停止导出"""
        self.running = False
        self.status_var.set("正在停止...")

    def run_export(self):
        """执行导出操作"""
        try:
            output_dir = self.output_dir_var.get()
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            self.log_message("=== 开始导出 ===")
            self.log_message(f"输出目录: {output_dir}")
            
            # 模拟剪映操作
            if not self.simulate_jianying_export(output_dir):
                raise RuntimeError("导出过程失败")

            self.log_message("导出完成！")
            messagebox.showinfo("完成", "所有片段已成功导出！")

        except Exception as e:
            self.log_message(f"导出失败: {str(e)}", "error")
            messagebox.showerror("错误", f"导出过程中出错:\n{str(e)}")
        finally:
            self.running = False
            self.root.after(0, lambda: [
                self.start_btn.config(state='normal'),
                self.stop_btn.config(state='disabled'),
                self.status_var.set("就绪")
            ])

    def simulate_jianying_export(self, output_dir):
        """模拟剪映导出流程"""
        # 1. 激活剪映窗口
        self.log_message("正在激活剪映窗口...")
        time.sleep(2)
        
        # 2. 定位时间轴
        self.log_message("定位时间轴区域...")
        timeline_pos = self.locate_timeline()
        if not timeline_pos:
            raise RuntimeError("无法定位时间轴")

        # 3. 识别片段
        self.log_message("识别视频片段...")
        segments = self.detect_segments(timeline_pos)
        if not segments:
            raise RuntimeError("未识别到任何片段")

        # 4. 执行导出
        success_count = 0
        for i, segment in enumerate(segments):
            if not self.running:
                break

            try:
                if self.export_single_segment(segment, output_dir, i+1):
                    success_count += 1
            except Exception as e:
                self.log_message(f"片段 {i+1} 导出失败: {str(e)}", "error")

        return success_count > 0

    def locate_timeline(self):
        """定位时间轴区域"""
        try:
            # 使用模板匹配或颜色识别
            screenshot = np.array(ImageGrab.grab())
            hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
            
            # 根据时间轴颜色特征定位
            lower = np.array([0, 0, 200])
            upper = np.array([180, 30, 255])
            mask = cv2.inRange(hsv, lower, upper)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                x,y,w,h = cv2.boundingRect(max(contours, key=cv2.contourArea))
                return (x, y, w, h)
        except Exception as e:
            self.log_message(f"定位时间轴失败: {str(e)}", "error")
        return None

    def detect_segments(self, timeline_pos):
        """识别时间轴片段"""
        segments = []
        try:
            x, y, w, h = timeline_pos
            roi = np.array(ImageGrab.grab(bbox=(x, y, x+w, y+h)))
            
            # 使用边缘检测识别片段分隔
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # 查找垂直线段作为分隔
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=30, maxLineGap=10)
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    if abs(x1 - x2) < 5:  # 垂直线
                        segments.append(x + x1)
            
            # 去重排序
            segments = sorted(list(set(segments)))
        except Exception as e:
            self.log_message(f"片段识别失败: {str(e)}", "error")
        
        return segments if segments else [0, w]  # 默认返回整个时间轴

    def export_single_segment(self, segment_pos, output_dir, index):
        """导出单个片段"""
        file_name = f"{self.file_prefix_var.get()}_{index}.mp4"
        output_path = os.path.join(output_dir, file_name)
        
        self.log_message(f"正在导出片段 {index}...")
        
        # 模拟操作流程
        try:
            # 1. 选择片段
            pyautogui.click(segment_pos, self.config["timeline_region"]["y"] + 10)
            time.sleep(0.5)
            
            # 2. 打开导出对话框
            pyautogui.hotkey(*self.config["shortcuts"]["export"])
            time.sleep(1)
            
            # 3. 设置输出路径
            pyautogui.write(output_path)
            time.sleep(0.5)
            
            # 4. 确认导出
            pyautogui.press('enter')
            time.sleep(2)  # 等待导出完成
            
            return os.path.exists(output_path)
        except Exception as e:
            self.log_message(f"导出片段 {index} 时出错: {str(e)}", "error")
            return False

    def run(self):
        """运行主循环"""
        self.root.mainloop()

if __name__ == "__main__":
    try:
        # 依赖检查
        import pyautogui
        import cv2
        import numpy as np
    except ImportError as e:
        print(f"缺少依赖: {str(e)}\n请执行: pip install -r requirements.txt")
        sys.exit(1)

    app = JianyingBatchExporter()
    app.run()
