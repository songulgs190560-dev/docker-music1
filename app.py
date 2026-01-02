from flask import Flask, render_template_string, request, redirect, url_for
import requests
import json
import os

app = Flask(__name__)

FAVORITES_FILE = "favorites.json"

# Favorileri dosyadan oku
def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Favorileri dosyaya kaydet
def save_favorites(favorites):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=4)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Songül Yağcı</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        :root { --bg-color: #121212; --card-color: #181818; --accent-color: #1DB954; --text-color: #ffffff; }
        body { font-family: 'Poppins', sans-serif; background-color: var(--bg-color); color: var(--text-color); margin: 0; padding: 20px; }
        .header { text-align: center; padding: 20px 0; }
        .search-box { display: flex; justify-content: center; gap: 10px; margin-bottom: 30px; }
        input { padding: 12px; width: 300px; border-radius: 25px; border: none; background: #282828; color: white; }
        button { padding: 12px 25px; border-radius: 25px; border: none; background: var(--accent-color); color: white; cursor: pointer; font-weight: 600; }
        .nav-links { margin-bottom: 20px; text-align: center; }
        .nav-links a { color: var(--accent-color); text-decoration: none; margin: 0 15px; font-weight: bold; }
        .container { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }
        .card { background: var(--card-color); padding: 15px; border-radius: 12px; text-align: center; position: relative; }
        .card img { width: 100%; border-radius: 8px; }
        .fav-btn { background: #ff4757; margin-top: 10px; width: 100%; }
        .remove-btn { background: #535c68; }
        audio { width: 100%; margin-top: 10px; filter: invert(0.8); }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎵 iTunes Explorer</h1>
        <div class="nav-links">
            <a href="/">🔍 Arama</a>
            <a href="/favorites">⭐ Favorilerim ({{ fav_count }})</a>
        </div>
        {% if show_search %}
        <div class="search-box">
            <form action="/" method="GET" style="display: flex; gap: 10px;">
                <input type="text" name="search" placeholder="Şarkı ara..." value="{{ term }}">
                <button type="submit">KEŞFET</button>
            </form>
        </div>
        {% endif %}
    </div>

    <div class="container">
        {% for track in tracks %}
        <div class="card">
            <img src="{{ track.artworkUrl100.replace('100x100', '400x400') }}">
            <h3>{{ track.trackName }}</h3>
            <p>{{ track.artistName }}</p>
            <audio controls src="{{ track.previewUrl }}"></audio>
            
            {% if show_search %}
            <form action="/add_favorite" method="POST">
                <input type="hidden" name="trackId" value="{{ track.trackId }}">
                <input type="hidden" name="trackName" value="{{ track.trackName }}">
                <input type="hidden" name="artistName" value="{{ track.artistName }}">
                <input type="hidden" name="artworkUrl100" value="{{ track.artworkUrl100 }}">
                <input type="hidden" name="previewUrl" value="{{ track.previewUrl }}">
                <button type="submit" class="fav-btn">⭐ Favoriye Ekle</button>
            </form>
            {% else %}
            <form action="/remove_favorite" method="POST">
                <input type="hidden" name="trackId" value="{{ track.trackId }}">
                <button type="submit" class="button remove-btn">🗑️ Kaldır</button>
            </form>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    term = request.args.get("search", "Tarkan")
    url = f"https://itunes.apple.com/search?term={term}&entity=song&limit=12"
    tracks = requests.get(url).json().get("results", [])
    favs = load_favorites()
    return render_template_string(HTML_TEMPLATE, tracks=tracks, term=term, fav_count=len(favs), show_search=True)

@app.route("/favorites")
def favorites_page():
    favs = load_favorites()
    return render_template_string(HTML_TEMPLATE, tracks=favs, fav_count=len(favs), show_search=False)

@app.route("/add_favorite", methods=["POST"])
def add_favorite():
    favs = load_favorites()
    track_id = request.form.get("trackId")
    
    # Eğer zaten ekliyse tekrar ekleme
    if not any(item['trackId'] == track_id for item in favs):
        favs.append(request.form.to_dict())
        save_favorites(favs)
    return redirect(url_for('index'))

@app.route("/remove_favorite", methods=["POST"])
def remove_favorite():
    favs = load_favorites()
    track_id = request.form.get("trackId")
    favs = [item for item in favs if item['trackId'] != track_id]
    save_favorites(favs)
    return redirect(url_for('favorites_page'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
