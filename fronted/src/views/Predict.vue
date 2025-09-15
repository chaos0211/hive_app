<template>
  <div class="bg-gray-50 font-inter text-gray-800 min-h-screen">
    <!-- 页面容器 -->
    <div class="container mx-auto px-4 py-6 max-w-7xl">
      <!-- 页面标题 -->
      <div class="mb-8">
        <h1 class="text-[clamp(1.5rem,3vw,2.5rem)] font-bold text-gray-800 mb-2">
          应用榜单数据分析
        </h1>
        <p class="text-gray-500">预测应用在榜单中的未来表现趋势与排名变化</p>
      </div>

      <!-- 筛选区 -->
      <div class="bg-white rounded-xl shadow-sm p-5 mb-8 transition-all duration-300 hover:shadow-md">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-5">
          <!-- 日期范围 -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">日期范围</label>
            <div class="flex space-x-2">
              <button
                v-for="d in [7,30,90]"
                :key="d"
                class="date-range-btn px-4 py-2 rounded-lg text-sm font-medium transition-all"
                :class="state.dateRange===d ? 'bg-primary text-white hover:bg-primary/90' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
                @click="setDateRange(d)"
              >
                {{ d }}天
              </button>
            </div>
          </div>

          <!-- 国家 -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">国家/地区</label>
            <div class="relative">
              <select
                id="country-select"
                v-model="state.country"
                class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-lg appearance-none bg-white border"
              >
                <option value="">选择国家/地区</option>
                <option v-for="c in state.countryData" :key="c.code" :value="c.code">{{ c.name }}</option>
              </select>
              <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                <i class="fas fa-chevron-down text-xs"></i>
              </div>
            </div>
          </div>

          <!-- 设备 -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">设备</label>
            <div class="flex space-x-2">
              <button
                v-for="dev in devices"
                :key="dev.value"
                class="device-btn px-4 py-2 rounded-lg text-sm font-medium transition-all"
                :class="state.device===dev.value ? 'bg-primary text-white hover:bg-primary/90' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
                @click="state.device = dev.value"
              >
                {{ dev.label }}
              </button>
            </div>
          </div>

          <!-- 榜单类型 -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">榜单类型</label>
            <div class="flex space-x-2">
              <button
                v-for="t in chartTypes"
                :key="t.value"
                class="chart-type-btn px-4 py-2 rounded-lg text-sm font-medium transition-all"
                :class="state.chartType===t.value ? 'bg-primary text-white hover:bg-primary/90' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
                @click="state.chartType = t.value"
              >
                {{ t.label }}
              </button>
            </div>
          </div>

          <!-- 榜单分类 -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">榜单分类</label>
            <div class="relative">
              <select
                id="category-select"
                v-model="state.category"
                class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-lg appearance-none bg-white border"
              >
                <option value="all">所有分类</option>
                <option value="games">游戏</option>
                <option value="apps">应用</option>
                <option value="social">社交</option>
                <option value="entertainment">娱乐</option>
                <option value="productivity">生产力</option>
                <option value="education">教育</option>
                <option value="finance">财务</option>
              </select>
              <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                <i class="fas fa-chevron-down text-xs"></i>
              </div>
            </div>
          </div>
        </div>

        <!-- 应用搜索 + 已选 -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <!-- 应用搜索 -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">应用搜索 (最多选择3个)</label>
            <div class="flex">
              <div class="relative flex-grow">
                <input
                  id="app-search"
                  v-model="searchKeyword"
                  type="text"
                  placeholder="输入应用名称或ID"
                  class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
                  @focus="openSearchModal"
                />
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <i class="fas fa-search text-gray-400"></i>
                </div>
              </div>
              <button
                id="search-btn"
                class="px-4 py-2 bg-primary text-white font-medium rounded-r-lg hover:bg-primary/90 transition-colors"
                @click="openSearchModal"
              >
                <i class="fas fa-search mr-1"></i> 搜索
              </button>
            </div>
          </div>

          <!-- 已选应用 -->
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700">
              已选应用 (<span id="selected-count">{{ state.selectedApps.length }}</span>/3)
            </label>
            <div id="selected-apps" class="flex flex-wrap gap-2">
              <template v-if="state.selectedApps.length">
                <div
                  v-for="app in selectedAppObjects"
                  :key="app.id"
                  class="flex items-center bg-blue-50 text-primary text-xs px-3 py-1.5 rounded-full"
                >
                  <img :src="app.icon" :alt="app.name" class="h-4 w-4 rounded-full mr-2" />
                  <span class="truncate max-w-[100px]">{{ app.name }}</span>
                  <button class="ml-1 text-primary/70 hover:text-primary" @click="removeSelected(app.id)">
                    <i class="fas fa-times-circle"></i>
                  </button>
                </div>
              </template>
              <div v-else class="text-xs text-gray-500 italic">暂无选择</div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex justify-end mt-6">
          <button
            id="reset-btn"
            class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 bg-white text-sm font-medium mr-3 hover:bg-gray-50 transition-colors"
            @click="onReset"
          >
            <i class="fas fa-redo mr-1"></i> 重置
          </button>
          <button
            id="analyze-btn"
            class="px-6 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors shadow-sm"
            @click="onAnalyze"
          >
            <i class="fas fa-chart-line mr-1"></i> 开始预测分析
          </button>
        </div>
      </div>

      <!-- 核心预测结果区：趋势 + TopN -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <!-- 预测趋势图 -->
        <div class="lg-col-span-2 bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-semibold text-gray-800">
              预测趋势图
              <span class="text-sm font-normal text-gray-500 ml-2">（未来{{ state.dateRange }}天）</span>
            </h2>
            <div class="flex space-x-2">
              <button class="p-2 rounded hover:bg-gray-100 text-gray-600 transition-colors" @click="downloadTrend">
                <i class="fas fa-download"></i>
              </button>
              <button class="p-2 rounded hover:bg-gray-100 text-gray-600 transition-colors" @click="fullscreenTrend">
                <i class="fas fa-expand"></i>
              </button>
            </div>
          </div>
          <div ref="trendRef" class="w-full h-[400px] bg-gray-50 rounded-lg p-2"></div>
        </div>

        <!-- 预测Top10榜单 -->
        <div class="bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md card-hover">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-semibold text-gray-800">预测Top10榜单</h2>
            <div class="flex space-x-2">
              <button class="p-2 rounded hover:bg-gray-100 text-gray-600 transition-colors" @click="downloadTopN">
                <i class="fas fa-download"></i>
              </button>
            </div>
          </div>
          <div class="overflow-x-auto rounded-lg border border-gray-100">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider rounded-tl-lg w-16">排名</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">应用信息</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">发行商</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider rounded-tr-lg">排名变化</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr
                  v-for="item in topNRows"
                  :key="item.rank"
                  class="hover:bg-gray-50 transition-colors"
                >
                  <td class="px-3 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div
                        class="flex-shrink-0 w-8 h-8 flex items-center justify-center rounded-full"
                        :class="item.rank<=3 ? 'bg-primary text-white font-bold' : 'bg-gray-100 text-gray-600'"
                      >
                        {{ item.rank }}
                      </div>
                    </div>
                  </td>
                  <td class="px-3 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="flex-shrink-0 h-10 w-10">
                        <img :src="item.icon" :alt="item.appName" class="h-10 w-10 rounded object-cover" />
                      </div>
                      <div class="ml-3">
                        <div class="text-sm font-medium text-gray-900">{{ item.appName }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-3 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ item.publisher }}
                  </td>
                  <td class="px-3 py-4 whitespace-nowrap">
                    <div
                      class="text-sm flex items-center"
                      :class="item.change>0 ? 'text-success' : item.change<0 ? 'text-danger' : 'text-gray-500'"
                    >
                      <i :class="item.change>0 ? 'fas fa-arrow-up mr-1' : item.change<0 ? 'fas fa-arrow-down mr-1' : 'fas fa-minus mr-1'"></i>
                      {{ Math.abs(item.change) }} ({{ item.changePercent }}%)
                    </div>
                  </td>
                </tr>
                <tr v-if="!topNRows.length">
                  <td colspan="4" class="px-4 py-6 text-center text-gray-400">暂无数据</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 模型评估区域（与原 HTML 一致的 4 卡 + 历史准确率趋势） -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <!-- MAE -->
          <div class="bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md card-hover">
            <div class="flex items-start">
              <div class="flex-shrink-0 bg-blue-50 p-3 rounded-lg">
                <i class="fas fa-crosshairs text-primary text-xl"></i>
              </div>
              <div class="ml-4">
                <h3 class="text-sm font-medium text-gray-500">平均绝对误差 (MAE)</h3>
                <p class="mt-1 text-2xl font-semibold text-gray-900">{{ kpi.mae }}</p>
                <p class="mt-1 text-xs text-success flex items-center">
                  <i class="fas fa-arrow-down mr-1"></i>较上期降低12.3%
                </p>
              </div>
            </div>
          </div>
          <!-- RMSE -->
          <div class="bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md card-hover">
            <div class="flex items-start">
              <div class="flex-shrink-0 bg-purple-50 p-3 rounded-lg">
                <i class="fas fa-square-root-alt text-purple-600 text-xl"></i>
              </div>
              <div class="ml-4">
                <h3 class="text-sm font-medium text-gray-500">均方根误差 (RMSE)</h3>
                <p class="mt-1 text-2xl font-semibold text-gray-900">{{ kpi.rmse }}</p>
                <p class="mt-1 text-xs text-success flex items-center">
                  <i class="fas fa-arrow-down mr-1"></i>较上期降低8.7%
                </p>
              </div>
            </div>
          </div>
          <!-- 置信区间 -->
          <div class="bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md card-hover">
            <div class="flex items-start">
              <div class="flex-shrink-0 bg-green-50 p-3 rounded-lg">
                <i class="fas fa-check-circle text-green-600 text-xl"></i>
              </div>
              <div class="ml-4">
                <h3 class="text-sm font-medium text-gray-500">95%置信区间</h3>
                <p class="mt-1 text-2xl font-semibold text-gray-900">±{{ kpi.ci }}排名</p>
                <p class="mt-1 text-xs text-gray-500">覆盖95%的预测结果</p>
              </div>
            </div>
          </div>
          <!-- 准确率 -->
          <div class="bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md card-hover">
            <div class="flex items-start">
              <div class="flex-shrink-0 bg-amber-50 p-3 rounded-lg">
                <i class="fas fa-chart-pie text-amber-600 text-xl"></i>
              </div>
              <div class="ml-4">
                <h3 class="text-sm font-medium text-gray-500">预测准确率</h3>
                <p class="mt-1 text-2xl font-semibold text-gray-900">
                  {{ kpi.acc }}<span class="text-lg">%</span>
                </p>
                <p class="mt-1 text-xs text-success flex items-center">
                  <i class="fas fa-arrow-up mr-1"></i>较上期提升2.1%
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 历史预测准确率趋势 -->
        <div class="bg-white rounded-xl shadow-sm p-5 transition-all duration-300 hover:shadow-md card-hover">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-lg font-semibold text-gray-800">历史预测准确率趋势</h2>
            <div class="flex space-x-2">
              <button class="p-2 rounded hover:bg-gray-100 text-gray-600 transition-colors" @click="downloadAccuracy">
                <i class="fas fa-download"></i>
              </button>
            </div>
          </div>
          <div ref="accuracyRef" class="w-full h-[300px] bg-gray-50 rounded-lg p-2"></div>
        </div>
      </div>
    </div>

    <!-- 加载遮罩 -->
    <div
      id="loading-overlay"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      :class="state.isLoading ? '' : 'hidden'"
    >
      <div class="bg-white rounded-lg p-8 max-w-md w-full mx-4">
        <div class="flex flex-col items-center">
          <div class="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
          <h3 class="text-lg font-medium text-gray-800 mb-2">数据处理中</h3>
          <p class="text-gray-500 text-center">{{ loadingMessage }}</p>
        </div>
      </div>
    </div>

    <!-- 搜索弹窗 -->
    <div
      id="search-modal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      :class="showSearch ? '' : 'hidden'"
      @click.self="showSearch=false"
    >
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden flex flex-col">
        <div class="p-4 border-b flex justify-between items-center">
          <h3 class="text-lg font-medium text-gray-800">搜索应用</h3>
          <button class="text-gray-500 hover:text-gray-700" @click="showSearch=false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="p-4">
          <div class="relative">
            <input
              id="modal-app-search"
              v-model.trim="modalKeyword"
              type="text"
              placeholder="输入应用名称或ID"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-primary focus:border-primary sm:text-sm"
              @input="doModalSearch"
              autofocus
            />
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <i class="fas fa-search text-gray-400"></i>
            </div>
          </div>
          <div class="mt-2 text-sm text-gray-500">最多可选择3个应用进行对比</div>
        </div>
        <div class="flex-grow overflow-y-auto p-4">
          <div class="space-y-2">
            <div
              v-for="app in modalResults"
              :key="app.id"
              class="flex items-center p-3 rounded-lg transition-colors"
              :class="isSelected(app.id)?'bg-blue-50 border border-blue-200':'hover:bg-gray-50 border border-transparent'"
            >
              <div class="flex-shrink-0 h-10 w-10">
                <img :src="app.icon" :alt="app.name" class="h-10 w-10 rounded object-cover" />
              </div>
              <div class="ml-3 flex-grow">
                <div class="text-sm font-medium text-gray-900">{{ app.name }}</div>
                <div class="text-xs text-gray-500">ID: {{ app.id }}</div>
              </div>
              <div class="flex-shrink-0">
                <input
                  type="checkbox"
                  class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                  :checked="isSelected(app.id)"
                  @change="toggleSelect(app.id)"
                />
              </div>
            </div>
            <div v-if="!modalResults.length" class="text-center py-8 text-gray-500">
              {{ modalKeyword ? '未找到匹配的应用' : '请输入应用名称或ID进行搜索' }}
            </div>
          </div>
        </div>
        <div class="p-4 border-t flex justify-end">
          <button class="px-6 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors shadow-sm" @click="confirmSelection">
            确认选择
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 说明：本 SFC 严格保留了原 HTML 的样式与布局（Tailwind 类名未变），逻辑基于原生脚本等价迁移。
// 后续你可把 mock 数据替换为真实后端接口。

