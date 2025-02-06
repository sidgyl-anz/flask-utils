from flask import Flask, render_template, request, send_file
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import zipfile
import requests
import time

app = Flask(__name__)
DOWNLOAD_FOLDER = 'static/downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

CHROME_BIN = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/bin/chromedriver")

# Configure Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.binary_location = CHROME_BIN

def download_images_from_gallery(gallery_num):
    url = f'https://platesmania.com/kr/gallery-{gallery_num}'

    try:
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        images = soup.find_all('img')
        driver.quit()
    except Exception as e:
        return f"❌ ChromeDriver Error: {str(e)}"

    count = 0
    for img in images:
        img_url = img.get('src')
        if img_url and img_url.startswith('/images/photos/'):
            full_img_url = 'https://platesmania.com' + img_url
            img_filename = f'gallery{gallery_num}_img{count}.jpg'
            file_path = os.path.join(DOWNLOAD_FOLDER, img_filename)
            try:
                img_data = requests.get(full_img_url).content
                with open(file_path, 'wb') as handler:
                    handler.write(img_data)
                count += 1
            except Exception as e:
                print(f"Failed to download {full_img_url}: {e}")

    return f"✅ Downloaded {count} images from Gallery {gallery_num}" if count else f"⚠️ No images found."

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/download', methods=['POST'])
def download():
    start_gallery = int(request.form['start_gallery'])
    end_gallery = int(request.form['end_gallery'])
    messages = [download_images_from_gallery(g) for g in range(start_gallery, end_gallery + 1)]
    return render_template('index.html', messages=messages)


@app.route('/check_chromedriver')
def check_chromedriver():
    try:
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)
        version = driver.capabilities['browserVersion']
        driver.quit()
        return f"✅ ChromeDriver is working! Version: {version}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
