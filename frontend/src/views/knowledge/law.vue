<template>
  <div class="knowledge-law">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="搜索法规名称/内容" clearable />
        </el-form-item>
        <el-form-item label="分类">
          <el-cascader
            v-model="searchForm.category"
            :options="categoryOptions"
            :props="{ checkStrictly: true }"
            clearable
            placeholder="选择分类"
          />
        </el-form-item>
        <el-form-item label="效力状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="现行有效" value="valid" />
            <el-option label="已修改" value="modified" />
            <el-option label="已废止" value="abolished" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 分类导航 -->
    <div class="category-nav">
      <el-tag
        v-for="cat in quickCategories"
        :key="cat.value"
        :type="activeCategory === cat.value ? '' : 'info'"
        :effect="activeCategory === cat.value ? 'dark' : 'plain'"
        @click="selectCategory(cat.value)"
      >
        {{ cat.label }}
      </el-tag>
    </div>

    <!-- 法规列表 -->
    <el-card class="list-card">
      <div class="law-list">
        <div v-for="law in lawList" :key="law.id" class="law-item" @click="viewLawDetail(law)">
          <div class="law-header">
            <el-tag :type="getStatusType(law.status)" size="small">{{ law.statusText }}</el-tag>
            <span class="law-source">{{ law.source }}</span>
          </div>
          <h3 class="law-title">{{ law.title }}</h3>
          <p class="law-summary">{{ law.summary }}</p>
          <div class="law-meta">
            <span>发布日期: {{ law.publishDate }}</span>
            <span>实施日期: {{ law.effectDate }}</span>
          </div>
          <div class="law-footer">
            <el-tag v-for="tag in law.tags" :key="tag" size="small" type="info">{{ tag }}</el-tag>
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

    <!-- 法规详情抽屉 -->
    <el-drawer v-model="detailVisible" :title="currentLaw?.title" size="50%" destroy-on-close>
      <div v-if="currentLaw" class="law-detail">
        <div class="detail-header">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="发布机关">{{ currentLaw.source }}</el-descriptions-item>
            <el-descriptions-item label="文号">{{ currentLaw.documentNumber }}</el-descriptions-item>
            <el-descriptions-item label="发布日期">{{ currentLaw.publishDate }}</el-descriptions-item>
            <el-descriptions-item label="实施日期">{{ currentLaw.effectDate }}</el-descriptions-item>
            <el-descriptions-item label="效力状态">
              <el-tag :type="getStatusType(currentLaw.status)" size="small">
                {{ currentLaw.statusText }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="时效性">{{ currentLaw.timeliness }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <el-divider />

        <div class="detail-content">
          <div class="toc">
            <h4>目录</h4>
            <el-tree :data="currentLaw.toc" default-expand-all :props="{ label: 'title' }" />
          </div>

          <div class="content-body" v-html="currentLaw.content"></div>
        </div>

        <div class="detail-actions">
          <el-button type="primary" @click="citeLaw">
            <el-icon><Document /></el-icon> 引用
          </el-button>
          <el-button @click="collectLaw">
            <el-icon><Star /></el-icon> 收藏
          </el-button>
          <el-button @click="downloadLaw">
            <el-icon><Download /></el-icon> 下载
          </el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Star, Download } from '@element-plus/icons-vue'

const searchForm = reactive({
  keyword: '',
  category: [] as string[],
  status: ''
})

const activeCategory = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)
const detailVisible = ref(false)
const currentLaw = ref<any>(null)

const categoryOptions = [
  {
    value: 'labor_contract',
    label: '劳动合同',
    children: [
      { value: 'contract_formation', label: '合同订立' },
      { value: 'contract_termination', label: '合同解除' },
      { value: 'contract_renewal', label: '合同续签' }
    ]
  },
  {
    value: 'salary',
    label: '工资福利',
    children: [
      { value: 'wage', label: '工资支付' },
      { value: 'overtime', label: '加班工资' },
      { value: 'annual_leave', label: '年休假' }
    ]
  },
  {
    value: 'work_injury',
    label: '工伤认定',
    children: [
      { value: 'injury_recognition', label: '工伤认定' },
      { value: 'disability_assessment', label: '伤残鉴定' },
      { value: 'compensation', label: '工伤赔偿' }
    ]
  }
]

const quickCategories = [
  { value: '', label: '全部' },
  { value: 'labor_contract', label: '劳动合同' },
  { value: 'salary', label: '工资福利' },
  { value: 'social_insurance', label: '社会保险' },
  { value: 'work_injury', label: '工伤认定' },
  { value: 'labor_dispute', label: '劳动争议' }
]

