<template>
  <div class="calculator-container">
    <el-row :gutter="20">
      <!-- 计算器面板 -->
      <el-col :xs="24" :lg="16">
        <el-card class="calculator-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">赔偿计算器</span>
              <el-radio-group v-model="calcType" @change="handleTypeChange">
                <el-radio-button label="illegal_termination">违法解除赔偿</el-radio-button>
                <el-radio-button label="overtime">加班费</el-radio-button>
                <el-radio-button label="annual_leave">年休假工资</el-radio-button>
                <el-radio-button label="work_injury">工伤赔偿</el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <!-- 违法解除赔偿计算 -->
          <el-form
            v-if="calcType === 'illegal_termination'"
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="120px"
          >
            <el-form-item label="入职日期" prop="entryDate">
              <el-date-picker
                v-model="form.entryDate"
                type="date"
                placeholder="选择入职日期"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="解除日期" prop="leaveDate">
              <el-date-picker
                v-model="form.leaveDate"
                type="date"
                placeholder="选择解除日期"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="月工资标准" prop="salary">
              <el-input-number
                v-model="form.salary"
                :min="0"
                :precision="2"
                placeholder="请输入月工资"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="工资构成">
              <el-row :gutter="10">
                <el-col :span="6">
                  <el-input v-model="form.salaryComponents.base" placeholder="基本工资" />
                </el-col>
                <el-col :span="6">
                  <el-input v-model="form.salaryComponents.performance" placeholder="绩效工资" />
                </el-col>
                <el-col :span="6">
                  <el-input v-model="form.salaryComponents.allowance" placeholder="补贴" />
                </el-col>
                <el-col :span="6">
                  <el-input v-model="form.salaryComponents.bonus" placeholder="奖金" />
                </el-col>
              </el-row>
            </el-form-item>
            <el-form-item label="所在城市" prop="city">
              <el-select v-model="form.city" placeholder="请选择城市" style="width: 100%">
                <el-option label="上海" value="上海" />
                <el-option label="北京" value="北京" />
                <el-option label="广州" value="广州" />
                <el-option label="深圳" value="深圳" />
                <el-option label="杭州" value="杭州" />
                <el-option label="南京" value="南京" />
                <el-option label="苏州" value="苏州" />
                <el-option label="成都" value="成都" />
              </el-select>
            </el-form-item>
            <el-form-item label="平均工资">
              <el-input-number
                v-model="form.averageSalary"
                :min="0"
                :precision="2"
                placeholder="解除前12个月平均工资"
                style="width: 100%"
              />
              <div class="form-tip">
                如不填写，将按月工资标准计算
              </div>
            </el-form-item>
            <el-form-item>
              <el-checkbox v-model="form.isHighSalaryCapped">
                存在高薪封顶情形（工资超过当地社平工资三倍）
              </el-checkbox>
            </el-form-item>
          </el-form>

          <!-- 加班费计算 -->
          <el-form
            v-else-if="calcType === 'overtime'"
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="120px"
          >
            <el-form-item label="月工资标准" prop="salary">
              <el-input-number
                v-model="form.salary"
                :min="0"
                :precision="2"
                placeholder="请输入月工资"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="加班时长" prop="overtimeHours">
              <el-input-number
                v-model="form.overtimeHours"
                :min="0"
                placeholder="加班小时数"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="加班类型" prop="overtimeType">
              <el-radio-group v-model="form.overtimeType">
                <el-radio label="weekday">工作日加班（1.5倍）</el-radio>
                <el-radio label="weekend">休息日加班（2倍）</el-radio>
                <el-radio label="holiday">法定节假日加班（3倍）</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>

          <!-- 年休假工资计算 -->
          <el-form
            v-else-if="calcType === 'annual_leave'"
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="120px"
          >
            <el-form-item label="月工资标准" prop="salary">
              <el-input-number
                v-model="form.salary"
                :min="0"
                :precision="2"
                placeholder="请输入月工资"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="应休年假天数" prop="annualLeaveDays">
              <el-input-number
                v-model="form.annualLeaveDays"
                :min="0"
                :max="15"
                placeholder="应休年假天数"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="已休年假天数" prop="usedLeaveDays">
              <el-input-number
                v-model="form.usedLeaveDays"
                :min="0"
                placeholder="已休年假天数"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="工作年限" prop="workYears">
              <el-input-number
                v-model="form.workYears"
                :min="0"
                placeholder="工作年限"
                style="width: 100%"
              />
            </el-form-item>
          </el-form>

          <!-- 工伤赔偿计算 -->
          <el-form
            v-else-if="calcType === 'work_injury'"
            ref="formRef"
            :model="form"
            :rules="rules"
            label-width="120px"
          >
            <el-form-item label="月工资标准" prop="salary">
              <el-input-number
                v-model="form.salary"
                :min="0"
                :precision="2"
                placeholder="请输入月工资"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="伤残等级" prop="injuryLevel">
              <el-select v-model="form.injuryLevel" placeholder="请选择伤残等级" style="width: 100%">
                <el-option v-for="i in 10" :key="i" :label="`${i}级`" :value="i" />
              </el-select>
            </el-form-item>
            <el-form-item label="所在城市" prop="city">
              <el-select v-model="form.city" placeholder="请选择城市" style="width: 100%">
                <el-option label="上海" value="上海" />
                <el-option label="北京" value="北京" />
                <el-option label="广州" value="广州" />
                <el-option label="深圳" value="深圳" />
              </el-select>
            </el-form-item>
          </el-form>

          <div class="form-actions">
            <el-button type="primary" size="large" :loading="calculating" @click="handleCalculate">
              开始计算
            </el-button>
            <el-button size="large" @click="handleReset">重置</el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 计算结果 -->
      <el-col :xs="24" :lg="8">
        <el-card class="result-card">
          <template #header>
            <span class="card-title">计算结果</span>
          </template>

          <div v-if="result" class="result-content">
            <div class="result-total">
              <span class="label">合计赔偿金额</span>
              <span class="amount">¥{{ formatAmount(result.totalAmount) }}</span>
            </div>

            <el-divider />

            <div class="result-items">
              <h4>计算明细</h4>
              <div v-for="item in result.items" :key="item.name" class="result-item">
                <div class="item-header">
                  <span class="item-name">{{ item.name }}</span>
                  <span class="item-amount">¥{{ formatAmount(item.amount) }}</span>
                </div>
                <div class="item-formula">{{ item.formula }}</div>
                <div class="item-basis">{{ item.basis }}</div>
              </div>
            </div>

            <el-divider />

            <div class="result-basis">
              <h4>法律依据</h4>
              <ul>
                <li v-for="(basis, index) in result.legalBasis" :key="index">
                  {{ basis }}
                </li>
              </ul>
            </div>

            <div class="result-actions">
              <el-button type="primary" @click="handleExport">导出计算说明</el-button>
              <el-button @click="handleInsertDocument">插入文书</el-button>
            </div>
          </div>

          <el-empty v-else description="请填写信息后开始计算" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { calculatorApi, type CompensationResult } from '@/api/calculator'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const formRef = ref<FormInstance>()
