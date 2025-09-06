<template>
  <div class="bg-secondary text-gray-200 font-inter min-h-screen bg-grid">
    <!-- 顶部导航栏 -->
    <header class="bg-primary/80 backdrop-blur-md border-b border-accent/20 sticky top-0 z-50">
      <div class="container mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-accent to-success flex items-center justify-center">
            <i class="fas fa-cloud text-white text-xl"></i>
          </div>
          <h1 class="text-[clamp(1.2rem,3vw,1.5rem)] font-bold text-white text-shadow">
            云管理平台数据大屏
          </h1>
        </div>
        <div class="flex items-center space-x-6">
          <div class="hidden md:flex items-center space-x-4">
            <div class="flex items-center space-x-2">
              <i class="fas fa-calendar-alt text-accent"></i>
              <span class="text-sm">{{ currentDate }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <i class="fas fa-clock text-accent"></i>
              <span class="text-sm">{{ currentTime }}</span>
            </div>
          </div>
          <div class="flex items-center space-x-3">
            <button class="w-9 h-9 rounded-full bg-dark-light flex items-center justify-center hover:bg-accent/20 transition-colors">
              <i class="fas fa-bell text-gray-300"></i>
            </button>
            <div class="flex items-center space-x-2">
              <img
                src="https://design.gemcoder.com/staticResource/echoAiSystemImages/56618f14ad2edddada7a9b5466558bb3.png"
                alt="用户头像"
                class="w-9 h-9 rounded-full object-cover border-2 border-accent/50"
              />
              <span class="hidden md:inline text-sm font-medium">管理员</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="container mx-auto px-4 py-6">
      <!-- 概览统计卡片 -->
      <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <!-- 订单总数 -->
        <div class="bg-primary/50 rounded-lg p-4 gradient-border card-glow">
          <div class="flex justify-between items-start mb-3">
            <div>
              <p class="text-gray-400 text-sm">订单总数</p>
              <h3 class="text-2xl font-bold mt-1">{{ stats.totalOrders }}</h3>
            </div>
            <div class="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center">
              <i class="fas fa-shopping-cart text-accent"></i>
            </div>
          </div>
          <div class="flex items-center text-sm">
            <span class="text-success flex items-center">
              <i class="fas fa-arrow-up mr-1"></i>
              12.5%
            </span>
            <span class="text-gray-400 ml-2">较上月</span>
          </div>
        </div>

        <!-- 已完成订单 -->
        <div class="bg-primary/50 rounded-lg p-4 gradient-border card-glow">
          <div class="flex justify-between items-start mb-3">
            <div>
              <p class="text-gray-400 text-sm">已完成订单</p>
              <h3 class="text-2xl font-bold mt-1">{{ stats.completedOrders }}</h3>
            </div>
            <div class="w-10 h-10 rounded-full bg-success/20 flex items-center justify-center">
              <i class="fas fa-check-circle text-success"></i>
            </div>
          </div>
          <div class="flex items-center text-sm">
            <span class="text-success flex items-center">
              <i class="fas fa-arrow-up mr-1"></i>
              8.3%
            </span>
            <span class="text-gray-400 ml-2">较上月</span>
          </div>
        </div>

        <!-- 运行中虚拟机 -->
        <div class="bg-primary/50 rounded-lg p-4 gradient-border card-glow">
          <div class="flex justify-between items-start mb-3">
            <div>
              <p class="text-gray-400 text-sm">运行中虚拟机</p>
              <h3 class="text-2xl font-bold mt-1">{{ stats.runningVms }}</h3>
            </div>
            <div class="w-10 h-10 rounded-full bg-warning/20 flex items-center justify-center">
              <i class="fas fa-server text-warning"></i>
            </div>
          </div>
          <div class="flex items-center text-sm">
            <span class="text-success flex items-center">
              <i class="fas fa-arrow-up mr-1"></i>
              5.7%
            </span>
            <span class="text-gray-400 ml-2">较上月</span>
          </div>
        </div>

        <!-- 资源利用率 -->
        <div class="bg-primary/50 rounded-lg p-4 gradient-border card-glow">
          <div class="flex justify-between items-start mb-3">
            <div>
              <p class="text-gray-400 text-sm">资源利用率</p>
              <h3 class="text-2xl font-bold mt-1">{{ stats.resourceUsage }}</h3>
            </div>
            <div class="w-10 h-10 rounded-full bg-danger/20 flex items-center justify-center">
              <i class="fas fa-chart-pie text-danger"></i>
            </div>
          </div>
          <div class="flex items-center text-sm">
            <span class="text-danger flex items-center">
              <i class="fas fa-arrow-up mr-1"></i>
              3.2%
            </span>
            <span class="text-gray-400 ml-2">较上月</span>
          </div>
        </div>
      </section>

      <!-- 图表和详细数据区域 -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- 左侧区域 -->
        <div class="space-y-6">
          <!-- 操作系统分类 -->
          <div class="bg-primary/50 rounded-lg p-5 gradient-border card-glow">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold">操作系统分类</h2>
              <div class="text-sm text-gray-400">
                <i class="fas fa-sync-alt mr-1"></i>
                实时
              </div>
            </div>
            <div class="h-[250px]" ref="osDistributionChart"></div>
          </div>

          <!-- 虚拟机运行状态 -->
          <div class="bg-primary/50 rounded-lg p-5 gradient-border card-glow">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold">虚拟机运行状态</h2>
              <div class="text-sm text-gray-400">
                <i class="fas fa-sync-alt mr-1"></i>
                实时
              </div>
            </div>
            <div class="h-[250px]" ref="vmStatusChart"></div>
          </div>

          <!-- 资源使用统计 -->
          <div class="bg-primary/50 rounded-lg p-5 gradient-border card-glow">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold">资源使用统计</h2>
              <div class="text-sm text-gray-400">
                <i class="fas fa-calendar-alt mr-1"></i>
                本月
              </div>
            </div>
            <div class="space-y-4">
              <div v-for="resource in resourceStats" :key="resource.name">
                <div class="flex justify-between mb-1">
                  <span class="text-sm">{{ resource.name }}</span>
                  <span class="text-sm font-medium">{{ resource.value }}%</span>
                </div>
                <div class="w-full bg-dark-light rounded-full h-2">
                  <div
                    :class="resource.colorClass"
                    class="h-2 rounded-full"
                    :style="{ width: resource.value + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 中间区域 -->
        <div class="space-y-6 lg:col-span-1">
          <!-- 虚拟机创建/回收趋势 -->
          <div class="bg-primary/50 rounded-lg p-5 gradient-border card-glow">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold">虚拟机创建/回收趋势</h2>
              <div class="text-sm text-gray-400">
                <i class="fas fa-calendar-alt mr-1"></i>
                近30天
              </div>
            </div>
            <div class="h-[300px]" ref="vmTrendChart"></div>
          </div>

          <!-- 服务健康状态 -->
          <div class="bg-primary/50 rounded-lg p-5 gradient-border card-glow">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold">服务健康状态</h2>
              <div class="text-sm text-gray-400">
                <i class="fas fa-sync-alt mr-1"></i>
                实时
              </div>
            </div>
            <div class="space-y-3">
              <div
                v-for="service in serviceStatus"
                :key="service.name"
                class="flex items-center justify-between p-3 bg-dark/50 rounded-lg"
              >
                <div class="flex items-center">
                  <div :class="service.statusDotClass" class="w-3 h-3 rounded-full mr-3"></div>
                  <span>{{ service.name }}</span>
                </div>
                <span :class="service.statusTextClass" class="text-sm">{{ service.statusText }}</span>
              </div>
            </div>
          </div>

          <!-- 最近告警信息 -->
          <div class="bg-primary/50 rounded-lg p-5 gradient-border card-glow">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold">最近告警信息</h2>
              <button class="text-sm text-accent hover:underline">查看全部</button>
            </div>
            <div class="space-y-3 max-h-[200px] overflow-y-auto pr-1">
              <div
                v-for="alert in alerts"
                :key="alert.id"
                :class="alert.borderClass"
                class="p-3 bg-dark/50 rounded-lg border-l-2"
              >
                <div class="flex justify-between items-start">
                  <h4 class="font-medium">{{ alert.title }}</h4>
                  <span class="text-xs text-gray-400">{{ alert.time }}</span>
                </div>
                <p class="text-sm text-gray-400 mt-1">{{ alert.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧区域 -->
        <div class="space-y-6">
          <!-- 订单分类统计 -->
          <div class="bg-primary/50 rounded-lg p-5 gradient-border card-glow">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold">订单分类统计</h2>
              <div class="text-sm text-gray-400">
                <i class="fas fa-calendar-alt mr-1"></i>
                本月
              </div>
            </div>
            <div class="h-[250px]" ref="orderCategoryChart"></div>
          </div>

          <!-- 订单创建/回收趋势 -->
          <div class="bg-primary/50 rounded-lg p-5 gradient-border card-glow">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold">订单创建/回收趋势</h2>
              <div class="text-sm text-gray-400">
                <i class="fas fa-calendar-alt mr-1"></i>
                近30天
              </div>
            </div>
            <div class="h-[250px]" ref="orderTrendChart"></div>
          </div>

          <!-- 虚拟机TOP10排行 -->
          <div class="bg-primary/50 rounded-lg p-5 gradient-border card-glow">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold">APP TOP10排行</h2>
              <div class="flex space-x-2">
                <button
                  :class="[
                    'px-2 py-1 text-xs rounded hover:bg-accent/30 transition-colors',
                    activeTab === 'system' ? 'bg-accent/20 text-accent' : 'bg-dark-light text-gray-300 hover:bg-dark-light/80'
                  ]"
                  @click="activeTab = 'system'"
                >
                  免费榜
                </button>
                <button
                  :class="[
                    'px-2 py-1 text-xs rounded hover:bg-accent/30 transition-colors',
                    activeTab === 'organization' ? 'bg-accent/20 text-accent' : 'bg-dark-light text-gray-300 hover:bg-dark-light/80'
                  ]"
                  @click="activeTab = 'organization'"
                >
                  付费榜
                </button>
              </div>
            </div>
            <div class="space-y-3 max-h-[200px] overflow-y-auto pr-1">
              <div
                v-for="(item, index) in topVms"
                :key="item.name"
                class="flex items-center justify-between p-2"
              >
                <div class="flex items-center">
                  <div
                    :class="item.rankBgClass"
                    class="w-8 h-8 rounded flex items-center justify-center mr-3"
                  >
                    <span :class="item.rankTextClass" class="font-medium">{{ index + 1 }}</span>
                  </div>
                  <div>
                    <h4 class="text-sm font-medium">{{ item.name }}</h4>
                    <p class="text-xs text-gray-400">{{ item.count }}台虚拟机</p>
                  </div>
                </div>
                <div class="w-24 bg-dark-light h-2 rounded-full overflow-hidden">
                  <div
                    :class="item.barColorClass"
                    class="h-full rounded-full"
                    :style="{ width: item.percentage + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <footer class="bg-primary/80 backdrop-blur-md border-t border-accent/20 py-4 mt-8">
      <div class="container mx-auto px-4 text-center text-sm text-gray-400">
        <p>© 2023 云管理平台数据大屏 | 系统版本 v2.5.3</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'

// 响应式数据
const currentDate = ref('')
const currentTime = ref('')
const activeTab = ref('system')

// 统计数据
const stats = ref({
  totalOrders: '12,845',
  completedOrders: '9,632',
  runningVms: '348',
  resourceUsage: '68.2%'
})

// 资源使用统计
const resourceStats = ref([
  { name: 'CPU使用率', value: 68, colorClass: 'bg-accent' },
  { name: '内存使用率', value: 75, colorClass: 'bg-success' },
  { name: '磁盘使用率', value: 42, colorClass: 'bg-warning' },
  { name: '网络流量', value: 83, colorClass: 'bg-danger' }
])

// 服务状态
const serviceStatus = ref([
  { name: '云服务器', statusDotClass: 'bg-success', statusTextClass: 'text-success', statusText: '正常运行中' },
  { name: '负载均衡', statusDotClass: 'bg-success', statusTextClass: 'text-success', statusText: '正常运行中' },
  { name: '数据库服务', statusDotClass: 'bg-warning', statusTextClass: 'text-warning', statusText: '负载较高' },
  { name: '对象存储', statusDotClass: 'bg-success', statusTextClass: 'text-success', statusText: '正常运行中' },
  { name: '监控服务', statusDotClass: 'bg-danger', statusTextClass: 'text-danger', statusText: '部分异常' }
])

// 告警信息
const alerts = ref([
  {
    id: 1,
    title: 'CPU使用率过高',
    description: '服务器 VM-8472 的CPU使用率持续15分钟超过90%',
    time: '10分钟前',
    borderClass: 'border-danger'
  },
  {
    id: 2,
    title: '磁盘空间不足',
    description: '服务器 VM-3256 的磁盘空间剩余不足10%',
    time: '1小时前',
    borderClass: 'border-warning'
  },
  {
    id: 3,
    title: '内存使用率警告',
    description: '服务器 VM-1983 的内存使用率达到85%',
    time: '3小时前',
    borderClass: 'border-warning'
  },
  {
    id: 4,
    title: '服务重启成功',
    description: '数据库服务已成功重启完成',
    time: '5小时前',
    borderClass: 'border-accent'
  }
])

// TOP虚拟机数据
const topVms = ref([
  {
    name: '企业资源管理系统',
    count: 128,
    percentage: 85,
    rankBgClass: 'bg-accent/20',
    rankTextClass: 'text-accent',
    barColorClass: 'bg-accent'
  },
  {
    name: '客户关系管理系统',
    count: 96,
    percentage: 72,
    rankBgClass: 'bg-success/20',
    rankTextClass: 'text-success',
    barColorClass: 'bg-success'
  },
  {
    name: '人力资源管理系统',
    count: 78,
    percentage: 65,
    rankBgClass: 'bg-warning/20',
    rankTextClass: 'text-warning',
    barColorClass: 'bg-warning'
  },
  {
    name: '财务管理系统',
    count: 65,
    percentage: 58,
    rankBgClass: 'bg-danger/20',
    rankTextClass: 'text-danger',
    barColorClass: 'bg-danger'
  },
  {
    name: '供应链管理系统',
    count: 42,
    percentage: 45,
    rankBgClass: 'bg-dark-light',
    rankTextClass: 'text-gray-300',
    barColorClass: 'bg-gray-400'
  }
])

// 图表引用
const osDistributionChart = ref(null)
const vmStatusChart = ref(null)
const vmTrendChart = ref(null)
const orderCategoryChart = ref(null)
const orderTrendChart = ref(null)

// 图表实例
let charts = []
let timeInterval = null

// 更新日期时间
const updateDateTime = () => {
  const now = new Date()

  const dateOptions = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
  currentDate.value = now.toLocaleDateString('zh-CN', dateOptions)

  const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit' }
  currentTime.value = now.toLocaleTimeString('zh-CN', timeOptions)
}

// 防抖函数
const debounce = (func, wait) => {
  let timeout
  return function(...args) {
    clearTimeout(timeout)
    timeout = setTimeout(() => func.apply(this, args), wait)
  }
}

// 初始化图表
const initCharts = () => {
  // 操作系统分类图表
  const osChart = echarts.init(osDistributionChart.value)
  const osOption = {
    color: ['#16C2D5', '#00CF95', '#FFC107', '#FF5252', '#7B61FF'],
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      textStyle: {
        color: '#ccc'
      }
    },
    series: [
      {
        name: '操作系统',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 4,
          borderColor: '#0A1931',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            color: '#fff'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 420, name: 'Linux' },
          { value: 280, name: 'Windows' },
          { value: 120, name: 'macOS' },
          { value: 80, name: 'Unix' },
          { value: 50, name: '其他' }
        ]
      }
    ]
  }
  osChart.setOption(osOption)

  // 虚拟机运行状态图表
  const vmChart = echarts.init(vmStatusChart.value)
  const vmOption = {
    color: ['#00CF95', '#FFC107', '#FF5252', '#7B61FF'],
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [
      {
        name: '运行状态',
        type: 'pie',
        radius: '70%',
        center: ['50%', '50%'],
        data: [
          { value: 280, name: '运行中' },
          { value: 45, name: '已停止' },
          { value: 15, name: '异常' },
          { value: 8, name: '维护中' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  vmChart.setOption(vmOption)

  // 虚拟机创建/回收趋势图表
  const vmTrendChartInstance = echarts.init(vmTrendChart.value)
  const vmTrendOption = {
    color: ['#16C2D5', '#FF5252'],
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['1日', '5日', '10日', '15日', '20日', '25日', '30日'],
      axisLine: {
        lineStyle: {
          color: '#334155'
        }
      },
      axisLabel: {
        color: '#94a3b8'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#334155'
        }
      },
      axisLabel: {
        color: '#94a3b8'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.05)'
        }
      }
    },
    series: [
      {
        name: '创建',
        type: 'line',
        smooth: true,
        data: [120, 190, 150, 230, 180, 250, 210],
        lineStyle: {
          width: 3
        },
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: {
          borderWidth: 2,
          borderColor: '#0A1931'
        }
      },
      {
        name: '回收',
        type: 'line',
        smooth: true,
        data: [80, 120, 100, 150, 130, 180, 160],
        lineStyle: {
          width: 3
        },
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: {
          borderWidth: 2,
          borderColor: '#0A1931'
        }
      }
    ]
  }
  vmTrendChartInstance.setOption(vmTrendOption)

  // 订单分类统计图表
  const orderCategoryChartInstance = echarts.init(orderCategoryChart.value)
  const orderCategoryOption = {
    color: ['#16C2D5', '#00CF95', '#FFC107', '#FF5252', '#7B61FF'],
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['云服务器', '数据库', '存储', '网络', '安全'],
      axisLine: {
        lineStyle: {
          color: '#334155'
        }
      },
      axisLabel: {
        color: '#94a3b8',
        rotate: 30,
        interval: 0
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#334155'
        }
      },
      axisLabel: {
        color: '#94a3b8'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.05)'
        }
      }
    },
    series: [
      {
        name: '订单数量',
        type: 'bar',
        barWidth: '60%',
        data: [3200, 1800, 1500, 1200, 900],
        itemStyle: {
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  }
  orderCategoryChartInstance.setOption(orderCategoryOption)

  // 订单创建/回收趋势图表
  const orderTrendChartInstance = echarts.init(orderTrendChart.value)
  const orderTrendOption = {
    color: ['#00CF95', '#FF5252'],
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['创建', '取消'],
      textStyle: {
        color: '#ccc'
      },
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['1日', '5日', '10日', '15日', '20日', '25日', '30日'],
      axisLine: {
        lineStyle: {
          color: '#334155'
        }
      },
      axisLabel: {
        color: '#94a3b8'
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        lineStyle: {
          color: '#334155'
        }
      },
      axisLabel: {
        color: '#94a3b8'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.05)'
        }
      }
    },
    series: [
      {
        name: '创建',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        data: [1200, 1900, 1500, 2300, 1800, 2500, 2100],
        itemStyle: {
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '取消',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        data: [300, 500, 400, 600, 500, 700, 600],
        itemStyle: {
          borderRadius: [4, 4, 0, 0]
        }
      }
    ]
  }
  orderTrendChartInstance.setOption(orderTrendOption)

  // 保存图表实例
  charts = [osChart, vmChart, vmTrendChartInstance, orderCategoryChartInstance, orderTrendChartInstance]
}

