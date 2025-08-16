<template>
  <div class="page-container">
    <slot />
  </div>
</template>

<script setup lang="ts">
// Page container component
</script>

<style scoped>
.page-container {
  padding: 20px;
  min-height: calc(100vh - 60px);
}
</style>
