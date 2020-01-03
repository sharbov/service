import subprocess

import waiting
from docker_test_tools.utils import get_health_check

# Define health check functions for the environment services
service_health_check = get_health_check(
    "service", url="http://host.docker.internal/service/api/v1"
)


def scale(service, instances):
    subprocess.check_call(
        ["docker-compose", "-p", "test", "scale", f"{service}={instances}",],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def wait_for_health(service, timeout):
    waiting.wait(
        lambda: b'"healthy"'
        in subprocess.check_output(
            [
                "docker",
                "inspect",
                "--format='{{json .State.Health.Status}}'",
                service,
            ],
        ),
        timeout_seconds=timeout,
        sleep_seconds=1,
        waiting_for="%s to be healthy" % service,
        expected_exceptions=(Exception,),
    )
