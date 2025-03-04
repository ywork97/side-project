from flask import Flask, render_template, request, jsonify
from chat_downloader import ChatDownloader
import threading
import time

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

app = Flask(__name__)

messages = []
messages_lock = threading.Lock()
downloading = False
stop_requested = False  # 중단 요청 여부를 위한 변수

# 기본 대체 이미지 URL
DEFAULT_IMAGE_URL = "https://dummyimage.com/40x40/cccccc/000000.png&text=No+Image"

def download_chat(url):
    global messages, downloading, stop_requested
    downloader = ChatDownloader()

    try:
        for chat_item in downloader.get_chat(url):
            # 중단 요청이 있으면 루프를 종료
            if stop_requested:
                print("채팅 수집 중단 요청이 들어왔습니다.")
                break

            # 1) author 파싱
            author = chat_item.get('author', {})
            if isinstance(author, dict):
                author_name = author.get('name', 'Unknown')
                # author.images 배열
                author_images = author.get('images', [])
            else:
                # author가 dict가 아닐 경우(문자열 등) 대비
                author_name = str(author) if author else 'Unknown'
                author_images = []

            # 2) author_images에서 가장 큰 해상도(혹은 특정 해상도)를 선택
            image_url = DEFAULT_IMAGE_URL
            if author_images:
                # 가장 큰 width를 가진 이미지를 선택
                max_width = 0
                for img in author_images:
                    # 예: {'url': '...', 'width': 64, 'height': 64, 'id': '64x64'}
                    w = img.get('width', 0)
                    if w > max_width:
                        max_width = w
                        image_url = img.get('url', DEFAULT_IMAGE_URL)

            # 3) 메시지 파싱
            message_text = chat_item.get('message', '')
            if isinstance(message_text, list):
                message_text = " ".join(str(m) for m in message_text)
            else:
                message_text = str(message_text)

            # 4) 뱃지 정보
            badges = chat_item.get('badges', [])

            # 5) 고유 ID
            message_id = chat_item.get('message_id') or str(time.time())

            new_chat = {
                'id': message_id,
                'author': author_name,
                'message': message_text,
                'badges': badges,
                'image_url': image_url  # 최종 선택된 이미지 URL
            }

            with messages_lock:
                messages.append(new_chat)
            # 디버깅 로그
            print("파싱된 메시지:", new_chat)
            time.sleep(0.1)
    except Exception as e:
        print("채팅 다운로드 중 오류:", e)
    finally:
        downloading = False

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/start', methods=['POST'])
def start():
    global downloading, messages, stop_requested
    url = request.form.get('url')
    if not url:
        return jsonify({'status': 'error', 'message': 'URL required'})

    with messages_lock:
        messages = []
    
    # 새로운 채팅 수집을 시작할 때 중단 요청 변수 초기화
    stop_requested = False

    if not downloading:
        downloading = True
        thread = threading.Thread(target=download_chat, args=(url,))
        thread.daemon = True
        thread.start()

    return jsonify({'status': 'started'})

@app.route('/stop', methods=['POST'])
def stop():
    global stop_requested
    stop_requested = True
    return jsonify({'status': 'stopped'})

@app.route('/get_messages')
def get_messages():
    global messages
    with messages_lock:
        new_msgs = messages.copy()
        messages.clear()
    return jsonify(new_msgs)

if __name__ == '__main__':
    app.run(debug=True)
