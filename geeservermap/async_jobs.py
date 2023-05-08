from threading import Thread
import atexit
import uuid
import time
from copy import deepcopy


class Async:
    _INTERVAL = 60
    _TIMEOUT = 300

    def __init__(self):
        self._jobs = {}
        self.cleanup_running = False
        atexit.register(self._terminate)

    def _run_cleanup(self):
        self.cleanup_thread = Thread(target=self._cleanup_timedout_jobs)
        self.cleanup_thread.start()

    # This MUST be called when flask wants to exit otherwise the process will hang for a while
    def _terminate(self):
        self._jobs = None
        try:
            self.cleanup_thread.join()
        except:
            pass

    def get_job_result(self, job_id):
        if not self._jobs:
            return None
        job = self._jobs.get(job_id)
        if job['state'] in ['finished', 'failed']:
            self.remove_job(job)
        return job

    def _create_job(self):
        job = { 'id': uuid.uuid4().hex, 'ready': False,
                'result': None, 'created':  time.time(),
                'state': 'created', 'finished': None
                }
        self._jobs[job['id']] = job
        if not self.cleanup_running:
            self._run_cleanup()
            self.cleanup_running = True
        return job

    def _start_job(self, thread, job):
        job['state'] = 'started'
        thread.daemon = True
        thread.start()

    def _finish_job(self, job, result):
        job['ready'] = True
        job['state'] = 'finished'
        if self._is_job_alive(job):
            job['result'] = result
            job['finished'] = time.time()

    def remove_job(self, job):
        if self._jobs and job['id'] in self._jobs:
            # logger.info(f'removing job {job["id"]}')
            del self._jobs[job['id']]

    def _is_job_alive(self, job):
        return self._jobs and job != None and job['id'] in self._jobs and job['ready'] != None

    # Iterate though jobs every minute and remove the stale ones
    def _cleanup_timedout_jobs(self):
        next_cleanup_time = time.time()
        while self._jobs != None:
            time.sleep(5)
            now = time.time()
            proxy = deepcopy(self._jobs)
            if proxy and now >= next_cleanup_time:
                for job in proxy.values():
                    if job['state'] == 'finished' and (job['finished'] + self._TIMEOUT > now):
                        self.remove_job(job)
                next_cleanup_time = time.time() + self._INTERVAL
        self.cleanup_running = False


asyncgee = Async()
