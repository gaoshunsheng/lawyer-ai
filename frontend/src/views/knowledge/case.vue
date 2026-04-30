<template>
  <div class="knowledge-case">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="案号/当事人/争议焦点" clearable />
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
        <el-form-item label="法院层级">
          <el-select v-model="searchForm.courtLevel" placeholder="全部层级" clearable>
            <el-option label="最高院" value="supreme" />
            <el-option label="高院" value="high" />
            <el-option label="中院" value="middle" />
            <el-option label="基层法院" value="primary" />
          </el-select>
        </el-form-item>
        <el-form-item label="裁判结果">
          <el-select v-model="searchForm.result" placeholder="全部结果" clearable>
            <el-option label="劳动者胜诉" value="employee_win" />
            <el-option label="用人单位胜诉" value="employer_win" />
            <el-option label="部分胜诉" value="partial_win" />
          </el-select>
        </el-form-item>
        <el-form-item label="裁判年份">
          <el-date-picker
            v-model="searchForm.year"
            type="year"
            placeholder="选择年份"
            value-format="YYYY"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 案例列表 -->
    <el-card class="list-card">
      <div class="case-list">
        <div v-for="caseItem in caseList" :key="caseItem.id" class="case-item" @click="viewCaseDetail(caseItem)">
          <div class="case-header">
            <div class="case-tags">
              <el-tag :type="getResultType(caseItem.result)" size="small">
                {{ caseItem.resultText }}
              </el-tag>
              <el-tag size="small" type="info">{{ caseItem.caseTypeText }}</el-tag>
            </div>
            <span class="case-date">{{ caseItem.judgeDate }}</span>
          </div>

          <h3 class="case-title">{{ caseItem.title }}</h3>
          <p class="case-number">案号: {{ caseItem.caseNumber }}</p>

          <div class="case-summary">
            <p>{{ caseItem.summary }}</p>
          </div>

          <div class="case-points">
            <span class="label">争议焦点:</span>
            <el-tag v-for="point in caseItem.disputeFocuses" :key="point" size="small" class="point-tag">
              {{ point }}
            </el-tag>
          </div>

          <div class="case-footer">
            <div class="court-info">
              <el-icon><OfficeBuilding /></el-icon>
              <span>{{ caseItem.court }}</span>
            </div>
            <div class="similar-info">
              相似度: <span class="similarity">{{ caseItem.similarity }}%</span>
            </div>
          </div>
        </div>
      </div>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :total="total"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 案例详情抽屉 -->
    <el-drawer v-model="detailVisible" :title="currentCase?.caseNumber" size="60%" destroy-on-close>
      <div v-if="currentCase" class="case-detail">
        <div class="detail-header">
          <h2>{{ currentCase.title }}</h2>
          <div class="meta-tags">
            <el-tag :type="getResultType(currentCase.result)">{{ currentCase.resultText }}</el-tag>
            <el-tag type="info">{{ currentCase.caseTypeText }}</el-tag>
            <el-tag>{{ currentCase.procedureText }}</el-tag>
          </div>
        </div>

        <el-divider />

        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="案号">{{ currentCase.caseNumber }}</el-descriptions-item>
            <el-descriptions-item label="法院">{{ currentCase.court }}</el-descriptions-item>
            <el-descriptions-item label="裁判日期">{{ currentCase.judgeDate }}</el-descriptions-item>
            <el-descriptions-item label="案由">{{ currentCase.causeOfAction }}</el-descriptions-item>
            <el-descriptions-item label="当事人">
              {{ currentCase.plaintiff }} vs {{ currentCase.defendant }}
            </el-descriptions-item>
            <el-descriptions-item label="审判程序">{{ currentCase.procedureText }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="detail-section">
          <h4>争议焦点</h4>
          <ul>
            <li v-for="(focus, index) in currentCase.disputeFocusList" :key="index">{{ focus }}</li>
          </ul>
        </div>

        <div class="detail-section">
          <h4>裁判要旨</h4>
          <p>{{ currentCase.judgmentPoints }}</p>
        </div>

        <div class="detail-section">
          <h4>裁判结果</h4>
          <p>{{ currentCase.judgmentResult }}</p>
        </div>

        <div class="detail-section">
          <h4>法律依据</h4>
          <div class="law-references">
            <el-tag v-for="law in currentCase.lawReferences" :key="law" class="law-tag">{{ law }}</el-tag>
          </div>
        </div>

        <div class="detail-section">
          <h4>裁判文书原文</h4>
          <div class="document-content" v-html="currentCase.documentContent"></div>
        </div>

        <div class="detail-actions">
          <el-button type="primary" @click="citeCase">
            <el-icon><Document /></el-icon> 引用到文书
          </el-button>
          <el-button @click="collectCase">
            <el-icon><Star /></el-icon> 收藏案例
          </el-button>
          <el-button @click="downloadCase">
            <el-icon><Download /></el-icon> 下载文书
          </el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { OfficeBuilding, Document, Star, Download } from '@element-plus/icons-vue'

const searchForm = reactive({
  keyword: '',
  caseType: '',
  courtLevel: '',
  result: '',
  year: ''
})

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(50)
const detailVisible = ref(false)
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
    caseType: 'illegal_termination',
    caseTypeText: '违法解除',
    procedure: 'second_instance',
    procedureText: '二审',
    summary: '用人单位以劳动者严重违纪为由解除劳动合同，但仅有口头警告记录，不足以证明严重违纪事实，构成违法解除。',
    disputeFocuses: ['违法解除', '严重违纪认定', '举证责任'],
    similarity: 85,
    causeOfAction: '劳动争议',
    plaintiff: '张三',
    defendant: '某科技公司',
    disputeFocusList: [
      '是否构成违法解除劳动合同',
      '用人单位规章制度是否经过民主程序',
      '解除通知是否依法送达'
    ],
    judgmentPoints: '用人单位主张劳动者严重违纪，应当承担举证责任。本案中，公司仅提供口头警告记录，无书面规章制度、无违纪通知送达证据，不足以证明劳动者存在严重违纪行为，应承担举证不能的不利后果，构成违法解除。',
    judgmentResult: '驳回上诉，维持原判。用人单位支付违法解除劳动合同赔偿金人民币132,000元。',
    lawReferences: ['《劳动合同法》第39条', '《劳动合同法》第48条', '《劳动合同法》第87条', '《劳动争议调解仲裁法》第6条'],
    documentContent: '<p>上海市第一中级人民法院</p><p>民事判决书</p><p>（2023）沪01民终12345号</p><p>...</p>'
  },
  {
    id: 2,
    title: '李四与某贸易公司工伤赔偿纠纷一审民事判决书',
    caseNumber: '(2023)沪0105民初6789号',
    court: '上海市长宁区人民法院',
    judgeDate: '2023-07-20',
    result: 'employee_win',
    resultText: '劳动者胜诉',
    caseType: 'work_injury',
    caseTypeText: '工伤赔偿',
    procedure: 'first_instance',
    procedureText: '一审',
    summary: '劳动者在工作时间和工作场所内，因工作原因受到事故伤害，应当认定为工伤，用人单位应当承担工伤保险责任。',
    disputeFocuses: ['工伤认定', '工伤保险责任', '赔偿标准'],
    similarity: 72,
    causeOfAction: '工伤保险待遇纠纷',
    plaintiff: '李四',
    defendant: '某贸易公司',
    disputeFocusList: ['是否构成工伤', '伤残等级认定', '赔偿金额计算'],
    judgmentPoints: '根据《工伤保险条例》第十四条规定，职工在工作时间和工作场所内，因工作原因受到事故伤害的，应当认定为工伤。用人单位未依法缴纳工伤保险费的，由用人单位支付工伤保险待遇。',
    judgmentResult: '用人单位支付工伤保险待遇共计人民币286,000元。',
    lawReferences: ['《工伤保险条例》第14条', '《工伤保险条例》第30条', '《工伤保险条例》第37条'],
    documentContent: '<p>上海市长宁区人民法院</p><p>民事判决书</p><p>（2023）沪0105民初6789号</p><p>...</p>'
  }
])

