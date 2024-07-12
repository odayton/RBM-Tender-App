import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure the upload folders exist
    os.makedirs(app.config['TECH_DATA_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OTHER_UPLOADS_FOLDER'], exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.blueprints.pumps import pumps_bp
    from app.blueprints.hydronics import hydronics_bp
    from app.blueprints.hydraulic import hydraulic_bp
    #from app.blueprints.quotes import quotes_bp
    from app.blueprints.admin import admin_bp

    app.register_blueprint(pumps_bp, url_prefix='/pumps')
    app.register_blueprint(hydronics_bp, url_prefix='/hydronics')
    app.register_blueprint(hydraulic_bp, url_prefix='/hydraulic')
    #app.register_blueprint(quotes_bp, url_prefix='/quotes')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.route('/')
    def home():
        return render_template('home.html', page_id='home')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