const calcType = ref('illegal_termination')
const calculating = ref(false)
const result = ref<CompensationResult | null>(null)

// 表单数据
const form = reactive({
  entryDate: '',
  leaveDate: '',
  salary: 0,
  salaryComponents: {
    base: '',
    performance: '',
    allowance: '',
    bonus: ''
  },
  city: '',
  averageSalary: 0,
  isHighSalaryCapped: false,
  overtimeHours: 0,
  overtimeType: 'weekday',
  annualLeaveDays: 5,
  usedLeaveDays: 0,
  workYears: 1,
  injuryLevel: 10
})

// 验证规则
const rules: FormRules = {
  entryDate: [{ required: true, message: '请选择入职日期', trigger: 'change' }],
  leaveDate: [{ required: true, message: '请选择解除日期', trigger: 'change' }],
  salary: [{ required: true, message: '请输入月工资', trigger: 'blur' }],
  city: [{ required: true, message: '请选择城市', trigger: 'change' }],
  overtimeHours: [{ required: true, message: '请输入加班时长', trigger: 'blur' }],
  annualLeaveDays: [{ required: true, message: '请输入应休年假天数', trigger: 'blur' }],
  injuryLevel: [{ required: true, message: '请选择伤残等级', trigger: 'change' }]
}

function handleTypeChange() {
  result.value = null
  formRef.value?.resetFields()
}

