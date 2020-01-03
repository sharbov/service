import logging
import sys
from collections import defaultdict

import statsd
from celery.events.snapshot import Polaroid

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(message)s",
)


class EventsTracker(Polaroid):
    """Record event snapshots and report to statsd."""

    clear_after = True  # clear after flush (incl, state.event_count).

    def __init__(self, *args, **kwargs):
        super(EventsTracker, self).__init__(*args, **kwargs)
        self.statsd = statsd.StatsClient(
            host=self.app.conf["STATSD_HOST"],
            port=self.app.conf["STATSD_PORT"],
        )
        self.worker_last_state = None
        self.worker_types = set()

    def on_shutter(self, state):
        """Called by celery every set interval with the updated state.

        :param celery.events.State state: Celery state.
        """
        if not state.event_count:  # No new events
            self.publish_workers_stats(worker_names=[])
            return

        self.publish_workers_stats(worker_names=list(state.workers.keys()))
        self.publish_tasks_stats(tasks=state.tasks.values())

    def publish_workers_stats(self, worker_names):
        """Publish worker stats.

        :param list[str] worker_names:
        """
        worker_type_counter = defaultdict(int)
        for worker_name in worker_names:
            worker_type, worker_host = worker_name.split("@")
            worker_type_counter[worker_type] += 1
            self.worker_types.add(worker_type)

        # Set missing workers count to zero
        for worker_type in self.worker_types:
            if worker_type not in worker_type_counter:
                worker_type_counter[worker_type] = 0

        for worker_type, count in worker_type_counter.items():
            self.statsd.gauge("celery.worker_count." + worker_type, count)

        if self.worker_last_state != worker_names:
            logging.info(dict(worker_type_counter))
            self.worker_last_state = worker_names

    def publish_tasks_stats(self, tasks):
        """Publish tasks stats.

        :param list[celery.events.state.Task] tasks: list of tasks.
        """
        for task in tasks:
            worker_type, worker_host = task.worker.hostname.split("@")
            logging.info(task)
            self.statsd.incr(
                stat="celery.tasks.{name}.{state}.{worker}.{host}".format(
                    name=task.name,
                    state=task.state,
                    worker=worker_type,
                    host=worker_host,
                )
            )
            if task.runtime:
                self.statsd.timing(
                    stat="celery.task_duration." + task.name,
                    delta=task.runtime * 1000,
                )
