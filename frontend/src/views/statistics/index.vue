<template>
  <div class="statistics-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon cases">
            <el-icon :size="28"><Briefcase /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ overview.totalCases }}</div>
            <div class="stat-label">案件总数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon documents">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ overview.totalDocuments }}</div>
            <div class="stat-label">文书总数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon consultations">
            <el-icon :size="28"><ChatDotSquare /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ overview.totalConsultations }}</div>
            <div class="stat-label">咨询次数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card">
          <div class="stat-icon winrate">
            <el-icon :size="28"><TrendCharts /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ overview.winRate }}%</div>
            <div class="stat-label">胜诉率</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>案件趋势</span>
              <el-radio-group v-model="trendPeriod" size="small" @change="loadTrendData">
                <el-radio-button label="week">近一周</el-radio-button>
                <el-radio-button label="month">近一月</el-radio-button>
                <el-radio-button label="year">近一年</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <span>案件类型分布</span>
          </template>
          <div ref="typeChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <span>案件状态分布</span>
          </template>
          <div ref="statusChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <span>胜诉率分析</span>
          </template>
          <div ref="winRateChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <el-col :xs="24" :lg="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>近期案件</span>
              <el-link type="primary" @click="goToCaseList">查看全部</el-link>
            </div>
          </template>
          <el-table :data="recentCases" style="width: 100%">
            <el-table-column prop="caseNumber" label="案号" min-width="150" show-overflow-tooltip />
            <el-table-column prop="title" label="案件名称" min-width="180" show-overflow-tooltip />
            <el-table-column prop="caseType" label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{ row.caseType }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag size="small" :type="getStatusType(row.status)">
                  {{ row.statusText }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="createdAt" label="创建时间" width="160" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card>
          <template #header>
            <span>办案律师排行</span>
          </template>
          <div class="lawyer-ranking">
            <div v-for="(lawyer, index) in lawyerRanking" :key="lawyer.id" class="ranking-item">
              <div class="ranking-index" :class="getRankClass(index)">
                {{ index + 1 }}
              </div>
              <div class="ranking-info">
                <div class="lawyer-name">{{ lawyer.name }}</div>
                <div class="lawyer-stats">
                  办案 {{ lawyer.caseCount }} 件 | 胜诉率 {{ lawyer.winRate }}%
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { statisticsApi } from '@/api/statistics'
import { ElMessage } from 'element-plus'
import { Briefcase, Document, ChatDotSquare, TrendCharts } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()

const trendPeriod = ref('month')
const trendChartRef = ref<HTMLElement>()
const typeChartRef = ref<HTMLElement>()
const statusChartRef = ref<HTMLElement>()
const winRateChartRef = ref<HTMLElement>()

const overview = ref({
  totalCases: 156,
  totalDocuments: 324,
  totalConsultations: 892,
  winRate: 78
})

const recentCases = ref([
  { id: 1, caseNumber: '(2024)沪0101民初12345号', title: '张三 vs 某科技公司', caseType: '违法解除', status: 'arbitration', statusText: '仲裁阶段', createdAt: '2024-01-15' },
  { id: 2, caseNumber: '(2024)沪0105民初6789号', title: '李四 vs 某贸易公司', caseType: '工伤赔偿', status: 'first_instance', statusText: '一审阶段', createdAt: '2024-01-14' },
  { id: 3, caseNumber: '(2024)沪0101民初11111号', title: '王五 vs 某餐饮公司', caseType: '加班费争议', status: 'pending', statusText: '待处理', createdAt: '2024-01-13' },
  { id: 4, caseNumber: '(2024)沪0101民初22222号', title: '赵六 vs 某制造公司', caseType: '年休假', status: 'closed', statusText: '已结案', createdAt: '2024-01-12' },
  { id: 5, caseNumber: '(2024)沪0101民初33333号', title: '钱七 vs 某互联网公司', caseType: '违法解除', status: 'second_instance', statusText: '二审阶段', createdAt: '2024-01-11' }
])

const lawyerRanking = ref([
  { id: 1, name: '李律师', caseCount: 45, winRate: 85 },
  { id: 2, name: '王律师', caseCount: 38, winRate: 82 },
  { id: 3, name: '张律师', caseCount: 32, winRate: 78 },
  { id: 4, name: '赵律师', caseCount: 28, winRate: 75 },
  { id: 5, name: '刘律师', caseCount: 25, winRate: 72 }
])

function loadTrendData() {
  initTrendChart()
}

function goToCaseList() {
  router.push('/case/list')
}

function getStatusType(status: string) {
  const types: Record<string, string> = {
    pending: 'info',
    arbitration: 'warning',
    first_instance: 'primary',
    second_instance: 'primary',
    closed: 'success'
  }
  return types[status] || 'info'
}

function getRankClass(index: number) {
  if (index === 0) return 'gold'
  if (index === 1) return 'silver'
  if (index === 2) return 'bronze'
  return ''
}

function initTrendChart() {
  if (!trendChartRef.value) return

  const chart = echarts.init(trendChartRef.value)
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['新增案件', '已结案件'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', boundaryGap: false, data: months },
    yAxis: { type: 'value' },
    series: [
      {
        name: '新增案件',
        type: 'line',
        smooth: true,
        lineStyle: { color: '#409eff' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        },
        data: [12, 15, 18, 22, 20, 28, 25, 30, 35, 32, 28, 40]
      },
      {
        name: '已结案件',
        type: 'line',
        smooth: true,
        lineStyle: { color: '#67c23a' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
          ])
        },
        data: [8, 10, 15, 18, 16, 22, 20, 25, 30, 28, 25, 35]
      }
    ]
  })
}

