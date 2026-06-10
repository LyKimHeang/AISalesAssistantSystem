from flask import Flask
from routes.user import user_bp
from routes.admin import admin_bp
from routes.auth import auth_bp
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# ── Upload folder for product images ──────────────────────────────────────────
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)   # create folder if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    from database import initialize_database, create_default_admin
    initialize_database()
    create_default_admin()
    app.run(debug=True)