import time

class TimeTracker(object):
    def __init__(self):
        self._start_time = 0.0
        self._end_time = 0.0
        self._job_counter = 0
        self._time_elapsed = 0.0
    
    def start_tracker(self):
        self._start_time = time.time()

    def end_tracker(self):
        self._end_time = time.time()

    def time_elapsed(self):
        if self._end_time > self._start_time:
            self._time_elapsed += self._end_time - self._start_time

    def inc_job_counter(self, cnt):
        self._job_counter += float(cnt)

    def get_job_count(self):
        return self._job_counter

    def get_time_elapsed(self):
        return self._time_elapsed

    def average_time_cost(self):
        ret = 0
        #self.time_elapsed()
        if self._job_counter > 0:
            ret = self._time_elapsed / self._job_counter
        return ret

    def clear(self):
        self._start_time = 0.0
        self._end_time = 0.0
        self._job_counter = 0
        self._time_elapsed = 0.0

