<template>
    <div class="relative w-full h-screen md:h-[400px] bg-gradient-to-r from-indigo-900 to-black text-white flex flex-col justify-center items-center px-4">
      <!-- 배경 이미지 추가 -->
      <div class="absolute inset-0 bg-[url('/src/assets/main.jpg')] bg-no-repeat bg-cover bg-center opacity-40"></div>
  
      <!-- 텍스트 컨테이너 -->
      <div class="relative z-10 text-center">
        <h1 class="text-3xl md:text-4xl font-bold mb-3">부동산의 모든 것을 담다</h1>
        <h2 class="text-lg md:text-xl text-gray-200">마이홈 픽!</h2>
      </div>
  
      <!-- 🔹 반응형 검색 바 -->
      <div class="relative z-10 flex items-center bg-white rounded-full shadow-lg w-full max-w-[700px] md:w-[80%] lg:w-[60%] h-14 px-4 mt-6">
        <select class="bg-transparent text-gray-700 font-medium outline-none">
          <option value="real_price">실거래가</option>
          <option value="sale">매물</option>
        </select>
        <input
          type="text"
          placeholder="지역, 지하철, 건물명, 학교명으로 검색해 보세요."
          class="w-full text-gray-900 outline-none px-3"
        />
        <button class="absolute right-1 top-1/2 transform -translate-y-1/2 w-[111px] h-[46px] bg-blue-600 text-white font-bold text-lg leading-6 tracking-tight rounded-full transition-all duration-100 hover:bg-blue-700">
        검색
      </button>
      </div>
    </div>
  </template>
  