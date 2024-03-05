from scope.device import Device

class Channel():
    def __init__(self, scope: Device):
        self.__scope = scope

        self.valueChangeListeners = []

        self.__allowedModes = ["STOP", "AUTO", "NORM", "SINGLE"]

        self.__default_param = {
            "TRIG_MODE": "AUTO"
        }
        
        self.__parammap = {"ATTN": "ATTENUATION", "CPL": "COUPLING", "OFST": "OFFSET", "VDIV": "VOLT_DIV", "UNIT": "UNIT", "BWL": "BANDWIDTH_LIMIT"}

        if not scope._simulated:
            qstr = ""
            for key in self.__parammap.keys():
                qstr += f"C{self.id}:{key}?\n"
            ans = self.__scope.query(qstr)
            for line in ans.splitlines():
                k, v = line.split(":")[1].split(" ")
                k = self.__parammap[k]
                print("WHATIS", k, v)
                if k in ["ATTENUATION"]:
                    v = float(v)
                if k in ["OFFSET", "VOLT_DIV"]:
                    v = float(v[:-1])
                elif k == "BANDWIDTH_LIMIT":
                    v = v == "ON"
                self.setCache(k, v)
                self.informValueListeners(k, v)
        else:
            for key in self.__parammap.keys():
               self.setCache(key, self.__parammap[key])

    def getCache(self, key):
        return self.__scope.cache[f"C{self.id}:{key}"]
    
    def setCache(self, key, value):
        self.__scope.cache[f"C{self.id}:{key}"] = value

    def _cmd(self, cmd: str):
        ''' Sends a command to the oscilloscope regarding this channel.
        
        Commands are prepended with the channel number, so only use this for channel specific commands in the form `C#:CMD ...`. Use _query() if you want to get the result of the command. '''
        if not self.__scope._simulated:
            self.__scope.cmd(f"C{self.id}:" + cmd)

    def _query(self, cmd: str):
        ''' Queries the oscilloscope for a value from this channel and waits for the result.
        
        Commands are prepended with the channel number, so only use this for channel specific commands in the form `C#:CMD ...`. Use _cmd() if you do not want to wait for any result. '''
        return self.__scope.query(f"C{self.id}:" + cmd)
    
    def getVal(self, field: str, source: any = "getVal", valType: str = None, valSuffix: int = 1) -> any:
        ''' Gets a value for this channel from the oscilloscope.
        
        If the scope is real, the scope is asked for the value and the reply is returned.
        If the scope is simulated the previously set value is returned
        
        Args:
            field: The name of the field to get
            source: The source of the request to be passed to listeners '''
        value = None
        if self.__scope._simulated:
            value = self.getCache(field)
        else:
            value = self._query(field + "?").split(" ")[1]
        if valType == "number":
            value = float(value[:-valSuffix])
        self.informValueListeners(field, value, source)
        return value
        
    def setVal(self, field: str, value: any, source: any = None):
        ''' Sets a value for the channel on the oscilloscope and notifies any listeners '''
        self.informValueListeners(field, value, source)
        if self.__scope._simulated:
            value = self.setCache(field, value)
        else:
            self._cmd(field + " " + str(value))

    def informValueListeners(self, field: str, value: any, source: any = None):
        ''' Informs all listeners of a change to a value
        
        This change could be either from a call to getVal or setVal.
        It is up to the listener to use source ignore any updates made by itself.
        
        Args:
            field: The field name that was updated
            value: The new value of that field
            source: What triggered the update, or None if none was specified
        '''
        if len(self.valueChangeListeners) > 0:
            for vud in self.valueChangeListeners:
                vud(field, value, source)
    
    def getAtten(self, source: any = None):
        return self.getVal("ATTENUATION")

    def setAtten(self, atten: float, source: any = None):
        if atten in self.__allowedAttens:
            self.setVal("ATTENUATION", atten, source)
        else:
            raise ValueError(str(atten) + " is not a valid attenuation")
        
    def setBWLimit(self, limit: bool = True, source: any = None):
        self.informValueListeners("BANDWIDTH_LIMIT", limit, source)
        if self.__scope._simulated:
            self.setCache("BANDWIDTH_LIMIT", limit)
        else:
            self.__scope.cmd_onoff(f"BANDWIDTH_LIMIT C{self.id},", limit)

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