<template>
  <div class="knowledge-container">
    <el-tabs v-model="activeTab" class="knowledge-tabs">
      <!-- 法规库 -->
      <el-tab-pane label="法规库" name="law">
        <div class="search-bar">
          <el-input
            v-model="lawSearch"
            placeholder="搜索法规..."
            prefix-icon="Search"
            clearable
            style="width: 300px"
            @keyup.enter="searchLaws"
          />
          <el-select v-model="lawCategory" placeholder="法规分类" clearable style="width: 200px">
            <el-option label="劳动合同" value="labor_contract" />
            <el-option label="工资福利" value="salary" />
            <el-option label="社会保险" value="social_insurance" />
            <el-option label="工伤认定" value="work_injury" />
            <el-option label="其他" value="other" />
          </el-select>
          <el-button type="primary" @click="searchLaws">搜索</el-button>
        </div>

        <div class="law-list">
          <div v-for="law in lawList" :key="law.id" class="law-item" @click="viewLaw(law)">
            <div class="law-header">
              <el-tag size="small">{{ law.category }}</el-tag>
              <span class="law-date">{{ law.publishDate }}</span>
            </div>
            <h3 class="law-title">{{ law.title }}</h3>
            <p class="law-summary">{{ law.summary }}</p>
            <div class="law-footer">
              <span><el-icon><View /></el-icon> {{ law.viewCount }}次浏览</span>
              <span><el-icon><Document /></el-icon> {{ law.referenceCount }}次引用</span>
            </div>
          </div>
        </div>

        <div class="pagination">
          <el-pagination
            v-model:current-page="lawPage"
            :total="lawTotal"
            :page-size="10"
            layout="prev, pager, next"
            @current-change="searchLaws"
          />
        </div>
      </el-tab-pane>

      <!-- 案例库 -->
      <el-tab-pane label="案例库" name="case">
        <div class="search-bar">
          <el-input
            v-model="caseSearch"
            placeholder="搜索案例..."
            prefix-icon="Search"
            clearable
            style="width: 300px"
            @keyup.enter="searchCases"
          />
          <el-select v-model="caseType" placeholder="案件类型" clearable style="width: 200px">
            <el-option label="违法解除" value="illegal_termination" />
            <el-option label="工伤赔偿" value="work_injury" />
            <el-option label="加班费争议" value="overtime" />
            <el-option label="年休假工资" value="annual_leave" />
          </el-select>
          <el-select v-model="caseResult" placeholder="裁判结果" clearable style="width: 150px">
            <el-option label="劳动者胜诉" value="employee_win" />
            <el-option label="用人单位胜诉" value="employer_win" />
            <el-option label="部分胜诉" value="partial_win" />
          </el-select>
          <el-button type="primary" @click="searchCases">搜索</el-button>
        </div>

        <div class="case-list">
          <div v-for="caseItem in caseList" :key="caseItem.id" class="case-item" @click="viewCase(caseItem)">
            <div class="case-header">
              <el-tag :type="getCaseResultType(caseItem.result)" size="small">
                {{ caseItem.resultText }}
              </el-tag>
              <span class="case-court">{{ caseItem.court }}</span>
            </div>
            <h3 class="case-title">{{ caseItem.title }}</h3>
            <p class="case-summary">{{ caseItem.summary }}</p>
            <div class="case-points">
              <span v-for="point in caseItem.keyPoints" :key="point" class="point-tag">
                {{ point }}
              </span>
            </div>
            <div class="case-footer">
              <span>案号: {{ caseItem.caseNumber }}</span>
              <span>裁判日期: {{ caseItem.judgeDate }}</span>
            </div>
          </div>
        </div>

        <div class="pagination">
          <el-pagination
            v-model:current-page="casePage"
            :total="caseTotal"
            :page-size="10"
            layout="prev, pager, next"
            @current-change="searchCases"
          />
        </div>
      </el-tab-pane>

      <!-- 知识列表 -->
      <el-tab-pane label="知识列表" name="list">
        <div class="action-bar">
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon> 添加知识
          </el-button>
        </div>

        <el-table :data="knowledgeList" style="width: 100%">
          <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
          <el-table-column prop="docType" label="类型" width="100">
            <template #default="{ row }">
              <el-tag size="small">{{ row.docTypeText }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="category" label="分类" width="120" />
          <el-table-column prop="createdAt" label="创建时间" width="160" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button type="primary" text size="small" @click="handleView(row)">查看</el-button>
              <el-button type="primary" text size="small" @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" text size="small" @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination">
          <el-pagination
            v-model:current-page="knowledgePage"
            :total="knowledgeTotal"
            :page-size="10"
            layout="total, prev, pager, next"
            @current-change="fetchKnowledgeList"
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 法规详情对话框 -->
    <el-dialog v-model="lawDetailVisible" :title="currentLaw?.title" width="800px" destroy-on-close>
      <div v-if="currentLaw" class="law-detail">
        <div class="law-meta">
          <span>发布机关: {{ currentLaw.publisher }}</span>
          <span>发布日期: {{ currentLaw.publishDate }}</span>
          <span>效力状态: <el-tag size="small" type="success">现行有效</el-tag></span>
        </div>
        <el-divider />
        <div class="law-content" v-html="currentLaw.content"></div>
        <div class="law-actions">
          <el-button type="primary" @click="handleCiteLaw(currentLaw)">
            <el-icon><Document /></el-icon> 引用到文书
          </el-button>
          <el-button @click="handleCollectLaw(currentLaw)">
            <el-icon><Star /></el-icon> 收藏
          </el-button>
        </div>
      </div>
    </el-dialog>

    <!-- 案例详情对话框 -->
    <el-dialog v-model="caseDetailVisible" :title="currentCase?.title" width="800px" destroy-on-close>
      <div v-if="currentCase" class="case-detail">
        <div class="case-meta">
          <span>案号: {{ currentCase.caseNumber }}</span>
          <span>法院: {{ currentCase.court }}</span>
          <span>裁判日期: {{ currentCase.judgeDate }}</span>
        </div>
        <el-divider />
        <div class="case-section">
          <h4>争议焦点</h4>
          <p>{{ currentCase.disputeFocus }}</p>
        </div>
        <div class="case-section">
          <h4>裁判要旨</h4>
          <p>{{ currentCase.judgmentPoints }}</p>
        </div>
        <div class="case-section">
          <h4>裁判结果</h4>
          <p>{{ currentCase.judgmentResult }}</p>
        </div>
        <div class="case-actions">
          <el-button type="primary" @click="handleCiteCase(currentCase)">
            <el-icon><Document /></el-icon> 引用到文书
          </el-button>
          <el-button @click="handleCollectCase(currentCase)">
            <el-icon><Star /></el-icon> 收藏
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, View, Document, Star } from '@element-plus/icons-vue'

