import time

from neoreccap import *


def main():
    # create an instance of the class
    dev = NeoRecCap()
    # search device and set device id
    dev.search_device()
    # open device
    dev.open()
    # setup device
    dev.setup()
    # start device
    dev.start()
    # take data from the device 10 times
    for i in range(10):
        time.sleep(0.01)
        d, data = dev.read()
    # stop device
    dev.stop()
    # close device
    dev.close()


if __name__ == "__main__":
    main()
