// scripts/scaffold-components.mjs
import fs from 'node:fs'
import path from 'node:path'

const COMPS = [
  // layout
  'src/components/layout/AppShell.vue',
  'src/components/layout/TopNav.vue',
  'src/components/layout/SideNav.vue',
  'src/components/layout/PageContainer.vue',

  // cockpit
  'src/components/cockpit/FilterBar.vue',
  'src/components/cockpit/KpiGrid.vue',
  'src/components/cockpit/KpiStatCard.vue',
  'src/components/cockpit/ChartCard.vue',
  'src/components/cockpit/CardEchartsLine.vue',
  'src/components/cockpit/CardEchartsPie.vue',
  'src/components/cockpit/CardEchartsMapCN.vue',
  'src/components/cockpit/CardEchartsGantt.vue',
  'src/components/cockpit/LiveFeedPanel.vue',

  // atoms
  'src/components/atoms/IconButton.vue',
  'src/components/atoms/SelectField.vue',
  'src/components/atoms/DateRangeField.vue',
  'src/components/atoms/Dropdown.vue',
  'src/components/atoms/GlobalSearch.vue',
  'src/components/atoms/NotificationBell.vue',
  'src/components/atoms/NotificationDropdown.vue',
  'src/components/atoms/ThemeToggle.vue',
  'src/components/atoms/UserMenu.vue',
  'src/components/atoms/UserDropdown.vue',
];

const TPL_MIN = (name) => `
<template>
  <div class="p-2">${name}（占位）</div>
</template>
<script setup lang="ts"></script>
<style scoped></style>
`.trim() + '\n';

