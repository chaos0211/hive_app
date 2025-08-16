<template>
  <el-date-picker
    v-model="dateValue"
    type="daterange"
    range-separator="至"
    start-placeholder="开始日期"
    end-placeholder="结束日期"
    format="YYYY-MM-DD"
    value-format="YYYY-MM-DD"
    @change="handleChange"
  />
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { DateRange, DatePreset } from '@/types'

interface Props {
  label: string
  modelValue: DateRange | DatePreset
  preset?: '7d' | '30d' | 'custom'
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: DateRange | DatePreset]
}>()

const dateValue = ref<[string, string] | null>(null)

watch(() => props.modelValue, (newValue) => {
  if (typeof newValue === 'object' && newValue.start && newValue.end) {
    dateValue.value = [newValue.start, newValue.end]
  } else {
    dateValue.value = null
  }
}, { immediate: true })

const handleChange = (value: [string, string] | null) => {
  if (value) {
    emit('update:modelValue', { start: value[0], end: value[1] })
  } else {
    emit('update:modelValue', '7d')
  }
}
</script>
