import socket

from typing import List
from scope.parameter import Parameter

class Device():
    def __init__(self, address: str, port: int = 5025, debug: bool = False, chcount: int = 4):
        self._simulated = False
        if address is None:
            self._simulated = True

        self.param : List[Parameter] = {}
        ''' The parameters of the device '''

        self.alts = {}  # Alternate parameter names
        self.valueChangeListeners = [] # Things that want to know when values change

        self._address = address
        self._port = port
        self._debug = debug
        self._sock = None
        print("Created device " + str(self._simulated))

    def dbg(self, str):
        if self._debug:
            print(str)

    def __enter__(self):
        if not self._simulated:
            self.__connect()
        return self

    def __exit__(self, exceptionType, exceptionValue, exceptionTraceback):
        if not self._simulated:
            self.__disconnect()

    def __connect(self):
        try:
            #create an AF_INET, STREAM socket (TCP)
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            raise Exception('Failed to create socket.')
        try:
            #Connect to remote server
            print("Connecting")
            self._sock.settimeout(3)
            self._sock.connect((self._address, self._port))
            self._sock.setblocking(0) # non-blocking mode, an exception occurs when no data is detected by the receiver
            #self._sock.settimeout(3)
        except socket.timeout:
            print("Timeout")
            raise TimeoutError("Could not connect to scope at " + self._address)
        except socket.error:
            print('failed to connect to ip ' + self._address)

    def __disconnect(self):
        if not self._simulated:
            self._sock.close()

    def _populateCache(self):
        print("Populating")
        if not self._simulated:
            self.getParams(self.param.keys())

    def informListeners(self, field: str, value: any, source: any = None):
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

    def getParam(self, name: str):
        _, v = self.getParams([name])[0]
        return v
    
    def getParams(self, names: List[str]):
        ret = {}
        if not self._simulated:
            qstr = ""
            for key in names:
                qstr += f"{key}?\n"
            ans = self.query(qstr)
            for line in ans.splitlines():
                k, v = self._processParam(line)
                ret[k] = v
        else:
            for key in names:
               ret[k] = self.param[v].value
        return ret
    
    def _processParam(self, line: str):
        k, v = line.split(" ")
        if k in self.alts:
            k = self.alts[k]
        print("WHATIS", k, v)
        # Set the value using the custom converter for the param
        self.param[k].setValue(v)
        v = self.param[k].value
        self.informListeners(k, v)
        return k, v
    
    def setParam(self, name: str, value: any, extSend: bool = False):
        self.param[name].setValue(value)
        if not self._simulated and not extSend:
            self.cmd(name + " " + self.param[name].getSendValue())
        self.informListeners(name, value)

    def query(self, cmd: str):
        ''' Queries the scope for something and gets a string reply. Waits for the reply to exit. Most commands here will end with a "?" '''
        dta = self.queryBytes(cmd)
        reply = dta.decode("utf-8")
        self.dbg("(" + str(len(dta)) + ") " + reply[:-1])
        return reply
    
    def queryBytes(self, cmd: str):
        ''' Queries the scope for something and gets a byte array reply. Waits for the reply to exit. Most commands here will end with a "?" '''
        try :
            #Send cmd string
            if cmd is not None:
                self.cmd(cmd)
        except socket.error:
            #Send failed
            raise ValueError('Send failed')

        self._sock.setblocking(True)
        self._sock.settimeout(1)
        # time.sleep(1)
        data_body = bytes() 
        while True:
            try:
                # time.sleep(0.01)
                server_replay = self._sock.recv(8000)
                #print(len(server_replay))
                data_body += server_replay
                self._sock.settimeout(0.1)
            except BlockingIOError:
                break
            except TimeoutError:
                break
        return data_body
    
    def cmd(self, cmd: str):
        ''' Sends a command and doesn't wait for a reply '''
        try :
            #Send cmd string
            self.dbg("Sending command " + cmd)
            self._sock.sendall(cmd.encode('ascii'))
            self._sock.sendall(b'\n') #Command termination
        except socket.error:
            #Send failed
            raise Exception('Send failed')