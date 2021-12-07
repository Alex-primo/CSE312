import socketserver
import secrets
import hashlib
import base64
import pymongo
import json
import bcrypt


global __chatSockets__
global __colorSockets__
__chatSockets__ = []
__colorSockets__ = []

UsersLoggedIn = []


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        received_data = self.request.recv(2048)
        if len(received_data) > 2048:
            received_data += self.request.recv(2048)

        if len(received_data) > 0:
            print(self.client_address[0] + " is sending data:")
            print(received_data)

            headersDict = makeHeaderDict(received_data)
            print(headersDict)

            if headersDict['PATH'] == "/":
                with open("LoginRegister.html", "r") as file:
                    b = file.read()
                    c = "{{reg success}}"
                    regMessage = ""
                    b = b.replace(c, regMessage)
                    l = "{{login mess}}"
                    b = b.replace(l, "")
                        
                respond = "HTTP/1.1 200 OK\r\n"
                respond += "Content-Type: text/html; charset=utf-8\r\n"
                respond += "X-Content-Type-Options: nosniff\r\n"
                respond += "ContentLength: " + str(len(b)) + "\r\n"
                respond += "\r\n"
                self.request.sendall(respond.encode() + b.encode())
                    
                self.request.sendall(respond.encode() + b)

            if headersDict['PATH'] == "/chat":
                with open("chat.html", "r") as file:
                    b = file.read()
                        
                respond = "HTTP/1.1 200 OK\r\n"
                respond += "Content-Type: text/html; charset=utf-8\r\n"
                respond += "X-Content-Type-Options: nosniff\r\n"
                respond += "ContentLength: " + str(len(b)) + "\r\n"
                respond += "\r\n"
                self.request.sendall(respond.encode() + b.encode())
                    
                self.request.sendall(respond.encode() + b)

            elif headersDict['PATH'] == '/image-upload':
                if headersDict['REQUEST'] == 'POST':
                    print("Profile Image", headersDict['PATH'])
                    temp = parseImage(headersDict,self)     #REMOVE THIS COMMENT temp here is the image bits, so like store it with the person in the database
                    # print("Here",temp)

                    data = received_data.decode()
                    username = findToken(data)
                    f = "image/" + username
                    with open(f, "wb") as file:
                        file.write(temp)

                    pic = ""
                    pic += "<img src=" + "imup/" + str(username) + ">" + "<br>"

                    with open("profile.html", "r") as file:
                        b = file.read()
                        c = "{{up load image}}"
                        b = b.replace(c, pic)
                        respond = "HTTP/1.1 200 OK\r\n"
                        respond += "Content-Type: text/html; charset=utf-8\r\n"
                        respond += "X-Content-Type-Options: nosniff\r\n"
                        respond += "ContentLength: " + str(len(b)) + "\r\n"
                        respond += "\r\n"
                        print(b)
                        self.request.sendall(respond.encode() + b.encode())
  

            elif headersDict['PATH'] == "/LogReg.js" or headersDict['PATH'] == "/chat.js":
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

            elif headersDict['PATH'] == "/profile":
                with open("profile.html", "r") as file:
                    b = file.read()
                    c = "{{name and comment}}"
                    regMessage = ""
                    b = b.replace(c, regMessage)
                    l = "{{up load image}}"
                    b = b.replace(l, "")
                    
                    respond = "HTTP/1.1 200 OK\r\n"
                    respond += "Content-Type: text/html; charset=utf-8\r\n"
                    respond += "X-Content-Type-Options: nosniff\r\n"
                    respond += "ContentLength: " + str(len(b)) + "\r\n"
                    respond += "\r\n"
                    self.request.sendall(respond.encode() + b.encode()) 

            elif headersDict['PATH'] == "/registerForm":
                data = received_data.decode()
                word2 = ""
                f = 0
                for i in data:
                    if f == 0:
                        if word2 != "boundary=":
                            if i != " ":
                                if i != "\r":
                                    if i != "\n":
                                        word2 += i
                            else:
                                word2 = ""
                                
                        else: 
                            print(word2)
                            f += 1
                            word2 = "--"
                    if f == 1:
                        if i != "\r":
                            if i != "\n":
                                word2 += i
                        else:
                            print(word2)
                            break
                d = data.split(word2)
                print ("This is data split", d)

                username = d[1].split("\r\n\r\n")
                username = username[1].split("\r\n")
                username = username[0]
                username = noHTML(username)
                password = d[2].split("\r\n\r\n")
                password = password[1].split("\r\n")
                password = password[0]
                print("UandP", username, password)

                passCheck = validatePassword(password)
                print("passCheck", passCheck)
                if passCheck == False:
                    with open("LoginRegister.html", "r") as file:
                        b = file.read()
                        c = "{{reg success}}"
                        regMessage = "<h4>" + " password does not meet criteria" + "<br></br>Password requirements must include: <br></br>A minimum length of 8<br></br>At least 1 lowercase character<br></br>At least 1 uppercase character<br></br>At least 1 number<br></br>At least 1 special character<br></br>Any additional criteria of your choosing<br></br></h4>"
                        b = b.replace(c, regMessage)
                        l = "{{login mess}}"
                        b = b.replace(l, "")

                    respond = "HTTP/1.1 200 OK\r\n"
                    respond += "Content-Type: text/html; charset=utf-8\r\n"
                    respond += "X-Content-Type-Options: nosniff\r\n"
                    respond += "ContentLength: " + str(len(b)) + "\r\n"
                    respond += "\r\n"
                    self.request.sendall(respond.encode() + b.encode())

                if passCheck == True:
                    print("inside true")

                    hashedPassword(username,password)

                    #2^80 bits of entropy is a password with length 13


                    with open("LoginRegister.html", "r") as file:
                        b = file.read()
                        c = "{{reg success}}"
                        regMessage = "<h4>" + username + " has sucessfully registered" + "</h4>"
                        b = b.replace(c, regMessage)
                        l = "{{login mess}}"
                        b = b.replace(l, "")
                    
                    respond = "HTTP/1.1 200 OK\r\n"
                    respond += "Content-Type: text/html; charset=utf-8\r\n"
                    respond += "X-Content-Type-Options: nosniff\r\n"
                    respond += "ContentLength: " + str(len(b)) + "\r\n"
                    respond += "\r\n"
                    self.request.sendall(respond.encode() + b.encode()) 
            elif headersDict['PATH'] == "/home":
                data = received_data.decode()
                with open("home.html", "r") as file:
                    b = file.read()
                    print(b)
                    l = "{users logged in}"
                    r = "<h3>List of logged in users</h3><br>"
                    for i in UsersLoggedIn:
                        r = r + "<img src=" + "imup/" + str(i) + ">" + "<br>" # this gets there profile picture if they have one saved  # image/[username] is where the image is stored
                        r = r + "<h5>" + i + " is currently logged in </h5>"
                        r = r + "<form action=" + "/dm" + " " + "id=" + "dm-form" + " " +  "method=" + "post" + " " +  "enctype=" + "multipart/form-data" + "><label for=" + "text-form-name" + ">Your Username: </label><input id=" + "text-form-message" + " " +  "type=" + "text" + " " +  "name=" + "DM2" + "><br/><label for=" + "form-message" + ">Message: </label><input id="+ "form-message" + " " +  "type=" +"text" + " " +  "name="+ i + "><input type=" + "submit" + " " +  "value=" + "Submit" + "></form><br>"
                                                                                                                                                                                                                #this could be a hidden feild or just use there token. The username of the current user/sender of the DM                                                                                                                                                             # i is the username of the person you are sending the DM to
                    b = b.replace(l, r)
                    tokenFound = findToken(data)  # send it data and it will return the current users USERNAME from the token
                    if tokenFound != None:
                        l2 = "{{login mess}}"
                        r2 = "<h1>" + str(tokenFound) + " is signed in </h1>"
                        b = b.replace(l2, r2)
                        c = "{{token found}}"
                        r = "<h1>Welcome back " + str(tokenFound) + "!</h1>"
                        b = b.replace(c, r)   
                    else:
                        c = "{{token found}}"
                        r = ""
                        l2 = "{{login mess}}"
                        b = b.replace(c, r)
                        b = b.replace(l2, r)
                
                respond = "HTTP/1.1 200 OK\r\n"
                respond += "Content-Type: text/html; charset=utf-8\r\n"
                respond += "X-Content-Type-Options: nosniff\r\n"
                respond += "ContentLength: " + str(len(b)) + "\r\n"
                respond += "\r\n"
                print("/home",respond)
                self.request.sendall(respond.encode() + b.encode())

            elif headersDict['PATH'] == "/loginForm":
                data = received_data.decode()
                word2 = ""
                f = 0
                for i in data:
                    if f == 0:
                        if word2 != "boundary=":
                            if i != " ":
                                if i != "\r":
                                    if i != "\n":
                                        word2 += i
                            else:
                                word2 = ""
                                
                        else: 
                            print(word2)
                            f += 1
                            word2 = "--"
                    if f == 1:
                        if i != "\r":
                            if i != "\n":
                                word2 += i
                        else:
                            print(word2)
                            break
                d = data.split(word2)
                print ("This is data split", d)

                username = d[1].split("\r\n\r\n")
                username = username[1].split("\r\n")
                username = username[0]
                password = d[2].split("\r\n\r\n")
                password = password[1].split("\r\n")
                password = password[0]
                print("LoginAuth", username, password)

                # check if the username exists
                userReal = userLookUp(username)
                print("BOOLIN", userReal)
                # if False user does not exsist
                if userReal == False:
                    with open("LoginRegister.html", "r") as file:
                        b = file.read()
                        c = "{{reg success}}"
                        b = b.replace(c, "")
                        l = "{{login mess}}"
                        b = b.replace(l, "<h1>Login failed</h1>")
                        print("HIIIIIIIIIIIIIIIII")
                        print(b)
                        tokenFound = findToken(data)  # send it data and it will return the current users USERNAME from the token
                        if tokenFound != None:
                            c = "{{token found}}"
                            r = "<h1>Welcome back " + str(tokenFound) + "!</h1>"
                            b = b.replace(c, r)
                        else:
                            c = "{{token found}}"
                            r = ""
                            b = b.replace(c, r)
                    
                        respond = "HTTP/1.1 200 OK\r\n"
                        respond += "Content-Type: text/html; charset=utf-8\r\n"
                        respond += "X-Content-Type-Options: nosniff\r\n"
                        respond += "ContentLength: " + str(len(b)) + "\r\n"
                        respond += "\r\n"
                        print("I'm Sending Unwanted data", respond)
                        self.request.sendall(respond.encode() + b.encode())
                # check the password
                if userReal == True:
                    
                    Hpassword = passwordCheck(username)
                    correctPass = bcrypt.checkpw(password.encode(),Hpassword)
                    if correctPass == False:
                        userReal = False
                        with open("LoginRegister.html", "r") as file:
                            b = file.read()
                            c = "{{reg success}}"
                            m = "{{visits}}"
                            b = b.replace(m, "")
                            l = "{{login mess}}"
                            b = b.replace(l, "<h1>Login failed</h1>")
                            tokenFound = findToken(data)  # send it data and it will return the current users USERNAME from the token
                            if tokenFound != None:
                                c = "{{token found}}"
                                r = "<h1>Welcome back " + str(tokenFound) + "!</h1>"
                                b = b.replace(c, r)
                            else:
                                c = "{{token found}}"
                                r = ""
                                b = b.replace(c, r)
                        
                        respond = "HTTP/1.1 200 OK\r\n"
                        respond += "Content-Type: text/html; charset=utf-8\r\n"
                        respond += "X-Content-Type-Options: nosniff\r\n"
                        respond += "ContentLength: " + str(len(b)) + "\r\n"
                        respond += "\r\n"
                        print("I'm Sending Unwanted data", respond)
                        self.request.sendall(respond.encode() + b.encode())
                # if correct then login if not send error

                if userReal == True:
                    
                    print("start salt")
                    cookToken = loginToken(username)
                    print("cookie salt", cookToken)
                    UsersLoggedIn.append(username)
                    with open("home.html", "r") as file:
                        b = file.read()
                        l = "{{login mess}}"
                        r = "<h1>" + username + " is signed in </h1>"
                        b = b.replace(l, r)
                        print(b)
                        l = "{users logged in}"
                        r = "<h3>List of logged in users</h3><br>"
                        for i in UsersLoggedIn:
                            r = r + "<h5>" + i + " is currently logged in </h5><br>"
                        b = b.replace(l, r)
                        tokenFound = findToken(data)  # send it data and it will return the current users USERNAME from the token
                        if tokenFound != None:
                            c = "{{token found}}"
                            r = "<h1>Welcome back " + str(tokenFound) + "!</h1>"
                            b = b.replace(c, r)
                        else:
                            c = "{{token found}}"
                            r = ""
                            b = b.replace(c, r)
                    
                    respond = "HTTP/1.1 301 Moved Permanently\r\n"
                    respond += "X-Content-Type-Options: nosniff\r\n"
                    respond += "Set-Cookie: id=" + str(cookToken) + "; Max-Age=3600; HttpOnly\r\n"
                    respond += "ContentLength: 0\r\n"
                    respond += "Location: /home\r\n"
                    respond += "\r\n"
                    self.request.sendall(respond.encode())


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
        
            
            
            elif '/imup/' in headersDict['PATH']:
                up = ""
                upfile = ""
                q = 0
                for i in headersDict['PATH']:
                    if q == 1:
                        upfile += i  
                    elif up == "/imup/":
                        q = 1
                        upfile += i  
                    else:
                        up += i

                print(up, upfile, q)
                upfile = "image/" + upfile
                with open(upfile, "rb") as file:
                    b = file.read()
                
                respond = "HTTP/1.1 200 OK\r\n"
                respond += "Content-Type: image/jpeg\r\n"
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
    if finalDict['PATH']  == "/image-upload":
        finalDict['DATA'] = data[data.index("\r\n\r\n".encode())+4:]
    if finalDict['PATH']  != "/image-upload":    
        finalDict['DATA'] = data[data.index("\r\n\r\n".encode())+4:].decode()
    return finalDict


