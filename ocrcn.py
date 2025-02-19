from cnocr import CnOcr

# 初始化OCR对象
ocr = CnOcr()

# 读取图像文件
img_path = '1.png'   # 替换为你的图像文件路径
with open(img_path, 'rb') as f:
    img_data = f.read()

# 使用OCR提取文字
result = ocr.ocr(img_data, cls=True)

# 输出提取结果
for line in result:
    print(f"文本: {line[1][0]}, 置信度: {line[1][1]}")
