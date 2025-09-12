<template>
  <div class="font-inter bg-gray-50 text-dark">
    <!-- 顶部导航栏 -->
    <header class="fixed top-0 left-0 right-0 bg-white shadow-sm z-50">
      <div class="container mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <i class="fas fa-chart-line text-primary text-2xl"></i>
          <h1 class="text-xl font-bold text-dark">AppRank Analytics</h1>
        </div>
        <div class="flex items-center space-x-4">
          <button class="text-gray-500 hover:text-primary transition-colors">
            <i class="fas fa-bell-o"></i>
          </button>
          <button class="text-gray-500 hover:text-primary transition-colors">
            <i class="fas fa-cog"></i>
          </button>
          <div class="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
            <span class="text-sm font-medium">A</span>
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="container mx-auto px-4 pt-24 pb-16">
      <!-- 1️⃣ 顶部筛选区 -->
      <section class="mb-8 sticky top-16 bg-white rounded-xl shadow-sm p-4 z-40">
        <div class="flex flex-wrap gap-4">
          <!-- 时间范围选择器 -->
          <div class="relative flex-1 min-w-[180px]">
            <select v-model="timeRange" class="w-full appearance-none bg-light border border-gray-200 rounded-lg py-3 px-4 pr-10 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all">
              <option value="30">最近 30 天</option>
              <option value="90">最近 90 天</option>
              <option value="180">最近 180 天</option>
              <option value="365">最近 1 年</option>
            </select>
            <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
              <i class="fas fa-chevron-down text-xs"></i>
            </div>
          </div>
          <!-- 榜单类型选择器 -->
          <div class="relative flex-1 min-w-[180px]">
            <select v-model="chartType" class="w-full appearance-none bg-light border border-gray-200 rounded-lg py-3 px-4 pr-10 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all">
              <option value="free">免费</option>
              <option value="paid">付费</option>
              <option value="grossing">畅销</option>
            </select>
            <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
              <i class="fas fa-chevron-down text-xs"></i>
            </div>
          </div>
          <!-- 地区选择器 -->
          <div class="relative flex-1 min-w-[180px]">
            <select v-model="region" class="w-full appearance-none bg-light border border-gray-200 rounded-lg py-3 px-4 pr-10 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all">
              <option value="cn">中国 (cn)</option>
              <option value="us">美国 (us)</option>
              <option value="jp">日本 (jp)</option>
              <option value="kr">韩国 (kr)</option>
              <option value="gb">英国 (gb)</option>
            </select>
            <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
              <i class="fas fa-chevron-down text-xs"></i>
            </div>
          </div>
          <!-- 设备选择器 -->
          <div class="relative flex-1 min-w-[180px]">
            <select v-model="device" class="w-full appearance-none bg-light border border-gray-200 rounded-lg py-3 px-4 pr-10 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all">
              <option value="iphone">iPhone</option>
              <option value="android">Android</option>
            </select>
            <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
              <i class="fas fa-chevron-down text-xs"></i>
            </div>
          </div>
        </div>
      </section>

      <!-- 2️⃣ 核心指标卡片区 -->
      <section class="mb-8">
        <h2 class="text-lg font-semibold mb-4 flex items-center">
          <i class="fas fa-chart-pie text-primary mr-2"></i>
          核心指标分析
        </h2>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- 新进榜应用数 -->
          <KpiCard
            subtitle="新进榜应用数"
            :value="newEntriesText"
            icon-class="fas fa-arrow-circle-up text-primary"
            icon-bg-class="bg-primary/10 text-primary"
            trend="12.5%"
            trend-type="up"
          />

          <!-- 掉榜应用数 -->
          <KpiCard
            subtitle="掉榜应用数"
            :value="droppedEntriesText"
            icon-class="fas fa-arrow-circle-down text-danger"
            icon-bg-class="bg-danger/10 text-danger"
            trend="8.3%"
            trend-type="down"
          />

    <!-- 热度最高类别（带进度条） -->
    <KpiCard
      :subtitle="`热度最高类别`"
      :value="topGenre"
      icon-class="fas fa-fire text-warning"
      icon-bg-class="bg-warning/10 text-warning"
      :progress="topGenrePct"
      :progress-color="'#F7BA1E'"
    />

    <!-- 整体波动指数（%） -->
    <KpiCard
      subtitle="整体波动指数"
      :value="volatilityIndex"
      value-suffix="%"
      icon-class="fas fa-chart-line text-secondary"
      icon-bg-class="bg-secondary/10 text-secondary"
      trend="4.2%"
      trend-type="up"
    />
  </div>
