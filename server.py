import socketserver
import secrets
import hashlib
import base64
import pymongo
import json

global __chatSockets__
global __colorSockets__
__chatSockets__ = []
__colorSockets__ = []

class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        global __chatSockets__
        global __colorSockets__
        received_data = self.request.recv(2048)

        if len(received_data) > 0:
            print(self.client_address[0] + " is sending data:")
            print(received_data)

            headersDict = makeHeaderDict(received_data)
            #print(headersDict)

            if headersDict['PATH'] == "/":
                with open("LoginRegister.html", "rb") as file:
                    b = file.read()
                        
                respond = "HTTP/1.1 200 OK\r\n"
                respond += "Content-Type: text/html; charset=utf-8\r\n"
                respond += "X-Content-Type-Options: nosniff\r\n"
                respond += "ContentLength: " + str(len(b)) + "\r\n"
                respond += "\r\n"
                    
                self.request.sendall(respond.encode() + b)

            elif headersDict['PATH'] == "/LogReg.js" or headersDict['PATH'] == "/homeJs.js":
                with open(headersDict['PATH'][1:], "rb") as file:
                    b = file.read()
                
                respond = "HTTP/1.1 200 OK\r\n"
                respond += "Content-Type: text/javascript; charset=utf-8\r\n"
                respond += "X-Content-Type-Options: nosniff\r\n"
                respond += "ContentLength: " + str(len(b)) + "\r\n"
                respond += "\r\n"
                self.request.sendall(respond.encode() + b)

            elif headersDict['PATH'] == "/style.css":
                with open("style.css", "rb") as file:
                    b = file.read()
                
                respond = "HTTP/1.1 200 OK\r\n"
                respond += "Content-Type: text/css; charset=utf-8\r\n"
                respond += "X-Content-Type-Options: nosniff\r\n"
                respond += "ContentLength: " + str(len(b)) + "\r\n"
                respond += "\r\n"
                self.request.sendall(respond.encode() + b)

            elif headersDict['PATH'] == "/favicon.ico":
                respond = "HTTP/1.1 200 OK\r\n"
                respond += "Content-Type: text/html\r\n"
                respond += "X-Content-Type-Options: nosniff\r\n"
                respond += "ContentLength: 11\r\n"
                respond += "\r\n"
                respond += "hello world"
                self.request.sendall(respond.encode())

            elif headersDict['PATH'] == "/home":
                with open("home.html", "rb") as file:
                    b = file.read()
                        
                respond = "HTTP/1.1 200 OK\r\n"
                respond += "Content-Type: text/html; charset=utf-8\r\n"
                respond += "X-Content-Type-Options: nosniff\r\n"
                respond += "ContentLength: " + str(len(b)) + "\r\n"
                respond += "\r\n"
                    
                self.request.sendall(respond.encode() + b)

            elif headersDict['PATH'] == "/chatsocket" or headersDict['PATH'] == "/colorsocket":
                GUID  = headersDict["Sec-WebSocket-Key"] + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
                acceptKey = hashlib.sha1(GUID.encode()).digest()
                acceptKey = base64.b64encode(acceptKey)
                acceptKey += b'\r\n\r\n'

                response = "HTTP/1.1 101 Switching Protocols\r\n"
                response += "Upgrade: websocket\r\n"
                response += "Connection: Upgrade\r\n"
                response += "Sec-WebSocket-Accept: "
                response = response.encode()
                response += acceptKey
                self.request.sendall(response)
                if(headersDict['PATH']) == "/chatsocket":   #chat is the chat and color will be color array
                    __chatSockets__.append(self)
                elif(headersDict['PATH']) == "/colorsocket":
                    __colorSockets__.append(self)
                while True:
                    received_data = self.request.recv(2048)
                    print("recieved socket data")
                    webSocketData(self,received_data,headersDict['PATH'])

            elif headersDict['REQUEST'] == 'POST':
                if headersDict['PATH'] == '/image-upload':
                    temp = parseImage(headersDict,self)     #REMOVE THIS COMMENT temp here is the image bits, so like store it with the person in the database
        

