from flask import Flask, render_template, request, send_file
import os
import time
import requests
from bs4 import BeautifulSoup
import zipfile

app = Flask(__name__)
DOWNLOAD_FOLDER = 'static/downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Headers to mimic real browser behavior
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://platesmania.com/",
    "Connection": "keep-alive",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1"
}

def download_images_from_gallery(gallery_num):
    url = f'https://platesmania.com/kr/gallery-{gallery_num}'
    session = requests.Session()  # Maintains session cookies
    session.headers.update(HEADERS)

    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"❌ Failed to access {url}: {e}"

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
                img_data = session.get(full_img_url, timeout=10).content
                with open(file_path, 'wb') as handler:
                    handler.write(img_data)
                count += 1
                print(f"✅ Downloaded {img_filename}")
            except Exception as e:
                print(f"⚠️ Failed to download {full_img_url}: {e}")
        
        time.sleep(2)  # Delay to prevent triggering anti-bot

    if count == 0:
        return f"⚠️ No images found in Gallery {gallery_num}."
    return f"✅ Downloaded {count} images from Gallery {gallery_num}."

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

@app.route('/download_all')
def download_all():
    zip_filename = 'all_images.zip'
    zip_filepath = os.path.join(DOWNLOAD_FOLDER, zip_filename)

    # Create ZIP file
    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for root, dirs, files in os.walk(DOWNLOAD_FOLDER):
            for file in files:
                if file != zip_filename:  # Avoid adding the ZIP itself
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, DOWNLOAD_FOLDER))

    return send_file(zip_filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
