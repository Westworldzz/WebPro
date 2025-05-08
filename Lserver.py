import socket
import threading
import struct
import hashlib
import os

class Server:
    def __init__(self,host,port,backlog):
        self.host = host
        self.port = port
        self.backlog = backlog
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(backlog)
        self.password_file = 'passwords.txt'
        self.file_lock = threading.Lock()
        # 确保密码文件存在
        if not os.path.exists(self.password_file):
            open(self.password_file, 'w').close()

    def start(self):
        print(f"Server started")
        while True:
            client_socket, addr = self.socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()#启动服务
    
    #读取完整长度的数据
    def recv_all(self, socket, length):
        data = b''#初始化空字符串
        while len(data) < length:
            packet = socket.recv(length - len(data))
            if not packet:
                return None
            data += packet#拼接数据
        return data
    
    def handle_client(self,client_socket):
        try:
            #读取消息头
            header = self.recv_all(client_socket,8)
            if not header:
                print("Connection has been closed")
                return
            total_length, command_id = struct.unpack('!II', header)#解析

            #读取消息体
            body_length = total_length - 8
            body = self.recv_all(client_socket, body_length)
            if not body:
                return
            
            #处理请求
            #注册
            if command_id == 1:
                self.handle_registration(client_socket,body)
            
            #登录
            elif command_id == 3:
                self.handle_login(client_socket,body)

            else:
                print("Unknown command")

        except Exception as e:
            print(f"Error handling client: {e}")

        finally:
            client_socket.close()
    
    def handle_registration(self,client_socket, body):
        username = body[:20].rstrip(b'\x00').decode('utf-8')
        password = body[20:50].rstrip(b'\x00').decode('utf-8')
        
        #检查用户名是否存在
        with self.file_lock:
            with open(self.password_file,'r') as f:
                for line in f:
                    existing_user, _ = line.strip().split(':', 1)
                    if username == existing_user:
                        #发送失败响应报文
                        status = b'\x00'
                        description = "Username already exists".ljust(64).encode('utf-8')[:64]
                        response_body = status + description
                        response_header = struct.pack('!II',8 + len(response_body), 2)
                        client_socket.sendall(response_header + response_body)
                        return
                
            # 生成哈希并保存
            hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
            with open(self.password_file, 'a') as f:
                f.write(f"{username}:{hashed}\n")

            #发送成功响应报文
            status = b'\x01'
            description = "Registrantion success".ljust(64).encode('utf-8')[:64]
            response_body = status + description
            response_header = struct.pack('!II',8 + len(response_body), 2)
            client_socket.sendall(response_header + response_body)

    def handle_login(self,client_socket,body):
        username = body[:20].rstrip(b'\x00').decode('utf-8')
        password = body[20:50].rstrip(b'\x00').decode('utf-8')
        hashed_input = hashlib.sha256(password.encode('utf-8')).hexdigest()

        exist = False#用户是否存在
        correct = False#密码是否正确
        with self.file_lock:
            with open(self.password_file,'r') as f:
                for line in f:
                    parts = line.strip().split(':', 1)
                    if (len(parts) != 2):
                        continue
                    user,pwd = parts
                    if (user == username):
                        exist = True
                        if (hashed_input == pwd):
                            correct = True
        #用户不存在
        if not exist:
            status = b'\x00'
            description = "Username does not exists".ljust(64).encode('utf-8')[:64]
        elif not correct:
            status = b'\x00'
            description = "Incorrect password".ljust(64).encode('utf-8')[:64]
        else:
            status = b'\x01'
            description = "Login successfully".ljust(64).encode('utf-8')[:64]

        response_body = status + description
        response_header = struct.pack('!II', 8 + len(response_body), 4)
        client_socket.sendall(response_header + response_body)

if __name__ =="__main__":
    server = Server('localhost' , 8080, 5)
    server.start()