def parseImage(headerDict, TCP):

    if int(headerDict['Content-Length']) > 2048:
            notDone = True
            while notDone:
                temp = TCP.request.recv(2048)
                headerDict['DATA'] += temp
                if len(temp) < 2048:
                    notDone = False

    boundaryKey = "--"+headerDict['Content-Type'][headerDict['Content-Type'].index("boundary=")+9:]
    lastboundaryKey = ('\r\n'+boundaryKey+"--\r\n").encode()
    boundaryKey = (boundaryKey + "\r\n").encode()
    dataSplit = headerDict['DATA'].split('\r\n\r\n'.encode())
    
    dataSplit[0] = dataSplit[0].decode()
    contentType = dataSplit[0][dataSplit[0].index('Content-Type: ')+14:]

    if contentType == 'image/jpeg' or contentType == 'image/png':
        return dataSplit[1][:dataSplit[1].index(lastboundaryKey)]
    return None


#handle when a socket sends data, and push that data to all other sockets
def webSocketData(tcp,data,socketType):
    global __chatSockets__
    global __colorSockets__
    if (data[0] & 15) == 8:   #closed connection
        if(socketType) == "/chatsocket":
                __chatSockets__.remove(tcp)
        elif(socketType) == "/colorsocket":
                __colorSockets__.remove(tcp)
        return None

    frameBytes = 0  
    frameLength = data[1]&127
    finalFrameLength = frameLength
    if frameLength == 126:
        frameBytes = 2
        finalFrameLength = (data[2]<<8)|data[3]
    if frameLength == 127:  
        frameBytes = 8
        finalFrameLength = data[2]
        counter = 3
        while counter != 9:
            finalFrameLength = (finalFrameLength<<8)|data[counter]
            counter += 1

    maskStart = frameBytes + 2  
    maskList = [data[maskStart],data[maskStart+1],data[maskStart+2],data[maskStart+3]]
    maskCount = 1
    payload = maskList[0] ^ data[frameBytes+6]
    for i in data[frameBytes+7:]:
        payload = (payload<<8) | (maskList[maskCount] ^ i)
        maskCount += 1
        maskCount = maskCount % 4
    payload = payload.to_bytes(len(data)-(frameBytes+6),'big')
    payload = payload.decode()
    payload = payload.replace('&',"&amp;")
    payload = payload.replace('<',"&lt;")
    payload = payload.replace('>',"&gt;")
    
    offset = 0
    response = 129
    payloadLength = len(payload)
    if payloadLength >= 126:
        if payloadLength < 65536:
            offset = 2
            response = response<<8 | 126
            response = response.to_bytes(2,'big')
            temp = payloadLength.to_bytes(2,'big')
            response = b"".join([response,temp])
        if payloadLength >= 65536:  
            offset = 8
            response = response<<8 | 127
            response = response.to_bytes(2,'big')
            temp = payloadLength.to_bytes(8,'big')
            response = b"".join([response,temp])
    else:
        response = response<<8 | payloadLength
        response = response.to_bytes(offset+2,'big')
    
    response = b"".join([response,payload.encode()])
    if(socketType) == "/chatsocket":
            for i in __chatSockets__:
                i.request.sendall(response)
    elif(socketType) == "/colorsocket":
            for i in __colorSockets__:
                i.request.sendall(response)


#convert the headers as BYTES into a dictionary
#request == 'REQUEST'
#path == 'PATH'
#data == 'DATA'
def makeHeaderDict(data):
    headerList = (data[:data.index("\r\n\r\n".encode())].decode()).split("\r\n")
    finalDict = {}
    firstLine = ''
    for i in headerList:
        if ":" in i:
            parts = i.split(": ")
            finalDict[parts[0]] = parts[1]
        else:
            firstLine = i

    request = firstLine[:firstLine.index(' ')]
    path = firstLine[firstLine.index(request+' ')+len(request)+1 : firstLine.index(' HTTP')]
    finalDict['REQUEST'] = request
    finalDict['PATH']  = path
    finalDict['DATA'] = data[data.index("\r\n\r\n".encode())+4:]
    return finalDict


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8000
    
    server = socketserver.ThreadingTCPServer((HOST,PORT), MyTCPHandler)
    server.serve_forever()