import * as echarts from 'echarts'
import { onMounted, onBeforeUnmount, reactive, ref, computed } from 'vue'

// ——— 状态 ———
const state = reactive({
  dateRange: 7 as 7|30|90,
  country: '' as string,
  device: 'iphone' as 'iphone'|'ipad'|'android',
  chartType: 'free' as 'free'|'paid'|'grossing',
  category: 'all' as string,
  selectedApps: [] as string[],
  countryData: [] as Array<{code:string; name:string}>,
  isLoading: false
})

const loadingMessage = ref('加载中...')
const searchKeyword = ref('')
const showSearch = ref(false)
const modalKeyword = ref('')
const modalResults = ref<Array<{id:string; name:string; publisher:string; icon:string}>>([])

// 设备/榜单类型字典（用于按钮）
const devices = [
  { value: 'iphone', label: 'iPhone' },
  { value: 'ipad', label: 'iPad' },
  { value: 'android', label: 'Android' },
]
const chartTypes = [
  { value: 'free', label: '免费' },
  { value: 'paid', label: '付费' },
  { value: 'grossing', label: '畅销' },
]

// ——— 模拟数据（保留原始逻辑） ———
const COLORS = ['#165DFF','#722ED1','#F53F3F','#FF7D00','#0FC6C2','#86909C','#00B42A','#F7BA1E','#8E44AD','#3498DB']

