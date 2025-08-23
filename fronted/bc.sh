# 进入前端目录

# 1) 覆盖 DefaultLayout（含顶栏+侧边栏，与截图一致的结构）
cat > src/layouts/DefaultLayout.vue <<'VUE'
<template>
  <div class="h-screen flex flex-col">
    <header class="bg-white h-16 border-b border-light-100 px-4 md:px-6 flex items-center justify-between shadow-sm">
      <div class="flex items-center">
        <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center mr-2">
          <i class="fas fa-chart-line text-primary"></i>
        </div>
        <h1 class="text-lg font-semibold hidden md:block">华为应用榜单数据分析平台</h1>
      </div>
      <div class="hidden md:flex">
        <div class="relative">
          <i class="fas fa-search text-info absolute left-3 top-3"></i>
          <input class="pl-10 pr-4 py-2 rounded-lg bg-light-100 border-0 outline-none text-sm w-64" placeholder="全局搜索..." />
        </div>
      </div>
      <div class="flex items-center gap-3">
        <button class="p-2 rounded-lg hover:bg-light-100 relative">
          <i class="fas fa-bell"></i>
          <span class="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full"></span>
        </button>
        <img class="w-8 h-8 rounded-full border" src="https://design.gemcoder.com/staticResource/echoAiSystemImages/b4836a22bb7346e0969480410c37b5b5.png" />
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden">
      <aside class="w-64 bg-white border-r border-light-100 flex-shrink-0 hidden md:flex flex-col">
        <nav class="flex-1 overflow-y-auto p-4">
          <ul class="space-y-1">
            <li>
              <RouterLink to="/cockpit" class="flex items-center px-3 py-2 text-sm font-medium rounded-lg bg-primary/10 text-primary">
                <i class="fas fa-tachometer-alt w-5 h-5 mr-3"></i> 驾驶舱
              </RouterLink>
            </li>
            <li>
              <div class="px-3 py-2 text-sm font-medium rounded-lg hover:bg-light-100 flex items-center justify-between cursor-pointer">
                <div class="flex items-center"><i class="fas fa-list-ol w-5 h-5 mr-3 text-info"></i>华为应用榜单</div>
                <i class="fas fa-chevron-down text-xs"></i>
              </div>
              <ul class="mt-1 ml-6 space-y-1">
                <li><a class="block px-3 py-2 text-sm rounded-lg hover:bg-light-100">榜单列表</a></li>
                <li><a class="block px-3 py-2 text-sm rounded-lg hover:bg-light-100">应用对比</a></li>
              </ul>
            </li>
            <li>
              <div class="px-3 py-2 text-sm font-medium rounded-lg hover:bg-light-100 flex items-center justify-between cursor-pointer">
                <div class="flex items-center"><i class="fas fa-chart-pie w-5 h-5 mr-3 text-info"></i>数据分析</div>
                <i class="fas fa-chevron-down text-xs"></i>
              </div>
            </li>
            <li>
              <div class="px-3 py-2 text-sm font-medium rounded-lg hover:bg-light-100 flex items-center justify-between cursor-pointer">
                <div class="flex items-center"><i class="fas fa-chart-line w-5 h-5 mr-3 text-info"></i>数据预测</div>
                <i class="fas fa-chevron-down text-xs"></i>
              </div>
              <ul class="mt-1 ml-6 space-y-1">
                <li><a class="block px-3 py-2 text-sm rounded-lg hover:bg-light-100">新建预测</a></li>
                <li><a class="block px-3 py-2 text-sm rounded-lg hover:bg-light-100">预测记录</a></li>
              </ul>
            </li>
            <li>
              <div class="px-3 py-2 text-sm font-medium rounded-lg hover:bg-light-100 flex items-center justify-between cursor-pointer">
                <div class="flex items-center"><i class="fas fa-database w-5 h-5 mr-3 text-info"></i>Hive 数据</div>
                <i class="fas fa-chevron-down text-xs"></i>
              </div>
            </li>
            <li>
              <a class="flex items-center px-3 py-2 text-sm font-medium rounded-lg hover:bg-light-100">
                <i class="fas fa-users w-5 h-5 mr-3 text-info"></i> 用户管理
              </a>
            </li>
          </ul>
        </nav>
        <div class="p-4 border-t border-light-100">
          <div class="bg-light-100 rounded-lg p-3 text-xs">
            <i class="fas fa-info-circle text-primary mr-2"></i>
            <div class="inline-block align-top">
              <div>系统版本: v1.0.0</div>
              <div class="text-info mt-1">上次更新: 2023-06-15</div>
            </div>
          </div>
        </div>
      </aside>

      <main class="flex-1 overflow-y-auto bg-light-200 p-4 md:p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
