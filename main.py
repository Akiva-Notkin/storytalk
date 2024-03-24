from flask import Flask, request, jsonify, render_template
from sklearn.metrics import pairwise_distances
import sqlite3
import ast
import re

app = Flask(__name__)

DATABASE = 'stored_embeddings.sqlite'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_embeddings_other_with_exclusion_list(exclusion_list, conn):
    query_str = f'SELECT * FROM embedded_stories WHERE id NOT IN ' \
                f'({",".join([str(x) for x in exclusion_list])})'
    embeddings = conn.execute(query_str).fetchall()
    return embeddings


def get_embedding_for_id(id, conn):
    # Query the database to get the embedding for the specified id
    embedding = conn.execute('SELECT * FROM embedded_stories WHERE id = ?', (id,)).fetchone()
    return embedding[3]


def find_closest_embedding(id, conn, seen):
    # Query the database to get all embeddings
    embedding = get_embedding_for_id(id, conn)

    embeddings = get_all_embeddings_other_with_exclusion_list([id] + seen, conn)

    # Extract the embeddings and their corresponding ids
    embedding_ids = [emb[0] for emb in embeddings]
    embeddings = [emb[3] for emb in embeddings]
    embeddings = [emb.replace('\n', '  ') for emb in embeddings]
    embeddings = [re.sub(r'\s+', ',', emb) for emb in embeddings]
    embeddings = [x[0] + x[2:] if x[1] == ',' else x for x in embeddings]
    embeddings = [ast.literal_eval(emb) for emb in embeddings]

    embedding = embedding.replace('\n', '  ')
    embedding = re.sub(r'\s+', ',', embedding)
    embedding = embedding[0] + embedding[2:] if embedding[1] == ',' else embedding
    embedding = ast.literal_eval(embedding)
    # Calculate the pairwise distances between the input embedding and all embeddings in the database
    distances = pairwise_distances([embedding], embeddings, metric='cosine')

    # Find the index of the closest embedding
    closest_index = distances.argmin()

    # Return the id of the closest embedding
    return embedding_ids[closest_index]

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/get-text', methods=['POST', 'GET'])
def get_text():
    data = request.json

    # Your logic here to determine which text to fetch
    # For example, let's assume you're looking for a text with a specific 'id'
    likes = data.get('likes', [])
    seen = data.get('seen', [])

    conn = get_db_connection()

    if len(likes) == 0:
        random_column = conn.execute('SELECT * FROM embedded_stories ORDER BY RANDOM() LIMIT 1').fetchone()
        while random_column[0] in seen:
            random_column = conn.execute('SELECT * FROM embedded_stories ORDER BY RANDOM() LIMIT 1').fetchone()
        return jsonify({'content': random_column[2], 'id': random_column[0]})

    closest_embed_dict = {}
    for like in likes:
        closest_embedding = find_closest_embedding(like, conn, seen)
        if closest_embedding in closest_embed_dict:
            closest_embed_dict[closest_embedding] += 1
        else:
            closest_embed_dict[closest_embedding] = 1

    closest_embed = max(closest_embed_dict, key=closest_embed_dict.get)
    text = conn.execute('SELECT * FROM embedded_stories WHERE id = ?', (closest_embed,)).fetchone()

    if text is None:
        return jsonify({'error': 'Text not found'}), 404

    response = jsonify({'content': text[2], 'id': text[0]})
    return response


if __name__ == '__main__':
    app.run(debug=True)