</section>

      <!-- 3️⃣ 波动与稳定分析 -->
      <section class="mb-8 bg-white rounded-xl shadow-sm p-5 border border-gray-100">
        <h2 class="text-lg font-semibold mb-5 flex items-center">
          <i class="fas fa-balance-scale-right text-primary mr-2"></i>
          波动与稳定分析
        </h2>
        <!-- 趋势折线图 -->
        <div class="mb-6">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-base font-medium">整体排名波动率趋势</h3>
            <div class="text-sm text-info">按日统计</div>
          </div>
          <div v-if="loadingVol" class="h-[300px] flex items-center justify-center text-info">加载中...</div>
          <VolatilityTrendChart
            v-else
            :labels="volLabels"
            :values="volValues"
            :height="400"
          />
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <TopAppsList
            title="稳定 Top10 应用"
            order="stable"
            :days="Number(timeRange)"
            :brandId="chartType === 'paid' ? 0 : chartType === 'free' ? 1 : 2"
            :country="region"
            :device="device"
            :limit="10"
          />
        </div>
        <div>
          <TopAppsList
            title="高波动应用 Top10"
            order="volatile"
            :days="Number(timeRange)"
            :brandId="chartType === 'paid' ? 0 : chartType === 'free' ? 1 : 2"
            :country="region"
            :device="device"
            :limit="10"
          />
        </div>
      </div>
      </section>

      <!-- 4️⃣ 类别趋势分析 -->
      <section class="mb-8 bg-white rounded-xl shadow-sm p-5 border border-gray-100">
        <h2 class="text-lg font-semibold mb-5 flex items-center">
          <i class="fas fa-chart-line text-primary mr-2"></i>
          类别趋势分析
        </h2>
        <div class="mb-4 flex flex-wrap items-center gap-4">
          <div class="relative flex-1 min-w-[200px]">
            <select v-model="genre"
              class="w-full appearance-none bg-light border border-gray-200 rounded-lg py-2 px-4 pr-10 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
            >
              <!-- 增长视图：显示“所有类别”选项 -->
              <option v-if="view === 'growth'" value="all">所有类别</option>
              <!-- 两个视图都显示真实类别列表（趋势视图不会显示 all） -->
              <option v-for="g in genreOptions" :key="g" :value="g">{{ g }}</option>
            </select>
            <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
              <i class="fas fa-chevron-down text-xs"></i>
            </div>
          </div>
          <div class="flex gap-2">
            <button :class="['genreViewBtn', view==='trend' ? 'filter-active' : 'bg-light', 'px-4','py-2','rounded-lg','text-sm','font-medium','transition-all']" @click="switchView('trend')">趋势视图</button>
            <button :class="['genreViewBtn', view==='growth' ? 'filter-active' : 'bg-light', 'px-4','py-2','rounded-lg','text-sm','font-medium','transition-all']" @click="switchView('growth')">增长视图</button>
          </div>
        </div>
        <!-- 生命周期趋势折线图 -->
        <div v-show="view==='trend'" class="min-h-[360px]">
          <GenreTrendChart
            :key="`trend-${timeRange}-${brandId}-${region}-${device}-${genre}`"
            :title="`${genreTitle}类别热度趋势`"
            :days="Number(timeRange)"
            :brandId="brandId"
            :country="region"
            :device="device"
            :genre="genre"
            :visible="view==='trend'"
          />
        </div>

        <!-- 类别增长率柱状图 -->
        <div v-show="view==='growth'">
          <GenreGrowthBar
            :days="Number(timeRange)"
            :brandId="brandId"
            :country="region"
            :device="device"
            :genre="genre"
            :visible="view==='growth'"
          />
        </div>
      </section>

      <!-- 5️⃣ 预测数据准备 -->
      <section class="mb-8 bg-white rounded-xl shadow-sm p-5 border border-gray-100">
        <h2 class="text-lg font-semibold mb-5 flex items-center">
          <i class="fas fa-cogs text-primary mr-2"></i>
          预测数据准备
        </h2>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- 特征重要性可视化 -->
          <div class="lg:col-span-2">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-base font-medium">特征重要性热力图</h3>
              <div class="text-sm text-info">对预测模型的影响权重</div>
            </div>
            <div ref="featureImportanceEl" class="chart-container"></div>
          </div>
          <!-- 数据导出与准备 -->
          <div class="card-gradient from-cardGradientStart to-cardGradientEnd rounded-xl p-5 border border-gray-100">
            <h3 class="text-base font-medium mb-4">数据导出</h3>
            <div class="space-y-4">
              <div class="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-100">
                <div>
                  <p class="text-sm font-medium">当前筛选数据</p>
                  <p class="text-xs text-info">包含所有指标与特征</p>
                </div>
                <button class="text-primary hover:text-primary/80 transition-colors" @click="openExportModal()">
                  <i class="fas fa-download mr-1"></i> 导出
                </button>
              </div>
              <div class="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-100">
                <div>
                  <p class="text-sm font-medium">特征工程数据集</p>
                  <p class="text-xs text-info">预处理后的建模数据</p>
                </div>
                <button class="text-primary hover:text-primary/80 transition-colors">
                  <i class="fas fa-download mr-1"></i> 导出
                </button>
              </div>
              <div class="flex items-center justify-between p-3 bg-white rounded-lg border border-gray-100">
                <div>
                  <p class="text-sm font-medium">时间序列数据</p>
                  <p class="text-xs text-info">按日聚合的历史趋势</p>
                </div>
                <button class="text-primary hover:text-primary/80 transition-colors">
                  <i class="fas fa-download mr-1"></i> 导出
                </button>
              </div>
            </div>
            <div class="mt-6">
              <button class="w-full bg-primary hover:bg-primary/90 text-white py-3 rounded-lg transition-colors flex items-center justify-center">
                <i class="fas fa-magic mr-2"></i> 生成预测模型输入
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 页脚 -->
    <footer class="bg-white border-t border-gray-200 py-6">
      <div class="container mx-auto px-4 text-center text-info text-sm">
        <p>AppRank Analytics © 2023 | 手机应用榜单数据分析平台</p>
        <p class="mt-1">为预测模型提供输入和趋势洞察</p>
      </div>
    </footer>

    <!-- 数据导出模态框 -->
    <div v-show="exportModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-xl p-6 w-full max-w-md mx-4 transform transition-all">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold">导出数据</h3>
          <button class="text-gray-400 hover:text-gray-600" @click="exportModal=false"><i class="fas fa-times"></i></button>
        </div>
        <div class="mb-5">
          <p class="text-sm text-info mb-4">请选择导出格式和数据范围</p>
          <div class="mb-4">
            <label class="block text-sm font-medium mb-2">导出格式</label>
            <div class="flex gap-3">
              <label class="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:border-primary transition-colors">
                <input type="radio" name="exportFormat" value="csv" v-model="exportFormat" class="mr-2"/> CSV
              </label>
              <label class="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:border-primary transition-colors">
                <input type="radio" name="exportFormat" value="json" v-model="exportFormat" class="mr-2"/> JSON
              </label>
            </div>
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium mb-2">数据范围</label>
            <div class="flex gap-3">
              <label class="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:border-primary transition-colors">
                <input type="radio" name="exportScope" value="current" v-model="exportScope" class="mr-2"/> 当前筛选
              </label>
              <label class="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer hover:border-primary transition-colors">
                <input type="radio" name="exportScope" value="all" v-model="exportScope" class="mr-2"/> 全部数据
              </label>
            </div>
          </div>
        </div>
        <div class="flex gap-3">
          <button class="flex-1 bg-primary hover:bg-primary/90 text-white py-2 rounded-lg transition-colors" @click="confirmExport">确认导出</button>
          <button class="flex-1 bg-light hover:bg-gray-200 py-2 rounded-lg transition-colors" @click="exportModal=false">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import VolatilityTrendChart from '@/components/charts/VolatilityTrendChart.vue'
