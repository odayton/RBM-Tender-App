from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
import os
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Application configuration
app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config.DevelopmentConfig')

# Set up logging
if not app.debug:
    if not os.path.exists('logs'):
        os.makedirs('logs')
    file_handler = RotatingFileHandler('logs/pump_management.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Pump Management startup')

# Ensure the upload folders exist
try:
    os.makedirs(app.config['TECH_DATA_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OTHER_UPLOADS_FOLDER'], exist_ok=True)
except OSError as e:
    app.logger.error(f"Error creating directories: {e}")

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Register blueprints
from blueprints.pumps import pumps_bp
from blueprints.hydronics import hydronics_bp
from blueprints.hydraulic import hydraulic_bp
from blueprints.quotes import quotes_bp

app.register_blueprint(pumps_bp, url_prefix='/pumps')
app.register_blueprint(hydronics_bp, url_prefix='/hydronics')
app.register_blueprint(hydraulic_bp, url_prefix='/hydraulic')
app.register_blueprint(quotes_bp, url_prefix='/quotes')

@app.route('/')
def home():
    return render_template('home.html', page_id='home')

if __name__ == '__main__':
    app.run()
