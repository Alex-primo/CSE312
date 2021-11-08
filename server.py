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

        with open("login.html", "rb") as file:
            b = file.read()
            print("HIIIIIIIIIIIIIIIII")
            print(b)
                
            respond = "HTTP/1.1 200 OK\r\n"
            respond += "Content-Type: text/html; charset=utf-8\r\n"
            respond += "X-Content-Type-Options: nosniff\r\n"
            respond += "ContentLength: " + str(len(b)) + "\r\n"
            respond += "\r\n"
            print("I'm Sending Unwanted data", respond)
            self.request.sendall(respond.encode() + b)
        


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8000
    
    server = socketserver.ThreadingTCPServer((HOST,PORT), MyTCPHandler)
    server.serve_forever()

