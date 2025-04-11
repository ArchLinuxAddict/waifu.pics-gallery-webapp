from flask import Flask, render_template, request, jsonify
from flask_caching import Cache
import requests
from typing import List, Dict, Set
import logging
from functools import lru_cache
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import json
import os
import asyncio
import aiohttp
from aiohttp import ClientSession, TCPConnector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure cache with more aggressive settings
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 7200  # Cache for 2 hours
})

# Constants
API_BASE_URL = 'https://api.waifu.pics/'
DEFAULT_IMAGES_PER_PAGE = 30
MAX_IMAGES_PER_PAGE = 100
MAX_CONCURRENT_REQUESTS = 20
REQUEST_TIMEOUT = 5
BATCH_SIZE = 5

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

# File to store seen images
SEEN_IMAGES_FILE = 'seen_images.json'

# Load seen images from file if it exists
def load_seen_images():
    if os.path.exists(SEEN_IMAGES_FILE):
        try:
            with open(SEEN_IMAGES_FILE, 'r') as f:
                return set(json.load(f))
        except Exception as e:
            logger.error(f"Error loading seen images: {str(e)}")
    return set()

# Save seen images to file
def save_seen_images(images):
    try:
        with open(SEEN_IMAGES_FILE, 'w') as f:
            json.dump(list(images), f)
    except Exception as e:
        logger.error(f"Error saving seen images: {str(e)}")

# Initialize seen images
seen_images = load_seen_images()
seen_images_lock = threading.Lock()

async def fetch_batch(session: ClientSession, category: str, prefix: str, batch_size: int):
    tasks = []
    for _ in range(batch_size):
        tasks.append(fetch_single_image(session, category, prefix))
    return await asyncio.gather(*tasks)

async def fetch_single_image(session: ClientSession, category: str, prefix: str):
    try:
        async with session.get(f"{API_BASE_URL}{prefix}{category}", timeout=REQUEST_TIMEOUT) as response:
            if response.status == 200:
                data = await response.json()
                with seen_images_lock:
                    if 'url' in data and data['url'] not in seen_images:
                        seen_images.add(data['url'])
                        save_seen_images(seen_images)
                        return {
                            'url': data['url'],
                            'category': category
                        }
    except Exception as e:
        logger.error(f"Error fetching image for category {category}: {str(e)}")
    return None

async def fetch_images_async(categories: List[str], prefix: str, num_images: int) -> List[Dict[str, str]]:
    try:
        images = []
        num_images = max(DEFAULT_IMAGES_PER_PAGE, num_images)
        
        connector = TCPConnector(limit=MAX_CONCURRENT_REQUESTS)
        async with ClientSession(connector=connector) as session:
            if len(categories) == 1:
                # For single category, make batch requests
                while len(images) < num_images:
                    batch_results = await fetch_batch(session, categories[0], prefix, BATCH_SIZE)
                    for result in batch_results:
                        if result:
                            images.append(result)
                            if len(images) >= num_images:
                                break
            else:
                # For multiple categories, distribute requests
                images_per_category = max(3, num_images // len(categories))
                for category in categories:
                    while len(images) < num_images:
                        batch_results = await fetch_batch(session, category, prefix, BATCH_SIZE)
                        for result in batch_results:
                            if result:
                                images.append(result)
                                if len(images) >= num_images:
                                    break
                        if len(images) >= num_images:
                            break
                    if len(images) >= num_images:
                        break
        
        return images[:num_images]
    except Exception as e:
        logger.error(f"Unexpected error in fetch_images_async: {str(e)}")
        return []

def run_async_fetch(categories, prefix, num_images):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(fetch_images_async(categories, prefix, num_images))
    finally:
        loop.close()

@app.route('/')
def index():
    try:
        category = request.args.get('category', 'sfw')
        selected_category = request.args.get('selected_category', '')
        
        if category not in ['sfw', 'nsfw']:
            return render_template('error.html', message="Invalid category"), 400

        available_categories = TYPE1_CATEGORIES if category == 'sfw' else TYPE2_CATEGORIES
        
        if selected_category and selected_category in available_categories:
            images = run_async_fetch([selected_category], f"{category}/", DEFAULT_IMAGES_PER_PAGE)
        else:
            images = run_async_fetch(available_categories, f"{category}/", DEFAULT_IMAGES_PER_PAGE)

        return render_template('index.html', 
                            images=images, 
                            category=category,
                            selected_category=selected_category,
                            available_categories=available_categories)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return render_template('error.html', message="An error occurred"), 500

@app.route('/load_more')
def load_more():
    try:
        category = request.args.get('category', 'sfw')
        selected_category = request.args.get('selected_category', '')
        page = int(request.args.get('page', 1))
        
        if category not in ['sfw', 'nsfw']:
            return jsonify({"error": "Invalid category"}), 400

        available_categories = TYPE1_CATEGORIES if category == 'sfw' else TYPE2_CATEGORIES
        
        if selected_category and selected_category in available_categories:
            images = run_async_fetch([selected_category], f"{category}/", DEFAULT_IMAGES_PER_PAGE * page)
        else:
            images = run_async_fetch(available_categories, f"{category}/", DEFAULT_IMAGES_PER_PAGE * page)

        return render_template('image_list.html', images=images)
    except Exception as e:
        logger.error(f"Error in load_more route: {str(e)}")
        return jsonify({"error": "An error occurred"}), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', message="Internal server error"), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
