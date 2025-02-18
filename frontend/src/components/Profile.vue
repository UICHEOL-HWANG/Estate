<template>
    <div class="max-w-3xl mx-auto p-6">
      <div v-if="user">
        <!-- ✅ 프로필 정보 박스 -->
        <div class="bg-white shadow-md rounded-lg p-6 flex items-center justify-between">
          <!-- 프로필 이미지 및 정보 -->
          <div class="flex items-center space-x-6">
            <img
              :src="user.profile_pic ? `${user.profile_pic}` : '/media/default_profile_pic.jpg'"
              alt="프로필 이미지"
              class="w-24 h-24 rounded-full border border-gray-300"
            />
            <div>
              <h2 class="text-2xl font-bold">{{ user.username }}</h2>
              <p class="text-gray-500 text-sm">ID: {{ user.id }}</p>
              <p v-if="user.intro" class="mt-2">{{ user.intro }}</p>
              <p v-else class="mt-2 text-gray-400">자기소개가 없습니다</p>
            </div>
          </div>
  
          <!-- ✅ 프로필 수정 버튼 -->
          <button @click="openProfileEditModal" class="text-blue-500 hover:text-blue-700 flex items-center space-x-1">
            <span>수정</span>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15.232 5.232l3.536 3.536M9 12l6.232-6.232a2 2 0 012.828 0l2.828 2.828a2 2 0 010 2.828L12 18l-6 1.5L9 12z" />
            </svg>
          </button>
        </div>
  
        <!-- ✅ 내가 작성한 댓글 -->
        <div class="mt-8">
          <h3 class="text-xl font-bold mb-4 text-center">📌 내가 작성한 댓글</h3>
          <div v-if="comments.length > 0">
            <div v-for="comment in comments" :key="comment.id" class="bg-gray-100 p-4 rounded-lg mb-4">
              <p class="text-gray-700">{{ comment.content }}</p>
              <p class="text-gray-500 text-sm mt-1">📅 {{ comment.created_at }}</p>
            </div>
          </div>
          <div v-else>
            <p class="text-gray-500 text-center">작성한 댓글이 없습니다.</p>
          </div>
        </div>
      </div>
  
      <!-- ✅ 프로필 수정 모달 -->
      <div v-if="isProfileEditModalOpen" class="fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center">
        <div class="bg-white p-6 rounded-lg shadow-lg w-96">
          <h3 class="text-lg font-bold mb-4">프로필 수정</h3>
  
          <label class="block text-sm font-medium text-gray-700">닉네임</label>
          <input v-model="editedUsername" type="text"
            class="w-full p-2 border rounded-md mb-3" placeholder="닉네임 입력" />
  
          <label class="block text-sm font-medium text-gray-700">자기소개</label>
          <textarea v-model="editedIntro" class="w-full p-2 border rounded-md" rows="3" placeholder="자기소개 입력"></textarea>
  
          <div class="flex justify-end space-x-2 mt-4">
            <button @click="closeProfileEditModal" class="px-4 py-2 text-gray-500 hover:text-gray-700">
              취소
            </button>
            <button @click="updateProfile"
              class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600">
              저장
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import { useAuthStore } from "../store/auth";
  
  export default {
    setup() {
      const authStore = useAuthStore();
      const user = ref(authStore.user);
      const comments = ref(authStore.comments);
  
      // ✅ 프로필 수정 모달 상태
      const isProfileEditModalOpen = ref(false);
      const editedUsername = ref("");
      const editedPassword = ref("");  // ✅ 비밀번호 추가
      const editedIntro = ref("");
  
      // ✅ 모달 열기 (기존 값 로드)
      const openProfileEditModal = () => {
        editedUsername.value = user.value?.username || "";
        editedIntro.value = user.value?.intro || "";
        editedPassword.value = "";  // ✅ 비밀번호는 공백으로 초기화
        isProfileEditModalOpen.value = true;
      };
  
      // ✅ 모달 닫기
      const closeProfileEditModal = () => {
        isProfileEditModalOpen.value = false;
      };
  
      // ✅ 프로필 업데이트 요청
      const updateProfile = async () => {
        const updatedData = {
          username: editedUsername.value,
          password: editedPassword.value || null,  // ✅ 비밀번호 입력이 없으면 null 처리
          intro: editedIntro.value
        };
  
        const result = await authStore.updateProfile(updatedData);
  
        if (result.success) {
          user.value.username = updatedData.username;
          user.value.intro = updatedData.intro;
          closeProfileEditModal();
        } else {
          alert(result.message);
        }
      };
  
      onMounted(async () => {
        await authStore.loadUser();
  
        if (!authStore.user) {
          alert("로그인이 필요한 페이지입니다.");
          window.location.href = "/";
        }
  
        user.value = authStore.user;
        comments.value = authStore.comments;
      });
  
      return {
        user,
        comments,
        isProfileEditModalOpen,
        editedUsername,
        editedPassword,  // ✅ 비밀번호 필드 추가
        editedIntro,
        openProfileEditModal,
        closeProfileEditModal,
        updateProfile
      };
    }
  };
  </script>
  