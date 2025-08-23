<template>
  <div class="card p-4 card-hover">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-info text-sm">{{ title }}</p>
        <h3 class="text-2xl font-bold mt-1">{{ value }}</h3>
        <p v-if="delta!==undefined" :class="['text-sm mt-2 flex items-center', delta>0?'text-success':'text-danger']">
          <i class="fas" :class="[delta>0?'fa-arrow-up':'fa-arrow-down','mr-1']"></i>
          {{ Math.abs(delta).toFixed(1) }}% <span class="text-info ml-1">vs {{ base }}</span>
        </p>
        <p v-else-if="sub" class="text-info text-sm mt-2">{{ sub }}</p>
      </div>
      <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="iconBg">
        <i class="fas" :class="icon"></i>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
defineProps<{ title:string; value:string|number; delta?:number; base?:string; sub?:string; icon:string; iconBg:string }>()
</script>
