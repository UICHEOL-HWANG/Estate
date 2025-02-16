<template>
    <nav class="bg-white shadow-md fixed top-0 left-0 w-full z-50">
      <div class="container mx-auto flex justify-between items-center p-4">
        <!-- 로고 -->
        <div class="text-2xl font-bold text-blue-600">
          <span>부동산플래닛</span>
        </div>
  
        <!-- 네비게이션 메뉴 -->
        <div v-if="isOpen || isDesktop" class="hidden md:flex space-x-6 text-gray-700">
          <a href="#" class="hover:text-blue-500">게시판</a>
          <a href="#" class="hover:text-blue-500">내 매물가격 예측하기</a>
        </div>
  
        <!-- 로그인/회원가입 버튼 (로그인 상태에 따라 변경) -->
        <div class="hidden md:flex space-x-4 items-center">
          <template v-if="authStore.isAuthenticated">
            <span class="text-gray-700 font-bold">{{ authStore.user?.username }}</span>
            <button @click="logout" class="px-4 py-2 text-red-600 border border-red-600 rounded-lg hover:bg-red-600 hover:text-white transition">
              로그아웃
            </button>
          </template>
          <template v-else>
            <button @click="openSignup" class="px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-600 hover:text-white transition">
              회원가입/로그인
            </button>
          </template>
        </div>
  
        <!-- 모바일 메뉴 버튼 -->
        <div class="md:hidden">
          <button @click="toggleMenu" class="text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>
            </svg>
          </button>
        </div>
      </div>
  
      <!-- 모바일 메뉴 -->
      <div v-if="isOpen" class="md:hidden bg-white shadow-md p-4">
        <a href="#" class="block py-2 hover:text-blue-500">게시판</a>
        <a href="#" class="block py-2 hover:text-blue-500">내 매물가격 예측하기</a>
        <button @click="openSignup" class="w-full px-4 py-2 text-blue-600 border border-blue-600 rounded-lg mt-4 hover:bg-blue-600 hover:text-white transition">
          회원가입/로그인
        </button>
      </div>
  
      <!-- ✅ 로그인 모달 -->
      <SignupModal :is-open="isSignupOpen" @close="isSignupOpen = false" />
    </nav>
  </template>
  
  <script>
  import { ref, onMounted, onBeforeUnmount } from "vue";
  import { useAuthStore } from "../store/auth";
  import SignupModal from "./SignupModal.vue";
  
  export default {
    components: { SignupModal },
    setup() {
      const authStore = useAuthStore(); 
      const isSignupOpen = ref(false);
      const isOpen = ref(false);
      const isDesktop = ref(window.innerWidth >= 768);
  
      const toggleMenu = () => {
        isOpen.value = !isOpen.value;
      };
  
      const openSignup = () => {
        console.log("모달 열림"); // ✅ 디버깅용 로그 추가
        isSignupOpen.value = true;
      };
  
      const handleResize = () => {
        isDesktop.value = window.innerWidth >= 768;
      };
  
      const logout = async () => {
        await authStore.logout();
        console.log("✅ 로그아웃 완료");
      };
  
      onMounted(() => {
      window.addEventListener("resize", handleResize);

      // ✅ 로그인 상태인 경우에만 사용자 정보 불러오기
      if (authStore.isAuthenticated) {
        console.log("🔍 로그인 상태 확인됨, 사용자 정보 불러오기...");
        authStore.loadUser();
      } else {
        console.log("❌ 로그인되지 않음, loadUser() 실행 안 함");
      }
      });
  
      onBeforeUnmount(() => {
        window.removeEventListener("resize", handleResize);
      });
  
      return {
        authStore,
        isSignupOpen,
        isOpen,
        isDesktop,
        toggleMenu,
        openSignup,
        logout,
      };
    },
  };
  </script>
  