const mockCountries = [
  { code: 'us', name: '美国' },{ code: 'cn', name: '中国' },{ code: 'jp', name: '日本' },
  { code: 'de', name: '德国' },{ code: 'fr', name: '法国' },{ code: 'uk', name: '英国' },
  { code: 'ca', name: '加拿大' },{ code: 'au', name: '澳大利亚' },{ code: 'kr', name: '韩国' },
  { code: 'sg', name: '新加坡' }
]

const mockApps = [
  { id:'123456', name:'TikTok', publisher:'TikTok Inc.', icon:'https://design.gemcoder.com/staticResource/echoAiSystemImages/6d3cd0fc3500c413f385b5e57dd33a25.png' },
  { id:'1475863182', name:'Instagram', publisher:'Meta Platforms, Inc.', icon:'https://design.gemcoder.com/staticResource/echoAiSystemImages/49acdead6076f91bae19dc6b9cf6c12f.png' },
  { id:'389801252', name:'Facebook', publisher:'Meta Platforms, Inc.', icon:'https://design.gemcoder.com/staticResource/echoAiSystemImages/a03d1a5028bfa0ca868e34aac6784ec8.png' },
  { id:'544007664', name:'YouTube', publisher:'Google LLC', icon:'https://design.gemcoder.com/staticResource/echoAiSystemImages/b4fcc50077b661700453f861ba2e804f.png' },
  { id:'1142110895', name:'Snapchat', publisher:'Snap Inc.', icon:'https://design.gemcoder.com/staticResource/echoAiSystemImages/541477b363244fc06af9c0bcaebc7694.png' },
  { id:'328401282', name:'WhatsApp', publisher:'WhatsApp Inc.', icon:'https://design.gemcoder.com/staticResource/echoAiSystemImages/77b7cbe572f5b840e350a33352a996ea.png' },
  { id:'1451383635', name:'Telegram', publisher:'Telegram FZ-LLC', icon:'https://design.gemcoder.com/staticResource/echoAiSystemImages/44932a182f094f791b065a8831297739.png' },
  { id:'1280458064', name:'Spotify', publisher:'Spotify AB', icon:'https://design.gemcoder.com/staticResource/echoAiSystemImages/14cef10de33d8e94815ea40f68390213.png' },
  { id:'529479190', name:'WeChat', publisher:'Tencent Holdings Limited', icon:'https://design.gemcoder.com/staticResource/echoAiSystemImages/f5132f61e5cdc164f83330da706fa84f.png' },
  { id:'1444383602', name:'Zoom', publisher:'Zoom Video Communications, Inc.', icon:'https://design.gemcoder.com/staticResource/echoAiSystemImages/bb7190d678f5488cd3746a34b0fed6cd.png' },
  { id:'1055511498', name:'Netflix', publisher:'Netflix, Inc.', icon:'https://design.gemcoder.com/staticResource/echoAiSystemImages/575afb27644d2e3b2268c91b34934dfa.png' },
  { id:'1114214755', name:'Disney+', publisher:'Disney', icon:'https://design.gemcoder.com/staticResource/echoAiSystemImages/269614931cbef3394562f0f634889255.png' }
]

