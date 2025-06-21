import time
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- 설정 ---
LOG_DIRECTORY = '.'  # sslsplit이 로그를 저장하는 디렉터리
# ------------

# 각 파일을 실시간으로 tail하는 함수 (하나의 스레드에서 실행됨)
def tail_file(filepath):
    """파일 끝에 추가되는 내용을 계속 읽어서 키워드를 찾는다."""
    print(f"[+] '{os.path.basename(filepath)}' 파일 감시 시작...")
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            # 파일의 처음부터 읽기 위해 seek(0, 2)를 사용하지 않음
            while True:
                line = f.read()#f.readline()
                if line:
                    print(f"line -------------> {line}")
                else:
                    # 파일의 끝에 도달하면 잠시 대기
                    time.sleep(0.1)
    except FileNotFoundError:
        print(f"[-] 파일이 삭제되었습니다: {os.path.basename(filepath)}")
    except Exception as e:
        print(f"[!] 에러 발생 ({os.path.basename(filepath)}): {e}")


# 파일 시스템 이벤트를 처리하는 핸들러
class MyEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        """파일이 생성되었을 때만 처리한다."""
        if not event.is_directory and event.src_path.endswith('.log'):
            # 각 파일을 별도의 스레드에서 감시하여 메인 스레드가 멈추지 않게 함
            thread = threading.Thread(target=tail_file, args=(event.src_path,), daemon=True)
            thread.start()

# 메인 실행 로직
if __name__ == "__main__":
    if not os.path.exists(LOG_DIRECTORY):
        os.makedirs(LOG_DIRECTORY)
        print(f"'{LOG_DIRECTORY}' 디렉터리가 생성되었습니다.")

    print(f"'{LOG_DIRECTORY}' 디렉터리에서 '.log' 파일 생성을 감시합니다...")
    
    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, LOG_DIRECTORY, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] 감시를 중지합니다.")
        observer.stop()
    
    observer.join()