def validatePassword(password):
    eightLen = 0
    oneUpper = 0
    oneLower = 0
    oneNum = 0
    oneSpecial = 0
    specialChar = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "+", "=", "{", "}", ";", ":", "'", "<", ">", ",", ".", "?", "/"]

    if len(password) >= 8:
            eightLen = 1

    for i in password:
        print("checkingggg", i, eightLen, oneNum, oneLower, oneUpper, oneSpecial)
        if i.isupper() == True:
            oneUpper = 1
        if i.islower() == True:
            oneLower = 1
        if i.isdigit() == True:
            oneNum = 1
        if i in specialChar:
            oneSpecial = 1

    print("2checkingggg", eightLen, oneNum, oneLower, oneUpper, oneSpecial)

    if eightLen == 1 and oneLower == 1 and oneUpper == 1 and oneNum == 1 and oneSpecial == 1:
        return True
    else:
        return False


def hashedPassword(username, password):
    print("inside hased")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    print("Hashed Password", hashed)

    dbconnect = pymongo.MongoClient('mongodb://mongo:27017/')
    db = dbconnect['hw3']
    collect = db["passwords"]
        
    regdic = {}
    regdic["username"] = username
    regdic["password"] = hashed
    print("insert register",regdic)
    collect.insert_one(regdic)

