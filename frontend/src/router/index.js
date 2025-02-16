import { createRouter, createWebHistory } from 'vue-router';
import Signup from "../components/Signup.vue"; // ✅ 올바른 파일명 적용

const routes = [
  {
    path: "/signup",
    name: "Signup",
    component: Signup, // ✅ 회원가입 페이지
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
