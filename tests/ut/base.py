import logging

import connexion
import mock
from flask_testing import TestCase

from service.config import Testing
from service.middleware.tracer import tracer
from service.orm import database
from service.worker import celery_app


class BaseTestCase(TestCase):
    def create_app(self):
        for logger_name in [
            "connexion.app",
            "connexion.operation",
            "connexion.apis.abstract",
            "connexion.apis.flask_api",
            "connexion.operations.secure",
            "connexion.operations.openapi3",
            "connexion.operations.abstract",
            "connexion.decorators.validation",
            "openapi_spec_validator.decorators",
            "openapi_spec_validator.validators",
        ]:
            logging.getLogger(logger_name).setLevel("ERROR")

        connexion_app = connexion.App(
            __name__, specification_dir="../../service"
        )
        app = connexion_app.app
        app.config.from_object(Testing)

        # Setup Database
        database.db.init_app(app)
        database.create(app)

        # Setup Celery
        celery_app.init_app(app=app)

        with mock.patch(
            "socket.gethostbyname", mock.MagicMock(return_valure="localhost")
        ):
            # Setup Jaeger tracer
            tracer.init_app(app)

        # Add APIs
        connexion_app.add_api(
            "spec.yaml", validate_responses=True, strict_validation=True
        )
        return app