<script setup lang="ts"></script>
VUE

# 2) 通用卡片/筛选/KPI组件
cat > src/components/common/ChartCard.vue <<'VUE'
<template>
  <div class="card p-4">
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold">{{ title }}</h3>
      <div class="flex items-center gap-2"><slot name="tools"/></div>
    </div>
    <slot />
  </div>
</template>
<script setup lang="ts">defineProps<{ title:string }>()</script>
VUE

cat > src/components/common/KpiCard.vue <<'VUE'
<template>
  <div class="card p-4 card-hover">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-info text-sm">{{ title }}</p>
        <h3 class="text-2xl font-bold mt-1">{{ value }}</h3>
        <p v-if="delta!==undefined" :class="['text-sm mt-2 flex items-center', delta>0?'text-success':'text-danger']">
          <i class="fas" :class="[delta>0?'fa-arrow-up':'fa-arrow-down','mr-1']"></i>
          {{ Math.abs(delta).toFixed(1) }}% <span class="text-info ml-1">vs {{ base }}</span>
        </p>
        <p v-else-if="sub" class="text-info text-sm mt-2">{{ sub }}</p>
      </div>
      <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="iconBg">
        <i class="fas" :class="icon"></i>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
defineProps<{ title:string; value:string|number; delta?:number; base?:string; sub?:string; icon:string; iconBg:string }>()
</script>
VUE

cat > src/components/common/FilterBar.vue <<'VUE'
<template>
  <div class="card p-4">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div>
        <label class="block text-sm font-medium mb-2">日期范围</label>
        <div class="relative">
          <i class="fas fa-calendar text-info absolute left-3 top-3"></i>
          <input class="block w-full pl-10 pr-8 py-2 border border-light-100 rounded-lg focus:ring-2 focus:ring-primary/30 outline-none bg-white" placeholder="最近7天"/>
          <i class="fas fa-chevron-down text-info absolute right-3 top-3"></i>
        </div>
      </div>
      <div>
        <label class="block text-sm font-medium mb-2">地区</label>
        <div class="relative">
          <i class="fas fa-map-marker-alt text-info absolute left-3 top-3"></i>
          <select class="block w-full pl-10 pr-8 py-2 border border-light-100 rounded-lg focus:ring-2 focus:ring-primary/30 outline-none bg-white appearance-none">
            <option>全国</option><option>北京</option><option>上海</option><option>广州</option><option>深圳</option>
          </select>
          <i class="fas fa-chevron-down text-info absolute right-3 top-3"></i>
        </div>
      </div>
      <div>
        <label class="block text-sm font-medium mb-2">分类</label>
        <div class="relative">
          <i class="fas fa-tags text-info absolute left-3 top-3"></i>
          <select class="block w-full pl-10 pr-8 py-2 border border-light-100 rounded-lg focus:ring-2 focus:ring-primary/30 outline-none bg-white appearance-none">
            <option>全部分类</option><option>游戏</option><option>社交</option><option>工具</option><option>娱乐</option><option>教育</option>
          </select>
          <i class="fas fa-chevron-down text-info absolute right-3 top-3"></i>
        </div>
      </div>
    </div>
    <div class="mt-4 flex justify-end gap-3">
      <button class="px-4 py-2 border border-light-100 rounded-lg hover:bg-light-100">重置</button>
      <button class="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90">应用筛选</button>
    </div>
  </div>
