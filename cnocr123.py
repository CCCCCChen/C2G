# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 23:13:07 2025

@author: C4Chen
"""
import cnocr

# 初始化 CNOCR
ocr = cnocr.CnOcr()

# 测试识别
test_image_path = '1.png'  # 请确保存在测试图片
result = ocr.ocr(test_image_path)

# 输出结果
print("CNOCR 安装成功！识别结果：")
for line in result:
    print(f"文本: {line['text']}, 位置: {line['position']}, 置信度: {line['score']}")