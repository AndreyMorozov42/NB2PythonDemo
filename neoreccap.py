import platform
import ctypes
import _ctypes
import time

# C error numbers
NR_ERR_OK = 0             # Success (no errors)
NR_ERR_ID = -1            # Invalid id
NR_ERR_FAIL = -2          # Operation failed
NR_ERR_PARAM = -3         # Incorrect argument

# NeoRecCap base sample rate enum
NR_RATE_125HZ = 0
NR_RATE_250HZ = 1
NR_RATE_500HZ = 2
NR_RATE_1000HZ = 3

# adc input rage in mV enum
NR_RANGE_mV150 = 0
NR_RANGE_mV300 = 1

# program working mode enum
NR_MODE_DATA = 0
NR_MODE_IMPEDANCE = 1
NR_MODE_TEST = 2

class NRDataSettings(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('DataRate', ctypes.c_uint8),
        ('InputRange', ctypes.c_uint8),
        ('EnabledChannels', ctypes.c_uint16)
    ]

class NREventSettings(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('EnabledEvents', ctypes.c_uint16),
        ('ActivityThreshold', ctypes.c_uint16)
    ]

class NRSetMode(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("Mode", ctypes.c_uint8)
    ]


class NeoRecCap(object):
    def __init__(self):
        # get OS architecture (64/86-bit)
        self.x64 = ("64" in platform.architecture()[0])

        # load library
        self.lib = None
        self._load_lib()
        # flag data acquisition
        self.running = False

        self.id = 0

    def _load_lib(self):
        try:
            if self.lib != None:
                _ctypes.FreeLibrary(self.lib._handle)
            # load/reload library
            if self.x64:
                self.lib = ctypes.windll.LoadLibrary("bin/x64/Release/nb2mcs.dll")
            else:
                self.lib = ctypes.windll.LoadLibrary("bin/x86/Release/nb2mcs.dll")
        except:
            self.lib = None
            if self.x64:
                print("failed to open library (x64/nb2mcs.dll)")
            else:
                print("failed to open library (x86/nb2mcs.dll)")

        # initialization library resources
        res = self.lib.nb2ApiInit()
        if res != NR_ERR_OK:
            print("can't initialize library resources")

    def search_device(self):
        """
        Search device and recieve count device
        """
        # start device search device
        count = 0
        while count == 0:
            # returns the number of devices
            count = self.lib.nb2GetCount()

    def open(self):
        """
        Open the hardware device and get a id device and device properties
        """
        if self.lib == None:
            print("library mcsdevices.dll not available")

        # get device id
        self.id = self.lib.nb2GetId(0)

        # open device
        res = self.lib.nb2Open(self.id)
        if res != NR_ERR_OK:
            print("failed to open device")

    def setup(self, data_rate=NR_RATE_250HZ, enb_channels=0xFFFF, input_range=NR_RANGE_mV150,
              activity_thr=1, enb_event=0x003F,
              mode=NR_MODE_DATA):
        """
        Setup device
        """
        data_settings = NRDataSettings()
        data_settings.DataRate = 0
        data_settings.InputRange = 0
        data_settings.EnabledChannels = 0

        event_settings = NREventSettings()
        event_settings.EnabledEvents = 0
        event_settings.ActivityThreshold = 0

        mode_settings = NRSetMode()
        mode_settings.Mode = 0

        err = self.lib.nb2SetDataSettings(self.id, ctypes.byref(data_settings))
        if err != NR_ERR_OK:
            print("failed to set data settings")

        err = self.lib.nb2SetEventSettings(self.id, ctypes.byref(event_settings))
        if err != NR_ERR_OK:
            print("failed to set event settings")

        err = self.lib.nb2SetMode(self.id, ctypes.byref(mode_settings))
        if err != NR_ERR_OK:
            print("failed to set mode")

    def stop(self):
        """
        Stop data acquisition
        """
        if not self.running:
            return
        self.running = False
        if self.id == None:
            print("device not open")
        err = self.lib.nb2Stop(self.id)
        if err != NR_ERR_OK:
            print("failed to stop device")

    def close(self):
        """
            Close hardware device
        """
        if self.lib == None:
            print("library nb2mcs.dll not available")

        if self.id != None:
            # check if data acquisition
            if self.running:
                try:
                    self.stop()
                except:
                    pass
            res = self.lib.nb2Close(self.id)
            if res != NR_ERR_OK:
                print("Can't close device")
            else:
                self.id = None
        pass

    def read(self):
        buffer = ctypes.create_string_buffer(10000 * 1024)

        # read data from device
        bytesread = self.lib.nb2GetData(self.id, ctypes.byref(buffer, 0), len(buffer))

        return bytesread