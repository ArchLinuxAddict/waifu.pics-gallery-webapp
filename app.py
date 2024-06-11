from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Constants
API_BASE_URL = 'https://api.waifu.pics/'

# Define categories
TYPE1_CATEGORIES = [
    'waifu', 'neko', 'shinobu', 'megumin', 'bully', 'cuddle', 'cry', 'hug', 'awoo',
    'kiss', 'lick', 'pat', 'smug', 'bonk', 'yeet', 'blush', 'smile', 'wave',
    'highfive', 'handhold', 'nom', 'bite', 'glomp', 'slap', 'kill', 'kick',
    'happy', 'wink', 'poke', 'dance', 'cringe'
]

TYPE2_CATEGORIES = [
    'waifu', 'neko', 'trap', 'blowjob'
]

# Number of images to fetch per request
IMAGES_PER_PAGE = 10

@app.route('/')
def index():
    # Determine category based on request args (default to SFW)
    category = request.args.get('category', 'sfw')

    if category == 'sfw':
        images = fetch_images(TYPE1_CATEGORIES, 'sfw/', IMAGES_PER_PAGE)
    elif category == 'nsfw':
        images = fetch_images(TYPE2_CATEGORIES, 'nsfw/', IMAGES_PER_PAGE)
    else:
        return "Invalid category", 400

    return render_template('index.html', images=images, category=category)

@app.route('/load_more')
def load_more():
    category = request.args.get('category', 'sfw')
    page = int(request.args.get('page', 1))
    
    if category == 'sfw':
        images = fetch_images(TYPE1_CATEGORIES, 'sfw/', IMAGES_PER_PAGE * page)
    elif category == 'nsfw':
        images = fetch_images(TYPE2_CATEGORIES, 'nsfw/', IMAGES_PER_PAGE * page)
    else:
        return "Invalid category", 400

    return render_template('image_list.html', images=images, category=category, page=page)

def fetch_images(categories, prefix, num_images):
    try:
        images = []
        for category in categories:
            response = requests.get(f"{API_BASE_URL}{prefix}{category}")
            response.raise_for_status()
            data = response.json()
            image_url = data['url']
            images.append({'url': image_url})
            # Break loop if enough images are fetched
            if len(images) >= num_images:
                break
        return images
    except requests.exceptions.RequestException as e:
        print('Error fetching images:', e)
        return []

if __name__ == '__main__':
    app.run(debug=True)
