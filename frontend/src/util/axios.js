import axios from "axios";
import { useAuthStore } from "../store/auth";

// ✅ 환경변수 또는 별도의 설정 파일에서 서버 IP 가져오기
const API_BASE_URL = "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,  // ✅ Django API 서버 주소
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// ✅ 요청 인터셉터: JWT 토큰 자동 추가 (회원가입 API는 예외 처리)
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();

    // ✅ 회원가입 API는 Authorization 헤더 제외
    const publicEndpoints = ["/api/users/register/"];

    if (!publicEndpoints.includes(config.url) && authStore.accessToken) {
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
