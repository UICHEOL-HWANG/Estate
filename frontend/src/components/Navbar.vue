<template>
  <nav class="bg-white shadow-md fixed top-0 left-0 w-full z-50">
    <div class="container mx-auto flex justify-between items-center p-4">
      <!-- 로고 -->
      <div class="text-2xl font-bold text-blue-600">
        <router-link to="/"><img src="../assets/logo.png" alt="로고"></router-link>
      </div>

      <!-- 네비게이션 메뉴 -->
      <div class="hidden md:flex space-x-6 text-gray-700">
        <router-link to="/board" class="hover:text-blue-500">게시판</router-link>
        <router-link to="/predict" class="hover:text-blue-500">내 매물 가격 예측하기</router-link>
      </div>

      <!-- 프로필 사진 및 드롭다운 -->
      <div class="hidden md:flex space-x-4 items-center">
        <template v-if="authStore.isAuthenticated">
          <div ref="profileRef" class="relative cursor-pointer flex items-center">
            <!-- 프로필 사진 -->
            <img
              :src="authStore.user?.profile_pic || defaultProfileImage"
              alt="프로필 사진"
              class="w-10 h-10 rounded-full border border-gray-300"
            />
          </div>
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
      <router-link to="/board" class="block py-2 hover:text-blue-500">게시판</router-link>
      <router-link to="/predict" class="block py-2 hover:text-blue-500">내 매물 가격 예측하기</router-link>
      <button @click="openSignup" class="w-full px-4 py-2 text-blue-600 border border-blue-600 rounded-lg mt-4 hover:bg-blue-600 hover:text-white transition">
        회원가입/로그인
      </button>
    </div>

    <!-- 로그인 모달 -->
    <SignupModal :is-open="isSignupOpen" @close="isSignupOpen = false" />
  </nav>
</template>

<script>
import { ref } from "vue";
import { useAuthStore } from "../store/auth";
import SignupModal from "./SignupModal.vue";

export default {
  components: { SignupModal },
  setup() {
    const authStore = useAuthStore();
    const isSignupOpen = ref(false);
    const isOpen = ref(false);
    const defaultProfileImage = "http://localhost:8000/media/default_profile_pic.jpg"; // ✅ 기본 프로필 이미지

    const toggleMenu = () => {
      isOpen.value = !isOpen.value;
    };

    const openSignup = () => {
      isSignupOpen.value = true;
    };

    return {
      authStore,
      isSignupOpen,
      isOpen,
      toggleMenu,
      openSignup,
      defaultProfileImage,
    };
  },
};
</script>
