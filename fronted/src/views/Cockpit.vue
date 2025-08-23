<template>
  <div>
    <div class="mb-6">
      <h1 class="text-[clamp(1.25rem,3vw,1.75rem)] font-bold">驾驶舱</h1>
      <p class="text-info mt-1">应用榜单数据分析概览</p>
    </div>

    <FilterBar class="mb-6" />

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4 mb-6">
      <KpiCard title="昨日采集量" value="12,845" :delta="8.2" base="前日" icon="fa-database" iconBg="bg-primary/10 text-primary"/>
      <KpiCard title="有效分区数" value="248" :delta="2.1" base="上周" icon="fa-cubes" iconBg="bg-secondary/10 text-secondary"/>
      <KpiCard title="Top1 应用" value="华为应用市场" sub="工具类 · 评分 4.8" icon="fa-trophy" iconBg="bg-success/10 text-success"/>
      <KpiCard title="Top 类目" value="游戏" sub="占比 32.5% · 128款应用" icon="fa-gamepad" iconBg="bg-warning/10 text-warning"/>
      <KpiCard title="预测覆盖率" value="89.7%" :delta="-1.3" base="上周" icon="fa-chart-line" iconBg="bg-primary/10 text-primary"/>
      <KpiCard title="任务成功率" value="96.2%" :delta="0.8" base="上周" icon="fa-check-circle" iconBg="bg-success/10 text-success"/>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <ChartCard title="Top N 应用排名趋势">
        <template #tools>
          <button class="px-3 py-1 text-xs bg-primary/10 text-primary rounded-lg">7天</button>
          <button class="px-3 py-1 text-xs hover:bg-light-100 rounded-lg">30天</button>
          <button class="p-1 text-info hover:text-dark-100"><i class="fas fa-expand"></i></button>
          <button class="p-1 text-info hover:text-dark-100"><i class="fas fa-download"></i></button>
        </template>
        <TrendChart />
      </ChartCard>

      <ChartCard title="分类占比">
        <template #tools>
          <button class="p-1 text-info hover:text-dark-100"><i class="fas fa-expand"></i></button>
          <button class="p-1 text-info hover:text-dark-100"><i class="fas fa-download"></i></button>
        </template>
        <CategoryPie />
      </ChartCard>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <ChartCard class="lg:col-span-2" title="地区分布热力图">
        <template #tools>
          <button class="p-1 text-info hover:text-dark-100"><i class="fas fa-expand"></i></button>
          <button class="p-1 text-info hover:text-dark-100"><i class="fas fa-download"></i></button>
        </template>
        <RegionHeat />
      </ChartCard>

      <div class="card p-4 flex flex-col">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold">实时任务与告警</h3>
          <button class="p-1 text-info hover:text-dark-100"><i class="fas fa-sync-alt"></i></button>
        </div>
        <div class="flex-1 overflow-y-auto scrollbar-hide space-y-3">
          <div class="p-3 bg-success/5 border border-success/20 rounded-lg">
            <div class="flex items-start">
              <div class="w-8 h-8 rounded-full bg-success/10 flex items-center justify-center text-success"><i class="fas fa-check-circle"></i></div>
              <div class="ml-3 flex-1 text-sm">
                <div>数据采集任务完成</div>
                <div class="text-xs text-info mt-1">应用榜单数据采集任务 #T20230615 已完成</div>
                <div class="text-xs text-info mt-1">刚刚</div>
              </div>
            </div>
          </div>
          <div class="p-3 bg-warning/5 border border-warning/20 rounded-lg">
            <div class="flex items-start">
              <div class="w-8 h-8 rounded-full bg-warning/10 flex items-center justify-center text-warning"><i class="fas fa-exclamation-triangle"></i></div>
              <div class="ml-3 flex-1 text-sm">
                <div>数据延迟警告</div>
                <div class="text-xs text-info mt-1">地区维度分析数据更新延迟超过30分钟</div>
                <div class="text-xs text-info mt-1">5分钟前</div>
              </div>
            </div>
          </div>
          <div class="p-3 bg-primary/5 border border-primary/20 rounded-lg">
            <div class="flex items-start">
              <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary"><i class="fas fa-info-circle"></i></div>
              <div class="ml-3 flex-1 text-sm">
                <div>预测任务开始</div>
                <div class="text-xs text-info mt-1">应用排名预测任务 #P20230615 已开始执行</div>
                <div class="text-xs text-info mt-1">12分钟前</div>
              </div>
            </div>
          </div>
          <div class="p-3 bg-danger/5 border border-danger/20 rounded-lg">
            <div class="flex items-start">
              <div class="w-8 h-8 rounded-full bg-danger/10 flex items-center justify-center text-danger"><i class="fas fa-exclamation-circle"></i></div>
              <div class="ml-3 flex-1 text-sm">
                <div>数据清洗失败</div>
                <div class="text-xs text-info mt-1">应用评论数据清洗任务 #C20230615 执行失败</div>
                <div class="text-xs text-info mt-1">25分钟前</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <ChartCard class="mb-6" title="任务运行状态">
      <template #tools>
        <button class="p-1 text-info hover:text-dark-100"><i class="fas fa-expand"></i></button>
        <button class="p-1 text-info hover:text-dark-100"><i class="fas fa-download"></i></button>
      </template>
      <TaskGantt />
    </ChartCard>
  </div>
</template>

<script setup lang="ts">
import FilterBar from "@/components/common/FilterBar.vue";
import KpiCard from "@/components/common/KpiCard.vue";
import ChartCard from "@/components/common/ChartCard.vue";
import TrendChart from "@/components/charts/TrendChart.vue";
import CategoryPie from "@/components/charts/CategoryPie.vue";
import RegionHeat from "@/components/charts/RegionHeat.vue";
import TaskGantt from "@/components/charts/TaskGantt.vue";
</script>
