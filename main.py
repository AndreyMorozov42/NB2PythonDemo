import time

from neoreccap import *


def main():
    dev = NeoRecCap()
    dev.search_device()
    dev.open()
    dev.setup()
    for i in range(5):
        print("id", dev.id)
        print("bytesread", dev.read())
        time.sleep(1)
    dev.stop()
    dev.close()


if __name__ == "__main__":
    main()