const activeTab = ref('law')

// 法规相关
const lawSearch = ref('')
const lawCategory = ref('')
const lawPage = ref(1)
const lawTotal = ref(100)
const lawDetailVisible = ref(false)
const currentLaw = ref<any>(null)

const lawList = ref([
  {
    id: 1,
    title: '中华人民共和国劳动合同法',
    category: '劳动合同',
    publishDate: '2012-12-28',
    summary: '为了完善劳动合同制度，明确劳动合同双方当事人的权利和义务，保护劳动者的合法权益，构建和发展和谐稳定的劳动关系，制定本法。',
    viewCount: 1234,
    referenceCount: 567,
    publisher: '全国人民代表大会常务委员会',
    content: '<h3>第一章 总则</h3><p>第一条 为了完善劳动合同制度...</p>'
  },
  {
    id: 2,
    title: '工伤保险条例',
    category: '工伤认定',
    publishDate: '2010-12-20',
    summary: '为了保障因工作遭受事故伤害或者患职业病的职工获得医疗救治和经济补偿，促进工伤预防和职业康复，分散用人单位的工伤风险，制定本条例。',
    viewCount: 892,
    referenceCount: 345,
    publisher: '国务院',
    content: '<h3>第一章 总则</h3><p>第一条 为了保障因工作遭受事故伤害...</p>'
  },
  {
    id: 3,
    title: '职工带薪年休假条例',
    category: '工资福利',
    publishDate: '2007-12-14',
    summary: '为了维护职工休息休假权利，调动职工工作积极性，根据劳动法和公务员法，制定本条例。',
    viewCount: 456,
    referenceCount: 123,
    publisher: '国务院',
    content: '<h3>第一条</h3><p>为了维护职工休息休假权利...</p>'
  }
])

// 案例相关
const caseSearch = ref('')
const caseType = ref('')
const caseResult = ref('')
const casePage = ref(1)
const caseTotal = ref(50)
const caseDetailVisible = ref(false)
const currentCase = ref<any>(null)

const caseList = ref([
  {
    id: 1,
    title: '张三与某科技公司劳动争议纠纷二审民事判决书',
    caseNumber: '(2023)沪01民终12345号',
    court: '上海市第一中级人民法院',
    judgeDate: '2023-08-15',
    result: 'employee_win',
    resultText: '劳动者胜诉',
    summary: '用人单位以劳动者严重违纪为由解除劳动合同，但仅有口头警告记录，不足以证明严重违纪事实，构成违法解除。',
    keyPoints: ['违法解除', '严重违纪认定', '举证责任'],
    disputeFocus: '是否构成违法解除',
    judgmentPoints: '用人单位主张劳动者严重违纪，应当承担举证责任...',
    judgmentResult: '驳回上诉，维持原判。用人单位支付违法解除赔偿金人民币XX元。'
  },
  {
    id: 2,
    title: '李四与某贸易公司工伤赔偿纠纷一审民事判决书',
    caseNumber: '(2023)沪0105民初6789号',
    court: '上海市长宁区人民法院',
    judgeDate: '2023-07-20',
    result: 'employee_win',
    resultText: '劳动者胜诉',
    summary: '劳动者在工作时间和工作场所内，因工作原因受到事故伤害，应当认定为工伤，用人单位应当承担工伤保险责任。',
    keyPoints: ['工伤认定', '工伤保险责任', '赔偿标准'],
    disputeFocus: '是否构成工伤',
    judgmentPoints: '根据《工伤保险条例》第十四条规定...',
    judgmentResult: '用人单位支付工伤保险待遇人民币XX元。'
  }
])