import { getVolatilityTrend } from '@/api/analytics'
import KpiCard from '@/components/common/KpiCard.vue'
import { getOverviewKpis } from '@/api/analytics'
import { getGenres } from '@/api/analytics'
import TopAppsList from '@/components/charts/TopAppsList.vue'
import GenreTrendChart from '@/components/charts/GenreTrendChart.vue'
import GenreGrowthBar from '@/components/charts/GenreGrowthBar.vue'

// —— 顶部筛选 ——
const timeRange = ref('30')
const chartType = ref<'free' | 'paid' | 'grossing'>('free')
const region = ref('cn')
const device = ref<'iphone' | 'android'>('iphone')
const genre = ref<'all' | string>('all')
const genreOptions = ref<string[]>([])
const brandId = computed(() => (chartType.value === 'paid' ? 0 : chartType.value === 'free' ? 1 : 2))
const view = ref<'trend'|'growth'>('trend')
const volLabels = ref<string[]>([])
const volValues = ref<number[]>([])
const loadingVol = ref(false)

// —— 指标卡片数据（先用示例，后续对接 API） ——
const newEntries = ref<number|null>(1248)
const droppedEntries = ref<number|null>(986)
const topGenre = ref('游戏')
const topGenrePct = ref(32.7)
const volatilityIndex = ref(28.4)

