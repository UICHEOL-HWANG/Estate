<template>
  <div class="font-pretendard text-gray-900">

    
    <!-- 🔹 회원가입 페이지(/signup)에서는 메인 콘텐츠 숨기기 -->
    <div v-if="$route.path !== '/signup'">
      <Navbar />
      <MainVisual />
      <MainContent />
    </div>

    <!-- 🔹 회원가입 페이지는 라우터에서 관리 -->
    <router-view />
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
