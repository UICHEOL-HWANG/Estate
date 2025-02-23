<template>
    <div class="h-screen flex flex-col items-center justify-center bg-gray-100 pt-16"> 
      <div class="max-w-lg w-full bg-white shadow-md rounded-lg p-6">
        <h2 class="text-2xl font-bold text-blue-600 mb-4 text-center">
          원하는 건물의 집값을 예측해드립니다
        </h2>
  
        <!-- 입력 필드 -->
        <div class="space-y-4">
          <div>
            <label class="block text-gray-700 font-semibold">층</label>
            <input v-model="floor" type="number" class="w-full border p-2 rounded-lg" placeholder="예: 3">
          </div>
  
          <div>
            <label class="block text-gray-700 font-semibold">법정동 코드</label>
            <input v-model="districtCode" type="number" class="w-full border p-2 rounded-lg" placeholder="예: 110101">
          </div>
  
          <div>
            <label class="block text-gray-700 font-semibold">건축년도</label>
            <input v-model="yearBuilt" type="number" class="w-full border p-2 rounded-lg" placeholder="예: 2005">
          </div>
  
          <div>
            <label class="block text-gray-700 font-semibold">건물면적 (㎡)</label>
            <input v-model="area" type="number" class="w-full border p-2 rounded-lg" placeholder="예: 85.0">
          </div>
  
          <!-- 예측 버튼 -->
          <button 
            @click="predictPrice"
            class="w-full bg-blue-500 text-white font-semibold p-2 rounded-lg hover:bg-blue-600 transition">
            예측하기
          </button>
        </div>
  
        <!-- 예측 결과 -->
        <div v-if="predictedPrice !== null" class="mt-6 p-4 bg-gray-200 rounded-lg text-center">
          <h3 class="text-lg font-semibold text-gray-800">예측된 집값</h3>
          <p class="text-xl font-bold text-blue-600">{{ predictedPrice }}</p>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref } from "vue";
  
  export default {
    setup() {
      // ✅ 변수 정의
      const floor = ref("");
      const districtCode = ref("");
      const yearBuilt = ref("");
      const area = ref("");
      const predictedPrice = ref(null);
  
      // ✅ 예측 요청 함수 (더미 데이터 사용)
      const predictPrice = () => {
        if (!floor.value || !districtCode.value || !yearBuilt.value || !area.value) {
          alert("모든 필드를 입력해주세요.");
          return;
        }
  
        // 더미 데이터 (실제 API 연동 시 Axios 사용)
        predictedPrice.value = Math.floor(Math.random() * 10000) + "만원";
      };
  
      return {
        floor,
        districtCode,
        yearBuilt,
        area,
        predictedPrice,
        predictPrice,
      };
    },
  };
  </script>
  