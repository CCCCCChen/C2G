from cnocr import CnOcr

# ��ʼ��OCR����
ocr = CnOcr()

# ��ȡͼ���ļ�
img_path = '1.png'   # �滻Ϊ���ͼ���ļ�·��
with open(img_path, 'rb') as f:
    img_data = f.read()

# ʹ��OCR��ȡ����
result = ocr.ocr(img_data, cls=True)

# �����ȡ���
for line in result:
    print(f"�ı�: {line[1][0]}, ���Ŷ�: {line[1][1]}")
