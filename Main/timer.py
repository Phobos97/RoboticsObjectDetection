import time


class Timer:
    def __init__(self):
        self.timestart = None
        self.timepause = None
        self.paused = None

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

        if self.reversed:
            elapsed_pause = self.timepause - time.time()
        else:
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


if __name__ == "__main__":
    timer = Timer()
    # print(timer.get_timer())

    timer.start_timer()
    print(f'{timer.timestart = }')
    time.sleep(1)
    timer.pause_timer()

    print(timer.get_timer())
    timer.reversed = True
    # time.sleep(1)
    timer.resume_timer()
    print(f'{timer.timestart = }')
    print(timer.get_timer())
    time.sleep(1)
    print(timer.get_timer())