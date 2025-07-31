import pyautogui
import json

print("剪映界面坐标校准工具")
print("请按提示操作（每个步骤有5秒准备时间）")

steps = {
    "timeline_top_left": "将鼠标移到时间轴左上角",
    "timeline_bottom_right": "将鼠标移到时间轴右下角",
    "export_button": "将鼠标移到导出按钮位置"
}

coordinates = {}
for name, prompt in steps.items():
    print(f"\n{prompt}...")
    time.sleep(5)
    coordinates[name] = pyautogui.position()

with open('assets/timeline_region.txt', 'w') as f:
    json.dump(coordinates, f)

print("校准完成！坐标已保存")