</template>
<script setup lang="ts"></script>
VUE

# 3) 图表组件（ECharts）
cat > src/components/charts/TrendChart.vue <<'VUE'
<template><div ref="el" class="w-full h-80"></div></template>
<script setup lang="ts">
import * as echarts from "echarts"; import { onMounted, ref } from "vue";
const el = ref<HTMLDivElement|null>(null);
onMounted(()=> {
  const chart = echarts.init(el.value!);
  chart.setOption({
    tooltip:{ trigger:"axis", axisPointer:{ type:"cross", label:{ backgroundColor:"#6a7985" }}},
    legend:{ data:["华为应用市场","微信","抖音","支付宝","淘宝"], top:0 },
    grid:{ left:"3%", right:"4%", bottom:"3%", containLabel:true },
    xAxis:[{ type:"category", boundaryGap:false, data:["6/10","6/11","6/12","6/13","6/14","6/15","6/16"]}],
    yAxis:[{ type:"value", max:20, inverse:true }],
    series:[
      { name:"华为应用市场", type:"line", stack:"Total", areaStyle:{}, data:[1,1,1,1,1,1,1] },
      { name:"微信", type:"line", stack:"Total", areaStyle:{}, data:[2,2,3,2,2,2,2] },
      { name:"抖音", type:"line", stack:"Total", areaStyle:{}, data:[3,3,2,3,3,3,3] },
      { name:"支付宝", type:"line", stack:"Total", areaStyle:{}, data:[4,4,4,4,5,4,4] },
      { name:"淘宝", type:"line", stack:"Total", areaStyle:{}, data:[5,5,5,5,4,5,5] },
    ],
  });
  window.addEventListener("resize", ()=>chart.resize());
});
</script>
VUE

cat > src/components/charts/CategoryPie.vue <<'VUE'
<template><div ref="el" class="w-full h-80"></div></template>
<script setup lang="ts">
import * as echarts from "echarts"; import { onMounted, ref } from "vue";
const el = ref<HTMLDivElement|null>(null);
onMounted(()=> {
  const chart = echarts.init(el.value!);
  chart.setOption({
    tooltip:{ trigger:"item" },
    legend:{ orient:"vertical", left:"left" },
    series:[{ name:"分类占比", type:"pie", radius:["40%","70%"], itemStyle:{ borderRadius:10, borderColor:"#fff", borderWidth:2 },
      label:{ show:false, position:"center" }, emphasis:{ label:{ show:true, fontSize:16, fontWeight:"bold" }}, labelLine:{ show:false },
      data:[{value:325,name:"游戏"},{value:244,name:"社交"},{value:188,name:"工具"},{value:155,name:"娱乐"},{value:102,name:"教育"},{value:85,name:"其他"}]}],
  });
  window.addEventListener("resize", ()=>chart.resize());
});
</script>
VUE