// 趋势图 mock
function generateMockTrendData(appIds: string[], days=7){
  const data:any[] = []
  const today = new Date()
  const dates:string[] = []
  for(let i=0;i<days;i++){
    const d = new Date(today)
    d.setDate(today.getDate()+i+1)
    dates.push(d.toLocaleDateString('zh-CN',{month:'numeric', day:'numeric'}))
  }
  appIds.forEach((id, idx)=>{
    const app = mockApps.find(a=>a.id===id) || {name:'未知应用', id}
    const baseRank = Math.floor(Math.random()*50)+1
    const ranks:number[] = []
    for(let i=0;i<days;i++){
      const fluct = Math.floor(Math.random()*10)-5
      let rank = baseRank + fluct + (i * (Math.random()>0.5?1:-1) * Math.random()*3)
      rank = Math.max(1, Math.round(rank))
      ranks.push(rank)
    }
    data.push({
      name: app.name,
      appId: app.id,
      type: 'line',
      data: ranks,
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { width:2, color: COLORS[idx%COLORS.length] },
      itemStyle: { color: COLORS[idx%COLORS.length] },
      emphasis: { focus:'series' },
      markPoint: { data: [{type:'max', name:'最高排名'},{type:'min', name:'最低排名'}] }
    })
  })
  return { dates, series:data }
}

