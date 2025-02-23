import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from "../store/auth"; // ✅ 인증 스토어 가져오기
import Signup from "../components/Signup.vue"; 
import Board from "../components/Board.vue";
import Write from "../components/Write.vue";
import BoardDetail from "../components/BoardDetail.vue";
import Profile from "../components/Profile.vue";
import Predict from "../components/Predict.vue"; // ✅ 예측 페이지 추가

const routes = [
  {
    path: "/signup",
    name: "Signup",
    component: Signup, // ✅ 회원가입 페이지
  },
  {
    path: "/board",
    name: "Board",
    component: Board, 
  },
  {
    path: "/write",
    name: "Write",
    component: Write, 
  },
  {
    path: "/board/:postId",
    name: "BoardDetail",
    component: BoardDetail,
    props: true, // ✅ 동적 라우팅 적용
  },
  {
    path: "/profile",
    name: "Profile",
    component: Profile
  },
  {
    path: "/predict",
    name: "Predict",
    component: Predict,
    meta: { requiresAuth: true }, // ✅ 로그인 필요
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// ✅ 전역 네비게이션 가드 추가 (로그인 검증)
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    alert("로그인이 필요합니다.");
    next("/signup"); // 로그인 페이지로 리다이렉트
  } else {
    next();
  }
});

export default router;
