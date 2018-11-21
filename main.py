from reader import *


if __name__ == '__main__':
    frameQueue = Queue()
    reader = Reader(frameQueue)
    proc = Processer(frameQueue)
    reader.setDaemon(True)
    # proc.setDaemon(True)

    reader.start()
    proc.start()