<template>
  <div class="dashboard-container">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-text">
        <h1>欢迎回来，{{ username }}</h1>
        <p>今天是 {{ currentDate }}，祝您工作愉快！</p>
      </div>
      <div class="quick-actions">
        <el-button type="primary" @click="goTo('/case/create')">
          <el-icon><Plus /></el-icon>
          创建案件
        </el-button>
        <el-button @click="goTo('/document/create')">
          <el-icon><Document /></el-icon>
          新建文书
        </el-button>
        <el-button @click="goTo('/chat')">
          <el-icon><ChatDotSquare /></el-icon>
          智能咨询
        </el-button>
      </div>
    </div>

    <!-- 数据统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="12" :sm="6">
        <div class="stat-card" @click="goTo('/case/list')">
          <div class="stat-icon case">
            <el-icon :size="28"><Briefcase /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalCases }}</div>
            <div class="stat-label">案件总数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card" @click="goTo('/case/list?status=active')">
          <div class="stat-icon active">
            <el-icon :size="28"><Timer /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.activeCases }}</div>
            <div class="stat-label">进行中</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card" @click="goTo('/document/list')">
          <div class="stat-icon document">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.totalDocuments }}</div>
            <div class="stat-label">文书总数</div>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card" @click="goTo('/chat')">
          <div class="stat-icon chat">
            <el-icon :size="28"><ChatDotSquare /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statistics.monthConsultations }}</div>
            <div class="stat-label">本月咨询</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 待办事项 -->
      <el-col :xs="24" :lg="12">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">待办事项</span>
              <el-link type="primary" :underline="false">查看全部</el-link>
            </div>
          </template>
          <div v-if="todoList.length" class="todo-list">
            <div
              v-for="item in todoList"
              :key="item.id"
              class="todo-item"
              :class="{ urgent: item.urgent }"
              @click="goTo(item.link)"
            >
              <div class="todo-content">
                <el-icon class="todo-icon" :class="item.type">
                  <component :is="getIcon(item.type)" />
                </el-icon>
                <div class="todo-info">
                  <div class="todo-title">{{ item.title }}</div>
                  <div class="todo-desc">{{ item.description }}</div>
                </div>
              </div>
              <div class="todo-time">{{ item.time }}</div>
            </div>
          </div>
          <el-empty v-else description="暂无待办事项" />
        </el-card>
      </el-col>

      <!-- 近期案件 -->
      <el-col :xs="24" :lg="12">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">近期案件</span>
              <el-link type="primary" :underline="false" @click="goTo('/case/list')">查看全部</el-link>
            </div>
          </template>
          <el-table :data="recentCases" style="width: 100%">
            <el-table-column prop="caseNumber" label="案号" min-width="150" show-overflow-tooltip />
            <el-table-column prop="title" label="案件名称" min-width="180" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ row.statusText }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="nextStep" label="下一步" width="100" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <!-- 案件分布图表 -->
      <el-col :xs="24" :lg="12">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">案件类型分布</span>
            </div>
          </template>
          <div ref="caseTypeChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <!-- 案件趋势图表 -->
      <el-col :xs="24" :lg="12">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">案件趋势</span>
            </div>
          </template>
          <div ref="caseTrendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { statisticsApi } from '@/api/statistics'
import { ElMessage } from 'element-plus'
import {
  Plus,
  Document,
  ChatDotSquare,
  Briefcase,
  Timer,
  Calendar,
  Bell,
  Warning
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()
const userStore = useUserStore()

// 数据
const statistics = ref({
  totalCases: 0,
  activeCases: 0,
  totalDocuments: 0,
  monthConsultations: 0
})

const todoList = ref<any[]>([])
const recentCases = ref<any[]>([])

// 图表引用
const caseTypeChartRef = ref<HTMLElement>()
const caseTrendChartRef = ref<HTMLElement>()

// 计算属性
const username = computed(() => userStore.userInfo?.name || '律师')
const currentDate = computed(() => {
  const date = new Date()
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  })
})

// 方法
function goTo(path: string) {
  router.push(path)
}

