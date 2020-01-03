import logging

from celery import chain
from connexion import NoContent
from flask import g
from kombu import exceptions

from service.managers import item as item_manager
from service.tasks.item import io_bound_task, cpu_bound_task


def create_item(item: dict) -> tuple:
    """Creates a new item.

    :param dict item: Creation parameters, see swagger for details.
    :return tuple (dict, int): (item response, status code)
    """
    record = item_manager.create_item(name=item["name"])
    carrier = getattr(g, "carrier", None)

    try:
        chain(
            cpu_bound_task.si(record.id, carrier=carrier).set(queue="cpu"),
            io_bound_task.si(record.id, carrier=carrier).set(queue="io"),
        ).apply_async()

    except exceptions.OperationalError:
        logging.error("Item %s creation failed, cleaning up", record.id)
        item_manager.delete_item(record.id)
        raise

    return record.to_dict(), 201


def get_item(item_id: str) -> tuple:
    """Returns a item based on a item ID.

    :param str item_id: ID of the requested item.
    :return tuple (dict, int): (item response, status code).
    """
    try:
        record = item_manager.get_item(item_id=item_id)
        return record.to_dict(), 200
    except ValueError as exc:
        return str(exc), 404


def update_item(item_id: str, item: dict) -> tuple:
    """Update item.

    :param str item_id: ID of the requested item.
    :param dict item: item parameters, see swagger for details.
    :return tuple (dict, int): (item response, status code).
    """
    try:
        record = item_manager.update_item(item_id=item_id, name=item["name"])
        return record.to_dict(), 200

    except ValueError as exc:
        return str(exc), 404


def list_items(
    page: int, page_size: int, order_by: str, order: str, status: str = None
) -> list:
    """Returns all items.

    :param int page: page number.
    :param int page_size: number of channels in a page.
    :param str order_by: order by given field name.
    :param str order : order by ascending or descending.
    :param str status: status to filter by.
    :return list[dict]: items.
    """
    return [
        record.to_dict()
        for record in item_manager.list_items(
            page=page,
            page_size=page_size,
            order_by=order_by,
            order=order,
            status=status,
        )
    ]


def delete_item(item_id: str) -> tuple:
    """Deletes a single item based on the ID supplied.

    :param str item_id: ID of the requested item.
    :return tuple (dict, int): (item response, status code).
    """
    try:
        item_manager.delete_item(item_id=item_id)
        return NoContent, 204

    except ValueError as exc:
        return str(exc), 404
