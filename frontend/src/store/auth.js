import { defineStore } from "pinia";
import api from "../util/axios";  // ✅ `axios.js`를 import

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    accessToken: localStorage.getItem("accessToken") || null,
    refreshToken: localStorage.getItem("refreshToken") || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    getUser: (state) => state.user,
  },

  actions: {
    async login(credentials) {
      try {
        console.log("🔍 로그인 요청 데이터:", credentials);

        const loginData = {
          username: credentials.username,
          password: credentials.password,
        };

        // ✅ `api.post`로 변경하여 Content-Type 포함
        const response = await api.post("/api/account/login/", loginData);

        console.log("✅ 로그인 성공:", response.data);

        this.accessToken = response.data.access;
        this.refreshToken = response.data.refresh;
        localStorage.setItem("accessToken", this.accessToken);
        localStorage.setItem("refreshToken", this.refreshToken);

        await this.loadUser(); // ✅ 로그인 후 사용자 정보 불러오기

        return { success: true };
      } catch (error) {
        console.error("🚨 로그인 실패:", error.response?.data || error.message);
        return { success: false, message: error.response?.data?.error || "로그인 실패" };
      }
    },

        // ✅ 프로필 수정 요청 추가
        async updateProfile(updatedData) {
          if (!this.accessToken) {
            console.warn("🚨 액세스 토큰 없음. 프로필을 업데이트할 수 없습니다.");
            return { success: false, message: "인증이 필요합니다." };
          }
    
          try {
            const response = await api.put("/api/users/profile/update/", updatedData, {
              headers: {
                Authorization: `Bearer ${this.accessToken}`,
                "Content-Type": "application/json",
              },
            });
    
            this.user.username = response.data.username;
            this.user.intro = response.data.intro;
    
            console.log("✅ 프로필 업데이트 성공:", response.data);
            return { success: true };
          } catch (error) {
            console.error("🚨 프로필 업데이트 실패:", error.response?.data || error.message);
            return { success: false, message: error.response?.data?.error || "프로필 업데이트 실패" };
          }
        },



    async signup(credentials) {
      try {
        const response = await api.post("/api/users/register/", {
          username: credentials.username,
          password: credentials.password,
        }, {
          headers: {
            "Content-Type": "application/json",
          },
        });

        console.log("✅ 회원가입 성공:", response.data);
        return { success: true };
      } catch (error) {
        console.error("🚨 회원가입 실패:", error.response?.data || error.message);
        return { success: false, message: error.response?.data?.error || "회원가입 실패" };
      }
    },

    async loadUser() {
      if (!this.accessToken) {
        console.warn("🚨 액세스 토큰 없음. 사용자 정보를 불러올 수 없습니다.");
        return;
      }

      try {
        const response = await api.get("/api/users/profile/", {
          headers: {
            Authorization: `Bearer ${this.accessToken}`, // ✅ Bearer 토큰 추가
          },
        });

        this.user = response.data.user;
        this.comments = response.data.comments; // ✅ 댓글 목록 저장
        console.log("✅ 사용자 정보 로드 성공:", this.user);
        console.log("✅ 사용자가 작성한 댓글 로드 성공:", this.comments);
      } catch (error) {
        console.error("🚨 사용자 정보를 가져오지 못했습니다:", error.response?.data || error.message);
        this.user = null;
        this.comments = []; // ✅ 댓글 목록 초기화
        this.logout(); // ✅ 사용자 정보 로드 실패 시 로그아웃
      }
    },

    async logout() {
      if (this.refreshToken) { // ✅ refreshToken이 있을 때만 API 요청
        try {
          await api.post("/api/account/logout/", { refresh: this.refreshToken }, {
            headers: {
              "Content-Type": "application/json",
            },
          });
        } catch (error) {
          console.warn("🚨 로그아웃 요청 실패:", error.response?.data || error.message);
        }
      }

      // ✅ 로그아웃 후 상태 초기화
      this.accessToken = null;
      this.refreshToken = null;
      this.user = null;
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");

      console.log("✅ 로그아웃 완료");
    },
  },
});
