<template>
  <div class="case-list-container">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="案号/当事人/律师"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="案件类型">
          <el-select v-model="searchForm.caseType" placeholder="全部类型" clearable>
            <el-option label="违法解除" value="illegal_termination" />
            <el-option label="工伤赔偿" value="work_injury" />
            <el-option label="加班费争议" value="overtime" />
            <el-option label="年休假工资" value="annual_leave" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="案件状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="仲裁阶段" value="arbitration" />
            <el-option label="一审阶段" value="first_instance" />
            <el-option label="二审阶段" value="second_instance" />
            <el-option label="已结案" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建案件
      </el-button>
      <el-button @click="handleImport">批量导入</el-button>
    </div>

    <!-- 案件列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="caseList"
        style="width: 100%"
        @row-click="handleRowClick"
      >
        <el-table-column prop="caseNumber" label="案号" min-width="180" show-overflow-tooltip />
        <el-table-column prop="title" label="案件名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="caseType" label="案件类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getCaseTypeTag(row.caseType)">
              {{ getCaseTypeLabel(row.caseType) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="plaintiff" label="原告/申请人" width="120" show-overflow-tooltip />
        <el-table-column prop="defendant" label="被告/被申请人" width="120" show-overflow-tooltip />
        <el-table-column prop="claimAmount" label="标的金额" width="120">
          <template #default="{ row }">
            {{ formatAmount(row.claimAmount) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lawyerName" label="办案律师" width="100" />
        <el-table-column prop="createdAt" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text size="small" @click.stop="handleDetail(row)">
              详情
            </el-button>
            <el-button type="primary" text size="small" @click.stop="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="primary" text size="small" @click.stop="handleAnalyze(row)">
              AI分析
            </el-button>
            <el-button type="danger" text size="small" @click.stop="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- AI分析对话框 -->
    <el-dialog
      v-model="analyzeDialogVisible"
      title="AI案件分析"
      width="700px"
      destroy-on-close
    >
      <div v-loading="analyzing" class="analyze-content">
        <template v-if="analysisResult">
          <div class="analysis-section">
            <h4>案件优势</h4>
            <ul>
              <li v-for="(item, index) in analysisResult.advantages" :key="index">
                {{ item }}
              </li>
            </ul>
          </div>
          <div class="analysis-section">
            <h4>案件风险</h4>
            <ul>
              <li v-for="(item, index) in analysisResult.risks" :key="index">
                {{ item }}
              </li>
            </ul>
          </div>
          <div class="analysis-section">
            <h4>建议策略</h4>
            <ol>
              <li v-for="(item, index) in analysisResult.strategies" :key="index">
                {{ item }}
              </li>
            </ol>
          </div>
          <div class="analysis-section">
            <h4>胜诉概率</h4>
            <el-progress
              :percentage="analysisResult.winProbability"
              :color="getWinProbabilityColor(analysisResult.winProbability)"
            />
            <p class="probability-text">{{ analysisResult.probabilityText }}</p>
          </div>
        </template>
        <el-empty v-else-if="!analyzing" description="暂无分析结果" />
      </div>
      <template #footer>
        <el-button @click="analyzeDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleExportAnalysis">导出报告</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCaseStore } from '@/stores/case'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import type { Case } from '@/types'

const router = useRouter()
const caseStore = useCaseStore()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  caseType: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 状态
const loading = ref(false)
const caseList = ref<Case[]>([])
const analyzeDialogVisible = ref(false)
const analyzing = ref(false)
const analysisResult = ref<any>(null)
const currentCase = ref<Case | null>(null)

// 方法
async function fetchData() {
  loading.value = true
  try {
    const res = await caseStore.fetchCases({
      ...searchForm,
      page: pagination.page,
      size: pagination.size
    })
    caseList.value = caseStore.caseList
    pagination.total = caseStore.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取数据失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchData()
}

function handleReset() {
  Object.assign(searchForm, {
    keyword: '',
    caseType: '',
    status: ''
  })
  handleSearch()
}

function handleCreate() {
  router.push('/case/create')
}

function handleImport() {
  ElMessage.info('批量导入功能开发中')
}

function handleRowClick(row: Case) {
  router.push(`/case/detail/${row.id}`)
}

function handleDetail(row: Case) {
  router.push(`/case/detail/${row.id}`)
}

function handleEdit(row: Case) {
  router.push(`/case/edit/${row.id}`)
}

async function handleAnalyze(row: Case) {
  currentCase.value = row
  analyzeDialogVisible.value = true
  analyzing.value = true
  analysisResult.value = null

  try {
    const res = await caseStore.analyzeCase(row.id)
    analysisResult.value = res.data
  } catch (error: any) {
    ElMessage.error(error.message || '分析失败')
  } finally {
    analyzing.value = false
  }
}

async function handleDelete(row: Case) {
  try {
    await ElMessageBox.confirm('确定要删除该案件吗？删除后无法恢复。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await caseStore.deleteCase(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

function handleExportAnalysis() {
  ElMessage.info('导出报告功能开发中')
}

function handleSizeChange(size: number) {
  pagination.size = size
  fetchData()
}

function handleCurrentChange(page: number) {
  pagination.page = page
  fetchData()
}

function getCaseTypeTag(type: string) {
  const types: Record<string, string> = {
    illegal_termination: 'danger',
    work_injury: 'warning',
    overtime: 'primary',
    annual_leave: 'success',
    other: 'info'
  }
  return types[type] || 'info'
}

function getCaseTypeLabel(type: string) {
  const labels: Record<string, string> = {
    illegal_termination: '违法解除',
    work_injury: '工伤赔偿',
    overtime: '加班费争议',
    annual_leave: '年休假工资',
    other: '其他'
  }
  return labels[type] || type
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

function getStatusLabel(status: string) {
  const labels: Record<string, string> = {
    pending: '待处理',
    arbitration: '仲裁阶段',
    first_instance: '一审阶段',
    second_instance: '二审阶段',
    closed: '已结案'
  }
  return labels[status] || status
}

function formatAmount(amount: number) {
  if (!amount) return '-'
  return `¥${amount.toLocaleString()}`
}

function formatDate(date: string) {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

function getWinProbabilityColor(probability: number) {
  if (probability >= 70) return '#67c23a'
  if (probability >= 40) return '#e6a23c'
  return '#f56c6c'
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.case-list-container {
  .search-card {
    margin-bottom: $spacing-md;
  }

  .action-bar {
    margin-bottom: $spacing-md;
  }

  .table-card {
    .el-table {
      cursor: pointer;
    }
  }

  .pagination {
    margin-top: $spacing-md;
    display: flex;
    justify-content: flex-end;
  }
}

.analyze-content {
  min-height: 200px;

  .analysis-section {
    margin-bottom: $spacing-lg;

    h4 {
      margin-bottom: $spacing-sm;
      color: $text-primary;
      font-size: $font-size-md;
    }

    ul, ol {
      padding-left: $spacing-lg;
      color: $text-regular;

      li {
        margin-bottom: $spacing-xs;
        line-height: 1.6;
      }
    }
  }

  .probability-text {
    margin-top: $spacing-sm;
    color: $text-secondary;
    font-size: $font-size-sm;
  }
}
</style>
