# flake8: noqa
from datetime import datetime
from uuid import uuid4

from service.orm.database import db, UUID_LENGTH, NAME_LENGTH, date_to_str

now_callback = datetime.utcnow


class Status(object):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    READY = "ready"
    ERROR = "error"


class Item(db.Model):
    """Item DB Model"""

    id = db.Column(
        db.String(UUID_LENGTH), default=lambda: str(uuid4()), primary_key=True
    )
    name = db.Column(db.String(NAME_LENGTH), unique=False, nullable=False)
    status = db.Column(db.String(NAME_LENGTH), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=now_callback)
    updated_at = db.Column(db.DateTime, nullable=False, default=now_callback)

    def __str__(self):
        """Return a string representation of the item."""
        return "Item(%s)" % ",".join(
            "%s=%s" % (k, v) for k, v in self.to_dict()
        )

    def to_dict(self):
        """Return a dictionary representation of the item."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "created_at": date_to_str(self.created_at),
            "updated_at": date_to_str(self.updated_at),
        }
