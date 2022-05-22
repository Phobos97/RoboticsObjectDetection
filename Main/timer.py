import time


class Timer:
    def __init__(self):
        self.timestart = None
        self.timepause = None
        self.paused = None
        self.reversed = False   # whether to run the timer backwards

    def start_timer(self):
        self.timestart = time.time()

    def pause_timer(self):
        if self.timestart is None:
            raise ValueError("time not started")

        if self.paused:
            raise ValueError("time is already paused")

        self.timepause = time.time()
        self.paused = True

    def resume_timer(self, backwards=False):
        if self.timestart is None:
            raise ValueError("time not started")

        if not self.paused:
            raise ValueError("time is not paused")

        elapsed_pause = time.time() - self.timepause
        self.timestart = self.timestart + elapsed_pause
        self.paused = False

    def get_timer(self):
        if self.timestart is None:
            raise ValueError("timer not started")
        if self.paused:
            return self.timepause - self.timestart
        else:
            if self.reversed:
                return self.timestart - time.time()
            else:
                return time.time() - self.timestart

    def get_start_time(self):
        return self.timestart

    def is_paused(self):
        return self.paused
