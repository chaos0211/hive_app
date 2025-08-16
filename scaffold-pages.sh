#!/usr/bin/env bash
set -euo pipefail

PAGES=(
  "src/pages/CockpitPage.vue"
  "src/pages/rank/RankListPage.vue"
  "src/pages/rank/RankComparePage.vue"
  "src/pages/rank/RankDetailPage.vue"
  "src/pages/analysis/AnalysisOverviewPage.vue"
  "src/pages/analysis/AnalysisCategoryPage.vue"
  "src/pages/analysis/AnalysisRegionPage.vue"
  "src/pages/analysis/AnalysisKeywordsPage.vue"
  "src/pages/forecast/ForecastCreatePage.vue"
  "src/pages/forecast/ForecastListPage.vue"
  "src/pages/forecast/ForecastDetailPage.vue"
  "src/pages/hive/HiveJobsPage.vue"
  "src/pages/hive/HiveQualityPage.vue"
  "src/pages/hive/HivePartitionsPage.vue"
  "src/pages/users/UsersPage.vue"
  "src/pages/AuthLoginPage.vue"
  "src/pages/AuthRegisterPage.vue"
  "src/pages/NotFoundPage.vue"
)

TPL='
<template>
  <div class="p-4">
    <h1 class="text-xl font-semibold">{{ title }}</h1>
    <p class="text-gray-500">（占位页面，待实现）</p>
  </div>
</template>
<script setup lang="ts">
const title = "PAGE_TITLE"
</script>
<style scoped></style>
'

created=0
for f in "${PAGES[@]}"; do
  if [ ! -f "$f" ]; then
    mkdir -p "$(dirname "$f")"
    printf "%s" "$TPL" > "$f"
    # 用文件名做默认标题
    bn="$(basename "$f" .vue)"
    sed -i '' "s/PAGE_TITLE/${bn}/" "$f" 2>/dev/null || true
    echo "created: $f"
    created=$((created+1))
  else
    echo "exists : $f"
  fi
done

echo "Done. created $created file(s)."