// 调整图表大小
const resizeCharts = debounce(() => {
  charts.forEach(chart => {
    chart.resize()
  })
}, 300)

// 生命周期
onMounted(async () => {
  // 设置当前日期和时间
  updateDateTime()
  timeInterval = setInterval(updateDateTime, 1000)

  // 等待DOM渲染完成后初始化图表
  await nextTick()
  initCharts()

  // 监听窗口大小变化
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  // 清理定时器
  if (timeInterval) {
    clearInterval(timeInterval)
  }

  // 销毁图表实例
  charts.forEach(chart => {
    chart.dispose()
  })

  // 移除事件监听
  window.removeEventListener('resize', resizeCharts)
})
</script>

<style>
/* 导入外部CSS */
@import url('https://cdn.tailwindcss.com');
@import url('https://cdn.bootcdn.net/ajax/libs/font-awesome/6.4.0/css/all.min.css');

/* Tailwind CSS 配置 - 这些是原文件中的颜色定义 */
.bg-primary { background-color: #0F2E58; }
.bg-primary\/50 { background-color: rgba(15, 46, 88, 0.5); }
.bg-primary\/80 { background-color: rgba(15, 46, 88, 0.8); }
.bg-secondary { background-color: #0A1931; }
.bg-accent { background-color: #16C2D5; }
.bg-accent\/20 { background-color: rgba(22, 194, 213, 0.2); }
.bg-accent\/30 { background-color: rgba(22, 194, 213, 0.3); }
.bg-success { background-color: #00CF95; }
.bg-success\/20 { background-color: rgba(0, 207, 149, 0.2); }
.bg-warning { background-color: #FFC107; }
.bg-warning\/20 { background-color: rgba(255, 193, 7, 0.2); }
.bg-danger { background-color: #FF5252; }
.bg-danger\/20 { background-color: rgba(255, 82, 82, 0.2); }
.bg-dark { background-color: #051024; }
.bg-dark\/50 { background-color: rgba(5, 16, 36, 0.5); }
.bg-dark-light { background-color: #1E293B; }
.bg-dark-light\/80 { background-color: rgba(30, 41, 59, 0.8); }

.text-accent { color: #16C2D5; }
.text-success { color: #00CF95; }
.text-warning { color: #FFC107; }
.text-danger { color: #FF5252; }

.border-accent\/20 { border-color: rgba(22, 194, 213, 0.2); }
.border-accent\/50 { border-color: rgba(22, 194, 213, 0.5); }
.border-accent { border-color: #16C2D5; }
.border-danger { border-color: #FF5252; }
.border-warning { border-color: #FFC107; }

.from-accent { --tw-gradient-from: #16C2D5; }
.to-success { --tw-gradient-to: #00CF95; }

/* 原文件中的自定义样式 */
.content-auto {
  content-visibility: auto;
}

.text-shadow {
  text-shadow: 0 0 8px rgba(22, 194, 213, 0.5);
}

.bg-grid {
  background-image: radial-gradient(rgba(22, 194, 213, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
}

.card-glow {
  box-shadow: 0 0 15px rgba(22, 194, 213, 0.15);
}

.gradient-border {
  position: relative;
  border-radius: 0.5rem;
  z-index: 0;
}

.gradient-border::before {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: 0.5rem;
  padding: 1px;
  background: linear-gradient(45deg, #16C2D5, #00CF95);
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  z-index: -1;
}

/* 基础样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', sans-serif;
}

/* Tailwind 基础类 */
.min-h-screen { min-height: 100vh; }
.container { max-width: 1200px; margin: 0 auto; }
.mx-auto { margin-left: auto; margin-right: auto; }
.px-4 { padding-left: 1rem; padding-right: 1rem; }
.py-3 { padding-top: 0.75rem; padding-bottom: 0.75rem; }
.py-4 { padding-top: 1rem; padding-bottom: 1rem; }
.py-6 { padding-top: 1.5rem; padding-bottom: 1.5rem; }
.p-2 { padding: 0.5rem; }
.p-3 { padding: 0.75rem; }
.p-4 { padding: 1rem; }
.p-5 { padding: 1.25rem; }
.m-0 { margin: 0; }
.mr-1 { margin-right: 0.25rem; }
.mr-3 { margin-right: 0.75rem; }
.ml-2 { margin-left: 0.5rem; }
.mt-1 { margin-top: 0.25rem; }
.mt-8 { margin-top: 2rem; }
.mb-1 { margin-bottom: 0.25rem; }
.mb-3 { margin-bottom: 0.75rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-6 { margin-bottom: 1.5rem; }
.w-3 { width: 0.75rem; }
.w-8 { width: 2rem; }
.w-9 { width: 2.25rem; }
.w-10 { width: 2.5rem; }
.w-24 { width: 6rem; }
.w-full { width: 100%; }
.h-2 { height: 0.5rem; }
.h-3 { height: 0.75rem; }
.h-8 { height: 2rem; }
.h-9 { height: 2.25rem; }
.h-10 { height: 2.5rem; }
.max-h-\[200px\] { max-height: 200px; }
.h-\[250px\] { height: 250px; }
.h-\[300px\] { height: 300px; }
.text-xs { font-size: 0.75rem; }
.text-sm { font-size: 0.875rem; }
.text-lg { font-size: 1.125rem; }
.text-xl { font-size: 1.25rem; }
.text-2xl { font-size: 1.5rem; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }
.text-white { color: #ffffff; }
.text-gray-200 { color: #e5e7eb; }
.text-gray-300 { color: #d1d5db; }
.text-gray-400 { color: #9ca3af; }
.rounded { border-radius: 0.25rem; }
.rounded-lg { border-radius: 0.5rem; }
.rounded-full { border-radius: 9999px; }
.border-2 { border-width: 2px; }
.border-b { border-bottom-width: 1px; }
.border-l-2 { border-left-width: 2px; }
.border-t { border-top-width: 1px; }
.flex { display: flex; }
.grid { display: grid; }
.hidden { display: none; }
.items-center { align-items: center; }
.items-start { align-items: flex-start; }
.justify-between { justify-content: space-between; }
.justify-center { justify-content: center; }
.space-x-2 > * + * { margin-left: 0.5rem; }
.space-x-3 > * + * { margin-left: 0.75rem; }
.space-x-4 > * + * { margin-left: 1rem; }
.space-x-6 > * + * { margin-left: 1.5rem; }
.space-y-3 > * + * { margin-top: 0.75rem; }
.space-y-4 > * + * { margin-top: 1rem; }
.space-y-6 > * + * { margin-top: 1.5rem; }
.grid-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }
.gap-4 { gap: 1rem; }
.gap-6 { gap: 1.5rem; }
.sticky { position: sticky; }
.top-0 { top: 0; }
.z-50 { z-index: 50; }
.overflow-hidden { overflow: hidden; }
.overflow-y-auto { overflow-y: auto; }
.object-cover { object-fit: cover; }
.backdrop-blur-md { backdrop-filter: blur(12px); }
.transition-colors { transition-property: color, background-color, border-color, text-decoration-color, fill, stroke; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }
.hover\:bg-accent\/20:hover { background-color: rgba(22, 194, 213, 0.2); }
.hover\:bg-accent\/30:hover { background-color: rgba(22, 194, 213, 0.3); }
.hover\:bg-dark-light\/80:hover { background-color: rgba(30, 41, 59, 0.8); }
.hover\:underline:hover { text-decoration-line: underline; }
.text-center { text-align: center; }
.pr-1 { padding-right: 0.25rem; }

/* 响应式类 */
@media (min-width: 768px) {
  .md\:flex { display: flex; }
  .md\:inline { display: inline; }
  .md\:grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (min-width: 1024px) {
  .lg\:grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .lg\:grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .lg\:col-span-1 { grid-column: span 1 / span 1; }
}

/* 渐变类 */
.bg-gradient-to-br { background-image: linear-gradient(to bottom right, var(--tw-gradient-stops)); }
.bg-gradient-to-br.from-accent.to-success {
  background-image: linear-gradient(to bottom right, #16C2D5, #00CF95);
}

/* 动态类 */
.text-\[clamp\(1\.2rem\,3vw\,1\.5rem\)\] {
  font-size: clamp(1.2rem, 3vw, 1.5rem);
}
</style>