// TopN mock
function generateMockTopNData(days=7){
  const shuffled = [...mockApps].sort(()=>0.5-Math.random())
  const topN = []
  for(let i=0;i<10;i++){
    const app = shuffled[i]
    const rank = i+1
    const prevRank = Math.max(1, rank + Math.floor(Math.random()*10)-5)
    const change = prevRank - rank
    const changePercent = Math.round(Math.abs(change)/prevRank*100)
    topN.push({
      rank,
      appName: app.name,
      publisher: app.publisher,
      appId: app.id,
      icon: app.icon,
      prevRank,
      change,
      changePercent
    })
  }
  return topN
}

// 历史准确率 mock
function generateMockAccuracyData(){
  const months = ['1月','2月','3月','4月','5月','6月']
  const acc = months.map(()=> 75 + Math.random()*15)
  return { months, accuracy: acc.map(a=> Math.round(a*10)/10) }
}

// ——— 选中应用映射 ———
const selectedAppObjects = computed(()=> state.selectedApps
  .map(id => mockApps.find(a=>a.id===id))
  .filter(Boolean) as typeof mockApps)

// ——— 图表实例 ———
const trendRef = ref<HTMLDivElement|null>(null)
const accuracyRef = ref<HTMLDivElement|null>(null)
let trendChart: echarts.ECharts | null = null
let accuracyChart: echarts.ECharts | null = null

