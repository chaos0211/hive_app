import type { RouteRecordRaw } from "vue-router";
import DefaultLayout from "@/layouts/DefaultLayout.vue";
import Login from "@/views/Login.vue";
import Register from "@/views/Register.vue";
import Cockpit from "@/views/Cockpit.vue";

const routes: RouteRecordRaw[] = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: Login },
  { path: "/register", component: Register },
  {
    path: "/",
    component: DefaultLayout,
    children: [
      { path: "/cockpit", component: Cockpit }
    ]
  }
];
export default routes;
