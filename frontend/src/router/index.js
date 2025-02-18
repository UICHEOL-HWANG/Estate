import { createRouter, createWebHistory } from 'vue-router';
import Signup from "../components/Signup.vue"; 
import Board from "../components/Board.vue";
import Write from "../components/Write.vue";
import BoardDetail from "../components/BoardDetail.vue";
import Profile from "../components//Profile.vue";

const routes = [
  {
    path: "/signup",
    name: "Signup",
    component: Signup, // ✅ 회원가입 페이지
  },
  {
    path : "/board",
    name : "Board",
    component : Board, 
  },
  {
    path : "/write",
    name : "Write",
    component : Write, 
  },
  {
    path: "/board/:postId",
    name: "BoardDetail",
    component: BoardDetail,
    props: true, // ✅ 동적 라우팅 적용
  },
  {
    path :  "/profile",
    name : "Profile",
    component : Profile
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
