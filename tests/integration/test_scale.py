import logging

import waiting

from tests.integration.base import BaseTest, sc
from tests.integration.tools import scale, wait_for_health


class TestScale(BaseTest):
    """Test service scale."""

    def setUp(self):
        super(TestScale, self).setUp()

        self.item_num = 500
        self.timeout_seconds = 100

    def test_scale(self):
        """Test API concurrency."""
        self.validate_service_under_stress()

    def test_scale_multi_instance(self):
        """Test service can scale horizontally."""
        scale("api", 2)
        self.addCleanup(lambda: scale("api", 1))

        scale("cpu_worker", 2)
        self.addCleanup(lambda: scale("cpu_worker", 1))

        wait_for_health("test_api_2", self.timeout_seconds)
        self.validate_service_under_stress()

    def validate_service_under_stress(self):
        """Test service can scale horizontally."""
        self.create_items()
        self.wait_for_items_to_be_created()
        self.wait_for_items_to_be_ready()
        self.delete_items()
        self.wait_for_items_to_be_deleted()

    def create_items(self):
        """Create items."""
        logging.info("Creating %s items", self.item_num)
        for i in range(self.item_num):
            self.client.create_item(
                item=sc.Item(name=self._testMethodName + str(i)),
                async_req=True,
            )

    def wait_for_items_to_be_created(self):
        """Wait for items to be created."""
        logging.info("Waiting for %s items to be created", self.item_num)
        waiting.wait(
            lambda: self.client.list_items(page=self.item_num, page_size=1),
            timeout_seconds=self.timeout_seconds,
            sleep_seconds=1,
            waiting_for="%s items to be created" % self.item_num,
        )

    def wait_for_items_to_be_ready(self):
        """Wait for items to be ready."""
        logging.info("Waiting for %s items to be ready", self.item_num)
        waiting.wait(
            lambda: len(
                self.client.list_items(page_size=self.item_num, status="ready")
            )
            == self.item_num,
            timeout_seconds=self.timeout_seconds,
            sleep_seconds=1,
            waiting_for="%s items to reach 'ready' state" % self.item_num,
        )

    def delete_items(self):
        """Delete all items."""
        logging.info("Deleting %s items", self.item_num)
        for item_record in self.client.list_items(page_size=self.item_num):
            self.client.delete_item(item_record.id, async_req=True)

    def wait_for_items_to_be_deleted(self):
        """Wait for items to be deleted."""
        logging.info("Waiting for %s items to be deleted", self.item_num)
        waiting.wait(
            lambda: len(self.client.list_items(page_size=self.item_num)) == 0,
            timeout_seconds=self.timeout_seconds,
            sleep_seconds=1,
            waiting_for="%s items to be deleted" % self.item_num,
        )
