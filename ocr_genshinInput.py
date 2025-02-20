# 提供网址，获取网页中的图片，缓存在/Genshin/web_temp
# 通过OCR识别图片中的文字
# 识别到特定关键字的图片，保存至/Genshin/img，同时暂停获取网页图片
# 对于/Genshin/img中的图片，提取图片文字，并保存至/Genshin/img_text
# 清除/Genshin/web_temp中的图片

import os
import shutil
from PIL import Image
# import pytesseract
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class GenshinOCR:
    def __init__(self):
        # 创建必要的目录
        self.web_temp_dir = "Genshin/img/fire"
        self.img_dir = "Genshin/img" 
        self.img_text_dir = "Genshin/img_text"
        
        # 设置 Tesseract 路径
        # pytesseract.pytesseract.tesseract_cmd = r'D:\TinySoftware\Tesseract\tesseract.exe'  # Windows路径
        
        # 初始化 Chrome 选项
        self.chrome_options = Options()
        self.chrome_options.add_argument('--ignore-certificate-errors')  # 忽略证书错误
        # self.chrome_options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        
        for dir in [self.web_temp_dir, self.img_dir, self.img_text_dir]:
            if not os.path.exists(dir):
                os.makedirs(dir)
                
    def get_web_images(self, url):
        """从网页获取图片并保存到临时目录"""
        driver = webdriver.Chrome(options=self.chrome_options)
        try:
            # 访问页面
            driver.get(url)
            print("页面已加载")
            base_url = url.split('//')[1].split('/')[0]  # 获取基础域名
            
            # 等待页面加载（等待图片元素出现）
            wait = WebDriverWait(driver, 10)
            try:
                print("等待初始图片元素加载...")
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))
                print("初始图片元素已加载")
                
                # 模拟鼠标点击以打开框，并等待图片加载完成
                print("尝试定位展开按钮...")
                
                try:
                    # 先尝试通过class_name定位
                    button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "ql-fold-title")))
                    print("找到展开按钮")
                    # driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(1)
                    # button.click()
                    # print("已点击展开按钮")
                    
                    # 等待新内容加载完成
                    time.sleep(3)  # 增加等待时间
                    
                    # 获取更新后的页面源码
                    print("获取页面源码...")
                    page_source = driver.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')
                    
                    # 查找所有图片
                    for img in soup.find_all(['img', 'div']):
                        img_url = img.get('src') or img.get('large')
                        if img_url and ('.png' in img_url or '.jpg' in img_url or '.jpeg' in img_url):
                            try:
                                # 修复URL格式
                                if img_url.startswith('//'):
                                    img_url = 'https:' + img_url
                                elif img_url.startswith('/'):
                                    img_url = f'https://{base_url}{img_url}'
                                elif not img_url.startswith('http'):
                                    img_url = f'https://{base_url}/{img_url}'
                                
                                print(f"尝试下载图片: {img_url}")  # 调试输出
                                
                                img_data = requests.get(img_url).content
                                # 修改文件名处理逻辑
                                # https://upload-bbs.miyoushe.com/upload/2024/11/04/79695828/bd4652ae774aa144ab6b194d27bc79a1_2990934284951142176.png?x-oss-process=image//resize,s_600/quality,q_80/auto-orient,0/interlace,1/format,png
                                base_name = os.path.basename(img_url).split('?')[0]  # 获取图片的基本名称，去掉查询参数
                                print(img_url)
                                if '.png' in img_url:
                                    base_name = img_url.split('.png', 1)[0].rsplit('/', 1)[-1] + '.png'  # 如果基本名称中包含png，取png前最后的斜杠到png作为名称
                                elif '/' in base_name:
                                    base_name = base_name.split('/')[-1]  # 如果基本名称中包含斜杠，取最后一部分
                                if ',' in base_name:
                                    base_name = base_name.replace(',', '.')  # 将基本名称中的逗号替换为点
                                img_name = base_name
                                img_path = os.path.join(self.web_temp_dir, img_name)
                                with open(img_path, 'wb') as f:
                                    f.write(img_data)
                                    print(f"成功保存图片: {img_path}")  # 调试输出
                            except Exception as e:
                                print(f"下载图片时出错: {str(e)}")
                                print(f"问题URL: {img_url}")  # 调试输出
                                continue
                except Exception as e:
                    print(f"点击操作或等待图片加载时出错: {e}")
                
            except Exception as e:
                print(f"等待图片元素加载时出错: {e}")
            
        except Exception as e:
            print(f"获取网页内容时出错: {str(e)}")
        finally:
            driver.quit()
            
        if not os.listdir(self.web_temp_dir):
            print("没有找到任何图片")
            return False
        return True
        
    def process_images(self, keywords):
        """处理临时目录中的图片"""
        print("开始处理临时目录中的图片...")
        for img_file in os.listdir(self.web_temp_dir):
            img_path = os.path.join(self.web_temp_dir, img_file)
            try:
                print(f"正在处理图片: {img_file}")
                # 使用其他OCR识别方法
                print("开始OCR文字识别...")
                # 使用EasyOCR进行文字识别
                import easyocr
                reader = easyocr.Reader(['ch_sim'])  # 选择简体中文
                result = reader.readtext(img_path)
                
                # 提取识别到的文字
                text = ' '.join([res[1] for res in result])
                print(f"识别到的文字内容: {text[:100]}...")  # 只显示前100个字符
                
                # 检查关键词
                print(f"检查关键词: {keywords}")
                if any(keyword in text for keyword in keywords):
                    print(f"找到匹配的关键词!")
                    # 移动图片到img目录
                    dest_path = os.path.join(self.img_dir, img_file)
                    print(f"移动图片到: {dest_path}")
                    shutil.move(img_path, dest_path)
                    
                    # 保存识别文字
                    text_file = os.path.join(self.img_text_dir, f"{img_file}.txt")
                    print(f"保存识别文字到: {text_file}")
                    with open(text_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    return True
                else:
                    print("未找到匹配的关键词")
            except Exception as e:
                print(f"处理图片 {img_file} 时出错: {str(e)}")
                continue
        print("所有图片处理完成")
        return False
        
    def clean_temp(self):
        """清理临时目录"""
        for file in os.listdir(self.web_temp_dir):
            os.remove(os.path.join(self.web_temp_dir, file))
def main():
    ocr = GenshinOCR()
    # 调试阶段使用固定网址和关键词
    # url = "https://www.miyoushe.com/ys/article/59125535"  # 火
    # url = "https://www.miyoushe.com/ys/article/58824544"  # 草
    #　url = "https://www.miyoushe.com/ys/article/58735977"  # 岩
    #url = "https://www.miyoushe.com/ys/article/47052062"  # 水
    # url = "https://www.miyoushe.com/ys/article/49735671"  # 风
    # lacking 雷和冰
    keywords = ["圣遗物"]

    # ocr.clean_temp()
    # ocr.get_web_images(url)
    if ocr.process_images(keywords):
        print("找到匹配的图片，已保存")
    # 

if __name__ == "__main__":
    main()

