import socket
import time
import threading
from concurrent.futures import ThreadPoolExecutor

def test_connection(host, port, conn_id):
    try:
        # 创建socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 尝试连接
        start_time = time.time() 
        sock.connect((host, port))
        
        # 发送测试消息
        sock.send(f"Test message {conn_id}".encode())
        
        # 接收响应
        response = sock.recv(1024).decode()
        elapsed = time.time() - start_time 
        
        print(f"Connection {conn_id}: Success (time: {elapsed:.3f}s)")
        sock.close()
        return (conn_id, True, elapsed)
    except Exception as e:
        print(f"Connection {conn_id}: Failed ({str(e)})")
        try:
            sock.close()
        except:
            pass
        return (conn_id, False, str(e))

def run_client(host="127.0.0.1", port=12001, num_connections=100):
    print(f"Attempting {num_connections} concurrent connections to {host}:{port}...")
    start_time = time.time()
    
    success = 0
    failure = 0
    latencies = []
    
    # 使用线程池并发执行连接测试
    with ThreadPoolExecutor(max_workers=num_connections) as executor:
        futures = [executor.submit(test_connection, host, port, i) for i in range(1, num_connections + 1)]
        
        for future in futures:
            conn_id, result, latency_or_error = future.result()
            if result:
                success += 1
                latencies.append(latency_or_error)
            else:
                failure += 1
    
    total_time = time.time() - start_time
    
    # 打印统计结果
    print("\n=== Connection Test Results ===")
    print(f"Total attempts: {num_connections}")
    print(f"Success: {success}")
    print(f"Failure: {failure}")
    print(f"Success rate: {success/num_connections*100:.2f}%")
    if success > 0:
        print(f"Average latency: {sum(latencies)/len(latencies):.3f}s")
    print(f"Total test time: {total_time:.3f}s")

if __name__ == "__main__":
    run_client()