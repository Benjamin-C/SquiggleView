from scope.device import Device
from scope.parameter import Parameter

class Trigger():
    def __init__(self, scope: Device):
        self.__scope = scope

        self.valueChangeListeners = []

        self.__allowedModes = ["STOP", "AUTO", "NORM", "SINGLE"]

        self.__scope.param[f"TRIG_MODE"] = Parameter(default=10, retype=str)
        self.__scope.alts["TRMD"] = "TRIG_MODE"

    def getCache(self, name):
        return self.__scope.param[name].value
    
    def getMode(self):
        return self.__scope.getParam("TRIG_MODE")
    
    def setMode(self, mode: str):
        # A few alternate valid modes
        if mode in self.__allowedModes:
            self.__scope.setParam("TRIG_MODE", mode)
        else:
            raise ValueError(mode + " is not a valid trigger mode")