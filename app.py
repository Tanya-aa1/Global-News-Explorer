
from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

# Connect to SQLite DB
def get_db_connection():
    conn = sqlite3.connect('news_data.db')
    conn.row_factory = sqlite3.Row
    return conn

#1. Get all news
@app.route('/news', methods=['GET'])
def get_all_news():
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM news')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

#2. filter news
@app.route('/news/filter', methods=['GET'])
def filter_news():
    country = request.args.get('country')
    source = request.args.get('source')
    keyword = request.args.get('keyword')
    year = request.args.get('year')
    language = request.args.get('language')


    query = "SELECT * FROM news WHERE 1=1"
    params = []

    def build_in_clause(field, values):
        values = [v.strip().lower() for v in values.split(',') if v.strip()]
        clause = " OR ".join([f"LOWER({field}) = ?" for _ in values])
        return f" AND ({clause})", values

    if country:
        clause, vals = build_in_clause("country", country)
        query += clause
        params.extend(vals)

    if source:
        clause, vals = build_in_clause("source", source)
        query += clause
        params.extend(vals)

    if year:
        years = [y.strip() for y in year.split(',') if y.strip()]
        year_conditions = " OR ".join(["publication_date LIKE ?"] * len(years))
        query += f" AND ({year_conditions})"
        params.extend([f"%{y}%" for y in years])

    if keyword:
        keywords = [k.strip() for k in keyword.split(',') if k.strip()]
        keyword_conditions = " OR ".join(["LOWER(title) LIKE ?"] * len(keywords))
        query += f" AND ({keyword_conditions})"
        params.extend([f"%{k.lower()}%" for k in keywords])

    if language:
        clause, vals = build_in_clause("language", language)
        query += clause
        params.extend(vals)


    conn = get_db_connection()
    cursor = conn.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


#3. Get distinct countries
@app.route('/news/countries', methods=['GET'])
def get_countries():
    conn = get_db_connection()
    cursor = conn.execute('SELECT DISTINCT country FROM news')
    countries = [row['country'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(countries)


#4. Get distinct sources
@app.route('/news/sources', methods=['GET'])
def get_sources():
    conn = get_db_connection()
    cursor = conn.execute('SELECT DISTINCT source FROM news')
    sources = [row['source'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(sources)

#5. Get distinct languages
@app.route('/news/languages', methods=['GET'])
def get_languages():
    conn = get_db_connection()
    cursor = conn.execute('SELECT DISTINCT language FROM news')
    languages = [row['language'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(languages)



# Run the app
if __name__ == '__main__':
    app.run(debug=True)

