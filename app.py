# app.py
from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)

# Database initialization
def init_db():
    with sqlite3.connect('queries.db') as conn:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            last_run TIMESTAMP
        )
        ''')
        
        conn.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY,
            query_id INTEGER,
            response_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(query_id) REFERENCES queries(id)
        )
        ''')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/queries', methods=['GET'])
def get_queries():
    with sqlite3.connect('queries.db') as conn:
        queries = conn.execute('SELECT * FROM queries').fetchall()
        return jsonify([{'id': q[0], 'title': q[1], 'body': q[2], 'last_run': q[3]} for q in queries])

@app.route('/queries', methods=['POST'])
def add_query():
    data = request.json
    with sqlite3.connect('queries.db') as conn:
        cur = conn.execute(
            'INSERT INTO queries (title, body) VALUES (?, ?)',
            (data['title'], data['body'])
        )
        return jsonify({'id': cur.lastrowid, 'title': data['title'], 'body': data['body']})

@app.route('/queries/<int:query_id>', methods=['DELETE'])
def delete_query(query_id):
    with sqlite3.connect('queries.db') as conn:
        conn.execute('DELETE FROM queries WHERE id = ?', (query_id,))
        return jsonify({'status': 'success'})

# Mock API call - replace with real Perplexity API later
def mock_api_call(query):
    return f"Mock response for query: {query}"

@app.route('/run_query/<int:query_id>', methods=['POST'])
def run_query(query_id):
    with sqlite3.connect('queries.db') as conn:
        query = conn.execute('SELECT * FROM queries WHERE id = ?', (query_id,)).fetchone()
        if query:
            response = mock_api_call(query[2])  # Mock API call
            conn.execute(
                'INSERT INTO responses (query_id, response_text) VALUES (?, ?)',
                (query_id, response)
            )
            conn.execute(
                'UPDATE queries SET last_run = ? WHERE id = ?',
                (datetime.now().isoformat(), query_id)
            )
            return jsonify({'status': 'success', 'response': response})
    return jsonify({'status': 'error', 'message': 'Query not found'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)