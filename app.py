# STREAMING_CHUNK:Importing required dependencies and initializing Flask application...
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for Google Apps Script requests


# STREAMING_CHUNK:Defining the FixedSizeQueue class with circular buffer queue logic...
class FixedSizeQueue:
    """
    고정 길이 큐 (Fixed-Size Queue / Ring Buffer) 구현 클래스.
    배열 기반의 원형 큐(Circular Queue) 구조를 사용하여 모듈러 연산으로 인덱스를 제어합니다.
    """

    def __init__(self, capacity=5):
        """
        1) 초기화 (Initialization)
        - capacity: 큐의 최대 저장 용량
        - time complexity: O(1)
        - space complexity: O(N)
        """
        self.capacity = capacity
        self.queue = [None] * capacity  # 고정된 크기의 리스트 생성
        self.front = 0                 # 맨 앞 요소의 인덱스
        self.rear = 0                  # 다음 삽입할 공간의 인덱스
        self.count = 0                 # 현재 저장된 데이터 개수

    def is_empty(self):
        """4) 상태 검사 - Empty 여부 (O(1))"""
        return self.count == 0

    def is_full(self):
        """4) 상태 검사 - Full 여부 (O(1))"""
        return self.count == self.capacity

    def push(self, value):
        """
        2) Push (Enqueue) - 데이터 추가
        - time complexity: O(1)
        - space complexity: O(1)
        """
        if self.is_full():
            return False, "Queue Overflow: 큐가 가득 찼습니다."
        
        self.queue[self.rear] = value
        self.rear = (self.rear + 1) % self.capacity  # 원형 포인터 이동
        self.count += 1
        return True, f"Push 성공: {value}"

    def pop(self):
        """
        2) Pop (Dequeue) - 데이터 꺼내기
        - time complexity: O(1)
        - space complexity: O(1)
        """
        if self.is_empty():
            return None, "Queue Underflow: 큐가 비어있습니다."
        
        val = self.queue[self.front]
        self.queue[self.front] = None  # 기존 데이터 초기화
        self.front = (self.front + 1) % self.capacity  # 원형 포인터 이동
        self.count -= 1
        return val, f"Pop 성공: {val}"

    def size(self):
        """3) 현재 데이터 개수(길이/크기) 반환 (O(1))"""
        return self.count

    def peek(self):
        """5) 전면(Front) 데이터 확인 (O(1))"""
        if self.is_empty():
            return None
        return self.queue[self.front]

    def clear(self):
        """6) 큐 전체 데이터 삭제 (O(1))"""
        self.queue = [None] * self.capacity
        self.front = 0
        self.rear = 0
        self.count = 0
        return "큐가 성공적으로 초기화되었습니다."

    def search_index(self, value):
        """
        7) 값의 index 검색 (Front 기준 상대 위치 및 저장 배열 절대 위치)
        - time complexity: O(N)
        - space complexity: O(1)
        """
        if self.is_empty():
            return -1
        
        for i in range(self.count):
            idx = (self.front + i) % self.capacity
            if self.queue[idx] == value:
                return i  # Front 기준 상대 index (0-based)
        return -1

    def count_occurrences(self, value):
        """
        8) 값의 개수(지정한 값의 등장 횟수) 반환
        - time complexity: O(N)
        - space complexity: O(1)
        """
        occurrences = 0
        for i in range(self.count):
            idx = (self.front + i) % self.capacity
            if self.queue[idx] == value:
                occurrences += 1
        return occurrences

    def contains(self, value):
        """9) 값의 존재 여부 검사 (O(N))"""
        return self.search_index(value) != -1

    def print_front_to_rear(self):
        """
        10) Front 부터 Rear 까지 순서대로 출력 (배열 리스트 반환)
        - time complexity: O(N)
        - space complexity: O(N)
        """
        result = []
        for i in range(self.count):
            idx = (self.front + i) % self.capacity
            result.append(self.queue[idx])
        return result

    def get_state(self):
        """전체 큐의 상태 및 복잡도 정보 종합 반환"""
        return {
            "capacity": self.capacity,
            "current_size": self.size(),
            "is_empty": self.is_empty(),
            "is_full": self.is_full(),
            "front_index": self.front,
            "rear_index": self.rear,
            "front_value": self.peek(),
            "elements_in_order": self.print_front_to_rear(),
            "internal_array": self.queue,
            "complexities": {
                "push": "O(1)",
                "pop": "O(1)",
                "peek": "O(1)",
                "search": "O(N)",
                "space": f"O({self.capacity})"
            }
        }


