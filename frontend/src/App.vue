<template>
  <div class="font-pretendard text-gray-900">
    <!-- 🔹 네비게이션 바 추가 -->
    <Navbar />

    <!-- 🔹 회원가입 페이지에서는 모든 컴포넌트 숨김 -->
    <div v-if="$route.path === '/signup'">
      <router-view />
    </div>

    <!-- 🔹 게시판 페이지(/board) 및 게시글 상세 페이지(/board/:postId) 중앙 정렬 -->
    <div v-else-if="$route.path.startsWith('/board')" class="flex flex-col items-center min-h-screen">
      <div class="max-w-6xl w-full mx-auto p-4 md:p-8">
        <router-view />
      </div>
    </div>

    <!-- 🔹 글 작성 페이지(/write) 중앙 정렬 -->
    <div v-else-if="$route.path === '/write'" class="flex justify-center items-center min-h-screen">
      <div class="max-w-screen-md w-full mx-auto p-6 md:p-12">
        <router-view />
      </div>
    </div>

    <!-- 🔹 프로필 페이지(/profile) 중앙 정렬 -->
    <div v-else-if="$route.path === '/profile'" class="flex justify-center items-center min-h-screen">
      <div class="max-w-screen-md w-full mx-auto p-6 md:p-12">
        <router-view />
      </div>
    </div>

    <!-- 🔹 예측 페이지(/predict) 중앙 정렬 -->
    <div v-else-if="$route.path === '/predict'" class="flex flex-col items-center min-h-screen bg-gray-100">
      <div class="max-w-screen-md w-full mx-auto p-6 md:p-12">
        <router-view />
      </div>
    </div>

    <!-- 🔹 기본 레이아웃 (홈, 기타 페이지) -->
    <div v-else>
      <MainVisual />
      <MainContent />
      <router-view />
    </div>
  </div>
</template>

<script>
import Navbar from "./components/Navbar.vue";
import MainVisual from "./components/MainVisual.vue";
import MainContent from "./components/MainContent.vue";

export default {
  components: {
    Navbar,
    MainVisual,
    MainContent,
  },
};
</script>
