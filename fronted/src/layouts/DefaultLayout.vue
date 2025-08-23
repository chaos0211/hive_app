<template>
  <div class="h-screen flex flex-col">
    <header class="bg-white h-16 border-b border-light-100 px-4 md:px-6 flex items-center justify-between shadow-sm">
      <div class="flex items-center">
        <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center mr-2">
          <i class="fas fa-chart-line text-primary"></i>
        </div>
        <h1 class="text-lg font-semibold hidden md:block">华为应用榜单数据分析平台</h1>
      </div>
      <div class="hidden md:flex">
        <div class="relative">
          <i class="fas fa-search text-info absolute left-3 top-3"></i>
          <input class="pl-10 pr-4 py-2 rounded-lg bg-light-100 border-0 outline-none text-sm w-64" placeholder="全局搜索..." />
        </div>
      </div>
      <div class="flex items-center gap-3">
        <button class="p-2 rounded-lg hover:bg-light-100 relative">
          <i class="fas fa-bell"></i>
          <span class="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full"></span>
        </button>
        <img class="w-8 h-8 rounded-full border" src="https://design.gemcoder.com/staticResource/echoAiSystemImages/b4836a22bb7346e0969480410c37b5b5.png" />
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden">
      <aside class="w-64 bg-white border-r border-light-100 flex-shrink-0 hidden md:flex flex-col">
        <nav class="flex-1 overflow-y-auto p-4">
          <ul class="space-y-1">
            <li>
              <RouterLink to="/cockpit" class="flex items-center px-3 py-2 text-sm font-medium rounded-lg bg-primary/10 text-primary">
                <i class="fas fa-tachometer-alt w-5 h-5 mr-3"></i> 驾驶舱
              </RouterLink>
            </li>
            <li>
              <div class="px-3 py-2 text-sm font-medium rounded-lg hover:bg-light-100 flex items-center justify-between cursor-pointer">
                <div class="flex items-center"><i class="fas fa-list-ol w-5 h-5 mr-3 text-info"></i>华为应用榜单</div>
                <i class="fas fa-chevron-down text-xs"></i>
              </div>
              <ul class="mt-1 ml-6 space-y-1">
                <li><a class="block px-3 py-2 text-sm rounded-lg hover:bg-light-100">榜单列表</a></li>
                <li><a class="block px-3 py-2 text-sm rounded-lg hover:bg-light-100">应用对比</a></li>
              </ul>
            </li>
            <li>
              <div class="px-3 py-2 text-sm font-medium rounded-lg hover:bg-light-100 flex items-center justify-between cursor-pointer">
                <div class="flex items-center"><i class="fas fa-chart-pie w-5 h-5 mr-3 text-info"></i>数据分析</div>
                <i class="fas fa-chevron-down text-xs"></i>
              </div>
            </li>
            <li>
              <div class="px-3 py-2 text-sm font-medium rounded-lg hover:bg-light-100 flex items-center justify-between cursor-pointer">
                <div class="flex items-center"><i class="fas fa-chart-line w-5 h-5 mr-3 text-info"></i>数据预测</div>
                <i class="fas fa-chevron-down text-xs"></i>
              </div>
              <ul class="mt-1 ml-6 space-y-1">
                <li><a class="block px-3 py-2 text-sm rounded-lg hover:bg-light-100">新建预测</a></li>
                <li><a class="block px-3 py-2 text-sm rounded-lg hover:bg-light-100">预测记录</a></li>
              </ul>
            </li>
            <li>
              <div class="px-3 py-2 text-sm font-medium rounded-lg hover:bg-light-100 flex items-center justify-between cursor-pointer">
                <div class="flex items-center"><i class="fas fa-database w-5 h-5 mr-3 text-info"></i>Hive 数据</div>
                <i class="fas fa-chevron-down text-xs"></i>
              </div>
            </li>
            <li>
              <a class="flex items-center px-3 py-2 text-sm font-medium rounded-lg hover:bg-light-100">
                <i class="fas fa-users w-5 h-5 mr-3 text-info"></i> 用户管理
              </a>
            </li>
          </ul>
        </nav>
        <div class="p-4 border-t border-light-100">
          <div class="bg-light-100 rounded-lg p-3 text-xs">
            <i class="fas fa-info-circle text-primary mr-2"></i>
            <div class="inline-block align-top">
              <div>系统版本: v1.0.0</div>
              <div class="text-info mt-1">上次更新: 2023-06-15</div>
            </div>
          </div>
        </div>
      </aside>

      <main class="flex-1 overflow-y-auto bg-light-200 p-4 md:p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
<script setup lang="ts"></script>
