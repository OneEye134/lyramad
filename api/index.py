from flask import Flask, render_template, request
import os, json, collections

app = Flask(__name__)
BAD_DIR = './api/bad'

# Load all JSON files
def load_profanities():
    profanities = {}
    for filename in os.listdir(BAD_DIR):
        if filename.endswith('.json'):
            path = os.path.join(BAD_DIR, filename)
            word = filename.split('_')[0]  # get "puta" from "puta_0832pm_april6.json"
            with open(path, 'r', encoding='utf-8') as f:
                profanities[word] = json.load(f)
    return profanities

profanities = load_profanities()

# Homepage
@app.route('/')
def index():
    categories = list(profanities.keys())
    return render_template('index.html', categories=categories)

# Search by category or word
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    results = []
    for word, entries in profanities.items():
        if query in word or query in ''.join([e['msg'].lower() for e in entries]):
            for e in entries:
                results.append({'word': word, **e})
    return render_template('search.html', query=query, results=results)

# Leaderboard
@app.route('/leaderboard')
def leaderboard():
    counter = collections.Counter()
    for entries in profanities.values():
        for e in entries:
            counter[e['name']] += 1
    top_users = counter.most_common(20)
    return render_template('leaderboard.html', top_users=top_users)

if __name__ == '__main__':
    app.run(debug=True)