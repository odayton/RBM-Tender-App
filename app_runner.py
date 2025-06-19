from app import create_app
import os

# Create application instance
app = create_app(os.getenv('FLASK_CONFIG') or 'development')

# Ensure required directories exist
required_dirs = [
    'uploads',
    'uploads/tech-data',
    'uploads/others',
    'extracted_historic_graphs',
    'extracted_blank_graphs',
    'instance',
    'logs'
]

for directory in required_dirs:
    if not os.path.exists(directory):
        os.makedirs(directory)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )