import os
import requests
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch10'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch10:{query}", download=False)
            results = []
            for entry in info.get('entries', []):
                if entry:
                    results.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'duration': entry.get('duration'),
                        'uploader': entry.get('uploader'),
                        'thumbnail': entry.get('thumbnail')
                    })
            return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['GET'])
def download():
    video_id = request.args.get('id')
    if not video_id:
        return "No ID provided", 400
        
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
            title = info.get('title', 'track').replace('/', '_')
        
        req = requests.get(audio_url, stream=True)
        response = Response(req.iter_content(chunk_size=1024*64), content_type='audio/mpeg')
        response.headers["Content-Disposition"] = f'attachment; filename="{title}.mp3"'
        return response
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