def userLookUp(username):
    dbconnect = pymongo.MongoClient('mongodb://mongo:27017/')
    db = dbconnect['hw3']
    collect = db["passwords"]
    for k in collect.find({},{"_id": 0, "username": 1}):
        print("userLook", k, k["username"])
        if str(k["username"]) == username:
            return True
    return False

def passwordCheck(username):
    dbconnect = pymongo.MongoClient('mongodb://mongo:27017/')
    db = dbconnect['hw3']
    collect = db["passwords"]
    hashedPass = ""
    for k in collect.find({},{"_id": 0, "username": 1, "password": 1}):
        print("userLook", k, k["password"])
        if str(k["username"]) == username:
            hashedPass = k["password"]
    return hashedPass

def findToken(data):
    foundCookie = data.find("id=")
            
    if foundCookie != -1:
        newdata = data.split("\r\n\r\n")
        newdata = newdata[0].split("\r\n")
        print("NEWDATA", newdata)
        cookie = ""
        for i in newdata:
            if i.find("Cookie:") != -1:
                cookie = i
                print("CCK",cookie)
        cookie = cookie.split("; ")
        print("CCL", cookie)
        visits = ""
        for i in cookie:
            if i.find("id=") != -1:
                visits = i
                print("VVV",visits)
        id = ""
        esign = 0
        for i in visits:
            if esign == 1:
                print(i)
                if i != "\r\n":
                    id = id + str(i)
            if i == "=":
                esign = 1
                
        print("cookie token", id)

        a1Hash = hashlib.sha256()
        a1Hash.update(id.encode())
        a1Hash = a1Hash.digest()
        print("Checking SHA256 hash",a1Hash)


        dbconnect = pymongo.MongoClient('mongodb://mongo:27017/')
        db = dbconnect['hw3']
        collect = db["salts"]
        username = ""
        for k in collect.find({},{"_id": 0, "username": 1, "token": 1}):
            print("userLook", k, k["token"])
            if k["token"] == a1Hash:
                username = k["username"]

        print("SHA256 username",username)


        return username
    else:
        return None

