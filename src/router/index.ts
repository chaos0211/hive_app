import { createRouter, createWebHistory } from "vue-router"
import type { RouteRecordRaw } from "vue-router"
import { useAuthStore } from "@/stores/auth"

// Layout components
import AppShell from "@/components/layout/AppShell.vue"

// Auth pages
import AuthLoginPage from "@/pages/auth/AuthLoginPage.vue"
import AuthRegisterPage from "@/pages/auth/AuthRegisterPage.vue"

// Main pages
import CockpitPage from "@/pages/CockpitPage.vue"
import RankListPage from "@/pages/rank/RankListPage.vue"
import RankComparePage from "@/pages/rank/RankComparePage.vue"
import RankDetailPage from "@/pages/rank/RankDetailPage.vue"
import AnalysisOverviewPage from "@/pages/analysis/AnalysisOverviewPage.vue"
import AnalysisCategoryPage from "@/pages/analysis/AnalysisCategoryPage.vue"
import AnalysisRegionPage from "@/pages/analysis/AnalysisRegionPage.vue"
import AnalysisKeywordsPage from "@/pages/analysis/AnalysisKeywordsPage.vue"
import ForecastCreatePage from "@/pages/forecast/ForecastCreatePage.vue"
import ForecastListPage from "@/pages/forecast/ForecastListPage.vue"
import ForecastDetailPage from "@/pages/forecast/ForecastDetailPage.vue"
import HiveJobsPage from "@/pages/hive/HiveJobsPage.vue"
import HiveQualityPage from "@/pages/hive/HiveQualityPage.vue"
import HivePartitionsPage from "@/pages/hive/HivePartitionsPage.vue"
import UsersPage from "@/pages/UsersPage.vue"
import NotFoundPage from "@/pages/NotFoundPage.vue"

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "login",
    component: AuthLoginPage,
    meta: {
      title: "登录",
      public: true,
    },
  },
  {
    path: "/register",
    name: "register",
    component: AuthRegisterPage,
    meta: {
      title: "注册",
      public: true,
    },
  },
  {
    path: "/",
    redirect: "/cockpit",
  },
  {
    path: "/",
    component: AppShell,
    children: [
      {
        path: "/cockpit",
        name: "cockpit",
        component: CockpitPage,
        meta: {
          title: "驾驶舱",
          icon: "gauge",
          roles: ["admin", "analyst", "operator", "viewer"],
        },
      },
      {
        path: "/rank",
        name: "rank",
        meta: {
          title: "华为应用榜单",
          icon: "ranking-star",
          roles: ["admin", "analyst", "operator", "viewer"],
        },
        children: [
          {
            path: "list",
            name: "rank-list",
            component: RankListPage,
            meta: {
              title: "榜单列表",
            },
          },
          {
            path: "compare",
            name: "rank-compare",
            component: RankComparePage,
            meta: {
              title: "应用对比",
            },
          },
          {
            path: ":appId",
            name: "rank-detail",
            component: RankDetailPage,
            meta: {
              title: "应用详情",
            },
            props: true,
          },
        ],
      },
      {
        path: "/analysis",
        name: "analysis",
        meta: {
          title: "数据分析",
          icon: "chart-pie",
          roles: ["admin", "analyst", "viewer"],
        },
        children: [
          {
            path: "overview",
            name: "analysis-overview",
            component: AnalysisOverviewPage,
            meta: {
              title: "总览",
            },
          },
          {
            path: "category",
            name: "analysis-category",
            component: AnalysisCategoryPage,
            meta: {
              title: "分类维度",
            },
          },
          {
            path: "region",
            name: "analysis-region",
            component: AnalysisRegionPage,
            meta: {
              title: "地区维度",
            },
          },
          {
            path: "keywords",
            name: "analysis-keywords",
            component: AnalysisKeywordsPage,
            meta: {
              title: "关键词",
            },
          },
        ],
      },
      {
        path: "/forecast",
        name: "forecast",
        meta: {
          title: "数据预测",
          icon: "trending-up",
          roles: ["admin", "analyst", "operator"],
        },
        children: [
          {
            path: "create",
            name: "forecast-create",
            component: ForecastCreatePage,
            meta: {
              title: "新建预测",
            },
          },
          {
            path: "list",
            name: "forecast-list",
            component: ForecastListPage,
            meta: {
              title: "预测记录",
            },
          },
          {
            path: ":id",
            name: "forecast-detail",
            component: ForecastDetailPage,
            meta: {
              title: "预测详情",
            },
            props: true,
          },
        ],
      },
      {
        path: "/hive",
        name: "hive",
        meta: {
          title: "Hive 数据",
          icon: "database",
          roles: ["admin", "operator", "analyst"],
        },
        children: [
          {
            path: "jobs",
            name: "hive-jobs",
            component: HiveJobsPage,
            meta: {
              title: "任务中心",
            },
          },
          {
            path: "quality",
            name: "hive-quality",
            component: HiveQualityPage,
            meta: {
              title: "数据质量",
            },
          },
          {
            path: "partitions",
            name: "hive-partitions",
            component: HivePartitionsPage,
            meta: {
              title: "分区预览",
            },
          },
        ],
      },
      {
        path: "/users",
        name: "users",
        component: UsersPage,
        meta: {
          title: "用户管理",
          icon: "users",
          roles: ["admin"],
        },
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: NotFoundPage,
    meta: {
      title: "404",
    },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Set page title
  document.title = to.meta.title ? `${to.meta.title} - 华为应用榜单数据分析平台` : "华为应用榜单数据分析平台"

  // Check authentication
  if (!to.meta.public && !authStore.isAuthenticated) {
    next("/login")
  } else if (to.meta.roles && !authStore.hasAnyRole(to.meta.roles as string[])) {
    next("/403")
  } else {
    next()
  }
})

export default router
