import socket
import threading
import time
import sys

def send_heartbeat(sock):
    #每5秒发送一次心跳包
    while True:
        try:
            # 发送心跳包，约定字符串 "heartbeat"
            sock.sendall("heartbeat".encode())
        except Exception as e:
            print("Heartbeat thread error:", e)
            break
        time.sleep(5)

def send_messages(sock):
    #客户端输入
    while True:
        try:
            msg = input()  # 等待键盘输入
            if msg:
                sock.sendall(msg.encode())
        except Exception as e:
            print("Sending message error:", e)
            break

def main():
    HOST = '127.0.0.1'  # 服务器地址，根据需要修改
    PORT = 12001         # 服务器端口

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT)) #连接服务器
    except Exception as e:
        print("Unable to connect to server:", e)
        sys.exit()

    print("Connected to server. You can start typing messages.")

    # 启动发送心跳包的线程
    heartbeat_thread = threading.Thread(target=send_heartbeat, args=(sock,), daemon=True)
    heartbeat_thread.start()

    # 主线程负责发送用户输入的消息
    send_messages(sock)

if __name__ == "__main__":
    main()