<template>
    <div class="min-h-screen flex flex-col items-center justify-center bg-gray-100">
      <!-- 로고 -->
      <img src="../assets/logo.png" alt="부동산플래닛 로고" class="h-12 mb-4" />
  
      <div class="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        <h2 class="text-2xl font-bold text-center text-gray-800 mb-6">개인회원 가입을 환영합니다!</h2>
  
        <!-- 🔹 소셜 로그인 버튼 -->
        <div class="space-y-3">
          <button class="w-full bg-yellow-400 text-black font-bold py-3 rounded-md flex items-center justify-center">
            <span class="mr-2">💬</span> 카카오로 가입
          </button>
          <button class="w-full bg-green-500 text-white font-bold py-3 rounded-md flex items-center justify-center">
            <span class="mr-2">N</span> 네이버로 가입
          </button>
          <button class="w-full bg-blue-600 text-white font-bold py-3 rounded-md flex items-center justify-center">
            <span class="mr-2">F</span> 페이스북으로 가입
          </button>
          <button class="w-full bg-gray-500 text-white font-bold py-3 rounded-md flex items-center justify-center">
            <span class="mr-2">✉️</span> 이메일로 가입
          </button>
        </div>
  
        <!-- 🔹 구분선 -->
        <div class="flex items-center my-6">
          <div class="flex-grow border-t border-gray-300"></div>
          <span class="px-3 text-gray-500 text-sm">또는</span>
          <div class="flex-grow border-t border-gray-300"></div>
        </div>
  
        <!-- 🔹 일반 회원가입 폼 -->
        <form @submit.prevent="handleSignup">
          <label class="block text-sm font-medium text-gray-700">아이디*</label>
          <input 
            v-model="username"
            type="text"
            placeholder="아이디를 입력하세요"
            class="w-full p-2 mt-1 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            required
          />
   
          <label class="block text-sm font-medium text-gray-700 mt-4">비밀번호*</label>
          <input 
            v-model="password"
            type="password"
            placeholder="비밀번호를 입력해주세요."
            class="w-full p-2 mt-1 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            required
            autocomplete="new-password"
          />
  
          <label class="block text-sm font-medium text-gray-700 mt-4">비밀번호 확인*</label>
          <input 
            v-model="confirmPassword"
            type="password"
            placeholder="비밀번호를 다시 입력해주세요."
            class="w-full p-2 mt-1 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            required
            autocomplete="new-password"
          />
  
          <p v-if="errorMessage" class="text-red-500 text-sm mt-2">{{ errorMessage }}</p>
  
          <!-- 🔹 회원가입 버튼 -->
          <button type="submit" class="w-full bg-blue-600 text-white font-bold py-3 rounded-md mt-4 hover:bg-blue-700 transition">
            회원가입
          </button>
        </form>
  
        <!-- 🔹 로그인 페이지 이동 -->
        <div class="text-center text-sm text-gray-600 mt-4">
          이미 계정이 있으신가요?
          <router-link to="/" class="text-blue-600 font-bold">로그인하기</router-link>
        </div>
      </div>

      <div v-if="showModal" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white p-6 rounded-lg shadow-lg max-w-sm">
        <h3 class="text-xl font-bold text-gray-800">회원가입 완료</h3>
        <p class="text-gray-600 mt-2">회원가입이 성공적으로 완료되었습니다!</p>
        <button @click="closeModal" class="w-full bg-blue-600 text-white font-bold py-2 rounded-md mt-4 hover:bg-blue-700 transition">
          로그인 페이지로 이동
        </button>
      </div>
    </div>
    </div>
  </template>
  
  <script>
  import { ref } from "vue";
  import { useAuthStore } from "../store/auth";
  import { useRouter } from "vue-router";
  
  export default {
    setup() {
      const authStore = useAuthStore();
      const router = useRouter();
      
      const username = ref("");
      const password = ref("");
      const confirmPassword = ref("");
      const errorMessage = ref("");
      const showModal = ref(false); // ✅ 모달 상태 추가 (오류 수정)
  
      const handleSignup = async () => {
        if (password.value !== confirmPassword.value) {
          errorMessage.value = "비밀번호가 일치하지 않습니다.";
          return;
        }
  
        try {
          const response = await authStore.signup({
            username: username.value,
            password: password.value,
          });
  
          if (response.success) {
            showModal.value = true; // ✅ 회원가입 완료 후 모달 표시
          } else {
            errorMessage.value = response.message || "회원가입 실패";
          }
        } catch (error) {
          errorMessage.value = "서버 오류가 발생했습니다. 다시 시도해주세요.";
        }
      };
  
      const closeModal = () => {
        showModal.value = false;
        router.push("/login"); // ✅ 로그인 페이지로 이동
      };
  
      return {
        username,
        password,
        confirmPassword,
        errorMessage,
        showModal, // ✅ 반환 객체에 `showModal` 추가 (오류 수정)
        handleSignup,
        closeModal,
      };
    },
  };
  </script>