async function handleCalculate() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  calculating.value = true
  try {
    const params: any = {
      type: calcType.value,
      entryDate: form.entryDate,
      leaveDate: form.leaveDate,
      salary: form.salary,
      city: form.city
    }

    if (calcType.value === 'illegal_termination') {
      params.averageSalary = form.averageSalary || form.salary
      params.isHighSalaryCapped = form.isHighSalaryCapped
    } else if (calcType.value === 'overtime') {
      params.overtimeHours = form.overtimeHours
      params.overtimeType = form.overtimeType
    } else if (calcType.value === 'annual_leave') {
      params.annualLeaveDays = form.annualLeaveDays
      params.usedLeaveDays = form.usedLeaveDays
      params.workYears = form.workYears
    } else if (calcType.value === 'work_injury') {
      params.injuryLevel = form.injuryLevel
    }

    const res = await calculatorApi.calculate(params)
    result.value = res.data
  } catch (error: any) {
    ElMessage.error(error.message || '计算失败')
  } finally {
    calculating.value = false
  }
}

function handleReset() {
  formRef.value?.resetFields()
  result.value = null
}

function handleExport() {
  ElMessage.info('导出功能开发中')
}

function handleInsertDocument() {
  ElMessage.info('插入文书功能开发中')
}

function formatAmount(amount: number) {
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.calculator-container {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: $spacing-md;

    .card-title {
      font-size: $font-size-lg;
      font-weight: 600;
    }
  }

  .calculator-card {
    .form-tip {
      font-size: $font-size-xs;
      color: $text-secondary;
      margin-top: 4px;
    }

    .form-actions {
      margin-top: $spacing-lg;
      display: flex;
      gap: $spacing-md;
    }
  }

  .result-card {
    position: sticky;
    top: $spacing-md;

    .card-title {
      font-size: $font-size-lg;
      font-weight: 600;
    }

    .result-content {
      .result-total {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: $spacing-lg 0;

        .label {
          font-size: $font-size-base;
          color: $text-secondary;
          margin-bottom: $spacing-sm;
        }

        .amount {
          font-size: 32px;
          font-weight: 600;
          color: $danger-color;
        }
      }

      .result-items {
        h4 {
          margin: 0 0 $spacing-md;
          color: $text-primary;
        }

        .result-item {
          padding: $spacing-md;
          background: $bg-page;
          border-radius: $border-radius;
          margin-bottom: $spacing-sm;

          .item-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;

            .item-name {
              font-weight: 500;
              color: $text-primary;
            }

            .item-amount {
              color: $primary-color;
              font-weight: 500;
            }
          }

          .item-formula {
            font-size: $font-size-sm;
            color: $text-secondary;
            margin-bottom: 4px;
          }

          .item-basis {
            font-size: $font-size-xs;
            color: $text-placeholder;
          }
        }
      }

      .result-basis {
        h4 {
          margin: 0 0 $spacing-sm;
          color: $text-primary;
        }

        ul {
          margin: 0;
          padding-left: $spacing-lg;

          li {
            margin-bottom: $spacing-xs;
            font-size: $font-size-sm;
            color: $text-regular;
          }
        }
      }

      .result-actions {
        margin-top: $spacing-lg;
        display: flex;
        gap: $spacing-sm;
      }
    }
  }
}

@media (max-width: 768px) {
  .calculator-container {
    .card-header {
      .el-radio-group {
        width: 100%;
        overflow-x: auto;
        flex-wrap: nowrap;
      }
    }

    .result-card {
      position: relative;
      margin-top: $spacing-lg;
    }
  }
}
</style>