const loadingText = '加载中...'
const newEntriesText = computed(() => newEntries.value == null ? loadingText : newEntries.value.toLocaleString())
const droppedEntriesText = computed(() => droppedEntries.value == null ? loadingText : droppedEntries.value.toLocaleString())

// —— 表格数据（示意） ——

// —— 图表容器 ——
const volatilityTrendEl = ref<HTMLDivElement|null>(null)
const featureImportanceEl = ref<HTMLDivElement|null>(null)

let volatilityTrendChart: echarts.ECharts | null = null
let featureImportanceChart: echarts.ECharts | null = null


async function fetchVolatility() {
  loadingVol.value = true
  try {
    const { labels, values } = await getVolatilityTrend({
      range: Number(timeRange.value),
      brand_id: brandId.value,
      country: region.value,
      device: device.value
    })
    volLabels.value = labels
    volValues.value = values
  } finally {
    loadingVol.value = false
  }
}

async function fetchGenres() {
  const items = await getGenres({
    days: Number(timeRange.value),
    brand_id: brandId.value,
    country: region.value,
    device: device.value,
  })
  genreOptions.value = Array.isArray(items) ? items : []
  // 与当前视图对齐：趋势视图不允许 all；增长视图允许 all
  if (view.value === 'trend') {
    if (genre.value === 'all' || !genreOptions.value.includes(genre.value)) {
      genre.value = genreOptions.value[0] || ''
    }
  } else {
    // 增长视图：默认 all，但允许手动选择具体类别；如果当前值不在列表且不是 all，回退到 all
    if (!genreOptions.value.includes(genre.value)) {
      genre.value = 'all'
    }
  }
}


const genreTitle = computed(() => (genre.value === 'all' ? '所有' : genre.value))

function switchView(v: 'trend'|'growth'){
  view.value = v
  if (v === 'growth') {
    // 增长视图：默认“所有类别”
    genre.value = 'all'
  } else {
    // 趋势视图：不允许 all；如果当前是 all 或不在列表里，默认第一个真实类别
    if (genre.value === 'all' || !genreOptions.value.includes(genre.value)){
      genre.value = genreOptions.value[0] || ''
    }
  }
}

watch([timeRange, chartType, region, device], () => {
  fetchGenres()
}, { immediate: true })

