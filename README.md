# Waifu Gallery Web App

A modern and responsive web application for browsing and sharing waifu images from [waifu.pics](https://waifu.pics/).

## Features

- 🖼️ Beautiful image gallery with hover effects
- 🔄 Infinite scroll loading
- 📋 Copy image URLs with one click
- 🔗 Direct image links
- 📱 Responsive design for all devices
- ⚡ Fast loading with image lazy loading
- 🎨 Modern and clean UI
- 🔒 SFW and NSFW categories

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/waifu-gallery.git
cd waifu-gallery
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the development server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Development

- The app uses Flask for the backend
- Frontend is built with vanilla HTML, CSS, and JavaScript
- Images are fetched from the waifu.pics API
- Caching is implemented to improve performance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- All images are provided by [waifu.pics](https://waifu.pics/)
- Font Awesome for the icons
- Flask and its ecosystem for the backend framework
