<template>
  <div v-if="isOpen" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
    <!-- 🔹 모달 컨테이너 -->
    <div class="bg-white w-full max-w-sm p-6 rounded-lg shadow-lg relative">
      
      <!-- 🔹 닫기 버튼 -->
      <button type="button" @click="closeModal" class="absolute top-4 right-4 text-gray-500 hover:text-gray-800">
        ✖
      </button>

      <!-- 🔹 로고 -->
      <div class="text-center mb-4">
        <img src="../assets/logo.png" alt="부동산플래닛 로고" class="h-10 mx-auto" />
      </div>

      <!-- 🔹 입력 폼 -->
      <form @submit.prevent="handleLogin">
        <label class="block text-sm font-medium text-gray-700">아아디*</label>
        <input 
          v-model="username"
          type="text"
          placeholder="아이디를 입력하세요"
          class="w-full p-2 mt-1 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          required
        />

        <label class="block text-sm font-medium text-gray-700 mt-3">비밀번호*</label>
        <input 
          v-model="password"
          type="password"
          placeholder="비밀번호를 입력해주세요."
          class="w-full p-2 mt-1 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          required
        />

        <p v-if="errorMessage" class="text-red-500 text-sm mt-2">{{ errorMessage }}</p>

        <div class="flex items-center mt-3">
          <input type="checkbox" v-model="rememberMe" class="mr-2">
          <span class="text-sm text-gray-600">아이디 저장</span>
        </div>

        <!-- 🔹 로그인 버튼 -->
        <button type="submit" class="w-full bg-blue-600 text-white font-bold py-2 rounded-md mt-4 hover:bg-blue-700 transition">
          로그인
        </button>
      </form>

      <!-- 🔹 비밀번호 찾기 -->
      <div class="text-center text-sm text-gray-500 mt-2">
        <a href="#" class="underline">이메일 · 비밀번호 찾기</a>
      </div>

      <!-- 🔹 소셜 로그인 -->
      <div class="flex justify-center space-x-4 mt-4">
        <button type="button" class="bg-green-500 w-10 h-10 rounded-full text-white flex items-center justify-center">N</button>
        <button type="button" class="bg-yellow-400 w-10 h-10 rounded-full text-white flex items-center justify-center">K</button>
        <button type="button" class="bg-blue-600 w-10 h-10 rounded-full text-white flex items-center justify-center">F</button>
      </div>

      <!-- 🔹 회원가입 -->
      <div class="text-center text-sm text-gray-600 mt-4">
        회원이 아니신가요?
        <router-link to="/signup" class="text-blue-600 font-bold">회원가입하기</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from "../store/auth";

export default {
  props: {
    isOpen: Boolean,
  },
  data() {
    return {
      username: "",
      password: "",
      rememberMe: false,
      errorMessage: "",
    };
  },
  methods: {
    closeModal() {
      console.log("모달 닫기 버튼 클릭됨"); // 🔍 디버깅용 로그 추가
      this.errorMessage = "";
      this.$emit("close");
      
    },
    async handleLogin(){
      try{
        const authStore = useAuthStore();

        const response = await authStore.login({
          "username" : this.username, 
          "password": this.password});

        if (response.success){
        this.closeModal();
        this.$emit("login-success"); // ✅ 부모 컴포넌트(Navbar)로 이벤트 전달
        }else{
          this.errorMessage = "아이디 또는 비밀번호가 올바르지 않습니다."; // ✅ 로그인 실패 메시지 표시
        }
      } catch (error){
        this.errorMessage = "서버 오류가 발생했습니다. 다시 시도해주세요.";      }
    }
  }
};
</script>
