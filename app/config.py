import os
import logging
from logging.handlers import RotatingFileHandler

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///instance/RBM_Product.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    TECH_DATA_FOLDER = os.path.join(UPLOAD_FOLDER, 'tech-data')
    OTHER_UPLOADS_FOLDER = os.path.join(UPLOAD_FOLDER, 'others')

    # Logging configuration
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    # Ensure instance folder exists
    @staticmethod
    def init_app(app):
        try:
            os.makedirs(app.instance_path, exist_ok=True)
        except OSError:
            pass

        # Configure logging
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/rbm_tender_app.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('RBM Tender App startup')

class DevelopmentConfig(Config):
    DEBUG = os.environ.get('DEBUG', 'true').lower() in ['true', 'on', '1']

class ProductionConfig(Config):
    DEBUG = os.environ.get('DEBUG', 'false').lower() in ['true', 'on', '1']

# Dictionary for easier config selection
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