cat > src/components/charts/RegionHeat.vue <<'VUE'
<template><div ref="el" class="w-full h-80"></div></template>
<script setup lang="ts">
import * as echarts from "echarts"; import { onMounted, ref } from "vue";
const el = ref<HTMLDivElement|null>(null);
onMounted(async ()=>{
  const chart = echarts.init(el.value!);
  const geo = await fetch("/china.json").then(r=>r.json());
  echarts.registerMap("china", geo as any);
  chart.setOption({
    tooltip:{ trigger:"item" },
    visualMap:{ min:0, max:200, left:"left", bottom:0, text:["高","低"], calculable:true },
    series:[{ name:"应用数量", type:"map", map:"china", roam:false, label:{ show:true },
      data:[
        {name:"北京",value:150},{name:"天津",value:80},{name:"上海",value:180},{name:"重庆",value:90},
        {name:"河北",value:70},{name:"河南",value:65},{name:"云南",value:50},{name:"辽宁",value:60},
        {name:"黑龙江",value:45},{name:"湖南",value:75},{name:"安徽",value:60},{name:"山东",value:90},
        {name:"新疆",value:40},{name:"江苏",value:120},{name:"浙江",value:130},{name:"江西",value:55},
        {name:"湖北",value:85},{name:"广西",value:50},{name:"甘肃",value:40},{name:"山西",value:50},
        {name:"内蒙古",value:35},{name:"陕西",value:70},{name:"吉林",value:45},{name:"福建",value:95},
        {name:"贵州",value:45},{name:"广东",value:170},{name:"青海",value:30},{name:"西藏",value:25},
        {name:"四川",value:100},{name:"宁夏",value:35},{name:"海南",value:40},{name:"台湾",value:50},
        {name:"香港",value:60},{name:"澳门",value:30}
      ]}],
  });
  window.addEventListener("resize", ()=>chart.resize());
});
</script>
VUE

cat > src/components/charts/TaskGantt.vue <<'VUE'
<template><div ref="el" class="w-full h-80"></div></template>
<script setup lang="ts">
import * as echarts from "echarts"; import { onMounted, ref } from "vue";
const el = ref<HTMLDivElement|null>(null);
onMounted(()=> {
  const chart = echarts.init(el.value!);
  const ms = (s:string)=> new Date(s).getTime();
  chart.setOption({
    tooltip:{ formatter:(p:any)=>`${p.data.name}<br/>开始: ${p.data.start}<br/>结束: ${p.data.end}` },
    grid:{ left:"10%", right:"10%", bottom:"15%" },
    xAxis:{ type:"time" }, yAxis:{ type:"category", data:["数据采集","数据清洗","数据分析","数据预测","报表生成"] },
    series:[{ type:"bar", barWidth:20, label:{ show:true, position:"inside", color:"#fff",
      formatter:(p:any)=>{ const s=new Date(p.data.value[0]).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
                           const e=new Date(p.data.value[1]).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}); return `${s} - ${e}`;}},
      data:[
        { name:"数据采集", start:"2023-06-15 08:00", end:"2023-06-15 09:30", value:[ms("2023-06-15 08:00"),ms("2023-06-15 09:30"),0], itemStyle:{ color:"#00B42A" }},
        { name:"数据清洗", start:"2023-06-15 09:30", end:"2023-06-15 10:45", value:[ms("2023-06-15 09:30"),ms("2023-06-15 10:45"),1], itemStyle:{ color:"#00B42A" }},
        { name:"数据分析", start:"2023-06-15 10:45", end:"2023-06-15 12:30", value:[ms("2023-06-15 10:45"),ms("2023-06-15 12:30"),2], itemStyle:{ color:"#00B42A" }},
        { name:"数据预测", start:"2023-06-15 12:30", end:"2023-06-15 14:15", value:[ms("2023-06-15 12:30"),ms("2023-06-15 14:15"),3], itemStyle:{ color:"#FF7D00" }},
        { name:"报表生成", start:"2023-06-15 14:15", end:"2023-06-15 15:00", value:[ms("2023-06-15 14:15"),ms("2023-06-15 15:00"),4], itemStyle:{ color:"#165DFF" }},
      ]}],
  });
  window.addEventListener("resize", ()=>chart.resize());
});
</script>
VUE

# 4) 驾驶舱页面（组合筛选/KPI/四张图）
cat > src/views/Cockpit.vue <<'VUE'
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
VUE

# 5) 准备中国地图（先放可用底图；如网络受限可稍后手动替换）
curl -L "https://unpkg.com/echarts@3.6.2/map/json/china.json" -o public/china.json

# 6) 如果没装 echarts（已装可跳过）
npm i echarts@^5.5.1

# 7) 重启 dev
npm run dev