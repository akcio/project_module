from reader import *


if __name__ == '__main__old':
    frameQueue = Queue()
    reader = Reader(frameQueue)
    proc = Processer(frameQueue)
    reader.setDaemon(True)
    # proc.setDaemon(True)

    reader.start()
    proc.start()


if __name__ == '__main__':
    frameQueue = Queue()
    out = dict()
    reader = Reader(frameQueue)
    worker = SkyWorker(frameQueue, out)
    proc = NewProcesser(frameQueue, out)
    reader.setDaemon(True)
    worker.setDaemon(True)

    reader.start()
    worker.start()
    proc.start()