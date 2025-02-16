<template>
  <div class="font-pretendard text-gray-900">
    <Navbar />
    <MainVisual />
    <MainContent/>
    <router-view />
  </div>
</template>


<script>
import Navbar from "./components/Navbar.vue";
import MainVisual from "./components/MainVisual.vue";
import MainContent from "./components/MainContent.vue";

export default {
  components: {
    Navbar,
    MainVisual,
    MainContent,

  },
};
</script>
