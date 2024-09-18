# run.py
import os
from app import create_app

os.environ['FLASK_ENV'] = 'development'
app = create_app('development')

if __name__ == '__main__':
    print("Starting the application...")
    print("URL: http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)