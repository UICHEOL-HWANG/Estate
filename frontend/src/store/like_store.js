import { defineStore } from "pinia";
import likeApi from "../util/like_axios"; // ✅ 좋아요 API 연결
import { useAuthStore } from "./auth"; // ✅ 인증 스토어 사용

export const useLikeStore = defineStore("like", {
  state: () => ({}),

  actions: {
    // ✅ 게시글 좋아요 토글
    async toggleLikePost(postId) {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        alert("로그인이 필요합니다.");
        return false;
      }

      try {
        const token = authStore.accessToken;
        const response = await likeApi.post(`/board_like/post/${postId}/toggle/`, {}, {
          headers: { Authorization: `${token}` }
        });

        console.log("✅ 게시글 좋아요 토글 성공:", response.data);
        return true;
      } catch (error) {
        console.error("🚨 게시글 좋아요 실패:", error.response?.data || error.message);
        return false;
      }
    },

    // ✅ 댓글 좋아요 토글 (NEW)
    async toggleLikeComment(commentId) {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        alert("로그인이 필요합니다.");
        return false;
      }

      try {
        const token = authStore.accessToken;
        const response = await likeApi.post(`/comment_like/comment/${commentId}/`, {}, {
          headers: { Authorization: `${token}` }
        });

        console.log("✅ 댓글 좋아요 토글 성공:", response.data);
        return true;
      } catch (error) {
        console.error("🚨 댓글 좋아요 실패:", error.response?.data || error.message);
        return false;
      }
    },
  },
});
