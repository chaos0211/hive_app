<template>
  <div class="qimai-app-compare">
    <div class="header">
      <h1 class="main-title"> app对比分析</h1>
      <div class="sub-header">
        <h2>竞品对比分析</h2>
        <p>全面对比不同应用的市场表现与用户反馈</p>
      </div>
    </div>

    <div class="filter-bar">
      <div class="region-filters">
        <select v-model="selectedCountry" class="filter-select">
          <option v-if="countries.length===0" value="">全部</option>
          <option v-for="c in countries" :key="c" :value="c">{{ countryLabel(c) }}</option>
        </select>
      </div>
      <div class="platform-filters">
        <select v-model="selectedDevice" class="filter-select">
          <option v-if="devices.length===0" value="">全部</option>
          <option v-for="d in devices" :key="d" :value="d">{{ deviceLabel(d) }}</option>
        </select>
      </div>
      <div class="time-filter">
        <select v-model.number="windowDays">
          <option :value="30">最近30天</option>
          <option :value="90">最近90天</option>
          <option :value="365">最近一年</option>
        </select>
      </div>
      <button class="export-button">导出数据</button>
    </div>

    <div class="compare-apps-section">
      <div class="section-header" style="gap:12px;">
        <h3>对比应用</h3>
        <div class="search-box" style="display:flex; align-items:center; gap:8px; margin-left:auto;">
          <div class="search-input-wrap" style="position:relative;">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="输入应用名或 app_id"
              style="width:260px; padding:8px 36px 8px 12px; border:1px solid #e0e0e0; border-radius:4px;"
              @keyup.enter="doSearch"
            />
            <button
              class="filter-btn"
              style="position:absolute; right:4px; top:50%; transform:translateY(-50%); padding:6px 10px;"
              @click="doSearch"
            >搜索</button>
          </div>
          <button
            v-if="showClear"
            class="filter-btn"
            @click="clearSearch"
          >清空</button>
        </div>
      </div>

      <div v-if="showResults" class="search-results" style="background:#fff; border:1px solid #eaeaea; border-radius:8px; padding:12px; margin:12px 0;">
        <div v-if="limitedResults.length===0" style="color:#999;">未找到匹配的应用</div>
        <ul v-else style="list-style:none; padding:0; margin:0;">
          <li v-for="(it, idx) in limitedResults" :key="it.app_id || idx" style="display:flex; justify-content:space-between; align-items:center; padding:8px 4px; border-bottom:1px solid #f5f5f5;">
            <div>
              <strong>{{ it.app_name || '未知' }}</strong>
              <span style="color:#999; margin-left:8px;">{{ it.app_id }}</span>
            </div>
            <div>
              <button class="filter-btn" @click="addToCompare(it)" :disabled="isSelected(it.app_id) || selectedApps.length >= 3">
                {{ isSelected(it.app_id) ? '已加入' : (selectedApps.length >= 3 ? '已满' : '加入对比') }}
              </button>
            </div>
          </li>
        </ul>
        <div style="display:flex; justify-content:flex-end; margin-top:8px;">
          <button v-if="showMoreVisible" class="filter-btn" @click="expandMore">更多</button>
        </div>
      </div>

      <div class="apps-list">
        <div v-for="(app, idx) in selectedApps" :key="app.app_id || idx" class="app-item" style="position:relative;">
          <div class="app-icon" :style="app.icon_url ? { backgroundImage: `url(${app.icon_url})`, backgroundSize: 'cover', backgroundPosition: 'center' } : {}"></div>
          <div class="app-details">
            <div class="app-name">{{ app.app_name || '未知' }}</div>
            <div class="app-subtitle">{{ app.publisher || '' }}</div>
          </div>
          <button class="remove-btn" @click="removeFromCompare(app.app_id)" style="position:absolute;top:4px;right:4px;background:#fff;border:1px solid #eee;border-radius:50%;width:22px;height:22px;line-height:20px;text-align:center;cursor:pointer;font-size:18px;padding:0;">×</button>
        </div>
        <div v-for="n in (3 - selectedApps.length)" :key="'placeholder-'+n" class="app-item">
          <div class="app-icon"></div>
          <div class="app-details">
            <div class="app-name">未选择</div>
            <div class="app-subtitle">—</div>
          </div>
        </div>
      </div>
    </div>

    <div class="comparison-content">
      <div class="tabs-navigation">
        <button class="tab-button" :class="{ active: currentTab==='应用信息' }" @click="switchTab('应用信息')">应用信息</button>
        <button class="tab-button" :class="{ active: currentTab==='应用评分' }" @click="switchTab('应用评分')">应用评分</button>
        <button class="tab-button" :class="{ active: currentTab==='榜单排名' }" @click="switchTab('榜单排名')">榜单排名</button>
        <button class="tab-button" :class="{ active: currentTab==='下载量/收入' }" @click="switchTab('下载量/收入')">下载量/收入</button>
      </div>

      <!-- 基础信息表格 -->
      <div class="content-panel" v-show="currentTab==='应用信息'">
        <table class="comparison-table">
          <thead>
            <tr>
              <th class="info-category">信息类别</th>
              <th
                v-for="(app, idx) in selectedApps"
                :key="app.app_id || idx"
                class="app-column"
              >{{ app.app_name || '未选择' }}</th>
              <th
                v-for="n in (3 - selectedApps.length)"
                :key="'header-placeholder-'+n"
                class="app-column"
              >未选择</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="field in infoFields" :key="field.key">
              <td class="category-cell">{{ field.label }}</td>
              <td
                v-for="(app, idx) in selectedApps"
                :key="app.app_id || idx"
                class="data-cell"
              >{{ formatField(app, field) }}</td>
              <td
                v-for="n in (3 - selectedApps.length)"
                :key="'data-placeholder-'+field.key+'-'+n"
                class="data-cell"
              ></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 评分概况 -->
      <div class="content-panel" v-show="currentTab==='应用评分'">
        <div class="rating-section">
          <div class="rating-card">
            <h4>微信</h4>
            <div class="rating-overview">
              <span class="rating-score">4.6</span>
              <span class="rating-count">120,345 条评分</span>
            </div>
            <div class="rating-breakdown">
              <div class="rating-row">
                <span class="star-label">5 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 75%"></div>
                </div>
                <span class="rating-percent">75%</span>
              </div>
              <div class="rating-row">
                <span class="star-label">4 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 15%"></div>
                </div>
                <span class="rating-percent">15%</span>
              </div>
              <div class="rating-row">
                <span class="star-label">3 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 7%"></div>
                </div>
                <span class="rating-percent">7%</span>
              </div>
              <div class="rating-row">
                <span class="star-label">2 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 2%"></div>
                </div>
                <span class="rating-percent">2%</span>
              </div>
              <div class="rating-row">
                <span class="star-label">1 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 1%"></div>
                </div>
                <span class="rating-percent">1%</span>
              </div>
            </div>
          </div>

          <div class="rating-card">
            <h4>支付宝</h4>
            <div class="rating-overview">
              <span class="rating-score">4.4</span>
              <span class="rating-count">98,765 条评分</span>
            </div>
            <div class="rating-breakdown">
              <div class="rating-row">
                <span class="star-label">5 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 68%"></div>
                </div>
                <span class="rating-percent">68%</span>
              </div>
              <div class="rating-row">
                <span class="star-label">4 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 20%"></div>
                </div>
                <span class="rating-percent">20%</span>
              </div>
              <div class="rating-row">
                <span class="star-label">3 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 8%"></div>
                </div>
                <span class="rating-percent">8%</span>
              </div>
              <div class="rating-row">
                <span class="star-label">2 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 3%"></div>
                </div>
                <span class="rating-percent">3%</span>
              </div>
              <div class="rating-row">
                <span class="star-label">1 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 1%"></div>
                </div>
                <span class="rating-percent">1%</span>
              </div>
            </div>
          </div>

          <div class="rating-card">
            <h4>淘宝</h4>
            <div class="rating-overview">
              <span class="rating-score">4.5</span>
              <span class="rating-count">156,789 条评分</span>
            </div>
            <div class="rating-breakdown">
              <div class="rating-row">
                <span class="star-label">5 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 72%"></div>
                </div>
                <span class="rating-percent">72%</span>
              </div>
              <div class="rating-row">
                <span class="star-label">4 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 18%"></div>
                </div>
                <span class="rating-percent">18%</span>
              </div>
              <div class="rating-row">
                <span class="star-label">3 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 7%"></div>
                </div>
                <span class="rating-percent">7%</span>
              </div>
              <div class="rating-row">
                <span class="star-label">2 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 2%"></div>
                </div>
                <span class="rating-percent">2%</span>
              </div>
              <div class="rating-row">
                <span class="star-label">1 星</span>
                <div class="rating-bar">
                  <div class="rating-fill" style="width: 1%"></div>
                </div>
                <span class="rating-percent">1%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 下载量趋势 -->
      <div class="content-panel" v-show="currentTab==='下载量/收入'">
        <div class="chart-section">
          <h3>下载量趋势</h3>
          <div class="chart-controls">
            <button class="chart-btn active">近30天</button>
            <button class="chart-btn">近90天</button>
            <button class="chart-btn">近一年</button>
          </div>
          <div class="chart-container">
            <div class="chart-placeholder">下载量趋势图表</div>
          </div>
        </div>

        <div class="chart-section">
          <h3>收入趋势</h3>
          <div class="chart-controls">
            <button class="chart-btn active">近30天</button>
            <button class="chart-btn">近90天</button>
            <button class="chart-btn">近一年</button>
          </div>
          <div class="chart-container">
            <div class="chart-placeholder">收入趋势图表</div>
          </div>
        </div>
      </div>

      <!-- 榜单排名趋势 -->
      <div class="content-panel" v-show="currentTab==='榜单排名'">
        <div class="chart-section">
          <h3>榜单排名趋势</h3>
          <div class="ranking-controls">
            <div class="ranking-categories">
              <button class="ranking-btn active">总榜</button>
              <button class="ranking-btn">社交</button>
              <button class="ranking-btn">工具</button>
              <button class="ranking-btn">购物</button>
            </div>
            <div class="ranking-periods">
              <button class="period-btn" :class="{ active: trendWindow===7 }" @click="setTrendWindow(7)">近7天</button>
              <button class="period-btn" :class="{ active: trendWindow===30 }" @click="setTrendWindow(30)">近30天</button>
              <button class="period-btn" :class="{ active: trendWindow===180 }" @click="setTrendWindow(180)">近180天</button>
              <button class="period-btn" :class="{ active: trendWindow===365 }" @click="setTrendWindow(365)">近一年</button>
            </div>
          </div>
            <div class="chart-container">
              <RankTrendChart
              :dates="trendDates"
              :series="trendSeries"
              :loading="trendLoading"
              :error="trendError"
              :width="chartWidth"
              :height="chartHeight"
              :padding="chartPaddingX"
              :showAverage="true"
          />
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import '@/assets/app-compare.css'
import http from '@/api/http'
import RankTrendChart from '@/components/charts/RankTrendChart.vue'
export default {
  watch: {
  selectedCountry() { this.fetchTrend() },
  selectedDevice() { this.fetchTrend() },
  trendWindow()    { this.fetchTrend() },
  selectedApps: {
    handler() { this.fetchTrend() }, // 选中/移除应用时刷新趋势
    deep: true
  }
},
  name: 'AppCompare',
  components: { RankTrendChart },
  data() {
    return {
      currentTab: '应用信息',
      countries: [],
      devices: [],
      selectedCountry: '',
      selectedDevice: '',
      windowDays: 30,
      searchQuery: '',
      searchResults: [],
      showResults: false,
      showLimit: 5,
      showClear: false,
      selectedApps: [],
      trendWindow: 7,        // 默认近7天
      trendLoading: false,
      trendError: '',
      trendDates: [],
      trendSeries: [],
      chartWidth: 800,
      chartHeight: 300,
      chartPaddingX: 20,
      infoFields: [
        { key: 'app_name', label: '应用标题' },
        { key: 'publisher', label: '公司' },
        { key: 'price', label: '应用价格' },
        { key: 'release_date', label: '发布日期' },
        { key: 'update_date', label: '更新日期' },
        { key: 'version', label: '最新版本' },
        { key: 'file_size_mb', label: '应用包大小' },
        { key: 'age_rating', label: '年龄评级' },
        { key: 'devices_supported', label: '支持设备' },
        { key: 'language', label: '语言' },
      ]
    }
  },
  created() {
  this.loadOptions().then(() => {
    this.setTrendWindow(7)  // 默认近7天
    this.fetchTrend()
  })
},
  methods: {
    switchTab(name) { this.currentTab = name },
    countryLabel(code) {
      if (!code) return '全部'
      const map = { cn: '中国', us: '美国', jp: '日本', kr: '韩国' }
      return map[code] ? map[code] + '区' : code
    },
    deviceLabel(code) {
      const map = { iphone: 'iOS', ipad: 'iPad', android: 'Android' }
      return map[code] || code
    },
    async loadOptions() {
      try {
        const [cRes, dRes] = await Promise.all([
          http.get('/api/v1/meta/options', { params: { fields: 'country' } }),
          http.get('/api/v1/meta/options', { params: { fields: 'device' } }),
        ])
        const cJson = cRes.data || {}
        const dJson = dRes.data || {}
        this.countries = Array.isArray(cJson.country) ? cJson.country : []
        this.devices = Array.isArray(dJson.device) ? dJson.device : []
        // 默认值：有数据取第一条；否则为空代表“全部”
        if (this.countries.length > 0) this.selectedCountry = this.countries[0]
        if (this.devices.length > 0) this.selectedDevice = this.devices[0]
      } catch (e) {
        console.error('加载筛选项失败', e)
        this.countries = []
        this.devices = []
        this.selectedCountry = ''
        this.selectedDevice = ''
      }
    },
    isSelected(appId) {
      return this.selectedApps.some(a => a.app_id === appId)
    },
    addToCompare(item) {
      if (!item || !item.app_id) return
      if (this.isSelected(item.app_id)) return
      if (this.selectedApps.length >= 3) {
        alert('对比位已满（最多 3 个）')
        return
      }
      // 只取需要的字段
      const app = {
        app_id: item.app_id,
        app_name: item.app_name || '未知',
        icon_url: item.icon_url || '',
        publisher: item.publisher || '',
        details: {}
      }
      this.selectedApps.push(app)
      this.fetchAppDetail(app.app_id)
    },
    async fetchAppDetail(appId) {
      try {
        const res = await http.get(`/api/v1/apps/${appId}`, {
          params: {
            country: this.selectedCountry || undefined,
            device: this.selectedDevice || undefined,
            window: this.windowDays || undefined
          }
        })
        const detail = res.data || {}
        const idx = this.selectedApps.findIndex(a => a.app_id === appId)
        if (idx >= 0) {
          this.selectedApps[idx] = {
            ...this.selectedApps[idx],
            ...detail
          }
        }
      } catch (e) {
        console.error('加载应用详情失败', e)
      }
    },
    removeFromCompare(appId) {
      this.selectedApps = this.selectedApps.filter(a => a.app_id !== appId)
    },
    async doSearch() {
      const q = (this.searchQuery || '').trim()
      if (!q) {
        // 空关键词：不触发任何变化
        return
      }
      // 有关键词才开始搜索 & 显示结果
      this.showLimit = 5
      this.showResults = true
      this.searchResults = []
      const params = new URLSearchParams({ q })
      if (this.selectedCountry) params.append('country', this.selectedCountry)
      if (this.selectedDevice) params.append('device', this.selectedDevice)
      if (this.windowDays) params.append('window', String(this.windowDays))
      try {
        const res = await http.get('/api/v1/apps/search', { params: Object.fromEntries(params) })
        const data = res.data
        const items = Array.isArray(data?.items) ? data.items : []
        this.searchResults = items.slice(0, 10)
        this.showClear = true
      } catch (e) {
        console.error('搜索失败', e)
        this.searchResults = []
        // 若失败仍显示结果框（可能显示“未找到匹配的应用”），并显示清空按钮便于重试
        this.showResults = true
        this.showClear = true
      }
    },
    clearSearch() {
      this.searchQuery = ''
      this.searchResults = []
      this.showResults = false
      this.showLimit = 5
      this.showClear = false
    },
    expandMore() {
      // 点击“更多”后，展示上限改为 10，并隐藏“更多”按钮
          this.showLimit = 10
        },
        formatField(app, field) {
      const v = app?.[field.key]
      if (v === null || v === undefined) return ''
      if (field.key === 'price') {
        // 统一两位小数展示；后端可能返回字符串，如 "0.00"
        const num = Number(v)
        if (Number.isFinite(num)) {
          return `${num.toFixed(2)} 元`
        }
        // 若无法转为数字：
        if (typeof v === 'string') {
          const sv = v.trim()
          // 已是形如 1 或 1.0/1.00 的字符串，补齐到两位
          const m = sv.match(/^\d+(?:\.\d+)?$/)
          if (m) {
            const n = Number(sv)
            return `${n.toFixed(2)} 元`
          }
          // 其他字符串（极少见），原样附加单位
          return sv ? `${sv}元` : ''
        }
        return ''
      }
      // file_size_mb: 加上 MB 后缀；保留两位小数
      if (field.key === 'file_size_mb') {
        if (typeof v === 'number') return `${v.toFixed(2)} MB`
        const num = Number(v)
        return Number.isFinite(num) ? `${num.toFixed(2)} MB` : ''
      }
      // 默认：数字转字符串（保留 0），字符串原样或空
      if (typeof v === 'number') return String(v)
      return v || ''
    },
    setTrendWindow(days) {
        if (this.trendWindow === days) return
        this.trendWindow = days
        this.fetchTrend()
      },
      async fetchTrend() {
        if (!this.selectedApps.length) {
          this.trendDates = []
          this.trendSeries = []
          return
        }
        this.trendLoading = true
        this.trendError = ''
        try {
          const ids = this.selectedApps.map(a => a.app_id).join(',')
          const maxPoints = Math.max(400, this.trendWindow * this.selectedApps.length + 50)
          const res = await http.get('/api/v1/rankings/trend', {
            params: {
              app_ids: ids,
              country: this.selectedCountry || undefined,
              device: this.selectedDevice || undefined,
              window: this.trendWindow,   // 7/30/180/365
              fill_missing: true,
              max_points: maxPoints,
            }
          })
          const payload = res.data || {}
          const series = Array.isArray(payload.series) ? payload.series : []
          this.trendDates = series.length ? series[0].points.map(p => p[0]) : []
          this.trendSeries = series
        } catch (e) {
          console.error('加载排名趋势失败', e)
          this.trendError = '加载失败'
          this.trendDates = []
          this.trendSeries = []
        } finally {
          this.trendLoading = false
        }
      },
      seriesColor(i) {
        const palette = ['#5470C6', '#91CC75', '#FAC858', '#EE6666', '#73C0DE', '#3BA272']
        return palette[i % palette.length]
      },

// 各应用平均排名的 Y 坐标（仅用有数据的点）
  }
,
  computed: {
    limitedResults() {
      return this.searchResults.slice(0, this.showLimit)
    },
    showMoreVisible() {
      // 即使少于 5 条，也要求显示“更多”按钮；点击后隐藏
      return this.showLimit === 5
    }
  },
}
</script>
