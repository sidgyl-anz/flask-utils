from flask import Flask, render_template, request, send_from_directory
import os
import time
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
DOWNLOAD_FOLDER = 'static/downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_images_from_gallery(gallery_num):
    url = f'https://platesmania.com/kr/gallery-{gallery_num}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Failed to access {url}: {e}"

    soup = BeautifulSoup(response.content, 'html.parser')
    images = soup.find_all('img')

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

    return f"Downloaded {count} images from Gallery {gallery_num}."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    start_gallery = int(request.form['start_gallery'])
    end_gallery = int(request.form['end_gallery'])

    messages = []
    for gallery_num in range(start_gallery, end_gallery + 1):
        message = download_images_from_gallery(gallery_num)
        messages.append(message)

    return render_template('index.html', messages=messages)

@app.route('/downloaded/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
