<template>
  <div class="min-h-[calc(100vh-64px)] flex items-center justify-center bg-gray-50 p-4">
    <div class="card p-6 max-w-md w-full">
      <h1 class="text-xl font-bold mb-4">用户注册</h1>
      <form class="space-y-3" @submit.prevent="$router.push('/login')">
        <input type="text" placeholder="用户名" class="w-full border rounded px-3 py-2" />
        <input type="email" placeholder="邮箱" class="w-full border rounded px-3 py-2" />
        <input type="password" placeholder="密码" class="w-full border rounded px-3 py-2" />
        <input type="password" placeholder="确认密码" class="w-full border rounded px-3 py-2" />
        <button class="w-full bg-primary text-white py-2 rounded">注册</button>
      </form>
      <p class="text-sm text-info mt-4">已有账户？<router-link to="/login" class="text-primary">立即登录</router-link></p>
    </div>
  </div>
</template>
<script setup lang="ts"></script>
