from flask import Flask, request, render_template
from googletrans import Translator
import mysql.connector
import redis

app = Flask(__name__)
translator = Translator()

# Configure MySQL
db_config = {
    'user': 'translator_user',
    'password': 'your_password',  # Replace with your MySQL user's password
    'host': 'mysql_ip',  # Replace with your MySQL VM IP
    'database': 'translator_db'
}

# Connect to MySQL
db = mysql.connector.connect(**db_config)
cursor = db.cursor()

# Connect to Redis
redis_client = redis.StrictRedis(host='redis_ip', port=6379, db=0)  # Replace with your Redis VM IP

@app.route('/', methods=['GET', 'POST'])
def index():
    translation = ""
    if request.method == 'POST':
        text = request.form['text']
        lang = request.form['lang']
        if lang == 'en_to_fr':
            translation = translator.translate(text, src='en', dest='fr').text
            redis_client.incr('total_translated_words', len(text.split()))
            redis_client.incr('en_to_fr_count')
        else:
            translation = translator.translate(text, src='fr', dest='en').text
            redis_client.incr('total_translated_words', len(text.split()))
            redis_client.incr('fr_to_en_count')

        # Save translation to MySQL
        cursor.execute(
            "INSERT INTO translations (source_lang, target_lang, original_text, translated_text, timestamp) VALUES (%s, %s, %s, %s, NOW())",
            (lang.split('_')[0], lang.split('_')[1], text, translation)
        )
        db.commit()

    return render_template('index.html', translation=translation)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
