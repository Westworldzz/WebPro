import socket
import threading
import time

# 全局字典：记录每个客户端最后一次发送心跳的时间
client_heartbeats = {}
#锁
client_lock = threading.Lock()

def client_handler(conn, addr):
    #处理单个客户端的消息接收
    print(f"Connected by {addr}")
    # 初始化该客户端的心跳时间
    with client_lock:
        client_heartbeats[conn] = time.time()
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                # 客户端关闭连接
                break
            message = data.decode().strip()
            if message.lower() == "heartbeat":
                # 如果收到心跳包，则更新心跳时间
                with client_lock:
                    client_heartbeats[conn] = time.time()
                print(f"Received heartbeat from {addr} at {time.ctime(client_heartbeats[conn])}")
            else:
                # 正常消息则输出到屏幕
                print(f"Message from {addr}: {message}")
    except Exception as e:
        print(f"Exception from {addr}: {e}")
    finally:
        with client_lock:
            if conn in client_heartbeats:
                del client_heartbeats[conn]
        conn.close()
        print(f"Connection closed for {addr}")

def heartbeat_monitor():
    #定时检查所有客户端的心跳状态，超过10秒未收到心跳则认为连接异常
    while True:
        time.sleep(1)  # 每秒检查一次
        now = time.time()
        with client_lock:
            for conn in list(client_heartbeats.keys()):
                if now - client_heartbeats[conn] > 10:
                    try:
                        peer = conn.getpeername()
                    except:
                        peer = "Unknown"
                    print(f"Connection {peer} is abnormal (no heartbeat in 10 seconds).")
                    try:
                        conn.close()
                    except:
                        pass
                    del client_heartbeats[conn]

def main():
    HOST = '0.0.0.0'
    PORT = 12001

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    # 启动心跳监控线程
    monitor_thread = threading.Thread(target=heartbeat_monitor, daemon=True)
    monitor_thread.start()

    while True:
        conn, addr = server_socket.accept()
        # 为每个连接启动一个线程处理数据收发
        t = threading.Thread(target=client_handler, args=(conn, addr), daemon=True)
        t.start()

if __name__ == "__main__":
    main()