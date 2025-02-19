# 提供网址，获取网页中的图片，缓存在/Genshin/web_temp
# 通过OCR识别图片中的文字
# 识别到特定关键字的图片，保存至/Genshin/img，同时暂停获取网页图片
# 对于/Genshin/img中的图片，提取图片文字，并保存至/Genshin/img_text
# 清除/Genshin/web_temp中的图片

import os
import shutil
from PIL import Image
import pytesseract
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
        self.web_temp_dir = "Genshin/web_temp"
        self.img_dir = "Genshin/img" 
        self.img_text_dir = "Genshin/img_text"
        
        # 初始化 Chrome 选项
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        
        for dir in [self.web_temp_dir, self.img_dir, self.img_text_dir]:
            if not os.path.exists(dir):
                os.makedirs(dir)
                
    def get_web_images(self, url):
        """从网页获取图片并保存到临时目录"""
        # 初始化 ChromeDriver
        service = Service('chromedriver的路径')
        driver = webdriver.Chrome(service=service, options=self.chrome_options)
        try:
            # 访问页面
            driver.get(url)
            
            # 等待页面加载（等待图片元素出现）
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))
            
            # 给页面一些额外时间完全加载
            time.sleep(3)
            
            # 获取页面源码
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 记录网页内容到文件
            with open('webpage_content.txt', 'w', encoding='utf-8') as f:
                f.write("网页内容:\n")
                f.write(str(soup))
            
            # 查找所有图片
            for img in soup.find_all(['img', 'div']):
                img_url = img.get('src') or img.get('large')
                if img_url and '.png' in img_url:
                    try:
                        # 确保URL是完整的
                        if not img_url.startswith('http'):
                            if img_url.startswith('//'):
                                img_url = 'https:' + img_url
                            else:
                                img_url = 'https://' + img_url
                                
                        img_data = requests.get(img_url).content
                        img_name = os.path.join(self.web_temp_dir, os.path.basename(img_url).split('?')[0])
                        with open(img_name, 'wb') as f:
                            f.write(img_data)
                    except Exception as e:
                        print(f"下载图片时出错: {str(e)}")
                        continue
                        
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
        for img_file in os.listdir(self.web_temp_dir):
            img_path = os.path.join(self.web_temp_dir, img_file)
            try:
                # OCR识别文字
                text = pytesseract.image_to_string(Image.open(img_path), lang='chi_sim')
                
                # 检查关键词
                if any(keyword in text for keyword in keywords):
                    # 移动图片到img目录
                    shutil.move(img_path, os.path.join(self.img_dir, img_file))
                    
                    # 保存识别文字
                    text_file = os.path.join(self.img_text_dir, f"{img_file}.txt")
                    with open(text_file, 'w', encoding='utf-8') as f:
                        f.write(text)
                    return True
            except:
                continue
        return False
        
    def clean_temp(self):
        """清理临时目录"""
        for file in os.listdir(self.web_temp_dir):
            os.remove(os.path.join(self.web_temp_dir, file))
def main():
    ocr = GenshinOCR()
    # 调试阶段使用固定网址和关键词
    url = "https://www.miyoushe.com/ys/article/58735977"
    keywords = ["一图流"]
    
    ocr.get_web_images(url)
    if ocr.process_images(keywords):
        print("找到匹配的图片，已保存")
    ocr.clean_temp()

if __name__ == "__main__":
    main()

