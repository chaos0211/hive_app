<template>
  <div class="page">
    <h2 class="title">手机应用榜单 · 榜单列表</h2>

    <!-- 筛选区 -->
    <form class="filters" @submit.prevent="onSearch">
      <div class="row">
        <label>
          榜单日期：
          <input type="date" v-model="q.chart_date" />
        </label>

        <label>
          类型（brand_id）：
          <select v-model="q.brand_id">
            <option value="">全部</option>
            <option :value="0">0 - 付费</option>
            <option :value="1">1 - 免费</option>
            <option :value="2">2 - 畅销</option>
          </select>
        </label>

        <label>
          应用大类（app_genre）：
          <input type="text" v-model.trim="q.app_genre" placeholder="如: GAME / TOOLS ..." />
        </label>

        <label>
          是否广告（is_ad）：
          <select v-model="q.is_ad">
            <option value="">全部</option>
            <option :value="true">有</option>
            <option :value="false">无</option>
          </select>
        </label>
      </div>

      <div class="row">
        <label>
          价格区间（¥）：
          <input class="price" type="number" step="0.01" v-model.number="q.price_min" placeholder="最低价" />
          <span class="sep">—</span>
          <input class="price" type="number" step="0.01" v-model.number="q.price_max" placeholder="最高价" />
        </label>

        <label>
          国家（country）：
          <input type="text" v-model.trim="q.country" placeholder="默认 cn" />
        </label>

        <label>
          设备（device）：
          <input type="text" v-model.trim="q.device" placeholder="默认 iphone" />
        </label>

        <label>
          榜单细分（genre）：
          <input type="text" v-model.trim="q.genre" placeholder="如: GAME_ACTION" />
        </label>
      </div>

      <div class="row actions">
        <button type="submit">查询</button>
        <button type="button" class="ghost" @click="onReset">重置</button>
      </div>
    </form>

    <!-- 表格 -->
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th @click="sort('chart_date')">榜单日期 {{ sortIcon('chart_date') }}</th>
            <th @click="sort('brand_id')">类型 {{ sortIcon('brand_id') }}</th>
            <th @click="sort('country')">国家 {{ sortIcon('country') }}</th>
            <th @click="sort('device')">设备 {{ sortIcon('device') }}</th>
            <th @click="sort('genre')">细分 {{ sortIcon('genre') }}</th>
            <th @click="sort('app_genre')">大类 {{ sortIcon('app_genre') }}</th>

            <th @click="sort('index')">序位 {{ sortIcon('index') }}</th>
            <th @click="sort('ranking')">排名 {{ sortIcon('ranking') }}</th>
            <th @click="sort('change')">变化 {{ sortIcon('change') }}</th>
            <th @click="sort('is_ad')">广告 {{ sortIcon('is_ad') }}</th>

            <th @click="sort('app_id')">App ID {{ sortIcon('app_id') }}</th>
            <th @click="sort('app_name')">应用名 {{ sortIcon('app_name') }}</th>
            <th>副标题</th>
            <th>图标</th>
            <th @click="sort('publisher')">发行方 {{ sortIcon('publisher') }}</th>
            <th>发行方ID</th>
            <th @click="sort('price')">价格 {{ sortIcon('price') }}</th>

            <th @click="sort('file_size_mb')">体积(MB) {{ sortIcon('file_size_mb') }}</th>
            <th @click="sort('continuous_first_days')">连续登顶天数 {{ sortIcon('continuous_first_days') }}</th>

            <th @click="sort('source')">来源 {{ sortIcon('source') }}</th>
            <th @click="sort('crawled_at')">抓取时间 {{ sortIcon('crawled_at') }}</th>
            <th @click="sort('updated_at')">更新时间 {{ sortIcon('updated_at') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id">
            <td>{{ row.chart_date }}</td>
            <td>{{ brandName(row.brand_id) }}</td>
            <td>{{ row.country }}</td>
            <td>{{ row.device }}</td>
            <td>{{ row.genre }}</td>
            <td>{{ row.app_genre }}</td>

            <td class="num">{{ row.index }}</td>
            <td class="num">{{ row.ranking }}</td>
            <td>{{ row.change }}</td>
            <td>
              <span :class="['tag', row.is_ad ? 'on' : 'off']">{{ row.is_ad ? '有' : '无' }}</span>
            </td>

            <td class="mono">{{ row.app_id }}</td>
            <td>{{ row.app_name }}</td>
            <td class="muted">{{ row.subtitle }}</td>
            <td>
              <img v-if="row.icon_url" :src="row.icon_url" alt="" class="icon"/>
            </td>
            <td>{{ row.publisher }}</td>
            <td class="mono">{{ row.publisher_id }}</td>
            <td class="num">{{ fmtPrice(row.price) }}</td>

            <td class="num">{{ fmtNum(row.file_size_mb) }}</td>
            <td class="num">{{ row.continuous_first_days ?? '' }}</td>

            <td class="muted">{{ row.source }}</td>
            <td class="muted">{{ fmtTime(row.crawled_at) }}</td>
            <td class="muted">{{ fmtTime(row.updated_at) }}</td>
          </tr>
          <tr v-if="!loading && rows.length === 0">
            <td colspan="22" class="empty">暂无数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="pager">
      <button :disabled="page===1 || loading" @click="goto(1)">«</button>
      <button :disabled="page===1 || loading" @click="goto(page-1)">‹</button>
      <span>第 {{ page }} / {{ totalPages }} 页</span>
      <button :disabled="page===totalPages || loading" @click="goto(page+1)">›</button>
      <button :disabled="page===totalPages || loading" @click="goto(totalPages)">»</button>

      <span class="gap"></span>
      <label>每页
        <select v-model.number="pageSize" @change="onSearch">
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
        </select>
        条
      </label>
    </div>
  </div>
</template>

<script>
import { fetchRankings } from '@/api/rankings'

export default {
  name: 'RankingList',
  data() {
    return {
      q: {
        chart_date: '',
        app_genre: '',
        is_ad: '',
        price_min: '',
        price_max: '',
        brand_id: '',
        country: '',
        device: '',
        genre: '',
      },
      sortBy: 'ranking',
      sortDir: 'asc', // asc | desc
      page: 1,
      pageSize: 20,
      total: 0,
      rows: [],
      loading: false,
    }
  },
  computed: {
    totalPages() {
      const n = Math.ceil(this.total / this.pageSize)
      return n || 1
    }
  },
  mounted() {
    this.onSearch()
  },
  methods: {
    async onSearch() {
      this.page = 1
      await this.load()
    },
    onReset() {
      this.q = { chart_date:'', app_genre:'', is_ad:'', price_min:'', price_max:'', brand_id:'', country:'', device:'', genre:'' }
      this.sortBy = 'ranking'
      this.sortDir = 'asc'
      this.page = 1
      this.pageSize = 20
      this.load()
    },
    sort(field) {
      if (this.sortBy === field) {
        this.sortDir = this.sortDir === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortBy = field
        this.sortDir = 'asc'
      }
      this.load()
    },
    sortIcon(field) {
      if (this.sortBy !== field) return '↕'
      return this.sortDir === 'asc' ? '↑' : '↓'
    },
    brandName(v) {
      return v === 0 ? '付费' : v === 1 ? '免费' : v === 2 ? '畅销' : v
    },
    fmtPrice(p) {
      if (p === null || p === undefined || p === '') return ''
      const n = Number(p)
      if (isNaN(n)) return String(p)
      return n.toFixed(2)
    },
    fmtNum(n) {
      if (n === null || n === undefined || n === '') return ''
      const v = Number(n)
      return isNaN(v) ? n : v.toLocaleString()
    },
    fmtTime(t) {
      return t ? String(t).replace('T',' ').replace('Z','') : ''
    },
    async goto(p) {
      if (p < 1 || p > this.totalPages || p === this.page) return
      this.page = p
      await this.load()
    },
    async load() {
      this.loading = true
      try {
        const params = {
          ...this.q,
          is_ad: this.q.is_ad === '' ? '' : (this.q.is_ad ? 1 : 0),
          price_min: this.q.price_min || '',
          price_max: this.q.price_max || '',
          sort_by: this.sortBy,
          sort_dir: this.sortDir,
          page: this.page,
          page_size: this.pageSize,
        }
        const cleaned = Object.fromEntries(
          Object.entries(params).filter(([_, v]) => v !== '' && v !== null && v !== undefined)
        )
        const res = await fetchRankings(cleaned)
        // 期望后端返回 { items:[], total:123 }
        this.rows = res.items || []
        this.total = Number(res.total || 0)
      } catch (e) {
        console.error(e)
        this.rows = []
        this.total = 0
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.page { padding: 16px; }
.title { font-size: 20px; font-weight: 700; margin-bottom: 12px; }
.filters { background: #fafafa; border: 1px solid #eee; border-radius: 8px; padding: 12px; margin-bottom: 12px; }
.filters .row { display: flex; flex-wrap: wrap; gap: 12px 16px; margin-bottom: 8px; }
.filters label { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.filters .price { width: 120px; }
.filters .sep { margin: 0 4px; color: #888; }
.filters .actions { justify-content: flex-end; }
.filters button { padding: 6px 12px; border-radius: 6px; border: 1px solid #ddd; background: #fff; cursor: pointer; }
.filters .ghost { background: #f6f6f6; }

.table-wrap { overflow: auto; border: 1px solid #eee; border-radius: 8px; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { padding: 8px 10px; border-bottom: 1px solid #f0f0f0; white-space: nowrap; }
th { position: sticky; top: 0; background: #fff; cursor: pointer; user-select: none; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
td.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
td.muted { color: #888; }
.empty { text-align: center; color: #999; padding: 24px 0; }

.icon { width: 28px; height: 28px; border-radius: 6px; object-fit: cover; box-shadow: 0 0 0 1px #eee; }

.pager { display: flex; align-items: center; gap: 8px; margin-top: 12px; }
.pager button { padding: 6px 10px; border: 1px solid #ddd; background: #fff; border-radius: 6px; cursor: pointer; }
.pager button:disabled { opacity: .5; cursor: not-allowed; }
.pager .gap { flex: 1; }
</style>