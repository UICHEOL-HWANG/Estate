import axios from "axios";

// ✅ 게시판 API 서버 주소
const BOARD_API_BASE_URL = "http://localhost:8008";

// ✅ 게시판 API용 axios 인스턴스 생성
const boardApi = axios.create({
  baseURL: BOARD_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// ✅ 요청 인터셉터 (추후 인증 필요 시 추가 가능)
boardApi.interceptors.request.use(
  (config) => {
    console.log(`📡 [Request] ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// ✅ 응답 인터셉터
boardApi.interceptors.response.use(
  (response) => {
    console.log(`✅ [Response]`, response.data);
    return response;
  },
  (error) => {
    console.error("🚨 [Error Response]", error);
    return Promise.reject(error);
  }
);


export default boardApi;