// KPI 演示数据
const kpi = reactive({ mae:'3.78', rmse:'5.24', ci:'4.6', acc:'89.3' })

// TopN 表
const topNRows = ref<any[]>([])

// ——— 动作 ———
function setDateRange(d:7|30|90){ state.dateRange = d }

function openSearchModal(){
  showSearch.value = true
  modalKeyword.value = ''
  modalResults.value = []
}

function isSelected(id:string){ return state.selectedApps.includes(id) }

function toggleSelect(id:string){
  if (isSelected(id)) {
    state.selectedApps = state.selectedApps.filter(x=>x!==id)
  } else {
    if (state.selectedApps.length >= 3) return
    state.selectedApps.push(id)
  }
}

function confirmSelection(){ showSearch.value=false }

function removeSelected(id:string){
  state.selectedApps = state.selectedApps.filter(x=>x!==id)
}

function doModalSearch(){
  const key = modalKeyword.value.toLowerCase().trim()
  if(!key){ modalResults.value = []; return }
  modalResults.value = mockApps.filter(a=> a.name.toLowerCase().includes(key) || a.id.includes(key))
}

function onReset(){
  state.selectedApps = []
  renderTrendChart()
  renderTopNTable()

  // 重置筛选
  state.dateRange = 7
  state.device = 'iphone'
  state.chartType = 'free'
  state.category = 'all'
  state.country = state.countryData[0]?.code || ''
  searchKeyword.value = ''
}

function onAnalyze(){
  if (!state.selectedApps.length) {
    alert('请至少选择一个应用进行分析'); return
  }
  showLoading('正在分析数据并生成预测结果...')
  setTimeout(()=>{
    renderTrendChart()
    renderTopNTable()
    hideLoading()
  }, 600)
}

function downloadTrend(){ if(trendChart) trendChart.dispatchAction({type:'takeGlobalCursor'}) }
function fullscreenTrend(){ if(trendChart) trendChart.resize() }
function downloadTopN(){ /* 可扩展导出 */ }
function downloadAccuracy(){ if(accuracyChart) accuracyChart.resize() }

function showLoading(msg='加载中...'){ state.isLoading = true; loadingMessage.value = msg }
function hideLoading(){ state.isLoading = false }

