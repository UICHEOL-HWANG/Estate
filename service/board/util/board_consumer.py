import redis
import json
import threading

r = redis.Redis(host="localhost", port=6378, decode_responses=True)

class BoardConsumer:
    """
    ✅ `post_stream`, `comment_stream`을 소비하는 FastAPI1 (board_service) Consumer
    - `post_stream` → 게시글 생성/수정/삭제 이벤트 처리
    - `comment_stream` → 댓글 생성/수정/삭제 이벤트 처리
    """
    def __init__(self):
        self.group = "board_consumer_group"
        self.consumer = "board_service"
        self.streams = {
            "post_stream": self.handle_post_event,
            "comment_stream": self.handle_comment_event
        }

        for stream in self.streams.keys():
            try:
                r.xgroup_create(stream, self.group, id="0", mkstream=True)
                print(f"📌 Redis Stream 그룹 생성 완료: {stream}")
            except redis.exceptions.ResponseError:
                print(f"📌 Redis Stream 그룹 이미 존재함: {stream}")

    def start(self):
        """
        ✅ FastAPI1에서 게시글/댓글 이벤트를 처리하는 Stream 실행
        """
        for stream_name in self.streams.keys():
            thread = threading.Thread(target=self.process_stream, args=(stream_name,))
            thread.daemon = True
            thread.start()

    def process_stream(self, stream_name):
        """
        ✅ 게시글 및 댓글 이벤트 처리
        """
        handler = self.streams[stream_name]
        print(f"📌 Redis Stream 대기 중: {stream_name}")

        while True:
            try:
                messages = r.xreadgroup(self.group, self.consumer, {stream_name: ">"}, count=1, block=1000)
                for stream, msgs in messages:
                    for msg_id, msg_data in msgs:
                        handler(msg_data)
                        r.xack(stream_name, self.group, msg_id)

            except Exception as e:
                print(f"🚨 Redis Consumer Error ({stream_name}): {e}")

    def handle_post_event(self, msg_data):
        """
        ✅ 게시글 CRUD 이벤트 처리
        """
        event_type = msg_data["event_type"]
        post_id = msg_data["post_id"]

        if event_type == "create":
            print(f"📌 새로운 게시글 생성 이벤트 처리: {msg_data}")
            r.setex(f"post_cache:{post_id}", 300, json.dumps(msg_data))
        elif event_type == "update":
            print(f"📌 게시글 수정 이벤트 처리: {msg_data}")
            r.setex(f"post_cache:{post_id}", 300, json.dumps(msg_data))
        elif event_type == "delete":
            print(f"📌 게시글 삭제 이벤트 처리: {msg_data}")
            r.delete(f"post_cache:{post_id}")

    def handle_comment_event(self, msg_data):
        """
        ✅ 댓글 CRUD 이벤트 처리
        """
        event_type = msg_data["event_type"]
        comment_id = msg_data["comment_id"]

        if event_type == "create":
            print(f"📌 새로운 댓글 생성 이벤트 처리: {msg_data}")
            r.setex(f"comment_cache:{comment_id}", 300, json.dumps(msg_data))
        elif event_type == "update":
            print(f"📌 댓글 수정 이벤트 처리: {msg_data}")
            r.setex(f"comment_cache:{comment_id}", 300, json.dumps(msg_data))
        elif event_type == "delete":
            print(f"📌 댓글 삭제 이벤트 처리: {msg_data}")
            r.delete(f"comment_cache:{comment_id}")
