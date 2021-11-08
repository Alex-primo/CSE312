import socketserver
import secrets
import hashlib
import base64
import pymongo
import json





class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        received_data = self.request.recv(2048).strip()
        print(self.client_address[0] + " is sending data:")
        print(received_data)
        


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8000
    
    server = socketserver.ThreadingTCPServer((HOST,PORT), MyTCPHandler)
    server.serve_forever()

