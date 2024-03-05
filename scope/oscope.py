import time
from PIL import Image
from io import BytesIO
from scope.device import Device
from scope.channel import Channel
from scope.parameter import Parameter

class Oscilloscope(Device):
    def __init__(self, address: str | None, debug: bool = False, chcount: int = 4):
        super().__init__(address, 5025, debug)
        self.__simchcount = chcount
        self.channel = []

        self.__scope.param[f"MENU"] = Parameter(default=True, retype=lambda s: s == True or s == "ON", sender=lambda s: "ON" if bool(s) else "OFF")

    def __dbg(self, str):
        if self._debug:
            print(str)

    def __enter__(self):
        print("enter")
        if not self._simulated:
            print("calling super")
            super().__enter__()
            print("Calling connect")
            self.__connect()
        else:
            self.__connect_sim()
        super()._populateCache()
        return self

    def __exit__(self, exceptionType, exceptionValue, exceptionTraceback):
        super().__exit__(exceptionType, exceptionValue, exceptionTraceback)

    def __connect_sim(self):
        self.brand = "Simulated"
        self.model = "Simulated"
        for i in range(self.__simchcount):
            self.channel.append(Channel(self, i+1))

    def __connect(self):
        print("Connecting")
        # Confirm that we are on an SDS2104
        ans = self.query("*idn?")
        try:
            ans = ans.split(",")
            self.brand = ans[0]
            self.model = ans[1]
        except Exception as e:
            print(ans)
            raise e

        if(self.brand != "Siglent Technologies" or self.model != "SDS1204X-E"):
            raise ValueError("Scope model " + self.brand + " " + self.model + " is not supported")
        print("Connected to " + self.brand + " " + self.model)
        # Get scope capabilities
        ans = self.query("CHS?").split(" ")
        self.channel = []
        print(ans)
        for i in range(int(ans[1])):
            self.channel.append(Channel(self, i+1))

    def screenshot(self, hidemenu: bool = False, retry = 1) -> Image:
        if self._simulated:
            return Image.open("test.png")
        else:
            try:
                if hidemenu:
                    self.setMenu(False)
                    time.sleep(0.1)
                bfs = 0
                buff = BytesIO()
                self.cmd("SCDP")
                while bfs < 768067:
                    temp = self.queryBytes(None)
                    bfs += len(temp)
                    buff.write(temp)
                ret = Image.open(buff)
                ret.load()
                return ret
            except OSError as e:
                if retry > 0:
                    self.dbg("Screenshot failed, trying again")
                    time.sleep(0.1)
                    return self.screenshot(hidemenu, retry-1)
                else:
                    raise e
    
    def setupFFTHoriz(self, min : float | None = None, max : float | None = None, center : float | None = None, span : float | None = None):
        ''' Sets the range of the FFT. Uses min and max freqs if they are supplied.'''
        if min is not None and max is not None:
            if max <= min:
                raise ValueError("max must be larger than min")
            # Set up by min/max
            center = (min + max) / 2
            span = (max - min)

        if center is not None and span is not None:
            # Set up by center span
            # Divide by 10 since the FFT is 10 divisions wide
            self.cmd(f"FFT_TDIV {span/10:g}")
            self.cmd(f"FFT_CENTER {center:g}")
        else:
            raise ValueError("You must specify either min and max frequencies, or center and span")

    # Channels
    def ch(self, ch: int) -> Channel:
        if 0 < ch <= len(self.channel):
            return self.channel[ch-1]
        else:
            raise ValueError("Invalid channel " + str(ch))
        
    def channelCount(self):
        return len(self.channel)
    
    def getMenu(self):
        return self.getParam("MENU")

    def setMenu(self, on: bool = False):
        self.setParam("MENU", on)