def loginToken(username):
    randomToken = ""
    randomToken = secrets.choice('abcdefghijklmnopqrstuvwxyz!@#$%^&*()-_+={,};:<>.?/1234567890')
    for i in range(22):
        randomToken += secrets.choice('abcdefghijklmnopqrstuvwxyz1234567890')
    print("random token", randomToken)
    #log_2(26^22) = 113 entropy

    a1Hash = hashlib.sha256()
    a1Hash.update(randomToken.encode())
    a1Hash = a1Hash.digest()
    print("SHA256 hash",a1Hash)

    dbconnect = pymongo.MongoClient('mongodb://mongo:27017/')
    db = dbconnect['hw3']
    collect = db["salts"]
    print("made salt")
    
    regdic = {}
    regdic["username"] = username
    regdic["token"] = a1Hash
    print("insert salts", randomToken, regdic)
    collect.insert_one(regdic)

    return randomToken


    

def validatePassword(password):
    eightLen = 0
    oneUpper = 0
    oneLower = 0
    oneNum = 0
    oneSpecial = 0
    specialChar = ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "_", "+", "=", "{", "}", ";", ":", "'", "<", ">", ",", ".", "?", "/"]

    if len(password) >= 8:
        eightLen = 1

    for i in password:
        print("checkingggg", i, eightLen, oneNum, oneLower, oneUpper, oneSpecial)
        if i.isupper() == True:
            oneUpper = 1
        if i.islower() == True:
            oneLower = 1
        if i.isdigit() == True:
            oneNum = 1
        if i in specialChar:
            oneSpecial = 1

    print("2checkingggg", eightLen, oneNum, oneLower, oneUpper, oneSpecial)

    if eightLen == 1 and oneLower == 1 and oneUpper == 1 and oneNum == 1 and oneSpecial == 1:
        return True
    else:
        return False

def parseImage(headerDict, TCP):

    if int(headerDict['Content-Length']) > 4096:
            notDone = True
            while notDone == True:
                temp = TCP.request.recv(2048)
                # print("temp", len(temp), temp)
                if headerDict.get('DATA') == "":
                    headerDict['DATA'] = temp
                    # print("data", headerDict['DATA'])
                    if len(temp) < 2048:
                        notDone = False
                elif headerDict.get('DATA') == " ":
                    headerDict['DATA'] = temp
                    # print("data", headerDict['DATA'])
                    if len(temp) < 2048:
                        notDone = False
                else:
                    headerDict['DATA'] += temp
                    # print("data", headerDict['DATA'])
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


def noHTML(x):
    b = x.replace("&", "&amp")
    c = b.replace("<", "&lt")
    d = c.replace(">", "&gt")
    return d


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 8000
    
    server = socketserver.ThreadingTCPServer((HOST,PORT), MyTCPHandler)
    server.serve_forever()

