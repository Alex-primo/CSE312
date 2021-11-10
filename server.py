import socketserver
import secrets
import hashlib
import base64
import pymongo
import json



class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        received_data = self.request.recv(2048)

        if len(received_data) > 0:
            print(self.client_address[0] + " is sending data:")
            print(received_data)

            headersDict = makeHeaderDict(received_data)
            print(headersDict)

            with open("login.html", "rb") as file:
                b = file.read()
                    
                respond = "HTTP/1.1 200 OK\r\n"
                respond += "Content-Type: text/html; charset=utf-8\r\n"
                respond += "X-Content-Type-Options: nosniff\r\n"
                respond += "ContentLength: " + str(len(b)) + "\r\n"
                respond += "\r\n"
                
                self.request.sendall(respond.encode() + b)


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
    finalDict['DATA'] = data[data.index("\r\n\r\n".encode())+4:].decode()
    return finalDict


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8000
    
    server = socketserver.ThreadingTCPServer((HOST,PORT), MyTCPHandler)
    server.serve_forever()