const TPLS = {
  'src/components/layout/AppShell.vue': `
<template>
  <div class="min-h-screen flex flex-col">
    <slot />
  </div>
</template>
<script setup lang="ts"></script>
<style scoped></style>
`.trim() + '\n',
  'src/components/layout/TopNav.vue': `
<template>
  <header class="h-12 px-4 flex items-center justify-between border-b">
    <div class="font-semibold">Huawei App Rank</div>
    <div class="flex items-center gap-3">
      <GlobalSearch />
      <NotificationBell />
      <ThemeToggle />
      <UserMenu />
    </div>
  </header>
</template>
<script setup lang="ts">
import GlobalSearch from '@/components/atoms/GlobalSearch.vue'
import NotificationBell from '@/components/atoms/NotificationBell.vue'
import ThemeToggle from '@/components/atoms/ThemeToggle.vue'
import UserMenu from '@/components/atoms/UserMenu.vue'
</script>
<style scoped></style>
`.trim() + '\n',
  'src/components/layout/SideNav.vue': `
<template>
  <aside class="w-56 border-r p-3 hidden md:block">
    <slot />
  </aside>
</template>
<script setup lang="ts"></script>
<style scoped></style>
`.trim() + '\n',
  'src/components/layout/PageContainer.vue': `
<template>
  <main class="flex-1 p-4 overflow-auto">
    <slot />
  </main>
</template>
<script setup lang="ts"></script>
<style scoped></style>
`.trim() + '\n',
  'src/components/cockpit/KpiGrid.vue': `
<template>
  <div class="grid gap-3" style="grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));">
    <KpiStatCard v-for="(k, idx) in items" :key="idx" :title="k.title" :value="k.value" :icon="k.icon" />
  </div>
</template>
<script setup lang="ts">
import KpiStatCard from './KpiStatCard.vue'
interface KpiItem { title: string; value: number | string; icon?: string }
defineProps<{ items: KpiItem[] }>()
</script>
<style scoped></style>
`.trim() + '\n',
  'src/components/cockpit/KpiStatCard.vue': `
<template>
  <div class="rounded-lg border p-4">
    <div class="text-sm text-gray-500">{{ title }}</div>
    <div class="text-2xl font-semibold mt-1">{{ value }}</div>
  </div>
</template>
<script setup lang="ts">
defineProps<{ title: string; value: number | string; icon?: string }>()
</script>
<style scoped></style>
`.trim() + '\n',
  'src/components/cockpit/ChartCard.vue': `
<template>
  <div class="rounded-lg border p-3">
    <div class="flex items-center justify-between mb-2">
      <h3 class="font-medium">{{ title }}</h3>
      <slot name="extra" />
    </div>
    <div class="h-72">
      <slot />
    </div>
  </div>
</template>
<script setup lang="ts">
defineProps<{ title: string }>()
</script>
<style scoped></style>
`.trim() + '\n',
  'src/components/cockpit/CardEchartsLine.vue': `
<template>
  <ChartCard :title="title">
    <v-chart class="h-72 w-full" :option="option" autoresize />
  </ChartCard>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import ChartCard from './ChartCard.vue'

type SeriesLine = { name: string; data: number[]; area?: boolean }
type Input = { x: string[]; series: SeriesLine[]; yAxis?: { inverse?: boolean; max?: number } }

const props = defineProps<{ title: string; data: Input }>()
const option = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { top: 0 },
  xAxis: { type: 'category', data: props.data?.x ?? [] },
  yAxis: { type: 'value', inverse: props.data?.yAxis?.inverse ?? false, max: props.data?.yAxis?.max },
  series: (props.data?.series ?? []).map(s => ({
    type: 'line',
    name: s.name,
    data: s.data,
    areaStyle: s.area ? {} : undefined,
    smooth: true
  }))
}))
</script>
<style scoped></style>
`.trim() + '\n',
  'src/components/cockpit/CardEchartsPie.vue': `
<template>
  <ChartCard :title="title">
    <v-chart class="h-72 w-full" :option="option" autoresize />
  </ChartCard>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import ChartCard from './ChartCard.vue'
type Slice = { name: string; value: number }
const props = defineProps<{ title: string; data: { series: Slice[] } }>()
const option = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { top: 0 },
  series: [{
    type: 'pie',
    radius: ['30%', '70%'],
    data: props.data?.series ?? []
  }]
}))
</script>
<style scoped></style>
`.trim() + '\n',
  'src/components/cockpit/CardEchartsMapCN.vue': `
<template>
  <ChartCard :title="title">
    <div class="h-72 w-full flex items-center justify-center text-gray-500">
      TODO: 注册 china.json 后渲染地图（当前为占位）
    </div>
  </ChartCard>
</template>
<script setup lang="ts">
import ChartCard from './ChartCard.vue'
defineProps<{ title: string; data?: unknown }>()
</script>
<style scoped></style>
`.trim() + '\n',
  'src/components/cockpit/CardEchartsGantt.vue': `
<template>
  <ChartCard :title="title">
    <div class="h-72 w-full flex items-center justify-center text-gray-500">
      TODO: 用 bar + time xAxis 模拟甘特（当前为占位）
    </div>
  </ChartCard>
</template>
<script setup lang="ts">
import ChartCard from './ChartCard.vue'
defineProps<{ title: string; data?: unknown }>()
</script>
<style scoped></style>
`.trim() + '\n',
  'src/components/cockpit/FilterBar.vue': `
<template>
  <div class="rounded-lg border p-3 flex gap-2 flex-wrap">
    <slot>筛选条（占位）</slot>
  </div>
</template>
<script setup lang="ts"></script>
<style scoped></style>
`.trim() + '\n',
  'src/components/cockpit/LiveFeedPanel.vue': `
<template>
  <div class="rounded-lg border p-3">
    <div class="font-medium mb-2">实时任务与告警</div>
    <ul class="space-y-2">
      <li v-for="i in (items ?? [])" :key="i.id" class="text-sm">{{ i.title }} - {{ i.time }}</li>
    </ul>
  </div>
</template>
<script setup lang="ts">
type FeedItem = { id: string; title: string; time: string }
defineProps<{ items?: FeedItem[] }>()
</script>
<style scoped></style>
`.trim() + '\n',
};

function ensureFile(f) {
  if (fs.existsSync(f)) {
    console.log('exists :', f)
    return
  }
  fs.mkdirSync(path.dirname(f), { recursive: true })
  const content = TPLS[f] ?? TPL_MIN(path.basename(f))
  fs.writeFileSync(f, content)
  console.log('created:', f)
}

let created = 0
for (const f of COMPS) {
  const before = fs.existsSync(f)
  ensureFile(f)
  if (!before) created++
}
console.log(`All done. created ${created} file(s).`)