function getIcon(type: string) {
  const icons: Record<string, any> = {
    case: Briefcase,
    document: Document,
    chat: ChatDotSquare,
    schedule: Calendar,
    warning: Warning
  }
  return icons[type] || Bell
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

async function fetchDashboardData() {
  try {
    const res = await statisticsApi.getDashboardData()
    statistics.value = res.data.statistics
    todoList.value = res.data.todoList || []
    recentCases.value = res.data.recentCases || []
  } catch (error: any) {
    ElMessage.error(error.message || '获取数据失败')
  }
}

function initCharts() {
  // 案件类型分布饼图
  if (caseTypeChartRef.value) {
    const chart = echarts.init(caseTypeChartRef.value)
    chart.setOption({
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        right: '5%',
        top: 'center'
      },
      series: [
        {
          name: '案件类型',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['35%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 16,
              fontWeight: 'bold'
            }
          },
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

  // 案件趋势折线图
  if (caseTrendChartRef.value) {
    const chart = echarts.init(caseTrendChartRef.value)
    chart.setOption({
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['新增案件', '结案']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['1月', '2月', '3月', '4月', '5月', '6月']
      },
      yAxis: {
        type: 'value'
      },
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
          data: [12, 15, 18, 22, 20, 28]
        },
        {
          name: '结案',
          type: 'line',
          smooth: true,
          lineStyle: { color: '#67c23a' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
              { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
            ])
          },
          data: [8, 10, 15, 18, 16, 22]
        }
      ]
    })
  }
}

onMounted(async () => {
  await fetchDashboardData()
  initCharts()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.dashboard-container {
  padding: 0;
}

.welcome-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;
  padding: $spacing-lg;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: $border-radius-large;
  color: #fff;

  .welcome-text {
    h1 {
      margin: 0 0 8px;
      font-size: 24px;
    }

    p {
      margin: 0;
      opacity: 0.9;
    }
  }

  .quick-actions {
    display: flex;
    gap: $spacing-sm;
  }
}

.stat-cards {
  margin-bottom: $spacing-lg;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: $spacing-md;
  background: $bg-color;
  border-radius: $border-radius;
  box-shadow: $box-shadow-light;
  cursor: pointer;
  transition: all $transition-duration $transition-timing;

  &:hover {
    transform: translateY(-2px);
    box-shadow: $box-shadow;
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: $border-radius;
    margin-right: $spacing-md;
    color: #fff;

    &.case {
      background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
    }

    &.active {
      background: linear-gradient(135deg, #e6a23c 0%, #b88230 100%);
    }

    &.document {
      background: linear-gradient(135deg, #67c23a 0%, #529b2e 100%);
    }

    &.chat {
      background: linear-gradient(135deg, #f56c6c 0%, #c45656 100%);
    }
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

.dashboard-card {
  margin-bottom: $spacing-lg;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .card-title {
      font-size: $font-size-md;
      font-weight: 600;
      color: $text-primary;
    }
  }
}

.todo-list {
  .todo-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: $spacing-md;
    border-radius: $border-radius;
    cursor: pointer;
    transition: background-color $transition-timing;

    &:hover {
      background-color: $bg-hover;
    }

    &.urgent {
      background-color: rgba($danger-color, 0.05);
    }

    &:not(:last-child) {
      border-bottom: 1px solid $border-lighter;
    }

    .todo-content {
      display: flex;
      align-items: center;
      gap: $spacing-md;

      .todo-icon {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: $border-radius;
        background: $bg-page;
        color: $text-secondary;

        &.case {
          color: $primary-color;
        }

        &.document {
          color: $success-color;
        }

        &.chat {
          color: $warning-color;
        }

        &.warning {
          color: $danger-color;
        }
      }

      .todo-info {
        .todo-title {
          font-size: $font-size-base;
          color: $text-primary;
          margin-bottom: 4px;
        }

        .todo-desc {
          font-size: $font-size-xs;
          color: $text-secondary;
        }
      }
    }

    .todo-time {
      font-size: $font-size-xs;
      color: $text-placeholder;
    }
  }
}

.chart-container {
  height: 300px;
}

.mt-20 {
  margin-top: 20px;
}

@media (max-width: 768px) {
  .welcome-section {
    flex-direction: column;
    text-align: center;
    gap: $spacing-md;

    .quick-actions {
      flex-wrap: wrap;
      justify-content: center;
    }
  }
}
</style>
