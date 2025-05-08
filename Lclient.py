import socket
import struct

class Client:
    def __init__(self,host,port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def start(self):
        try:
            self.socket.connect((self.host, self.port)) #连接服务器
            print("Connect successfully")
            while True:
                print("\nChoose command:")
                print("1. Register")
                print("2. Login") 
                print("3. Exit")
            
                choice = input("Please input command(1-3): ").strip()
                if choice == "1":
                    self.handle_registration()
                elif choice == "2":
                    self.handle_login()
                elif choice == "3":
                    print("Good Bye!")
                    break
                else:
                    print("Invalid input,input again")
        except Exception as e:
            print("Unable to connect to server:", e)
            return
        finally:
            self.socket.close()

    def recv_all(self, socket, length):
        data = b''
        while len(data) < length:
            packet = socket.recv(length - len(data))
            if not packet:
                return None
            data += packet
        return data
    
    #处理注册
    def handle_registration(self):
        print("\n[User Registration]")
        username = input("Username(at most 20 bytes): ").strip()
        password = input("password(at most 30 bytes): ").strip()

        if len(username) > 20:
            print("Username is too long")
            return
        if len(password) > 30:
            print("password is too long")
            return
        
        #封装注册消息体
        username_bytes = username.encode('utf-8').ljust(20, b'\x00')[:20]
        password_bytes = password.encode('utf-8').ljust(30, b'\x00')[:30]
        body = username_bytes + password_bytes
        #封装注册消息头
        total_length = 8 + len(body)
        command_id = 1
        header = struct.pack('!II', total_length, command_id)
        self.socket.sendall(header + body)

        #接收响应
        response_header = self.recv_all(self.socket, 8)
        if not response_header:
            print("Registration failed: No response")
            return
        total_len, cmd_id = struct.unpack('!II', response_header) 
        if cmd_id != 2:
            print("Registration failed: Invalid response type")
            return
        response_body = self.recv_all(self.socket, total_len - 8)
        if not response_body:
            print("Registration failed: Incomplete response")
            return
        status = response_body[0]
        description = response_body[1:65].rstrip(b'\x00').decode('utf-8')
        print(f"Registration Status: {'Success' if status == 1 else 'Failed'}, Description: {description}")

    #处理登录
    def handle_login(self):
        print("\n[User Login]")
        username = input("Username(at most 20 bytes): ").strip()
        password = input("password(at most 30 bytes): ").strip()
        if len(username) > 20:
            print("Username is too long")
            return
        if len(password) > 30:
            print("password is too long")
            return
        
        #封装登录消息体
        username_bytes = username.encode('utf-8').ljust(20, b'\x00')[:20]
        password_bytes = password.encode('utf-8').ljust(30, b'\x00')[:30]
        body = username_bytes + password_bytes
        #封装登录消息头
        total_length = 8 + len(body)
        command_id = 3
        header = struct.pack('!II', total_length, command_id)
        self.socket.sendall(header + body)

         #接收响应
        response_header = self.recv_all(self.socket, 8)
        if not response_header:
            print("Login failed: No response")
            return
        total_len, cmd_id = struct.unpack('!II', response_header) 
        if cmd_id != 4:
            print("Login failed: Invalid response type")
            return
        response_body = self.recv_all(self.socket, total_len - 8)
        if not response_body:
            print("Login failed: Incomplete response")
            return
        status = response_body[0]
        description = response_body[1:65].rstrip(b'\x00').decode('utf-8')
        print(f"Registration Status: {'Success' if status == 1 else 'Failed'}, Description: {description}")

if __name__ == "__main__":
    client = Client('localhost', 8080)
    client.start()