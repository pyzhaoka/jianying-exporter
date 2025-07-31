import cv2
import pyautogui
import numpy as np
import time

class JianYingHelper:
    def __init__(self, config):
        self.config = config
        self.template = cv2.imread('assets/segment_template.png', 0)
        
    def detect_segments(self, mode='auto'):
        """识别时间轴片段"""
        if mode == 'template':
            return self._detect_by_template()
        elif mode == 'manual':
            return self._manual_selection()
        else:
            return self._auto_detect()

    def _detect_by_template(self):
        """通过图像模板识别片段"""
        screenshot = pyautogui.screenshot(region=self.config['timeline_region'])
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        res = cv2.matchTemplate(img, self.template, cv2.TM_CCOEFF_NORMED)
        return [x[0] for x in np.argwhere(res >= 0.8)]

    def export_segments(self, segments, output_dir, base_name):
        """执行分段导出"""
        pyautogui.hotkey(*self.config['shortcuts']['select_all'])
        time.sleep(1)
        
        success = 0
        for i, pos in enumerate(segments):
            if self._export_single(pos, output_dir, f"{base_name}_{i+1}"):
                success += 1
        return success
