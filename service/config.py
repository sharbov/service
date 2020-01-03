import os


class Config(object):
    """Base configuration."""

    DEBUG = False
    TESTING = False
    DEVELOPMENT = False

    # SQLAlchemy Config
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Celery Config
    CELERY_IGNORE_RESULT = True
    BROKER_TRANSPORT_OPTIONS = {
        "max_retries": 3,
        "interval_start": 0,
        "interval_step": 0.2,
        "interval_max": 0.5,
    }

    # Tracing Config
    TRACER_ENABLED = 0
    TRACER_HOST = None
    SERVICE_NAME = "service"

    # Metric Config
    METRICS_ENABLED = 0
    STATSD_HOST = None
    STATSD_PORT = None


class Testing(Config):
    """Testing configuration."""

    TESTING = True

    # SQLAlchemy Config
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # Celery Config
    BROKER_URL = "fake-broker-url"
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


class Development(Config):
    """Development configuration."""

    DEVELOPMENT = True
    DEBUG = True

    # SQLAlchemy Config
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:pass@postgres:5432/service"
    )
    # Celery Config
    BROKER_URL = "pyamqp://admin:mypass@rabbitmq//"

    # Tracing Config
    TRACER_ENABLED = int(os.environ.get("TRACE_ENABLED", 0))
    TRACER_HOST = "jaeger"
    SERVICE_NAME = os.environ.get("SERVICE_NAME")

    # Metric Config
    METRICS_ENABLED = int(os.environ.get("METRICS_ENABLED", 0))
    STATSD_HOST = "statsd"
    STATSD_PORT = 9125


class Production(Config):
    """Production configuration."""

    # SQLAlchemy Config
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Celery Config
    BROKER_URL = os.environ.get("BROKER_URL")

    # Metrics Config
    METRICS_ENABLED = int(os.environ.get("METRICS_ENABLED", 0))
    STATSD_HOST = os.environ.get("STATSD_HOST")
    STATSD_PORT = int(os.environ.get("STATSD_PORT", 0))

    # Tracing Config
    TRACER_ENABLED = int(os.environ.get("TRACE_ENABLED", 0))
    TRACER_HOST = os.environ.get("TRACE_HOST")
    SERVICE_NAME = os.environ.get("SERVICE_NAME")
