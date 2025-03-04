import logging
from chat_downloader import ChatDownloader

def download_and_print_chat(url):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info(f"채팅 다운로드 시작: {url}")
    downloader = ChatDownloader()
    
    try:
        chat = downloader.get_chat(url)
        for idx, message in enumerate(chat, start=1):
            logging.info(f"메시지 {idx}:")
            # 메시지의 모든 파라미터(키와 값) 출력
            for key, value in message.items():
                logging.info(f"    {key}: {value}")
    except Exception as e:
        logging.error(f"오류 발생: {e}")
    logging.info("채팅 다운로드 완료.")

if __name__ == "__main__":
    # 테스트할 스트리밍 URL (실제 URL로 수정)
    stream_url = "https://www.youtube.com/watch?v=a-sanSTdrjE&ab_channel=%EC%A1%B0%EC%84%A0%EC%9D%BC%EB%B3%B4"
    download_and_print_chat(stream_url)
