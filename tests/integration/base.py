import os
import importlib
import logging

from docker_test_tools import base_test
from docker_test_tools.utils import get_health_check

sc = importlib.import_module("service_client")

SERVICE_HOST = os.environ.get("SERVICE_HOST", "localhost")
SERVICE_BASE_URL = f"http://{SERVICE_HOST}/service/api/v1"
SERVICE_PROXY_HEALTH_CHECK = get_health_check(
    service_name="service",
    url=f"{SERVICE_BASE_URL}/health",
    expected_status=204,
)


class BaseTest(base_test.BaseDockerTest):
    """Base integration test."""

    REQUIRED_HEALTH_CHECKS = [
        SERVICE_PROXY_HEALTH_CHECK,
    ]

    def setUp(self):
        """Initialize the client."""
        super(BaseTest, self).setUp()

        logging.info("Initializing the service client")
        self.client = sc.DefaultApi(sc.ApiClient())
        self.client.api_client.configuration.host = SERVICE_BASE_URL