const lawList = ref([
  {
    id: 1,
    title: '中华人民共和国劳动合同法',
    source: '全国人民代表大会常务委员会',
    documentNumber: '主席令第65号',
    publishDate: '2007-06-29',
    effectDate: '2008-01-01',
    status: 'valid',
    statusText: '现行有效',
    timeliness: '现行有效',
    summary: '为了完善劳动合同制度，明确劳动合同双方当事人的权利和义务，保护劳动者的合法权益，构建和发展和谐稳定的劳动关系，制定本法。',
    tags: ['劳动合同', '合同订立', '合同解除'],
    content: '<h3>第一章 总则</h3><p>第一条 为了完善劳动合同制度，明确劳动合同双方当事人的权利和义务...</p>',
    toc: [
      { title: '第一章 总则', children: [{ title: '第一条' }, { title: '第二条' }] },
      { title: '第二章 劳动合同的订立', children: [{ title: '第七条' }, { title: '第八条' }] }
    ]
  },
  {
    id: 2,
    title: '中华人民共和国劳动合同法实施条例',
    source: '国务院',
    documentNumber: '国务院令第535号',
    publishDate: '2008-09-18',
    effectDate: '2008-09-18',
    status: 'valid',
    statusText: '现行有效',
    timeliness: '现行有效',
    summary: '为了贯彻实施《中华人民共和国劳动合同法》，制定本条例。',
    tags: ['劳动合同', '实施细则'],
    content: '<h3>第一章 总则</h3><p>第一条 为了贯彻实施《中华人民共和国劳动合同法》...</p>',
    toc: []
  },
  {
    id: 3,
    title: '工伤保险条例',
    source: '国务院',
    documentNumber: '国务院令第586号',
    publishDate: '2010-12-20',
    effectDate: '2011-01-01',
    status: 'valid',
    statusText: '现行有效',
    timeliness: '现行有效',
    summary: '为了保障因工作遭受事故伤害或者患职业病的职工获得医疗救治和经济补偿，促进工伤预防和职业康复，分散用人单位的工伤风险，制定本条例。',
    tags: ['工伤认定', '工伤保险', '赔偿标准'],
    content: '<h3>第一章 总则</h3><p>第一条 为了保障因工作遭受事故伤害...</p>',
    toc: []
  }
])

function handleSearch() {
  ElMessage.info('搜索法规')
}

function handleReset() {
  Object.assign(searchForm, { keyword: '', category: [], status: '' })
}

function selectCategory(value: string) {
  activeCategory.value = value
  handleSearch()
}

function handlePageChange(page: number) {
  currentPage.value = page
  handleSearch()
}

function viewLawDetail(law: any) {
  currentLaw.value = law
  detailVisible.value = true
}

function getStatusType(status: string) {
  const types: Record<string, string> = {
    valid: 'success',
    modified: 'warning',
    abolished: 'danger'
  }
  return types[status] || 'info'
}

function citeLaw() {
  ElMessage.success('已添加到引用列表')
}

function collectLaw() {
  ElMessage.success('收藏成功')
}

function downloadLaw() {
  ElMessage.info('正在下载...')
}

onMounted(() => {
  // 加载法规数据
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.knowledge-law {
  .search-card {
    margin-bottom: $spacing-md;
  }

  .category-nav {
    margin-bottom: $spacing-md;
    display: flex;
    flex-wrap: wrap;
    gap: $spacing-sm;

    .el-tag {
      cursor: pointer;
    }
  }

  .list-card {
    .law-list {
      display: grid;
      gap: $spacing-md;
    }

    .law-item {
      padding: $spacing-lg;
      border: 1px solid $border-lighter;
      border-radius: $border-radius;
      cursor: pointer;
      transition: all $transition-timing;

      &:hover {
        border-color: $primary-color;
        box-shadow: $box-shadow-light;
      }

      .law-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: $spacing-sm;

        .law-source {
          font-size: $font-size-xs;
          color: $text-secondary;
        }
      }

      .law-title {
        margin: 0 0 $spacing-sm;
        font-size: $font-size-md;
        color: $text-primary;
      }

      .law-summary {
        margin: 0 0 $spacing-sm;
        font-size: $font-size-sm;
        color: $text-secondary;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .law-meta {
        display: flex;
        gap: $spacing-lg;
        font-size: $font-size-xs;
        color: $text-placeholder;
        margin-bottom: $spacing-sm;
      }

      .law-footer {
        display: flex;
        gap: $spacing-xs;
      }
    }

    .pagination {
      margin-top: $spacing-lg;
      display: flex;
      justify-content: flex-end;
    }
  }

  .law-detail {
    .detail-header {
      margin-bottom: $spacing-lg;
    }

    .detail-content {
      .toc {
        margin-bottom: $spacing-lg;
        padding: $spacing-md;
        background: $bg-page;
        border-radius: $border-radius;

        h4 {
          margin: 0 0 $spacing-sm;
        }
      }

      .content-body {
        line-height: 1.8;

        h3 {
          margin: $spacing-lg 0 $spacing-md;
          padding-bottom: $spacing-sm;
          border-bottom: 1px solid $border-lighter;
        }

        p {
          margin: $spacing-sm 0;
          text-indent: 2em;
        }
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
