import time
from timer import Timer

timer = Timer()
timer.start_timer()
print('start', timer.get_start_time())
while timer.get_timer() < 20:
    print(timer.get_timer())

print("TIMER ENDED", timer.get_timer())