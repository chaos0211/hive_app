<template>
  <div class="min-h-[calc(100vh-64px)] flex items-center justify-center bg-gradient-to-br from-primary/5 to-secondary/5 p-4">
    <div class="w-full max-w-md card p-6">
      <h1 class="text-xl font-bold mb-4">登录</h1>
      <form class="space-y-3" @submit.prevent="$router.push('/cockpit')">
        <input type="text" placeholder="用户名" class="w-full border rounded px-3 py-2" />
        <input type="password" placeholder="密码" class="w-full border rounded px-3 py-2" />
        <button class="w-full bg-primary text-white py-2 rounded">登录</button>
      </form>
      <p class="text-sm text-info mt-4">没有账户？<router-link to="/register" class="text-primary">去注册</router-link></p>
    </div>
  </div>
</template>
<script setup lang="ts"></script>
