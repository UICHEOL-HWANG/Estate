<template>
    <div class="max-w-screen-md mx-auto p-6 mt-16 bg-white rounded-lg shadow-md">
      <!-- 🔹 제목 -->
      <h2 class="text-2xl font-bold text-gray-800 mb-6 text-center">📝 게시물 작성</h2>
  
      <form @submit.prevent="submitPost">
        <!-- 🔹 제목 입력 -->
        <div class="mb-4">
          <label class="block text-gray-700 font-semibold">제목</label>
          <input
            type="text"
            v-model="title"
            class="w-full px-4 py-2 mt-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="게시물 제목을 입력하세요"
            required
          />
        </div>
  
        <!-- 🔹 내용 입력 -->
        <div class="mb-4">
          <label class="block text-gray-700 font-semibold">내용</label>
          <textarea
            v-model="content"
            class="w-full px-4 py-2 mt-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 h-40 resize-none"
            placeholder="게시물 내용을 입력하세요"
            required
          ></textarea>
        </div>
  
        <!-- 🔹 버튼 (작성 / 취소) -->
        <div class="flex justify-end space-x-4">
          <button
            type="button"
            @click="cancelPost"
            class="px-4 py-2 text-gray-600 border rounded-lg hover:bg-gray-200 transition"
          >
            취소
          </button>
          <button
            type="submit"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg shadow-md hover:bg-blue-600 transition"
            :disabled="loading"
          >
            {{ loading ? "작성 중..." : "작성 완료" }}
          </button>
        </div>
      </form>
    </div>
  </template>
  
  <script>
  import { ref } from "vue";
  import { useRouter } from "vue-router";
  import { useBoardStore } from "../store/board"; // ✅ 게시판 스토어 사용
  
  export default {
    setup() {
      const title = ref("");
      const content = ref("");
      const router = useRouter();
      const boardStore = useBoardStore();
      const loading = ref(false); // ✅ 로딩 상태
  
      // ✅ 게시물 작성 API 호출
      const submitPost = async () => {
        if (!title.value || !content.value) {
          alert("제목과 내용을 입력해주세요.");
          return;
        }
  
        loading.value = true;
        const success = await boardStore.writePost(title.value, content.value);
        loading.value = false;
  
        if (success) {
          router.push("/board"); // ✅ 게시판으로 이동
        }
      };
  
      // ✅ 취소 버튼 클릭 → 게시판으로 이동
      const cancelPost = () => {
        router.push("/board");
      };
  
      return {
        title,
        content,
        loading,
        submitPost,
        cancelPost,
      };
    },
  };
  </script>
  