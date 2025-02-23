import redis
import json
import threading

r = redis.Redis(host="localhost", port=6378, decode_responses=True)

class LikeConsumer:
    """
    ✅ `post_like_stream`, `comment_like_stream`을 소비하는 (like_service) Consumer
    - `post_like_stream` → 게시글 좋아요 이벤트 처리
    - `comment_like_stream` → 댓글 좋아요 이벤트 처리
    """
    def __init__(self):
        self.group = "like_consumer_group"
        self.consumer = "like_service"
        self.streams = {
            "post_like_stream": self.handle_post_like,
            "comment_like_stream": self.handle_comment_like
        }

        for stream in self.streams.keys():
            try:
                r.xgroup_create(stream, self.group, id="0", mkstream=True)
                print(f"📌 Redis Stream 그룹 생성 완료: {stream}")
            except redis.exceptions.ResponseError:
                print(f"📌 Redis Stream 그룹 이미 존재함: {stream}")

    def start(self):
        """
        ✅  좋아요 이벤트를 처리하는 Stream 실행
        """
        for stream_name in self.streams.keys():
            thread = threading.Thread(target=self.process_stream, args=(stream_name,))
            thread.daemon = True
            thread.start()

    def process_stream(self, stream_name):
        """
        ✅ 게시글 및 댓글 좋아요 이벤트 처리
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

    def handle_post_like(self, msg_data):
        """
        ✅ 게시글 좋아요 이벤트 처리
        """
        post_id = msg_data["post_id"]
        like_cache_key = f"like_count:post:{post_id}"
        new_like_count = int(r.get(like_cache_key) or 0) + 1
        r.set(like_cache_key, new_like_count)

        print(f"📌 게시글 {post_id}의 좋아요 캐시 업데이트 완료")

    def handle_comment_like(self, msg_data):
        """
        ✅ 댓글 좋아요 이벤트 처리
        """
        comment_id = msg_data["comment_id"]
        like_cache_key = f"like_count:comment:{comment_id}"
        new_like_count = int(r.get(like_cache_key) or 0) + 1
        r.set(like_cache_key, new_like_count)

        print(f"📌 댓글 {comment_id}의 좋아요 캐시 업데이트 완료")