// ——— 渲染图表 ———
function renderTrendChart(){
  if (!trendChart || !trendRef.value) return
  if (state.selectedApps.length===0){
    trendChart.setOption({
      title:{ text:'请选择应用进行分析', left:'center', top:'center', textStyle:{ color:'#9CA3AF', fontSize:16 }},
      tooltip:{ trigger:'axis', axisPointer:{ type:'cross' } },
      grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true },
      xAxis:{ type:'category', data:[] },
      yAxis:{ type:'value', inverse:true, min:1, axisLabel:{ formatter:'{value}' } },
      series:[]
    }, true)
    return
  }
  const { dates, series } = generateMockTrendData(state.selectedApps, state.dateRange)
  const maxRank = Math.max(...series.flatMap((s:any)=>s.data)) + 10
  const option: echarts.EChartsOption = {
    tooltip:{
      trigger:'axis',
      axisPointer:{ type:'cross', label:{ backgroundColor:'#6a7985' }},
      formatter(params:any){
        let res = `${params[0].name}<br/>`
        params.forEach((it:any)=>{
          res += `<span style="display:inline-block;margin-right:5px;width:10px;height:10px;border-radius:50%;background-color:${it.color};"></span>`
          res += `${it.seriesName}: 第${it.data}名<br/>`
        })
        return res
      }
    },
    legend:{ data: series.map((s:any)=>s.name), top:0, left:'center', orient:'horizontal', backgroundColor:'transparent', textStyle:{ fontSize:12 }},
    grid:{ left:'3%', right:'4%', bottom:'10%', top:'15%', containLabel:true },
    xAxis:{ type:'category', data:dates, axisLabel:{ interval:0, rotate:30, fontSize:12 }, axisLine:{ lineStyle:{ color:'#E5E7EB' } }, splitLine:{ show:false }},
    yAxis:{ type:'value', inverse:true, min:1, max:maxRank, axisLabel:{ formatter:'{value}' }, axisLine:{ show:false }, splitLine:{ lineStyle:{ color:'#F3F4F6' } } },
    series,
    dataZoom:[{ type:'slider', show:true, xAxisIndex:0, bottom:0, start:0, end:100, height:8, handleSize:'100%', backgroundColor:'#F3F4F6', fillerColor:'#CBD5E1', borderColor:'transparent' }]
  }
  trendChart.setOption(option, true)
}

function renderTopNTable(){
  topNRows.value = generateMockTopNData(state.dateRange)
}

function renderAccuracyChart(){
  if (!accuracyChart) return
  const { months, accuracy } = generateMockAccuracyData()
  const option: echarts.EChartsOption = {
    tooltip:{ trigger:'axis', axisPointer:{ type:'shadow' }, formatter:'{b}: {c}%' },
    grid:{ left:'3%', right:'4%', bottom:'3%', containLabel:true },
    xAxis:{ type:'category', data:months, axisLine:{ lineStyle:{ color:'#E5E7EB' } }, splitLine:{ show:false } },
    yAxis:{ type:'value', min:70, max:95, axisLabel:{ formatter:'{value}%' }, axisLine:{ show:false }, splitLine:{ lineStyle:{ color:'#F3F4F6' } } },
    series:[{
      name:'预测准确率', type:'line', data:accuracy, smooth:true, symbol:'circle', symbolSize:8,
      lineStyle:{ width:3, color:'#165DFF' }, itemStyle:{ color:'#165DFF', borderColor:'#fff', borderWidth:2 },
      areaStyle:{ color: new (echarts as any).graphic.LinearGradient(0,0,0,1,[{offset:0, color:'rgba(22, 93, 255, 0.3)'},{offset:1, color:'rgba(22, 93, 255, 0)'}]) },
      markLine:{ data:[{ type:'average', name:'平均值', lineStyle:{ color:'#FF7D00' } }], label:{ formatter:'平均值: {c}%' } }
    }]
  }
  accuracyChart.setOption(option, true)
}

// ——— 生命周期 ———
onMounted(()=>{
  // 初始化国家数据 & 默认选中
  state.countryData = mockCountries
  state.country = state.countryData[0]?.code || ''

  // init charts
  trendChart = echarts.init(trendRef.value as HTMLDivElement)
  accuracyChart = echarts.init(accuracyRef.value as HTMLDivElement)
  window.addEventListener('resize', onResize)

  // 初始渲染
  showLoading('初始化数据加载中...')
  setTimeout(()=>{
    renderTrendChart()
    renderTopNTable()
    renderAccuracyChart()
    hideLoading()
  }, 500)
})

onBeforeUnmount(()=>{
  window.removeEventListener('resize', onResize)
  trendChart?.dispose()
  accuracyChart?.dispose()
  trendChart = null
  accuracyChart = null
})

function onResize(){
  trendChart?.resize()
  accuracyChart?.resize()
}
</script>

<style scoped>
/* 保留原页面的视觉风格，Tailwind 类已写在模板中，这里无需额外样式 */
:deep(.card-hover){ transition: all .3s ease; }
:deep(.card-hover:hover){ transform: translateY(-4px); box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04); }

/* tailwind 扩展色名在你的项目里应已配置（primary 等）；如未配置，可在全局 tailwind.config.js 中加入。 */
</style>