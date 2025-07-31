import unittest
import os
from src.jianying_utils import JianYingHelper
from unittest.mock import patch, MagicMock

class TestExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_config = {
            "shortcuts": {"select_all": ["ctrl", "a"]},
            "timeline_region": {"x": 0, "y": 0, "width": 100, "height": 100}
        }
        
    def test_segment_detection(self):
        """测试片段识别"""
        helper = JianYingHelper(self.test_config)
        
        # 模拟OpenCV匹配结果
        with patch('cv2.matchTemplate') as mock_match:
            mock_match.return_value = np.array([[0.9, 0.8, 0.7]])
            segments = helper.detect_segments(mode='template')
            self.assertEqual(len(segments), 2)  # 匹配到2个有效片段

    def test_export_validation(self):
        """测试导出验证"""
        with patch('os.listdir') as mock_listdir:
            mock_listdir.return_value = ['video1.mp4', 'video2.mp4']
            helper = JianYingHelper(self.test_config)
            result = helper.validate_export(2, 2)  # 预期2个，实际2个
            self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
