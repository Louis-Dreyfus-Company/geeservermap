"""The Async class is used to manage async flask jobs."""

import atexit
import time
import uuid
from contextlib import suppress
from threading import Thread
from typing import Optional


class Async:
    """The Async class is used to manage async flask jobs."""

    _INTERVAL: int = 60
    "Interval between cleanup jobs in seconds"

    _TIMEOUT: int = 300
    "Timeout in seconds"

    _jobs: dict
    "Dictionary of existing jobs"

    cleanup_running: bool = False
    "Flag to indicate if the cleanup thread is running"

    cleanup_thread: Optional[Thread] = None
    "Thread that runs the cleanup job"

    def __init__(self):
        """Init the Async class by setting up the jobs dictionary."""
        self._jobs = {}
        atexit.register(self._terminate)

    def _run_cleanup(self):
        """Init and Run the cleanup thread."""
        self.cleanup_thread = Thread(target=self._cleanup_timedout_jobs)
        self.cleanup_thread.start()

    def _terminate(self):
        """Method to terminate the jobs on flask exit."""
        self._jobs = None
        with suppress(Exception):
            self.cleanup_thread.join()

    def get_job_result(self, job_id: dict) -> Optional[dict]:
        """Get the result of a job.

        Args:
            job_id: The job id to get the result from.

        Returns:
            The job result if the job is finished, else None.
        """
        job = self._jobs.get(job_id, None)
        if job is not None and job["state"] in ["finished", "failed"]:
            self.remove_job(job)

        return job

    def _create_job(self) -> dict:
        """Create a new job."""
        job = {
            "id": uuid.uuid4().hex,
            "ready": False,
            "result": None,
            "created": time.time(),
            "state": "created",
            "finished": None,
        }
        self._jobs[job["id"]] = job
        if not self.cleanup_running:
            self._run_cleanup()
            self.cleanup_running = True

        return job

    def _start_job(self, thread: Thread, job: dict):
        """Start a specific job from the thread.

        Args:
            thread: The thread to start the job from.
            job: The job to start.
        """
        job["state"] = "started"
        thread.daemon = True
        thread.start()

    def _finish_job(self, job: dict, result):
        """Terminate a specific job.

        Args:
            job: The job to terminate.
            result: The result of the job.
        """
        job["ready"] = True
        job["state"] = "finished"
        if self._is_job_alive(job):
            job["result"] = result
            job["finished"] = time.time()

    def remove_job(self, job):
        """Remove a job from the jobs dictionary.

        Args:
            job: The job to remove.
        """
        self._jobs.pop(job["id"], None)

    def _is_job_alive(self, job: Optional[dict]) -> bool:
        """Check if the job is alive.

        Args:
            job: The job to check.
        """
        exist = job is not None and job["id"] in self._jobs
        ready = job["ready"] is not None

        return exist and ready

    def _cleanup_timedout_jobs(self):
        """Cleanup timedout jobs.

        This method is run in a thread and iterates through the jobs every minute and removes the stale ones.
        """
        next_cleanup_time = time.time()
        while self._jobs is not None:
            time.sleep(5)
            now = time.time()
            if self._jobs and now >= next_cleanup_time:
                for job in self._jobs.values():
                    finished = job["state"] == "finished"
                    timeout = job["finished"] + self._TIMEOUT
                    if finished and timeout > now:
                        self.remove_job(job)
                next_cleanup_time = time.time() + self._INTERVAL
        self.cleanup_running = False


# init the class as a singleton
asyncgee = Async()
