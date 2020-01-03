import logging

import waiting

from tests.integration.base import BaseTest, sc


class TestItemAPI(BaseTest):
    """Test item APIs."""

    def test_item_api(self):
        """Test Item APIs."""
        logging.info("Validating item list is empty")
        self.assertEqual(self.client.list_items(), [])

        logging.info("Creating a new item")
        created_item = self.client.create_item(item=sc.Item(name="test-name"))
        logging.info("Validating the created item %s", created_item)
        self.assertIsNotNone(created_item.id)
        self.assertIsNotNone(created_item.created_at)
        self.assertIsNotNone(created_item.updated_at)
        self.assertEqual(created_item.name, "test-name")
        self.assertEqual(created_item.status, "pending")

        logging.info("Waiting for item %s to be created", created_item.id)
        waiting.wait(
            lambda: self.client.get_item(created_item.id).status == "ready",
            timeout_seconds=10,
            sleep_seconds=1,
            waiting_for="item %s to reach 'ready' state" % created_item.id,
        )
        logging.info("Getting item %s", created_item.id)
        get_item = self.client.get_item(created_item.id)

        logging.info("Validating the get item %s", get_item)
        self.assertEqual(get_item.id, created_item.id)
        self.assertEqual(get_item.name, created_item.name)
        self.assertEqual(get_item.created_at, created_item.created_at)
        self.assertGreater(get_item.updated_at, created_item.updated_at)
        self.assertEqual(get_item.status, "ready")

        logging.info("Validating item list contains the item")
        self.assertEqual(self.client.list_items(), [get_item,])

        logging.info("Updating item %s", created_item.id)
        update_item = self.client.update_item(
            item_id=created_item.id, item=sc.Item(name="updated-name")
        )
        logging.info("Validating the updated item %s", update_item)
        self.assertEqual(update_item.name, "updated-name")
        self.assertEqual(update_item.id, created_item.id)
        self.assertEqual(update_item.created_at, created_item.created_at)
        self.assertGreater(update_item.updated_at, created_item.updated_at)

        logging.info("Deleting item %s", created_item.id)
        self.client.delete_item(created_item.id)

        logging.info("Validating item list is empty")
        self.assertEqual(self.client.list_items(), [])
