import time

class Timer:

    def __init__(self):
        self.start_time = 0
        self.isActive = False

    def start(self):
        self.start_time = time.time()
        self.isActive = True

    
    def stop(self):
        if self.isActive:
            self.isActive = False
            return time.time() - self.start_time
        return 0