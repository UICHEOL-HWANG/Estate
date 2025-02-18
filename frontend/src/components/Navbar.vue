<template>
  <nav class="bg-white shadow-md fixed top-0 left-0 w-full z-50">
    <div class="container mx-auto flex justify-between items-center p-4">
      <!-- 로고 -->
      <div class="text-2xl font-bold text-blue-600">
        <router-link to="/"><img src="../assets/logo.png" alt=""></router-link>
      </div>

      <!-- 네비게이션 메뉴 -->
      <div class="hidden md:flex space-x-6 text-gray-700">
        <router-link to="/board" class="hover:text-blue-500">게시판</router-link>
        <router-link to="/predict" class="hover:text-blue-500">내 매물가격 예측하기</router-link>
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
      <router-link to="/predict" class="block py-2 hover:text-blue-500">내 매물가격 예측하기</router-link>
      <button @click="openSignup" class="w-full px-4 py-2 text-blue-600 border border-blue-600 rounded-lg mt-4 hover:bg-blue-600 hover:text-white transition">
        회원가입/로그인
      </button>
    </div>

    <!-- 로그인 모달 -->
    <SignupModal :is-open="isSignupOpen" @close="isSignupOpen = false" />
  </nav>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, watch, nextTick, computed } from "vue";
import tippy from "tippy.js";
import "tippy.js/dist/tippy.css";
import { useAuthStore } from "../store/auth";
import SignupModal from "./SignupModal.vue";

export default {
  components: { SignupModal },
  setup() {
    const authStore = useAuthStore();
    const isSignupOpen = ref(false);
    const isOpen = ref(false);
    const isDesktop = ref(window.innerWidth >= 768);
    const profileRef = ref(null);
    const defaultProfileImage = "http://localhost:8000/media/default_profile_pic.jpg"; // ✅ 기본 프로필 이미지

    const toggleMenu = () => {
      isOpen.value = !isOpen.value;
    };

    const openSignup = () => {
      console.log("모달 열림");
      isSignupOpen.value = true;
    };

    const handleResize = () => {
      isDesktop.value = window.innerWidth >= 768;
    };

    const logout = async () => {
      await authStore.logout();
      console.log("✅ 로그아웃 완료");

      if (window.tippyInstance) {
        window.tippyInstance.hide();
      }
    };

    // ✅ 드롭다운 메뉴 생성 함수 (오류 해결을 위해 `setup()` 내부에 포함)
    const createDropdownMenu = () => {
      const container = document.createElement("div");
      container.classList.add("p-4", "bg-white", "shadow-md", "rounded-lg", "text-center");

      const profileLink = document.createElement("a");
      profileLink.href = "/profile"; // ✅ 내 프로필 페이지 링크 수정
      profileLink.classList.add("block", "py-2", "text-gray-700", "hover:text-blue-500");
      profileLink.innerText = "내 프로필";

      const logoutBtn = document.createElement("button");
      logoutBtn.classList.add(
        "w-full",
        "mt-2",
        "px-4",
        "py-2",
        "text-red-600",
        "border",
        "border-red-600",
        "rounded-lg",
        "hover:bg-red-600",
        "hover:text-white",
        "transition"
      );
      logoutBtn.innerText = "로그아웃";

      // ✅ 로그아웃 클릭 시 드롭다운 닫기
      logoutBtn.addEventListener("click", () => {
        logout();
        if (window.tippyInstance) {
          window.tippyInstance.hide();
        }
      });

      container.appendChild(profileLink);
      container.appendChild(logoutBtn);

      return container;
    };

    const setupTippy = async () => {
      await nextTick();

      if (profileRef.value) {
        tippy(profileRef.value, {
          content: createDropdownMenu(),
          allowHTML: true,
          interactive: true,
          placement: "bottom",
          trigger: "click",
          theme: "custom",
          onShow(instance) {
            window.tippyInstance = instance;
          },
        });
      }
    };

    onMounted(() => {
      window.addEventListener("resize", handleResize);

      if (authStore.isAuthenticated) {
        console.log("🔍 로그인 상태 확인됨, 사용자 정보 불러오기...");
        authStore.loadUser();
        setupTippy();
      }
    });

    onBeforeUnmount(() => {
      window.removeEventListener("resize", handleResize);
    });

    watch(
      () => authStore.isAuthenticated,
      (newVal) => {
        if (newVal) {
          console.log("✅ 로그인됨 - Tippy.js 다시 적용");
          setupTippy();
        }
      }
    );

    return {
      authStore,
      isSignupOpen,
      isOpen,
      isDesktop,
      toggleMenu,
      openSignup,
      logout,
      profileRef,
      defaultProfileImage,
      createDropdownMenu, // ✅ `setup()`에서 반환하여 참조 가능하도록 설정
    };
  },
};
</script>>

<style>
/* ✅ Tippy.js의 'light' 테마를 커스텀으로 변경 */
/* ✅ Tippy.js 드롭다운 스타일 */
.tippy-box[data-theme="custom"] {
    background-color: white !important;  /* 🔹 배경 흰색 */
    color: black !important;  /* 🔹 텍스트 색상 검은색 */
    box-shadow: none !important;  /* 🔹 그림자 제거 */
    border: 1px solid #ddd !important;  /* 🔹 테두리 추가 */
    border-radius: 8px !important;  /* 🔹 둥근 모서리 */
}

/* ✅ Tippy.js 화살표 색상 변경 */
.tippy-box[data-theme="custom"] .tippy-arrow {
    color: white !important; /* 🔹 화살표를 흰색으로 변경 */
}

/* ✅ Tippy.js의 아래쪽 화살표 배경색 변경 */
.tippy-box[data-theme="custom"][data-placement^="bottom"] .tippy-arrow::before {
    border-bottom-color: white !important;
}

/* ✅ Tippy.js의 위쪽 화살표 배경색 변경 */
.tippy-box[data-theme="custom"][data-placement^="top"] .tippy-arrow::before {
    border-top-color: white !important;
}

/* ✅ Tippy.js의 왼쪽 화살표 배경색 변경 */
.tippy-box[data-theme="custom"][data-placement^="left"] .tippy-arrow::before {
    border-left-color: white !important;
}

/* ✅ Tippy.js의 오른쪽 화살표 배경색 변경 */
.tippy-box[data-theme="custom"][data-placement^="right"] .tippy-arrow::before {
    border-right-color: white !important;
}

/* Tippy.js 기본 padding 제거 */
.tippy-content {
    padding: 0 !important; /* ✅ padding 제거 */
}


</style>