import logging
from flask import Flask, render_template_string, request
import socket
import threading
import time
import numpy as np
import tempfile
import os

app = Flask(__name__)

# 서버 설정
UDP_HOST = '0.0.0.0'
UDP_PORT = 9999
TCP_PORT = 8888

# Tailwind CSS와 커스텀 스타일
tailwind_cdn = "https://cdn.tailwindcss.com"
custom_css = '''
<style>
@keyframes neon {
    0%, 100% {
        text-shadow:
            0 0 10px #fff,
            0 0 20px #fff,
            0 0 30px #e60073,
            0 0 40px #e60073,
            0 0 50px #e60073,
            0 0 60px #e60073,
            0 0 70px #e60073;
    }
    50% {
        text-shadow:
            0 0 5px #fff,
            0 0 10px #ff4da6,
            0 0 15px #ff4da6,
            0 0 20px #ff4da6,
            0 0 25px #ff4da6,
            0 0 30px #ff4da6,
            0 0 35px #ff4da6;
    }
}

.neon-text {
    color: #fff;
    animation: neon 1.5s infinite alternate;
}

.neon-button {
    position: relative;
    display: inline-block;
    padding: 15px 30px;
    color: #fff;
    text-transform: uppercase;
    text-decoration: none;
    background-color: transparent;
    border: 2px solid #fff;
    border-radius: 5px;
    transition: 0.5s;
}

.neon-button:hover {
    background-color: #fff;
    color: #000;
    box-shadow: 0 0 20px #fff, 0 0 30px #ff00de, 0 0 40px #ff00de;
}

.glow {
    animation: glow 1s infinite alternate;
}

@keyframes glow {
    from {
        box-shadow: 0 0 5px #ff00de, 0 0 10px #ff00de, 0 0 15px #ff00de;
    }
    to {
        box-shadow: 0 0 20px #ff00de, 0 0 30px #ff00de, 0 0 40px #ff00de;
    }
}
</style>
'''

# UDP 서버 구현
def start_udp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_HOST, UDP_PORT))
    logging.info(f"UDP 서버 시작됨 - {UDP_HOST}:{UDP_PORT}")
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            logging.info(f"UDP 패킷 수신: {addr} -> {len(data)} bytes")
            # Echo 응답
            sock.sendto(data, addr)
        except Exception as e:
            logging.error(f"UDP 서버 에러: {e}")

# TCP SYN 테스트용 서버
def start_tcp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((UDP_HOST, TCP_PORT))
    sock.listen(5)
    logging.info(f"TCP 서버 시작됨 - {UDP_HOST}:{TCP_PORT}")
    
    while True:
        try:
            client, addr = sock.accept()
            logging.info(f"TCP 연결 수락: {addr}")
            client.close()
        except Exception as e:
            logging.error(f"TCP 서버 에러: {e}")

# 부하 테스트 함수들
def recursive_function(n):
    if n == 0:
        return 1
    return n * recursive_function(n - 1)

def matrix_multiplication(size):
    a = np.random.rand(size, size)
    b = np.random.rand(size, size)
    result = np.dot(a, b)
    return result

def io_heavy_task():
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for _ in range(1000000):
            temp_file.write(b"This is a heavy I/O task\n")
        temp_file_path = temp_file.name

    with open(temp_file_path, 'r') as f:
        _ = f.readlines()

    os.remove(temp_file_path)

def heavy_task():
    matrix_multiplication(2000)
    io_heavy_task()
    try:
        recursive_function(1000)
    except RecursionError:
        pass

# 라우트 정의
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>융보공 보안 테스트 서버</title>
        <script src="{{ tailwind_cdn }}"></script>
        {{ custom_css | safe }}
    </head>
    <body class="bg-black text-white">
        <div class="flex flex-col items-center justify-center min-h-screen space-y-8">
            <h1 class="text-6xl font-extrabold neon-text">융보공 보안 테스트 서버</h1>
            <div class="space-y-4">
                <a href="/compute" class="neon-button glow block">CPU/메모리 부하 테스트</a>
                <a href="/slowloris" class="neon-button glow block">Slowloris 테스트</a>
                <a href="/flood" class="neon-button glow block">플러딩 테스트</a>
            </div>
            <div class="mt-8 text-center">
                <p>UDP 서버: 포트 9999</p>
                <p>TCP 서버: 포트 8888</p>
            </div>
        </div>
    </body>
    </html>
    ''', tailwind_cdn=tailwind_cdn, custom_css=custom_css)

@app.route('/compute')
def compute():
    start_time = time.time()
    heavy_task()
    duration = time.time() - start_time

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>연산 결과</title>
        <script src="{{ tailwind_cdn }}"></script>
        {{ custom_css | safe }}
    </head>
    <body class="bg-black text-white">
        <div class="flex flex-col items-center justify-center min-h-screen space-y-6">
            <h1 class="text-5xl font-extrabold neon-text">연산 결과</h1>
            <p class="text-2xl">복합 부하 작업 완료</p>
            <p class="text-xl">연산 시간: {{ duration | round(2) }} 초</p>
            <a href="/" class="neon-button glow">메인 페이지로 돌아가기</a>
        </div>
    </body>
    </html>
    ''', duration=duration, tailwind_cdn=tailwind_cdn, custom_css=custom_css)

@app.route('/slowloris')
def slowloris_test():
    """Slowloris 취약점 테스트를 위한 엔드포인트"""
    response = ""
    for i in range(10000):  # 많은 양의 데이터
        response += f"데이터 청크 {i}\n"
        if i % 100 == 0:  # 100줄마다
            time.sleep(0.1)  # 0.1초 지연
    return response, 200

@app.route('/flood', methods=['GET', 'POST'])
def flood_test():
    """플러딩 테스트를 위한 엔드포인트"""
    if request.method == 'POST':
        # 대량의 데이터 처리 시뮬레이션
        data = request.get_data()
        
        # 메모리 부하를 위한 큰 리스트 생성
        memory_load = [x for x in range(100000)]
        
        # CPU 부하
        matrix = np.random.rand(500, 500)
        result = np.dot(matrix, matrix)
        
        # I/O 부하
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("X" * len(data) * 2)  # 받은 데이터의 2배 크기
            temp_file_path = temp_file.name
            
        # 파일 읽기
        with open(temp_file_path, 'r') as f:
            content = f.read()
            
        # 파일 삭제
        os.remove(temp_file_path)
        
        # 의도적인 지연
        time.sleep(0.5)  # 0.5초 지연
        
        return f"Processed: {len(data)} bytes with heavy computation", 200
    
    # GET 요청도 부하를 주도록 수정
    else:
        # CPU 부하
        matrix = np.random.rand(200, 200)
        result = np.dot(matrix, matrix)
        
        # 메모리 부하
        memory_load = [x for x in range(50000)]
        
        # 의도적인 지연
        time.sleep(0.2)  # 0.2초 지연
        
        return "Flood Test Endpoint (with heavy computation)", 200

if __name__ == '__main__':
    # 로깅 설정
    logging.basicConfig(
        filename='server.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # UDP 서버 시작
    udp_thread = threading.Thread(target=start_udp_server, daemon=True)
    udp_thread.start()
    
    # TCP 서버 시작
    tcp_thread = threading.Thread(target=start_tcp_server, daemon=True)
    tcp_thread.start()
    
    # Flask 앱 시작
    app.run(host='0.0.0.0', port=5000)