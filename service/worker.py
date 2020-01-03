from contextlib import ExitStack

from celery import Celery
from celery.signals import worker_process_init
from flask import has_app_context

from service.middleware.tracer import tracer
from service.orm.database import db


class InstrumentedCelery(Celery):
    """Celery wrapper for flask apps."""

    def __init__(self, *args, **kwargs):
        """Initialize celery."""
        super(InstrumentedCelery, self).__init__(*args, **kwargs)

        self.app = None
        self.tracing_enabled = None

    def init_app(self, app):
        """Set the flask app & patch celery task."""
        self.app = app
        self.tracing_enabled = app.config["TRACER_ENABLED"]

        self.config_from_object(app.config)
        self.conf.update(
            worker_redirect_stdouts=False,
            worker_hijack_root_logger=False,
            worker_prefetch_multiplier=1,
        )
        self.patch_task()

    def patch_task(self):
        """Patch celery tasks to use middleware."""
        TaskBase = self.Task
        _celery = self

        class InstrumentedTask(TaskBase):
            """Patched celery task"""

            abstract = True

            def __call__(self, *args, **kwargs):
                """Run the task using middleware context."""
                ctx_managers = []

                # Patch task to publish tracing info to jaeger
                if _celery.tracing_enabled:
                    ctx_managers.append(
                        tracer.start_span(self.name, kwargs.get("carrier"))
                    )

                # Patch task to use flask app context
                if not has_app_context():
                    ctx_managers.append(_celery.app.app_context())

                with ExitStack() as stack:
                    for ctx_manager in ctx_managers:
                        stack.enter_context(ctx_manager)
                    return TaskBase.__call__(self, *args, **kwargs)

        self.Task = InstrumentedTask


celery_app = InstrumentedCelery()


@worker_process_init.connect
def initialize_worker(**_):
    """Cleanup pre-fork variables.

    Celery fork's the parent process, db engine & connection pool included.
    But, the db connections should not be shared across processes, so we
    to dispose of all existing connections.
    Same goes for Jaeger tracer.
    """
    # cleanup jaeger instance
    tracer.init_app(celery_app.app)

    # cleanup db connections
    with celery_app.app.app_context():
        db.engine.dispose()