# STREAMING_CHUNK:Global Queue Instance definition and HTTP Endpoint Routing...
# 글로벌 큐 인스턴스 (기본 크기: 5)
global_queue = FixedSizeQueue(capacity=5)


@app.route('/', methods=['GET'])
def index():
    """헬스 체크 및 서버 설명"""
    return jsonify({
        "status": "online",
        "service": "Fixed-Size Queue Cloud Run API Server",
        "queue_state": global_queue.get_state()
    })


@app.route('/api/queue', methods=['POST'])
def handle_queue_action():
    """
    단일 통신 API 엔드포인트: 10가지 큐 동작 요청 처리
    """
    data = request.get_json() or {}
    action = data.get('action')
    val = data.get('value')
    capacity = data.get('capacity', 5)

    global global_queue
    message = ""
    success = True

    try:
        # 1) 초기화
        if action == 'init':
            global_queue = FixedSizeQueue(capacity=int(capacity))
            message = f"용량 {capacity}의 고정 길이 큐가 초기화되었습니다."

        # 2) push
        elif action == 'push':
            if val is None or str(val).strip() == "":
                return jsonify({"success": False, "message": "삽입할 값을 입력하세요."}), 400
            success, message = global_queue.push(val)

        # 2) pop
        elif action == 'pop':
            pop_val, message = global_queue.pop()
            success = pop_val is not None

        # 3) 현재 데이터 개수 반환
        elif action == 'size':
            message = f"현재 데이터 개수: {global_queue.size()}"

        # 4) 상태 검사 (full / empty)
        elif action == 'status':
            message = f"Is Empty: {global_queue.is_empty()}, Is Full: {global_queue.is_full()}"

        # 5) 전면 (Front) 데이터 확인
        elif action == 'peek':
            front_val = global_queue.peek()
            message = f"Front 데이터: {front_val}" if front_val is not None else "큐가 비어 있습니다."

        # 6) 큐 전체 데이터 삭제
        elif action == 'clear':
            message = global_queue.clear()

        # 7) 값의 index 검색
        elif action == 'search_index':
            idx = global_queue.search_index(val)
            message = f"값 '{val}'의 상대 인덱스: {idx}" if idx != -1 else f"값 '{val}'을(를) 찾을 수 없습니다."

        # 8) 값의 개수
        elif action == 'count_value':
            cnt = global_queue.count_occurrences(val)
            message = f"값 '{val}'의 개수: {cnt}개"

        # 9) 값의 존재 여부 검사
        elif action == 'contains':
            found = global_queue.contains(val)
            message = f"값 '{val}' 존재 여부: {'존재함 (True)' if found else '없음 (False)'}"

        # 10) Front부터 Rear까지 출력
        elif action == 'print_all':
            elements = global_queue.print_front_to_rear()
            message = f"Front -> Rear 순서 데이터: {elements}"

        else:
            return jsonify({"success": False, "message": f"지원하지 않는 액션: {action}"}), 400

        # 결과 종합 반환
        return jsonify({
            "success": success,
            "message": message,
            "queue_state": global_queue.get_state()
        })

    except Exception as e:
        return jsonify({"success": False, "message": f"서버 오류: {str(e)}"}), 500


if __name__ == '__main__':
    # Cloud Run 기본 포트 8080 대응
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
