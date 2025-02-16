import axios from "axios";
import { useAuthStore } from "../store/auth";



const api = axios.create({
    baseURL: "http://localhost:8000",  // ✅ Django API 서버 주소
    headers: {
      "Content-Type": "application/json",
    },
    withCredentials: true,
  });
  
  // ✅ 요청 인터셉터: JWT 토큰 자동 추가
  api.interceptors.request.use(
    (config) => {
      const authStore = useAuthStore();
      if (authStore.accessToken) {
        config.headers.Authorization = `Bearer ${authStore.accessToken}`;
      }

      return config;
    },
    (error) => Promise.reject(error)
  );
  
  // ✅ 응답 인터셉터: 액세스 토큰 만료 시 자동 갱신
  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const authStore = useAuthStore();
      const originalRequest = error.config;
  
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true; // 무한 루프 방지
  
        const refreshed = await authStore.refreshAccessToken();
        if (refreshed) {
          originalRequest.headers.Authorization = `Bearer ${authStore.accessToken}`;
          return api(originalRequest); // 실패한 요청 재시도
        }
      }
  
      return Promise.reject(error);
    }
  );
  
  export default api;