function initTypeChart() {
  if (!typeChartRef.value) return

  const chart = echarts.init(typeChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { orient: 'vertical', right: '5%', top: 'center' },
    series: [
      {
        name: '案件类型',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
        data: [
          { value: 45, name: '违法解除', itemStyle: { color: '#409eff' } },
          { value: 28, name: '工伤赔偿', itemStyle: { color: '#67c23a' } },
          { value: 22, name: '加班费争议', itemStyle: { color: '#e6a23c' } },
          { value: 15, name: '年休假工资', itemStyle: { color: '#f56c6c' } },
          { value: 10, name: '其他', itemStyle: { color: '#909399' } }
        ]
      }
    ]
  })
}

function initStatusChart() {
  if (!statusChartRef.value) return

  const chart = echarts.init(statusChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['待处理', '仲裁阶段', '一审阶段', '二审阶段', '已结案'] },
    yAxis: { type: 'value' },
    series: [
      {
        type: 'bar',
        barWidth: '50%',
        data: [
          { value: 15, itemStyle: { color: '#909399' } },
          { value: 35, itemStyle: { color: '#e6a23c' } },
          { value: 28, itemStyle: { color: '#409eff' } },
          { value: 12, itemStyle: { color: '#409eff' } },
          { value: 66, itemStyle: { color: '#67c23a' } }
        ]
      }
    ]
  })
}

function initWinRateChart() {
  if (!winRateChartRef.value) return

  const chart = echarts.init(winRateChartRef.value)
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['胜诉', '败诉', '和解'] },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: { type: 'category', data: ['违法解除', '工伤赔偿', '加班费争议', '年休假'] },
    yAxis: { type: 'value' },
    series: [
      { name: '胜诉', type: 'bar', stack: 'total', data: [35, 22, 15, 12], itemStyle: { color: '#67c23a' } },
      { name: '败诉', type: 'bar', stack: 'total', data: [5, 3, 4, 2], itemStyle: { color: '#f56c6c' } },
      { name: '和解', type: 'bar', stack: 'total', data: [5, 3, 3, 1], itemStyle: { color: '#e6a23c' } }
    ]
  })
}

async function fetchStatistics() {
  try {
    const res = await statisticsApi.getOverview()
    if (res.data) {
      overview.value = {
        totalCases: res.data.caseStatistics?.total || 156,
        totalDocuments: res.data.documentStatistics?.total || 324,
        totalConsultations: res.data.consultationStatistics?.total || 892,
        winRate: res.data.winRateStatistics?.overall || 78
      }
    }
  } catch (error: any) {
    console.error('获取统计数据失败:', error)
  }
}

onMounted(() => {
  fetchStatistics()
  initTrendChart()
  initTypeChart()
  initStatusChart()
  initWinRateChart()

  // 响应窗口大小变化
  window.addEventListener('resize', () => {
    echarts.getInstanceByDom(trendChartRef.value!)?.resize()
    echarts.getInstanceByDom(typeChartRef.value!)?.resize()
    echarts.getInstanceByDom(statusChartRef.value!)?.resize()
    echarts.getInstanceByDom(winRateChartRef.value!)?.resize()
  })
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.statistics-container {
  .stat-cards {
    margin-bottom: $spacing-lg;
  }

  .stat-card {
    display: flex;
    align-items: center;
    padding: $spacing-lg;
    background: $bg-color;
    border-radius: $border-radius;
    box-shadow: $box-shadow-light;

    .stat-icon {
      width: 56px;
      height: 56px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: $border-radius;
      margin-right: $spacing-md;
      color: #fff;

      &.cases { background: linear-gradient(135deg, #409eff 0%, #337ecc 100%); }
      &.documents { background: linear-gradient(135deg, #67c23a 0%, #529b2e 100%); }
      &.consultations { background: linear-gradient(135deg, #e6a23c 0%, #b88230 100%); }
      &.winrate { background: linear-gradient(135deg, #f56c6c 0%, #c45656 100%); }
    }

    .stat-info {
      .stat-value {
        font-size: 28px;
        font-weight: 600;
        color: $text-primary;
      }
      .stat-label {
        font-size: $font-size-sm;
        color: $text-secondary;
      }
    }
  }

  .chart-card {
    margin-bottom: $spacing-lg;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .chart-container {
      height: 300px;
    }
  }

  .mt-20 {
    margin-top: 20px;
  }

  .lawyer-ranking {
    .ranking-item {
      display: flex;
      align-items: center;
      padding: $spacing-md;
      border-radius: $border-radius;
      transition: background-color $transition-timing;

      &:hover {
        background-color: $bg-hover;
      }

      &:not(:last-child) {
        border-bottom: 1px solid $border-lighter;
      }

      .ranking-index {
        width: 28px;
        height: 28px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: $bg-page;
        color: $text-secondary;
        font-weight: 600;
        margin-right: $spacing-md;

        &.gold { background: linear-gradient(135deg, #FFD700, #FFA500); color: #fff; }
        &.silver { background: linear-gradient(135deg, #C0C0C0, #A0A0A0); color: #fff; }
        &.bronze { background: linear-gradient(135deg, #CD7F32, #8B4513); color: #fff; }
      }

      .ranking-info {
        flex: 1;

        .lawyer-name {
          font-weight: 500;
          color: $text-primary;
        }

        .lawyer-stats {
          font-size: $font-size-xs;
          color: $text-secondary;
        }
      }
    }
  }
}
</style>
