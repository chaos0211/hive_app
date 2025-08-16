cat > scaffold-components.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

# ===== 要创建的组件清单 =====
COMPS=(
  # layout
  "src/components/layout/AppShell.vue"
  "src/components/layout/TopNav.vue"
  "src/components/layout/SideNav.vue"
  "src/components/layout/PageContainer.vue"

  # cockpit
  "src/components/cockpit/FilterBar.vue"
  "src/components/cockpit/KpiGrid.vue"
  "src/components/cockpit/KpiStatCard.vue"
  "src/components/cockpit/ChartCard.vue"
  "src/components/cockpit/CardEchartsLine.vue"
  "src/components/cockpit/CardEchartsPie.vue"
  "src/components/cockpit/CardEchartsMapCN.vue"
  "src/components/cockpit/CardEchartsGantt.vue"
  "src/components/cockpit/LiveFeedPanel.vue"

  # atoms
  "src/components/atoms/IconButton.vue"
  "src/components/atoms/SelectField.vue"
  "src/components/atoms/DateRangeField.vue"
  "src/components/atoms/Dropdown.vue"
  "src/components/atoms/GlobalSearch.vue"
  "src/components/atoms/NotificationBell.vue"
  "src/components/atoms/NotificationDropdown.vue"
  "src/components/atoms/ThemeToggle.vue"
  "src/components/atoms/UserMenu.vue"
  "src/components/atoms/UserDropdown.vue"
)

# ===== 通用最小模板 =====
TPL_MIN='
<template>
  <div class="p-2">[PLACEHOLDER]</div>
</template>
<script setup lang="ts"></script>
<style scoped></style>
'

# ===== 一些带基础实现的模板 =====
read -r -d '' TPL_LAYOUT <<"EOF"
<template>
  <div class="min-h-screen flex flex-col">
    <slot />
  </div>
</template>
<script setup lang="ts"></script>
<style scoped></style>
EOF

read -r -d '' TPL_TOPNAV <<"EOF"
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
EOF

read -r -d '' TPL_SIDENAV <<"EOF"
<template>
  <aside class="w-56 border-r p-3 hidden md:block">
    <slot />
  </aside>
</template>
<script setup lang="ts"></script>
<style scoped></style>
EOF

read -r -d '' TPL_PAGECONTAINER <<"EOF"
<template>
  <main class="flex-1 p-4 overflow-auto">
    <slot />
  </main>
</template>
<script setup lang="ts"></script>
<style scoped></style>
EOF

read -r -d '' TPL_KPIGRID <<"EOF"
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
EOF

read -r -d '' TPL_KPISTAT <<"EOF"
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
EOF

read -r -d '' TPL_CHARTCARD <<"EOF"
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
EOF

read -r -d '' TPL_LINE <<"EOF"
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
EOF

read -r -d '' TPL_PIE <<"EOF"
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
EOF

read -r -d '' TPL_MAPCN <<"EOF"
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
EOF

read -r -d '' TPL_GANTT <<"EOF"
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
EOF

read -r -d '' TPL_FILTERBAR <<"EOF"
<template>
  <div class="rounded-lg border p-3 flex gap-2 flex-wrap">
    <slot>筛选条（占位）</slot>
  </div>
</template>
<script setup lang="ts"></script>
<style scoped></style>
EOF

read -r -d '' TPL_LIVEFEED <<"EOF"
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
EOF

# ===== 写文件函数 =====
write_if_missing () {
  local path="$1" ; local content="$2"
  if [ ! -f "$path" ]; then
    mkdir -p "$(dirname "$path")"
    printf "%s" "$content" > "$path"
    echo "created: $path"
  else
    echo "exists : $path"
  fi
}

# ===== 按类型写入合理模板 =====
for f in "${COMPS[@]}"; do
  case "$f" in
    *"layout/AppShell.vue")       write_if_missing "$f" "$TPL_LAYOUT" ;;
    *"layout/TopNav.vue")         write_if_missing "$f" "$TPL_TOPNAV" ;;
    *"layout/SideNav.vue")        write_if_missing "$f" "$TPL_SIDENAV" ;;
    *"layout/PageContainer.vue")  write_if_missing "$f" "$TPL_PAGECONTAINER" ;;
    *"cockpit/KpiGrid.vue")       write_if_missing "$f" "$TPL_KPIGRID" ;;
    *"cockpit/KpiStatCard.vue")   write_if_missing "$f" "$TPL_KPISTAT" ;;
    *"cockpit/ChartCard.vue")     write_if_missing "$f" "$TPL_CHARTCARD" ;;
    *"cockpit/CardEchartsLine.vue") write_if_missing "$f" "$TPL_LINE" ;;
    *"cockpit/CardEchartsPie.vue")  write_if_missing "$f" "$TPL_PIE" ;;
    *"cockpit/CardEchartsMapCN.vue") write_if_missing "$f" "$TPL_MAPCN" ;;
    *"cockpit/CardEchartsGantt.vue") write_if_missing "$f" "$TPL_GANTT" ;;
    *"cockpit/FilterBar.vue")     write_if_missing "$f" "$TPL_FILTERBAR" ;;
    *"cockpit/LiveFeedPanel.vue") write_if_missing "$f" "$TPL_LIVEFEED" ;;
    *)                            write_if_missing "$f" "${TPL_MIN/\[PLACEHOLDER\]/$(basename "$f")}" ;;
  esac
done

echo "All done."
SH

chmod +x scaffold-components.sh
./scaffold-components.sh