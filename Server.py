import socket as so
import threading
import os

s = so.socket(so.AF_INET,so.SOCK_STREAM)
IP = so.gethostbyname(so.gethostname())
s.bind(("",80))
s.listen()
def getListDir(folder = "./"):
    return os.listdir(folder)

def getHtmlForDirectoryListing(data,files,folders):
    retDiv = f"""<title>FTP Server</title><body style="background-color:rgba(10,10,10,0.9);">
        <center><h2 style="color:rgba(200,200,200,0.85)">Go to this link in other devices to access the files: <a style="color:white;text-decoration:none;" href="http://{IP}">http://{IP}</a></h2></center>
        <h1 style="color:antiquewhite">Directory Listing {data}</h1><br>
        <h2 style="color:antiquewhite">Folders</h2>
        <ul style="list-style:none;">"""

    for content in folders:
        retDiv+=f'<li style="margin-top:2px"><a style="font-size:30px;color:white;text-decoration:none;" href="/{data}/{content}" >{content}</a></li>'
    retDiv+=f'</ul><br><hr><h2 style="color:antiquewhite">Files</h2><ul>'
    
    for content in files:
        retDiv+=f'<li style="margin-top:2px"><a style="font-size:20px;color:white;text-decoration:none;" href="/{data}/{content}" target="_blank">{content}</a></li>'
    retDiv+=f"</ul><br></body>"
    return retDiv

def handleConnection(conn:so.socket):
    try:
        data = conn.recv(1000).split(b"\r")[0]
        data = "."+data.split(b" ")[1].decode().strip()
        data = data.replace("%20"," ")
        data = data.replace("%24","$")
        data = data.replace("%25","%")
        data = data.replace("%26","&")
        data = data.replace("%3D","=")
        if data[-1]=="/":
            data = data[:-1]
        print(data)
        if os.path.isdir(data):
            contents = getListDir(data)
            folders = [c for c in contents if os.path.isdir(data+"/"+c)]
            files = [co for co in contents if os.path.isfile(data+"/"+co)]
            retDiv = getHtmlForDirectoryListing(data,files,folders)
            conn.send(b"HTTP/1.1 200 OK\r\n\n"+retDiv.encode())
        elif os.path.isfile(data):
            try:
                file = open(data,"rb")
                filesize = int(os.stat(data).st_size)
                chunkSize = int(filesize*0.1)
                if chunkSize<1000:
                    chunkSize=1000
                fileData = file.read(chunkSize)
                conn.send(b"HTTP/1.1 200\r\nConnection: keep-alive\r\nContent-length:"+str(filesize).encode()+b"\r\n\n")
                while len(fileData)>0:
                    conn.send(fileData)
                    fileData = file.read(chunkSize)
            except FileNotFoundError:
                conn.send(b"HTTP/1.1 200 OK\r\n\n<h1>404 Not Found</h1>")
            except Exception as e:
                conn.send(f"HTTP/1.1 500 OK\r\n\n<h1>500 Internal Server Error:</h1><h3>{e}</h3>".encode())
        else:
            conn.send(b"HTTP/1.1 200 OK\r\n\n<h1>404 Not Found</h1>")
        conn.close()
    except Exception as e:
        try:
            conn.close()
        except:
            pass
        print(f"Connection lost due to an error")
    
print(f"Go to link: http://{IP}")
threading.Thread(target=os.system,args=[f"start http://{IP}"]).start()

while True:
    conn,addr=s.accept()
    print("Connected from",addr[0])
    threading.Thread(target=handleConnection,args=[conn]).start()