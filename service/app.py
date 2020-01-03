#!/usr/bin/env python
"""Service Entry Point."""
import logging
import os
import sys

import connexion
from swagger_ui_bundle import swagger_ui_3_path

from service.middleware.tracer import tracer
from service.orm import database
from service.worker import celery_app

logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s [%(name)s]",
)
# Create a Connexion App
connexion_app = connexion.App(
    __name__,
    specification_dir="./",
    options={
        "swagger_ui": True,
        "serve_spec": True,
        "swagger_path": swagger_ui_3_path,
        "swagger_url": None,
    },
)
app = connexion_app.app
app.url_map.strict_slashes = False
connexion_app.add_api(
    "spec.yaml", validate_responses=True, strict_validation=True
)
# Setup Configuration
app.config.from_object(os.environ["APP_SETTINGS"])

# Setup Database
database.db.init_app(app)
database.create(app)

# Setup Jaeger tracer
tracer.init_app(app)

# Setup Celery
celery_app.init_app(app)
