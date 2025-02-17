import { defineStore } from "pinia";
import boardApi from "../util/board_axios"; // ✅ 게시판 API 불러오기
import { useAuthStore } from "./auth"; // ✅ 인증 스토어 불러오기

export const useBoardStore = defineStore("board", {
  state: () => ({
    posts: [],
    postDetail: null, // ✅ 게시글 상세 데이터 저장
    comments: [], // ✅ 댓글 목록 저장
    loading: false,
  }),

  actions: {
    // ✅ 모든 게시글 불러오기
    async fetchPosts() {
      this.loading = true;
      try {
        const response = await boardApi.get("/board/all/");
        this.posts = response.data.map(post => ({
          id: post.id,
          title: post.title,
          author: post.author_name,
          created_at: post.created_at,
          likes: post.like_count,
          comments: post.comment_count,
        }));
        console.log("✅ 게시글 불러오기 성공:", this.posts);
      } catch (error) {
        console.error("🚨 게시글 불러오기 실패:", error);
      } finally {
        this.loading = false;
      }
    },

    // ✅ 특정 게시글 상세 조회
    async fetchPostDetail(postId) {
      this.loading = true;
      try {
        const authStore = useAuthStore();
        const token = authStore.accessToken;

        const response = await boardApi.get(`/board/${postId}`, {
          headers: { Authorization: `${token}` },
        });

        this.postDetail = response.data;
        console.log("✅ 게시글 상세 조회 성공:", this.postDetail);
      } catch (error) {
        console.error("🚨 게시글 상세 조회 실패:", error);
      } finally {
        this.loading = false;
      }
    },

    // ✅ 댓글 목록 불러오기
    async fetchComments(postId) {
      this.loading = true;
      try {
        const response = await boardApi.get(`/comment/${postId}/`);
        this.comments = response.data.map(comment => ({
          id: comment.id,
          author: comment.author_name,
          content: comment.content,
          created_at: comment.created_at,
        }));
        console.log("✅ 댓글 불러오기 성공:", this.comments);
      } catch (error) {
        console.error("🚨 댓글 불러오기 실패:", error);
      } finally {
        this.loading = false;
      }
    },

    // ✅ 게시글 작성
    async writePost(title, content) {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        alert("로그인이 필요합니다.");
        return false;
      }

      try {
        this.loading = true;
        const token = authStore.accessToken;

        const response = await boardApi.post(
          "/board/",
          { title, content },
          { headers: { Authorization: `${token}` } }
        );

        console.log("✅ 게시글 작성 성공:", response.data);
        alert("게시글이 성공적으로 작성되었습니다.");

        // ✅ 새 게시글을 store에 추가
        this.posts.unshift({
          id: response.data.post.id,
          title: response.data.post.title,
          author: response.data.post.author,
          created_at: response.data.post.created_at,
          likes: 0,
          comments: 0,
        });

        return true;
      } catch (error) {
        console.error("🚨 게시글 작성 실패:", error);
        alert("게시글 작성에 실패했습니다.");
        return false;
      } finally {
        this.loading = false;
      }
    },

    // ✅ 댓글 작성
    async writeComment(postId, content) {
      const authStore = useAuthStore();
      if (!authStore.isAuthenticated) {
        alert("로그인이 필요합니다.");
        return false;
      }

      try {
        this.loading = true;
        const token = authStore.accessToken;

        const response = await boardApi.post(
          `/comment/${postId}/`,
          { content },
          { headers: { Authorization: `${token}` } }
        );

        console.log("✅ 댓글 작성 성공:", response.data);

        // ✅ 새 댓글을 store에 추가
        this.comments.unshift({
          id: response.data.comment.id,
          author: authStore.user.username,
          content: content,
          created_at: new Date().toISOString(),
        });

        return true;
      } catch (error) {
        console.error("🚨 댓글 작성 실패:", error);
        alert("댓글 작성에 실패했습니다.");
        return false;
      } finally {
        this.loading = false;
      }
    },
  },
});
