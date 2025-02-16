<template>
    <div class="bg-gray-100 py-10">
      <div class="max-w-5xl mx-auto px-4">
        
        <!-- 🔹 상단 추천 서비스 섹션 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div class="bg-blue-100 rounded-xl p-5 flex items-center">
            <div class="text-left">
              <h3 class="text-lg font-bold">자산관리 비즈 정기구독 서비스</h3>
              <p class="text-sm text-gray-600">베타 서비스 기간 내 무료! 전적 실습 검사 무제한 제공!</p>
            </div>
          </div>
          <div class="bg-blue-200 rounded-xl p-5 flex items-center">
            <div class="text-left">
              <h3 class="text-lg font-bold">AI 추정가와 공시가격을 한번에</h3>
              <p class="text-sm text-gray-600">전국 아파트 및 빌라 동호수별로 확인해 보세요.</p>
            </div>
          </div>
        </div>
  
        <!-- 🔹 인기 서비스 아이콘 리스트 -->
        <div class="bg-white shadow-md rounded-xl p-6 mb-6">
          <h3 class="text-lg font-bold mb-4">인기 서비스</h3>
          <div class="grid grid-cols-3 md:grid-cols-6 gap-4 text-center">
            <div>
              <div class="w-12 h-12 mx-auto bg-yellow-200 rounded-full flex items-center justify-center">
                📊
              </div>
              <p class="text-sm mt-2">실거래가</p>
            </div>
            <div>
              <div class="w-12 h-12 mx-auto bg-blue-200 rounded-full flex items-center justify-center">
                🏠
              </div>
              <p class="text-sm mt-2">매물</p>
            </div>
            <div>
              <div class="w-12 h-12 mx-auto bg-green-200 rounded-full flex items-center justify-center">
                🔍
              </div>
              <p class="text-sm mt-2">탐색</p>
            </div>
            <div>
              <div class="w-12 h-12 mx-auto bg-indigo-200 rounded-full flex items-center justify-center">
                🏢
              </div>
              <p class="text-sm mt-2">자산관리</p>
            </div>
            <div>
              <div class="w-12 h-12 mx-auto bg-pink-200 rounded-full flex items-center justify-center">
                📈
              </div>
              <p class="text-sm mt-2">인사이트</p>
            </div>
            <div>
              <div class="w-12 h-12 mx-auto bg-gray-200 rounded-full flex items-center justify-center">
                🏢
              </div>
              <p class="text-sm mt-2">딜정보</p>
            </div>
          </div>
        </div>
  
        <!-- 🔹 딜정보 리스트 -->
        <div class="bg-white shadow-md rounded-xl p-6 mb-6">
          <h3 class="text-lg font-bold mb-4">딜정보</h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-gray-300 rounded-full"></div>
                <div>
                  <p class="text-sm font-medium">코람코자산</p>
                  <p class="text-xs text-gray-500">주유소 13건 입찰 <span class="text-red-500">2/19 마감</span></p>
                </div>
              </div>
              <button class="text-blue-600 text-sm">자세히 보기</button>
            </div>
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-gray-300 rounded-full"></div>
                <div>
                  <p class="text-sm font-medium">지에스엔디</p>
                  <p class="text-xs text-gray-500">역세권 개발 부지 42건 매각</p>
                </div>
              </div>
              <button class="text-blue-600 text-sm">자세히 보기</button>
            </div>
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-gray-300 rounded-full"></div>
                <div>
                  <p class="text-sm font-medium">키움투자자산운용</p>
                  <p class="text-xs text-gray-500">보유 자산 3건 매각</p>
                </div>
              </div>
              <button class="text-blue-600 text-sm">자세히 보기</button>
            </div>
          </div>
        </div>
  
        <!-- 🔹 앱 다운로드 배너 -->
        <div class="bg-gray-200 rounded-xl p-6 text-center">
          <h3 class="text-lg font-bold">앱으로 더 간편하게, 지금 다운로드 받아보세요.</h3>
          <div class="flex justify-center space-x-4 mt-4">
            <img src="/src/assets/google-play.png" alt="Google Play" class="w-32 h-10" />
            <img src="/src/assets/app-store.png" alt="App Store" class="w-32 h-10" />
          </div>
        </div>
  
      </div>
    </div>
  </template>
  