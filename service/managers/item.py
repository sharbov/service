import datetime
import logging

from sqlalchemy import text

from service.orm.database import db
from service.orm.item import Item, Status


def create_item(name: str) -> Item:
    """Creates a new item.

    :param str name: item name.
    :return Item item: created item.
    """
    logging.info("Creating item named %s", name)
    item_record = Item(name=name, status=Status.PENDING)
    db.session.add(item_record)
    db.session.commit()
    return item_record


def get_item(item_id: str) -> Item:
    """Returns a item based on a item ID.

    :param str item_id: ID of the requested item.
    :return Item item: requested item.
    :raise ValueError: Item not found.
    """
    logging.debug("Getting item %s details", item_id)
    item = Item.query.filter(Item.id == item_id).one_or_none()
    if item is None:
        raise ValueError("Item %s not found" % item_id)

    return item


def update_item(item_id: str, name: str = None, status: str = None) -> Item:
    """Update item.

    :param str item_id: ID of the requested item
    :param str name: item name.
    :param str status: item status.
    :return Item item: updated item.
    :raise ValueError: Item not found.
    """
    logging.debug(
        "Updating item %s using name %s, status %s", item_id, name, status
    )
    item_record = get_item(item_id)
    item_record.name = name if name else item_record.name
    item_record.status = status if status else item_record.status
    item_record.updated_at = datetime.datetime.utcnow()
    db.session.add(item_record)
    db.session.commit()
    return item_record


def list_items(
    page: int, page_size: int, order_by: str, order: str, status: str = None
) -> list:
    """Returns all items.

    :param int page: page number.
    :param int page_size: number of channels in a page.
    :param str order_by: order by given field name.
    :param str order : order by ascending or descending.
    :param str status: status to filter by.
    :return list[Item]: items.
    """
    logging.debug(
        "Getting items, page %d, page size %d, "
        "sorting by %s, order %s, status %s",
        page,
        page_size,
        order_by,
        order,
        status,
    )
    query = Item.query

    if status:
        query = query.filter_by(status=status)

    if order_by or order:
        query = query.order_by(text(f"{order_by} {order}"))

    if page or page_size:
        query = query.paginate(page, page_size, error_out=False)

    return [item_record for item_record in query.items]


def delete_item(item_id: str):
    """Deletes a single item based on the ID supplied.

    :param str item_id: ID of the requested item.
    :raise ValueError: Item not found.
    """
    logging.info("Deleting item %s", item_id)
    item_record = get_item(item_id)
    db.session.delete(item_record)
    db.session.commit()
