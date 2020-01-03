import logging

from service.managers import item as item_manager
from service.orm.item import Status
from service.worker import celery_app


@celery_app.task(name="cpu_task")
def cpu_bound_task(item_id, carrier=None):
    """CPU bound background task.

    :param str item_id: ID of the requested item.
    :param dict carrier: tracing carrier.
    """
    try:
        logging.info("CPU bound task for item %s started", item_id)
        item_manager.update_item(item_id=item_id, status=Status.IN_PROGRESS)
        logging.info("CPU bound task for item %s ended successfully", item_id)
    except:  # noqa: E722
        item_manager.update_item(item_id=item_id, status=Status.ERROR)
        raise


@celery_app.task(name="io_task")
def io_bound_task(item_id, carrier=None):
    """IO bound background task.

    :param str item_id: ID of the requested item.
    :param dict carrier: tracing carrier.
    """
    try:
        logging.info("IO bound task for item %s started", item_id)
        item_manager.update_item(item_id=item_id, status=Status.READY)
        logging.info("IO bound task for item %s ended successfully", item_id)
    except:  # noqa: E722
        item_manager.update_item(item_id=item_id, status=Status.ERROR)
        raise
