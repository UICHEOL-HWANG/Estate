import axios from "axios";

// ✅ 좋아요 API 서버 주소
const LIKE_API_BASE_URL = "http://localhost:8002";

// ✅ 좋아요 API용 axios 인스턴스 생성
const likeApi = axios.create({
  baseURL: LIKE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// ✅ 요청 인터셉터: 인증 토큰 자동 추가
likeApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("accessToken");
    if (token) {
      config.headers.Authorization = `${token}`;
    }
    console.log(`📡 [Request] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// ✅ 응답 인터셉터
likeApi.interceptors.response.use(
  (response) => {
    console.log(`✅ [Response]`, response.data);
    return response;
  },
  (error) => {
    console.error("🚨 [Error Response]", error);
    return Promise.reject(error);
  }
);

export default likeApi;
