from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy

# Define a naming convention for all database constraints (keys, indexes, etc.).
# This solves the "Constraint must have a name" error with SQLite and Alembic.
metadata = MetaData(
    naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

# Use the 'metadata' parameter, which is correct for Flask-SQLAlchemy v2.x
db = SQLAlchemy(metadata=metadata)