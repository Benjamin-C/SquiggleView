from scope.device import Device

from scope.parameter import Parameter

class Channel():
    def __init__(self, scope: Device, id: int):
        self.id = id    
        self.__scope = scope

        self.valueChangeListeners = []

        self.__allowedAttens = {0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000}
        self.__allowedCouple = {"A1M", "D1M", "GND"}
        self.__allowedUnits = {"A", "V"}

        self.__scope.alts[f"C{id}:ATTN"] = f"C{id}:ATTENUATION"
        self.__scope.alts[f"C{id}:CPL"]  = f"C{id}:COUPLING"
        self.__scope.alts[f"C{id}:OFST"] = f"C{id}:OFFSET"
        self.__scope.alts[f"C{id}:VDIV"] = f"C{id}:VOLT_DIV"
        self.__scope.alts[f"C{id}:BWL"]  = f"C{id}:BANDWIDTH_LIMIT"

        self.__scope.param[f"C{id}:ATTENUATION"]     = Parameter(default=10,    retype=float, sender=lambda s: f"{s:g}")
        self.__scope.param[f"C{id}:COUPLING"]        = Parameter(default="D1M", retype=str)
        self.__scope.param[f"C{id}:OFFSET"]          = Parameter(default=0,     retype=lambda s: float(s[:-1]))
        self.__scope.param[f"C{id}:VOLT_DIV"]        = Parameter(default=1.0,   retype=lambda s: float(s[:-1]))
        self.__scope.param[f"C{id}:UNIT"]            = Parameter(default="V",   retype=str)
        self.__scope.param[f"C{id}:BANDWIDTH_LIMIT"] = Parameter(default=False, retype=lambda s: s == True or s == "ON", sender=lambda s: "ON" if bool(s) else "OFF")
    
    def getCache(self, name: str):
        return self.__scope.param[f"C{self.id}:{name}"].value

    def getVal(self, name: str, source: any = "getVal") -> any:
        ''' Gets a value for this channel from the oscilloscope. '''
        k,v = self.__scope.getParam("C{self.id}:{name}")
        return v
        
    def setVal(self, field: str, value: any, source: any = None):
        ''' Sets a value for the channel on the oscilloscope and notifies any listeners '''
        self.__scope.setParam(f"C{self.id}:{field}", value)
    
    def getAtten(self, source: any = None):
        return self.getVal("ATTENUATION")

    def setAtten(self, atten: float, source: any = None):
        if atten in self.__allowedAttens:
            self.setVal("ATTENUATION", atten, source)
        else:
            raise ValueError(str(atten) + " is not a valid attenuation")
        
    def setBWLimit(self, limit: bool = True, source: any = None):
        paramName = f"C{self.id}:BANDWIDTH_LIMIT"
        self.__scope.setParam(paramName, limit, extSend=True)
        if not self.__scope._simulated:
            self.__scope.cmd(f"BANDWIDTH_LIMIT C{self.id},{self.__scope.param[paramName].getSendValue()}")

    def getBWLimit(self):
        if self.__scope._simulated:
            return self.getCache("BANDWIDTH_LIMIT")
        return self.__scope.query_onoff(f"C{self.id}:BANDWIDTH_LIMIT?")
    
    def getCoupling(self):
        return self.getVal("COUPLING")
    
    def cacheCouplingHR(self):
        return self.getCache("COUPLING").replace("A1M", "AC").replace("D1M", "DC")
    
    def setCoupling(self, mode: str, source: any = None):
        # A few alternate valid modes
        mode = mode.upper().replace("AC", "A1M").replace("DC", "D1M")
        if mode in self.__allowedCouple:
            self.setVal("COUPLING", mode, source)
        else:
            raise ValueError(mode + " is not a valid coupling")
    
    def setOffset(self, offset: float, source: any = None):
        self.setVal("OFFSET", offset, source)

    def getOffset(self):
        return self.getVal("OFFSET")
    
    def setScale(self, vdiv, source: any = None):
        self.setVal("VOLT_DIV", vdiv, source)

    def getScale(self):
        return self.getVal("VOLT_DIV")

    def setUnit(self, unit: str, source: any = None):
        unit = unit[0].upper()
        if unit in self.__allowedUnits:
            self.setVal("UNIT", unit, source)
        else:
            raise ValueError(unit + " is not a valid unit")

    def getUnit(self):
        return self.getVal("UNIT")
    
    def __str__(self):
        return f"CH{self.id} {self.atten}X "