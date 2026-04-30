<template>
  <div class="case-detail-container">
    <el-skeleton v-if="loading" animated />
    <template v-else>
      <!-- 案件头部 -->
      <el-card class="header-card">
        <div class="case-header">
          <div class="case-info">
            <h1>{{ caseDetail.title }}</h1>
            <div class="case-meta">
              <span>案号: {{ caseDetail.caseNumber }}</span>
              <el-tag :type="getStatusType(caseDetail.status)">
                {{ getStatusLabel(caseDetail.status) }}
              </el-tag>
              <span>标的金额: ¥{{ formatAmount(caseDetail.claimAmount) }}</span>
            </div>
          </div>
          <div class="case-actions">
            <el-button type="primary" @click="handleEdit">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button @click="handleAnalyze">
              <el-icon><DataAnalysis /></el-icon> AI分析
            </el-button>
            <el-button @click="handleCreateDocument">
              <el-icon><Document /></el-icon> 生成文书
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 案件详情 -->
      <el-tabs v-model="activeTab" class="detail-tabs">
        <el-tab-pane label="基本信息" name="info">
          <el-card>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="案件类型">{{ caseDetail.caseType }}</el-descriptions-item>
              <el-descriptions-item label="案件状态">
                <el-tag :type="getStatusType(caseDetail.status)">
                  {{ getStatusLabel(caseDetail.status) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="原告/申请人">{{ caseDetail.plaintiff }}</el-descriptions-item>
              <el-descriptions-item label="被告/被申请人">{{ caseDetail.defendant }}</el-descriptions-item>
              <el-descriptions-item label="办案律师">{{ caseDetail.lawyerName }}</el-descriptions-item>
              <el-descriptions-item label="立案日期">{{ caseDetail.filingDate }}</el-descriptions-item>
              <el-descriptions-item label="标的金额">¥{{ formatAmount(caseDetail.claimAmount) }}</el-descriptions-item>
              <el-descriptions-item label="创建时间">{{ caseDetail.createdAt }}</el-descriptions-item>
              <el-descriptions-item label="争议焦点" :span="2">
                <el-tag v-for="focus in caseDetail.disputeFocus" :key="focus" class="focus-tag">
                  {{ focus }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="案件描述" :span="2">
                {{ caseDetail.description }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="时间线" name="timeline">
          <el-card>
            <div class="timeline-header">
              <span>案件时间线</span>
              <el-button type="primary" size="small" @click="handleAddTimeline">
                <el-icon><Plus /></el-icon> 添加事件
              </el-button>
            </div>
            <el-timeline>
              <el-timeline-item
                v-for="event in timeline"
                :key="event.id"
                :timestamp="event.date"
                placement="top"
              >
                <el-card shadow="hover">
                  <h4>{{ event.title }}</h4>
                  <p>{{ event.description }}</p>
                </el-card>
              </el-timeline-item>
            </el-timeline>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="证据管理" name="evidence">
          <el-card>
            <div class="evidence-header">
              <span>证据列表</span>
              <el-button type="primary" size="small" @click="handleUploadEvidence">
                <el-icon><Upload /></el-icon> 上传证据
              </el-button>
            </div>
            <el-table :data="evidenceList" style="width: 100%">
              <el-table-column prop="name" label="证据名称" min-width="200" />
              <el-table-column prop="type" label="证据类型" width="120" />
              <el-table-column prop="uploadTime" label="上传时间" width="160" />
              <el-table-column prop="size" label="文件大小" width="100" />
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button type="primary" text size="small" @click="handlePreviewEvidence(row)">
                    查看
                  </el-button>
                  <el-button type="primary" text size="small" @click="handleDownloadEvidence(row)">
                    下载
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="关联文书" name="documents">
          <el-card>
            <div class="document-header">
              <span>关联文书</span>
              <el-button type="primary" size="small" @click="handleCreateDocument">
                <el-icon><Plus /></el-icon> 新建文书
              </el-button>
            </div>
            <el-table :data="documents" style="width: 100%">
              <el-table-column prop="title" label="文书名称" min-width="200" />
              <el-table-column prop="docType" label="文书类型" width="120" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag size="small">{{ row.statusText }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="updatedAt" label="更新时间" width="160" />
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button type="primary" text size="small" @click="handleViewDocument(row)">
                    查看
                  </el-button>
                  <el-button type="primary" text size="small" @click="handleEditDocument(row)">
                    编辑
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-tab-pane>

        <el-tab-pane label="AI分析" name="analysis">
          <el-card v-if="analysisResult">
            <div class="analysis-section">
              <h3>案件优势</h3>
              <ul>
                <li v-for="(item, index) in analysisResult.advantages" :key="index">
                  <el-icon color="#67c23a"><SuccessFilled /></el-icon>
                  {{ item }}
                </li>
              </ul>
            </div>
            <div class="analysis-section">
              <h3>案件风险</h3>
              <ul>
                <li v-for="(item, index) in analysisResult.risks" :key="index">
                  <el-icon color="#f56c6c"><WarningFilled /></el-icon>
                  {{ item }}
                </li>
              </ul>
            </div>
            <div class="analysis-section">
              <h3>建议策略</h3>
              <ol>
                <li v-for="(item, index) in analysisResult.strategies" :key="index">{{ item }}</li>
              </ol>
            </div>
            <div class="analysis-section">
              <h3>胜诉概率</h3>
              <el-progress
                :percentage="analysisResult.winProbability"
                :color="getWinProbabilityColor(analysisResult.winProbability)"
              />
              <p class="probability-text">{{ analysisResult.probabilityText }}</p>
            </div>
            <div class="analysis-section">
              <h3>类似案例</h3>
              <el-table :data="analysisResult.similarCases" style="width: 100%">
                <el-table-column prop="caseNumber" label="案号" width="180" />
                <el-table-column prop="title" label="案件名称" min-width="200" />
                <el-table-column prop="result" label="结果" width="100" />
                <el-table-column prop="similarity" label="相似度" width="100">
                  <template #default="{ row }">
                    {{ row.similarity }}%
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
          <el-empty v-else description="暂无AI分析结果">
            <el-button type="primary" @click="handleAnalyze">开始分析</el-button>
          </el-empty>
        </el-tab-pane>
      </el-tabs>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCaseStore } from '@/stores/case'
import { ElMessage } from 'element-plus'
import { Edit, DataAnalysis, Document, Plus, Upload, SuccessFilled, WarningFilled } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const caseStore = useCaseStore()

const loading = ref(true)
const activeTab = ref('info')

const caseDetail = ref({
  id: 1,
  title: '张三 vs 某科技公司 - 违法解除劳动争议',
  caseNumber: '(2024)沪0101民初12345号',
  caseType: '违法解除',
  status: 'arbitration',
  plaintiff: '张三',
  defendant: '某科技公司',
  lawyerName: '李律师',
  claimAmount: 150000,
  filingDate: '2024-01-10',
  createdAt: '2024-01-10 10:00:00',
  disputeFocus: ['是否构成违法解除', '赔偿金计算标准', '加班费是否应支持'],
  description: '劳动者入职公司3年7个月，公司以严重违纪为由解除劳动合同，但仅有口头警告记录，劳动者主张违法解除赔偿金。'
})

const timeline = ref([
  { id: 1, date: '2024-01-15', title: '举证期限届满', description: '需要在规定时间内提交全部证据材料' },
  { id: 2, date: '2024-01-10', title: '提交仲裁申请', description: '已向劳动人事争议仲裁委员会提交仲裁申请书' },
  { id: 3, date: '2024-01-05', title: '解除劳动合同', description: '公司以严重违纪为由解除劳动合同' },
  { id: 4, date: '2020-06-01', title: '入职', description: '劳动者入职公司，担任软件工程师' }
])

const evidenceList = ref([
  { id: 1, name: '劳动合同.pdf', type: '合同', uploadTime: '2024-01-11 14:30', size: '2.3MB' },
  { id: 2, name: '工资条.xlsx', type: '工资记录', uploadTime: '2024-01-11 14:35', size: '156KB' },
  { id: 3, name: '考勤记录.pdf', type: '考勤', uploadTime: '2024-01-11 14:40', size: '890KB' },
  { id: 4, name: '解除通知.pdf', type: '通知', uploadTime: '2024-01-11 14:45', size: '456KB' }
])

const documents = ref([
  { id: 1, title: '劳动仲裁申请书', docType: '仲裁申请书', status: 'finalized', statusText: '已定稿', updatedAt: '2024-01-10' },
  { id: 2, title: '证据清单', docType: '证据清单', status: 'draft', statusText: '草稿', updatedAt: '2024-01-12' }
])

const analysisResult = ref<any>(null)

async function fetchCaseDetail() {
  loading.value = true
  try {
    const id = route.params.id as string
    // await caseStore.fetchCaseDetail(id)
    // caseDetail.value = caseStore.caseDetail

    // 模拟AI分析结果
    analysisResult.value = {
      advantages: [
        '公司规章制度未经民主程序，解除依据不足',
        '考勤记录显示无旷工行为',
        '有录音证明解除时未说明具体理由',
        '解除通知未依法送达'
      ],
      risks: [
        '加班费主张缺乏加班审批记录',
        '年休假已休部分需进一步核实',
        '部分证据原件可能难以获取'
      ],
      strategies: [
        '重点收集公司规章制度公示证据',
        '补充收集领导安排加班的聊天记录',
        '申请证人出庭作证',
        '准备多个备选调解方案'
      ],
      winProbability: 78,
      probabilityText: '基于127件相似案例分析，胜诉概率较高',
      similarCases: [
        { caseNumber: '(2023)沪01民终12345号', title: '张某 vs 某科技公司', result: '胜诉', similarity: 85 },
        { caseNumber: '(2022)京02民终6789号', title: '李某 vs 某贸易公司', result: '胜诉', similarity: 82 }
      ]
    }
  } catch (error: any) {
    ElMessage.error(error.message || '获取案件详情失败')
  } finally {
    loading.value = false
  }
}

function handleEdit() {
  router.push(`/case/edit/${caseDetail.value.id}`)
}

async function handleAnalyze() {
  ElMessage.info('正在分析中...')
  // 实际调用AI分析
}

function handleCreateDocument() {
  router.push({ path: '/document/create', query: { caseId: caseDetail.value.id } })
}

function handleAddTimeline() {
  ElMessage.info('添加时间线事件')
}

function handleUploadEvidence() {
  ElMessage.info('上传证据')
}

function handlePreviewEvidence(row: any) {
  ElMessage.info('预览证据')
}

function handleDownloadEvidence(row: any) {
  ElMessage.info('下载证据')
}

function handleViewDocument(row: any) {
  router.push(`/document/edit/${row.id}`)
}

function handleEditDocument(row: any) {
  router.push(`/document/edit/${row.id}`)
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
  return amount?.toLocaleString() || '0'
}

function getWinProbabilityColor(probability: number) {
  if (probability >= 70) return '#67c23a'
  if (probability >= 40) return '#e6a23c'
  return '#f56c6c'
}

onMounted(() => {
  fetchCaseDetail()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.case-detail-container {
  .header-card {
    margin-bottom: $spacing-lg;

    .case-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;

      .case-info {
        h1 {
          margin: 0 0 $spacing-sm;
          font-size: $font-size-xl;
        }

        .case-meta {
          display: flex;
          align-items: center;
          gap: $spacing-md;
          color: $text-secondary;

          .el-tag {
            margin-left: 0;
          }
        }
      }

      .case-actions {
        display: flex;
        gap: $spacing-sm;
      }
    }
  }

  .detail-tabs {
    :deep(.el-tabs__content) {
      padding: $spacing-md 0;
    }
  }

  .timeline-header,
  .evidence-header,
  .document-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: $spacing-md;
    font-weight: 600;
  }

  .focus-tag {
    margin-right: $spacing-xs;
  }

  .analysis-section {
    margin-bottom: $spacing-lg;

    h3 {
      margin: 0 0 $spacing-md;
      font-size: $font-size-md;
      color: $text-primary;
    }

    ul, ol {
      margin: 0;
      padding-left: $spacing-lg;

      li {
        margin-bottom: $spacing-sm;
        display: flex;
        align-items: flex-start;
        gap: $spacing-xs;

        .el-icon {
          margin-top: 4px;
        }
      }
    }

    .probability-text {
      margin-top: $spacing-sm;
      color: $text-secondary;
    }
  }
}

@media (max-width: 768px) {
  .case-detail-container {
    .header-card {
      .case-header {
        flex-direction: column;
        gap: $spacing-md;

        .case-actions {
          width: 100%;
          flex-wrap: wrap;
        }
      }
    }
  }
}
</style>
