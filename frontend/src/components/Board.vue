<template>
    <div class="max-w-screen-lg mx-auto p-4 mt-16">
      <!-- 🔹 게시판 소개 블록 -->
      <div class="bg-gray-100 p-6 rounded-lg shadow-md text-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">📢 자유 게시판</h2>
        <p class="text-gray-600 mt-2">다양한 주제로 자유롭게 이야기할 수 있는 공간입니다.</p>
      </div>
  
      <!-- 🔹 "글 작성" 버튼 -->
      <div class="flex justify-end mt-4 mb-8">  <!-- ✅ 여백 추가 -->
        <button
          @click="handleWriteClick"
          class="bg-blue-500 text-white px-4 py-2 rounded-lg shadow-md hover:bg-blue-600 transition w-full md:w-auto"
        >
          글 작성
        </button>
      </div>

      <!-- 🔹 로그인 모달 -->
      <SignupModal :is-open="isSignupOpen" @close="isSignupOpen = false" />
  
      <!-- 🔹 로딩 상태 -->
      <div v-if="loading" class="text-center py-10">
        <p class="text-lg font-semibold text-gray-500">⏳ 게시글을 불러오는 중...</p>
      </div>
  
      <!-- 🔹 게시판 목록 -->
      <div v-if="paginatedPosts.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="post in paginatedPosts" :key="post.id" 
        @click="goToDetail(post.id)"
        class="bg-white p-8 rounded-lg shadow-md border">
          <h2 class="text-lg font-bold text-gray-900 hover:text-blue-600 cursor-pointer">
            {{ post.title }}
          </h2>
          <div class="text-gray-500 text-sm mt-2">
            <span>작성자: {{ post.author }}</span>
          </div>
          <div class="flex justify-between items-center mt-3 text-gray-500 text-xs">
            <div class="flex space-x-4">
              <span class="flex items-center">👍 {{ post.likes }}</span>
              <span class="flex items-center">💬 {{ post.comments }}</span>
            </div>
            <span class="text-gray-400">{{ formatDate(post.created_at) }}</span>
          </div>
        </div>
      </div>
  
      <!-- 🔹 게시물이 없을 경우 -->
      <div v-else-if="!loading" class="text-center text-gray-500 py-10">
        <p class="text-lg font-semibold">아직 게시물이 없습니다.</p>
        <p class="text-sm">첫 번째 게시글을 작성해보세요!</p>
      </div>
  
      <!-- 🔹 페이지네이션 -->
      <div v-if="posts.length > 0" class="flex justify-center mt-6 space-x-4">
        <button 
          @click="prevPage"
          :disabled="currentPage === 1"
          class="px-4 py-2 border rounded-lg text-gray-600 bg-white shadow-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          이전
        </button>
  
        <span class="px-4 py-2 border rounded-lg bg-blue-500 text-white shadow-md">
          {{ currentPage }} / {{ totalPages }}
        </span>
  
        <button 
          @click="nextPage"
          :disabled="currentPage === totalPages"
          class="px-4 py-2 border rounded-lg text-gray-600 bg-white shadow-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          다음
        </button>
      </div>
    </div>
</template>

<script>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";  // ✅ 인증 스토어 가져오기
import boardApi from "../util/board_axios"; // ✅ 게시판 API 불러오기
import SignupModal from "../components/SignupModal.vue";

export default {
  components: { SignupModal },
  setup() {
    const posts = ref([]);
    const loading = ref(true);
    const currentPage = ref(1);
    const postsPerPage = 6;
    const router = useRouter();
    const authStore = useAuthStore(); // ✅ 인증 상태 가져오기
    const isSignupOpen = ref(false); // ✅ 로그인 모달 상태

    // ✅ 게시물 데이터 불러오기
    const fetchPosts = async () => {
      loading.value = true;
      try {
        const response = await boardApi.get("/board/all/");
        // ✅ API 데이터 매핑
        posts.value = response.data.map(post => ({
          id: post.id,
          title: post.title,
          author: post.author ? `ID : ${post.author}` : "Unknown", // ✅ 작성자 정보 추가
          created_at: post.created_at,
          likes: post.like_count, // ✅ 좋아요 수 매핑
          comments: post.comment_count, // ✅ 댓글 수 매핑
        }));
        console.log("✅ 게시글 불러오기 성공:", posts.value);
      } catch (error) {
        console.error("🚨 게시글 불러오기 실패:", error);
      } finally {
        loading.value = false;
      }
    };

    // ✅ 날짜 포맷 함수 추가
    const formatDate = (dateString) => {
      if (!dateString) return "날짜 없음"; // ✅ Null 처리
      const date = new Date(dateString);
      return date.toLocaleDateString("ko-KR", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      });
    };

    // ✅ 페이지네이션 계산
    const totalPages = computed(() => Math.ceil(posts.value.length / postsPerPage));

    const paginatedPosts = computed(() => {
      const start = (currentPage.value - 1) * postsPerPage;
      const end = start + postsPerPage;
      return posts.value.slice(start, end);
    });

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++;
      }
    };

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
      }
    };

    const handleWriteClick = () => {
      if (!authStore.isAuthenticated) {
        alert("로그인 후 작성해주세요."); // ✅ Alert 메시지
        isSignupOpen.value = true; // ✅ 로그인 모달 열기
      } else {
        router.push("/write"); // ✅ 로그인된 경우 글 작성 페이지 이동
      }
    };
        // ✅ 게시글 클릭 시 상세 페이지로 이동
    const goToDetail = (postId) => {
      router.push(`/board/${postId}`);
    };


    // ✅ 페이지 로드 시 게시물 데이터 불러오기
    onMounted(fetchPosts);

    return {
      posts,
      loading,
      currentPage,
      totalPages,
      paginatedPosts,
      formatDate,
      nextPage,
      prevPage,
      handleWriteClick,
      isSignupOpen, // ✅ 로그인 모달 상태
      goToDetail
    };
  },
};
</script>
