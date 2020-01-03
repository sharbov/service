from flask_sqlalchemy import SQLAlchemy
from retry import retry
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

UUID_LENGTH = 36
NAME_LENGTH = 50

db = SQLAlchemy(engine_options={"pool_pre_ping": True})


def date_to_str(date_time):
    """Return a string representation of the given date-time."""
    return date_time.isoformat("T") + "Z" if date_time else None


@retry(tries=10, delay=1, max_delay=60, backoff=2, jitter=(2, 4))
def create(app):
    """Create service database on start up."""
    with app.app_context():
        engine = create_engine(
            app.config["SQLALCHEMY_DATABASE_URI"], convert_unicode=True
        )
        if not database_exists(engine.url):
            create_database(engine.url)
        db.create_all()
