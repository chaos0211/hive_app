<template>
  <el-card class="filter-bar">
    <el-form :model="form" inline>
      <el-form-item label="时间范围">
        <DateRangeField
          label=""
          v-model="form.dateRange"
          :preset="form.dateRange"
        />
      </el-form-item>
      
      <el-form-item label="地区">
        <SelectField
          label=""
          v-model="form.region"
          :options="regionOptions"
        />
      </el-form-item>
      
      <el-form-item label="分类">
        <SelectField
          label=""
          v-model="form.category"
          :options="categoryOptions"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="handleApply">应用</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import DateRangeField from '@/components/atoms/DateRangeField.vue'
import SelectField from '@/components/atoms/SelectField.vue'
import type { CockpitFilters } from '@/types'

interface Props {
  initial?: CockpitFilters
}

const props = defineProps<Props>()

const emit = defineEmits<{
  apply: [filters: CockpitFilters]
  reset: []
}>()

const form = reactive<CockpitFilters>({
  dateRange: props.initial?.dateRange || '7d',
  region: props.initial?.region || '',
  category: props.initial?.category || ''
})

const regionOptions = [
  { label: '全部', value: '' },
  { label: '中国', value: 'CN' },
  { label: '美国', value: 'US' },
  { label: '日本', value: 'JP' }
]

const categoryOptions = [
  { label: '全部', value: '' },
  { label: '游戏', value: 'game' },
  { label: '社交', value: 'social' },
  { label: '工具', value: 'tools' }
]

const handleApply = () => {
  emit('apply', { ...form })
}

const handleReset = () => {
  form.dateRange = '7d'
  form.region = ''
  form.category = ''
  emit('reset')
}
</script>

<style scoped>
.filter-bar {
  margin-bottom: 20px;
}
</style>
