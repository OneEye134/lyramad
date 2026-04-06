from flask import Flask, render_template, request, send_from_directory, abort
import os, json, collections, urllib.parse

app = Flask(__name__)
BAD_DIR = './api/bad'

def load_profanities():
    profanities = {}
    for filename in os.listdir(BAD_DIR):
        if filename.endswith('.json'):
            path = os.path.join(BAD_DIR, filename)
            word = filename.split('_')[0].lower()
            with open(path, 'r', encoding='utf-8') as f:
                profanities[word] = json.load(f)
    return profanities

profanities = load_profanities()

@app.context_processor
def inject_categories():
    return dict(categories=list(profanities.keys()))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    results = []
    for word, entries in profanities.items():
        if query in word or any(query in e['msg'].lower() for e in entries):
            for e in entries:
                results.append({'word': word, **e})
    return render_template('search.html', query=query, results=results)

@app.route('/leaderboard')
def leaderboard():
    counter = collections.Counter()
    for entries in profanities.values():
        for e in entries:
            counter[e['name']] += 1
    top_users = counter.most_common(20)
    return render_template('leaderboard.html', top_users=top_users)

@app.route('/leaderboard/<word>')
def word_leaderboard(word):
    word = word.lower()
    if word not in profanities:
        return f"No data for {word}", 404
    counter = collections.Counter()
    for e in profanities[word]:
        counter[e['name']] += 1
    top_users = counter.most_common(20)
    return render_template('leaderboard.html', top_users=top_users, word=word)

PFP_DIR = './api/pfp'  # Folder where profile pictures are stored

@app.route('/api/pfp/<path:name>')
def profile_pic(name):
    # Decode URL-encoded characters
    decoded_name = urllib.parse.unquote(name)

    # Remove dangerous characters to prevent directory traversal
    safe_name = decoded_name.replace('/', '_').replace('\\', '_')

    # Construct filename with .jpg
    filename = f"{safe_name}.jpg"
    file_path = os.path.join(PFP_DIR, filename)

    if os.path.exists(file_path):
        return send_from_directory(PFP_DIR, filename)
    else:
        # Return default avatar if the file doesn't exist
        return send_from_directory(PFP_DIR, 'Oompa Loompa.jpg')

if __name__ == '__main__':
    app.run(debug=True)