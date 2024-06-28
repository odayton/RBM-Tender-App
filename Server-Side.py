import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from config import Config

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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
