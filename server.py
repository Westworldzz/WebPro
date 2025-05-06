import socket
import time

def run_server(port=12001, backlog=5):
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(('', port))
    listen_socket.listen(backlog)
    print(f"Server is listening on port {port} with backlog {backlog}")

    try:
        while True:
            # 故意延迟accept，制造队列堆积
            time.sleep(1)  # 每1秒才accept一个连接
            
            client_socket, addr = listen_socket.accept()
            print(f"Accepted connection from: {addr}")
            
            # 简单处理客户端消息
            msg = client_socket.recv(1024).decode()
            client_socket.send(f"Echo: {msg}".encode())
            client_socket.close()
            
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        listen_socket.close()

if __name__ == "__main__":
    run_server()