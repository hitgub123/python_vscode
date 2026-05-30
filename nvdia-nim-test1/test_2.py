import sys
import os
import unittest

# 将 test_2.py 所在目录添加到 sys.path，以便正确导入 a2 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from a2 import score_to_grade


class TestScoreToGrade(unittest.TestCase):
    def test_excellent(self):
        """测试大于90分返回优秀"""
        self.assertEqual(score_to_grade(95), '优秀')
        self.assertEqual(score_to_grade(100), '优秀')
        self.assertEqual(score_to_grade(91), '优秀')

    def test_pass(self):
        """测试大于60分返回及格"""
        self.assertEqual(score_to_grade(61), '及格')
        self.assertEqual(score_to_grade(75), '及格')
        self.assertEqual(score_to_grade(90), '及格')
        self.assertEqual(score_to_grade(60.5), '及格')

    def test_fail(self):
        """测试不及格情况"""
        self.assertEqual(score_to_grade(60), '不及格')
        self.assertEqual(score_to_grade(30), '不及格')
        self.assertEqual(score_to_grade(0), '不及格')
        self.assertEqual(score_to_grade(-10), '不及格')

    def test_edge_cases(self):
        """测试边界值"""
        self.assertEqual(score_to_grade(91), '优秀')   # 刚好大于90
        self.assertEqual(score_to_grade(90), '及格')   # 等于90
        self.assertEqual(score_to_grade(61), '及格')   # 刚好大于60
        self.assertEqual(score_to_grade(60), '不及格')  # 等于60


if __name__ == '__main__':
    unittest.main()
