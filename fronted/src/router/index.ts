import type { RouteRecordRaw } from "vue-router";
import DefaultLayout from "@/layouts/DefaultLayout.vue";
import Login from "@/views/Login.vue";
import Register from "@/views/Register.vue";
import Cockpit from "@/views/Cockpit.vue";
import RankingList from "@/views/RankingList.vue";
// import RankingList from "@/views/Analytiscs.vue";

const routes: RouteRecordRaw[] = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  {
    path: "/",
    component: DefaultLayout,
    children: [
      { path: "/cockpit", component: Cockpit },
      { path: "/ranking", component: RankingList },
      { path: '/app-compare', component: () => import('@/views/AppCompare.vue'), meta: { title: '应用对比' } },
      { path: '/bigscreen', component: () => import('@/views/BigScreen.vue'), meta: { title: '可视化大屏' } },
      { path: "/analytics", component: () => import("@/views/Analytics.vue"), meta: { title: "数据分析" } }    ]
  }
];
export default routes;
