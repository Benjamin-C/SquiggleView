import socket

class Device():
    def __init__(self, address: str, port: int = 5025, debug: bool = False, chcount: int = 4):
        self._simulated = False
        if address is None:
            self._simulated = True
        self.cache = {}
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
            self._sock.connect((self._address, self._port))
            self._sock.setblocking(0) # non-blocking mode, an exception occurs when no data is detected by the receiver
            #self._sock.settimeout(3) 
        except socket.error:
            print ('failed to connect to ip ' + self._address)

    def __disconnect(self):
        if not self._simulated:
            self._sock.close()

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