// 知识列表相关
const knowledgePage = ref(1)
const knowledgeTotal = ref(30)

const knowledgeList = ref([
  { id: 1, title: '违法解除劳动合同的认定标准', docType: 'article', docTypeText: '文章', category: '劳动法', createdAt: '2024-01-15' },
  { id: 2, title: '工伤认定流程及注意事项', docType: 'guide', docTypeText: '指引', category: '工伤', createdAt: '2024-01-14' },
  { id: 3, title: '加班费计算方法汇总', docType: 'article', docTypeText: '文章', category: '工资', createdAt: '2024-01-13' }
])

function searchLaws() {
  ElMessage.info('搜索法规')
}

function searchCases() {
  ElMessage.info('搜索案例')
}

function fetchKnowledgeList() {
  // 获取知识列表
}

function viewLaw(law: any) {
  currentLaw.value = law
  lawDetailVisible.value = true
}

function viewCase(caseItem: any) {
  currentCase.value = caseItem
  caseDetailVisible.value = true
}

function getCaseResultType(result: string) {
  const types: Record<string, string> = {
    employee_win: 'success',
    employer_win: 'danger',
    partial_win: 'warning'
  }
  return types[result] || 'info'
}

function handleCreate() {
  ElMessage.info('添加知识')
}

function handleView(row: any) {
  ElMessage.info('查看知识')
}

function handleEdit(row: any) {
  ElMessage.info('编辑知识')
}

async function handleDelete(row: any) {
  try {
    await ElMessageBox.confirm('确定要删除该知识吗？', '提示', { type: 'warning' })
    ElMessage.success('删除成功')
  } catch {
    // 取消删除
  }
}

function handleCiteLaw(law: any) {
  ElMessage.success('已添加引用')
}

function handleCollectLaw(law: any) {
  ElMessage.success('收藏成功')
}

function handleCiteCase(caseItem: any) {
  ElMessage.success('已添加引用')
}

function handleCollectCase(caseItem: any) {
  ElMessage.success('收藏成功')
}

onMounted(() => {
  // 初始化数据
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.knowledge-container {
  .knowledge-tabs {
    background: $bg-color;
    border-radius: $border-radius;
    padding: $spacing-md;
  }

  .search-bar {
    display: flex;
    gap: $spacing-sm;
    margin-bottom: $spacing-lg;
  }

  .action-bar {
    margin-bottom: $spacing-md;
  }

  .law-list, .case-list {
    display: grid;
    gap: $spacing-md;
  }

  .law-item, .case-item {
    padding: $spacing-lg;
    border: 1px solid $border-lighter;
    border-radius: $border-radius;
    cursor: pointer;
    transition: all $transition-timing;

    &:hover {
      border-color: $primary-color;
      box-shadow: $box-shadow-light;
    }

    .law-header, .case-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: $spacing-sm;

      .law-date, .case-court {
        font-size: $font-size-xs;
        color: $text-secondary;
      }
    }

    .law-title, .case-title {
      margin: 0 0 $spacing-sm;
      font-size: $font-size-md;
      color: $text-primary;
    }

    .law-summary, .case-summary {
      margin: 0 0 $spacing-sm;
      font-size: $font-size-sm;
      color: $text-secondary;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .case-points {
      display: flex;
      flex-wrap: wrap;
      gap: $spacing-xs;
      margin-bottom: $spacing-sm;

      .point-tag {
        padding: 2px 8px;
        background: rgba($primary-color, 0.1);
        color: $primary-color;
        border-radius: $border-radius-small;
        font-size: $font-size-xs;
      }
    }

    .law-footer, .case-footer {
      display: flex;
      gap: $spacing-md;
      font-size: $font-size-xs;
      color: $text-placeholder;

      span {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }

  .pagination {
    margin-top: $spacing-lg;
    display: flex;
    justify-content: center;
  }

  .law-detail, .case-detail {
    .law-meta, .case-meta {
      display: flex;
      gap: $spacing-lg;
      font-size: $font-size-sm;
      color: $text-secondary;
    }

    .law-content {
      line-height: 1.8;
    }

    .case-section {
      margin-bottom: $spacing-lg;

      h4 {
        margin: 0 0 $spacing-sm;
        color: $text-primary;
      }

      p {
        margin: 0;
        color: $text-regular;
        line-height: 1.8;
      }
    }

    .law-actions, .case-actions {
      margin-top: $spacing-lg;
      display: flex;
      gap: $spacing-sm;
    }
  }
}
</style>
