// Auto-generated types for Huawei App Rank Analysis frontend
// Keep in sync with backend contracts (FastAPI).

// KPI
export type Trend = "up" | "down"
export type Accent = "primary" | "secondary" | "success" | "warning" | "danger"

export interface KpiDelta {
  value: number | string
  trend: Trend
  base: string
}

export interface KpiItem {
  title: string
  value: number | string
  icon: string
  accent?: Accent
  delta?: KpiDelta
  subtext?: string
}

// Line chart (Top N rank trend)
export interface SeriesLine {
  name: string
  data: number[]
  area?: boolean
}

export interface LineInput {
  x: string[] // time axis
  series: SeriesLine[]
  yAxis?: { inverse?: boolean; max?: number }
}

// Category pie
export interface PieSlice {
  name: string
  value: number
}
export interface PieInput {
  legend?: "left" | "right" | "top" | "bottom"
  series: PieSlice[]
}

// China map heat
export interface MapDatum {
  name: string
  value: number
}
export interface MapInput {
  min: number
  max: number
  data: MapDatum[]
}

// Gantt-like chart (task timeline)
export interface GanttItem {
  name: string
  start: string | number // ISO string or timestamp
  end: string | number
  lane: string
  color?: string
}
export interface GanttInput {
  lanes: string[]
  items: GanttItem[]
}

// Live feed / notifications
export type FeedType = "success" | "warning" | "info" | "danger"
export interface FeedItem {
  id: string
  type: FeedType
  title: string
  detail: string
  time: string // "刚刚" | "5分钟前" | ISO timestamp in real impl
}

// Filters used in cockpit & analysis
export interface DateRange {
  start: string
  end: string
}
export type DatePreset = "7d" | "30d"
export interface CockpitFilters {
  dateRange?: DateRange | DatePreset
  region?: string
  category?: string
}

// Rank list row
export interface RankRow {
  rank: number
  deltaRank?: number
  appName: string
  appId: string
  category: string
  rating?: number
  installs?: number
  publisher?: string
  region: string
  date: string // 'YYYY-MM-DD'
}

// Forecast
export type ForecastMetric = "rank" | "download" | "heat"
export type ForecastModel = "Auto" | "Prophet" | "LightGBM"
export interface ForecastTask {
  id: string
  target: { type: "app" | "category" | "region"; value: string }
  metric: ForecastMetric
  model: ForecastModel
  horizon: 7 | 14 | 30
  owner: string
  startTime: string
  duration?: number // seconds
  status: "success" | "failed" | "running" | "queued"
}

export interface ForecastDetail {
  series: LineInput // history + forecast + CI bands if encoded as extra series
  metrics: { MAE: number; MAPE: number; RMSE: number }
  featureImportance?: Array<{ name: string; value: number }>
}

// User
export interface User {
  id: string
  username: string
  email: string
  roles: string[]
  status: "enabled" | "disabled"
  createdAt: string
  lastLogin?: string
}
