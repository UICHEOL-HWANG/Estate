<template>
    <!-- ✅ 로딩 중 -->
    <div v-if="loading" class="flex justify-center items-center min-h-screen">
      <p class="text-gray-500 text-lg">⏳ 게시글을 불러오는 중...</p>
    </div>

    <!-- ✅ 게시글이 없을 때 -->
    <div v-else-if="!loading && !post.id" class="flex justify-center items-center min-h-screen">
      <p class="text-red-500 text-lg">❌ 게시글을 불러올 수 없습니다.</p>
    </div>

    <!-- ✅ 게시글이 정상적으로 있을 때 -->
    <div v-else class="flex justify-center items-center min-h-screen">
      <div class="max-w-4xl w-full mx-auto bg-gray-100 p-6 md:p-8 rounded-lg shadow-md">
        
        <!-- ✅ 작성자 정보 -->
        <div class="flex items-center space-x-3 mb-4">
          <img src="https://via.placeholder.com/40" alt="Profile" class="w-10 h-10 rounded-full" />
          <div>
            <span class="font-bold text-gray-900">{{ post.author }}</span>
            <p class="text-gray-500 text-sm">작성일: {{ formatDate(post.created_at) }}</p>
          </div>
        </div>

        <!-- ✅ 게시글 제목 -->
        <h2 class="text-xl font-bold text-gray-900 hover:text-blue-500">
          {{ post.title }}
        </h2>

        <!-- ✅ 게시글 내용 -->
        <p class="mt-4 text-gray-800 leading-relaxed">
          {{ post.content }}
        </p>

        <!-- ✅ 좋아요 & 댓글 -->
        <div class="flex items-center mt-6 text-gray-600 space-x-6">
          <span class="flex items-center cursor-pointer" @click="likePost(post.id)">
            👍 좋아요: {{ post.like_count }}
          </span>
          <span class="flex items-center">💬 댓글: {{ post.comment_count }}</span>
        </div>

        <!-- ✅ 댓글 목록 -->
        <div v-if="comments.length > 0" class="mt-8 bg-white p-4 rounded-lg shadow">
          <h3 class="text-lg font-semibold text-gray-800">📝 댓글</h3>
          <div v-for="comment in comments" :key="comment.id" class="bg-gray-100 p-3 mt-3 rounded-lg shadow">
            <div class="flex justify-between items-center">
              <div class="flex items-center space-x-3">
                <span class="font-bold text-gray-900">{{ comment.author }}</span>
                <p class="text-gray-500 text-sm">{{ formatDate(comment.created_at) }}</p>
              </div>
              <span class="cursor-pointer text-gray-600" @click="likeComment(comment.id)">
                👍 {{ comment.like_count }}
              </span>
            </div>
            <p class="mt-2 text-gray-700">{{ comment.content }}</p>
          </div>
        </div>

        <!-- ✅ 댓글 입력 폼 -->
        <div class="mt-4 bg-white p-4 rounded-lg shadow">
          <h3 class="text-lg font-semibold text-gray-800">💬 댓글 작성</h3>
          <textarea
            v-model="newComment"
            class="w-full px-4 py-2 mt-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 h-20 resize-none"
            placeholder="댓글을 입력하세요"
          ></textarea>
          <div class="flex justify-end mt-2">
            <button
              @click="submitComment"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg shadow-md hover:bg-blue-600 transition"
            >
              작성
            </button>
          </div>
        </div>

        <!-- ✅ 목록으로 돌아가기 버튼 -->
        <div class="flex justify-end mt-8">
          <button
            @click="goBack"
            class="px-6 py-3 border rounded-lg text-gray-600 hover:bg-gray-200 transition"
          >
            목록으로 돌아가기
          </button>
        </div>
      </div>
    </div>
</template>

<script>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useBoardStore } from "../store/board";
import { useLikeStore } from "../store/like_store";

export default {
  setup() {
    const route = useRoute();
    const router = useRouter();
    const boardStore = useBoardStore();
    const likeStore = useLikeStore();
    const newComment = ref("");

    // ✅ 게시글 데이터 가져오기
    const post = computed(() => boardStore.postDetail || {});
    const comments = computed(() => boardStore.comments || []);
    const loading = computed(() => boardStore.loading);

    // ✅ 게시글 상세 조회 및 댓글 조회 실행
    onMounted(() => {
      boardStore.fetchPostDetail(route.params.postId);
      boardStore.fetchComments(route.params.postId);
    });

    // ✅ 날짜 포맷 함수
    const formatDate = (dateString) => {
      if (!dateString) return "날짜 없음";
      const date = new Date(dateString);
      return date.toLocaleDateString("ko-KR", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      });
    };

    // ✅ 댓글 작성 함수
    const submitComment = async () => {
      if (!newComment.value.trim()) {
        alert("댓글을 입력하세요.");
        return;
      }

      const success = await boardStore.writeComment(route.params.postId, newComment.value);
      if (success) {
        newComment.value = "";
        boardStore.fetchComments(route.params.postId);
      }
    };

// ✅ 게시글 좋아요 함수 (UI 즉시 반영 + API 동기화)
const likePost = async (postId) => {
  const success = await likeStore.toggleLikePost(postId);
  if (success) {
    // ✅ UI 즉시 반영 (서버 응답 기다리지 않음)
    post.value.like_count += success.liked ? 1 : -1;

    // ✅ 서버 데이터 동기화 (백엔드에서 변경된 데이터 적용)
    setTimeout(() => boardStore.fetchPostDetail(postId), 500); // 약간의 딜레이 후 동기화
  }
};

    // ✅ 댓글 좋아요 함수 (토글 방식)
    const likeComment = async (commentId) => {
      const success = await likeStore.toggleLikeComment(commentId);
      if (success) {
        boardStore.fetchComments(route.params.postId);
      }
    };

    // ✅ 뒤로가기 함수
    const goBack = () => {
      router.push("/board");
    };

    return {
      post,
      comments,
      loading,
      newComment,
      formatDate,
      submitComment,
      likePost,
      likeComment,
      goBack,
    };
  },
};
</script>