function handleSearch() {
  ElMessage.info('搜索案例')
}

function handleReset() {
  Object.assign(searchForm, { keyword: '', caseType: '', courtLevel: '', result: '', year: '' })
}

function handlePageChange(page: number) {
  currentPage.value = page
  handleSearch()
}

function viewCaseDetail(caseItem: any) {
  currentCase.value = caseItem
  detailVisible.value = true
}

function getResultType(result: string) {
  const types: Record<string, string> = {
    employee_win: 'success',
    employer_win: 'danger',
    partial_win: 'warning'
  }
  return types[result] || 'info'
}

function citeCase() {
  ElMessage.success('已添加到引用列表')
}

function collectCase() {
  ElMessage.success('收藏成功')
}

function downloadCase() {
  ElMessage.info('正在下载...')
}

onMounted(() => {
  // 加载案例数据
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.knowledge-case {
  .search-card {
    margin-bottom: $spacing-md;
  }

  .list-card {
    .case-list {
      display: grid;
      gap: $spacing-md;
    }

    .case-item {
      padding: $spacing-lg;
      border: 1px solid $border-lighter;
      border-radius: $border-radius;
      cursor: pointer;
      transition: all $transition-timing;

      &:hover {
        border-color: $primary-color;
        box-shadow: $box-shadow-light;
      }

      .case-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: $spacing-sm;

        .case-tags {
          display: flex;
          gap: $spacing-xs;
        }

        .case-date {
          font-size: $font-size-xs;
          color: $text-secondary;
        }
      }

      .case-title {
        margin: 0 0 $spacing-xs;
        font-size: $font-size-md;
        color: $text-primary;
      }

      .case-number {
        margin: 0 0 $spacing-sm;
        font-size: $font-size-sm;
        color: $text-secondary;
      }

      .case-summary {
        margin-bottom: $spacing-sm;

        p {
          margin: 0;
          font-size: $font-size-sm;
          color: $text-regular;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      }

      .case-points {
        display: flex;
        align-items: center;
        gap: $spacing-xs;
        margin-bottom: $spacing-sm;

        .label {
          font-size: $font-size-xs;
          color: $text-secondary;
        }

        .point-tag {
          font-size: $font-size-xs;
        }
      }

      .case-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .court-info {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: $font-size-xs;
          color: $text-secondary;
        }

        .similarity {
          font-size: $font-size-sm;
          font-weight: 600;
          color: $primary-color;
        }
      }
    }

    .pagination {
      margin-top: $spacing-lg;
      display: flex;
      justify-content: flex-end;
    }
  }

  .case-detail {
    .detail-header {
      h2 {
        margin: 0 0 $spacing-sm;
        font-size: $font-size-lg;
      }

      .meta-tags {
        display: flex;
        gap: $spacing-xs;
      }
    }

    .detail-section {
      margin-bottom: $spacing-lg;

      h4 {
        margin: 0 0 $spacing-md;
        padding-bottom: $spacing-sm;
        border-bottom: 1px solid $border-lighter;
        color: $text-primary;
      }

      p {
        margin: 0;
        line-height: 1.8;
        color: $text-regular;
      }

      ul {
        margin: 0;
        padding-left: $spacing-lg;

        li {
          margin-bottom: $spacing-xs;
          line-height: 1.6;
        }
      }

      .law-references {
        display: flex;
        flex-wrap: wrap;
        gap: $spacing-xs;

        .law-tag {
          cursor: pointer;

          &:hover {
            color: $primary-color;
          }
        }
      }

      .document-content {
        padding: $spacing-md;
        background: $bg-page;
        border-radius: $border-radius;
        line-height: 1.8;
        max-height: 400px;
        overflow-y: auto;
      }
    }

    .detail-actions {
      margin-top: $spacing-lg;
      padding-top: $spacing-lg;
      border-top: 1px solid $border-lighter;
      display: flex;
      gap: $spacing-sm;
    }
  }
}
</style>