// —— 初始化与更新 ——
watch([timeRange, chartType, region, device, genre, view], async ()=>{
  refreshKpis()
  await fetchVolatility()
  await nextTick()
  initCharts()
}, { immediate: true })

onMounted(async () => {
  await nextTick()
  initCharts()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  destroyCharts()
})

function handleResize(){
  volatilityTrendChart?.resize();
  featureImportanceChart?.resize();
}

function destroyCharts(){
  volatilityTrendChart?.dispose(); volatilityTrendChart=null
  featureImportanceChart?.dispose(); featureImportanceChart=null
}

function initCharts(){
  initFeatureImportanceChart()
}

function genLastNDates(n:number){
  const dates:string[]=[]
  const today=new Date()
  for(let i=n-1;i>=0;i--){
    const d=new Date(today); d.setDate(today.getDate()-i)
    dates.push(`${d.getMonth()+1}/${d.getDate()}`)
  }
  return dates
}




function initFeatureImportanceChart(){
  if(!featureImportanceEl.value) return
  // 复用已存在实例，避免重复 init 警告
  const existed = echarts.getInstanceByDom(featureImportanceEl.value)
  if (existed) {
    featureImportanceChart = existed
  } else {
    featureImportanceChart = echarts.init(featureImportanceEl.value)
  }
  const features = ['游戏','社交','购物','工具','教育','娱乐','新闻','健康','免费','付费','iPhone','Android','CN','US','JP','KR']
  const importance = features.map(()=> +(Math.random()*0.6+0.2).toFixed(2))
  const option: echarts.EChartsOption = {
    tooltip:{ trigger:'item', backgroundColor:'rgba(255,255,255,0.9)', borderColor:'#EBEEF5', borderWidth:1, padding:10, textStyle:{color:'#303133'}, formatter:(p:any)=> `${p.name}<br/>重要性权重: ${p.value}` },
    grid:{ left:'10%', right:'4%', bottom:'15%', containLabel:true },
    xAxis:{ type:'category', data:['重要性权重'], axisLine:{show:false}, axisLabel:{show:false}, splitLine:{show:false} },
    yAxis:{ type:'category', data:features, axisLine:{show:false}, axisLabel:{ color:'#909399' }, splitLine:{show:false} },
    visualMap:{ min:0.2, max:0.8, calculable:true, orient:'horizontal', left:'center', bottom:0, textStyle:{ color:'#909399' }, inRange:{ color:['#E0F2FF','#165DFF'] } },
    series:[{ name:'特征重要性', type:'heatmap', data: features.map((_,i)=>[0,i,importance[i]]), label:{ show:true, color:'#303133', formatter:(p:any)=> p.data[2] }, itemStyle:{ borderRadius:4 } }]
  }
  featureImportanceChart.clear()
  featureImportanceChart.setOption(option)
}

async function refreshKpis(){
  try {
    const data = await getOverviewKpis({
      country: region.value,
      device: device.value,
      brand_id: brandId.value,
      days: Number(timeRange.value)
    })
    newEntries.value = data.new_entries
    droppedEntries.value = data.dropped_entries
    topGenre.value = data.top_genre.name
    topGenrePct.value = data.top_genre.pct
    volatilityIndex.value = data.volatility_index
  } catch (e) {
    // 失败时保留旧值即可
  }
}

// 导出
const exportModal = ref(false)
const exportFormat = ref<'csv'|'json'>('csv')
const exportScope = ref<'current'|'all'>('current')
function openExportModal(){ exportModal.value = true }
function confirmExport(){
  alert(`正在导出${exportScope.value==='current'?'当前筛选':'全部'}数据，格式：${exportFormat.value.toUpperCase()}`)
  exportModal.value = false
}
</script>

<style scoped>
/* 转换自原 HTML 中的自定义工具类 */
.card-gradient { background: linear-gradient(135deg, var(--tw-gradient-stops)); }
.chart-container { width: 100%; height: 300px; }
@media (min-width: 768px){ .chart-container { height: 350px; } }
@media (min-width: 1024px){ .chart-container { height: 400px; } }
.filter-active { background-color: #165DFF; color: #fff; border-color: #165DFF; }
</style>