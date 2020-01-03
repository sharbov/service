import logging

import waiting

from tests.integration.base import BaseTest, SERVICE_PROXY_HEALTH_CHECK, sc


class TestServicesFailure(BaseTest):
    """Validate behaviour on services down scenarios."""

    def test_api_down(self):
        """Validate service-api down scenario."""
        logging.info("Validating health api response")
        self.assertIsNone(self.client.get_health())

        logging.info("Validating health when service-api is down")
        with self.controller.container_down(
            name="api", health_check=SERVICE_PROXY_HEALTH_CHECK
        ):
            with self.assertRaises(sc.exceptions.ApiException) as cm:
                self.client.get_health(_request_timeout=1)
            self.assertEqual(404, cm.exception.status)

    def test_worker_down(self):
        """Validate service-worker down scenario."""
        logging.info("Validating api when service-worker is down")
        with self.controller.container_down(name="cpu_worker"):
            created_item = self.client.create_item(
                item=sc.Item(name="worker-down")
            )
            self.addCleanup(self.client.delete_item, created_item.id)

        logging.info("Validating task complete once the worker recover")
        waiting.wait(
            lambda: self.client.get_item(created_item.id).status == "ready",
            timeout_seconds=30,
            sleep_seconds=1,
            waiting_for="item %s to reach 'ready' state",
        )

    def test_postgres_down(self):
        """Validate postgres down scenario."""
        with self.controller.container_stopped(name="postgres"):
            logging.info("Validate listing items fails when postgres is down")
            with self.assertRaises(sc.exceptions.ApiException) as cm:
                self.client.list_items(_request_timeout=10)
            self.assertEqual(500, cm.exception.status)

        logging.info("Validate api succeeds when postgres recovers")
        self.assertIsNotNone(self.client.list_items())

    def test_rabbitmq_down(self):
        """Validate rabbitmq down scenario."""
        with self.controller.container_stopped(name="rabbitmq"):
            logging.info("Validate listing items works when rabbitmq is down")
            self.client.list_items(_request_timeout=1)

            logging.info("Validate creating item fails when rabbitmq is down")
            with self.assertRaises(sc.exceptions.ApiException) as cm:
                self.client.create_item(item=sc.Item(name="rabbitmq-down"))
            self.assertEqual(500, cm.exception.status)

    def test_jaeger_down(self):
        """Validate jaeger down scenario."""
        with self.controller.container_stopped(name="jaeger"):
            logging.info("Validate APIs work when jaeger is down")
            self.client.list_items(_request_timeout=1)
            item = self.client.create_item(item=sc.Item(name="jaeger-down"))
            self.client.get_item(item.id)
            self.client.update_item(item.id, item=sc.Item(name="updated"))
            self.client.delete_item(item.id)

    def test_statsd_down(self):
        """Validate statsd down scenario."""
        with self.controller.container_stopped(name="statsd"):
            logging.info("Validate APIs work when statsd is down")
            self.client.list_items(_request_timeout=1)
            item = self.client.create_item(item=sc.Item(name="statsd-down"))
            self.client.get_item(item.id)
            self.client.update_item(item.id, item=sc.Item(name="updated"))
            self.client.delete_item(item.id)
