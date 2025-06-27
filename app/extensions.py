from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_security import Security
from flask_wtf.csrf import CSRFProtect  # <-- Add this import

# Other extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
security = Security()
csrf = CSRFProtect()  # <-- Add this line to create the csrf object