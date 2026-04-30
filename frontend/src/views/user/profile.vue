<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 个人信息卡片 -->
      <el-col :xs="24" :lg="8">
        <el-card class="profile-card">
          <div class="avatar-section">
            <el-avatar :size="100" :src="userInfo.avatar">
              <el-icon :size="40"><UserFilled /></el-icon>
            </el-avatar>
            <el-upload
              class="avatar-upload"
              action="/api/user/avatar"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
            >
              <el-button size="small" text>更换头像</el-button>
            </el-upload>
          </div>
          <div class="user-info">
            <h2>{{ userInfo.name || userInfo.username }}</h2>
            <p class="user-role">{{ getRoleLabel(userInfo.role) }}</p>
            <p class="user-dept">{{ userInfo.department }}</p>
          </div>
          <div class="user-stats">
            <div class="stat-item">
              <div class="stat-value">{{ userStats.caseCount }}</div>
              <div class="stat-label">经办案件</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ userStats.winRate }}%</div>
              <div class="stat-label">胜诉率</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ userStats.documentCount }}</div>
              <div class="stat-label">生成文书</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 信息编辑区域 -->
      <el-col :xs="24" :lg="16">
        <el-card>
          <el-tabs v-model="activeTab">
            <el-tab-pane label="基本信息" name="info">
              <el-form
                ref="infoFormRef"
                :model="infoForm"
                :rules="infoRules"
                label-width="100px"
                class="info-form"
              >
                <el-form-item label="用户名">
                  <el-input v-model="userInfo.username" disabled />
                </el-form-item>
                <el-form-item label="姓名" prop="name">
                  <el-input v-model="infoForm.name" placeholder="请输入姓名" />
                </el-form-item>
                <el-form-item label="邮箱" prop="email">
                  <el-input v-model="infoForm.email" placeholder="请输入邮箱" />
                </el-form-item>
                <el-form-item label="手机号" prop="phone">
                  <el-input v-model="infoForm.phone" placeholder="请输入手机号" />
                </el-form-item>
                <el-form-item label="执业证号" prop="licenseNumber">
                  <el-input v-model="infoForm.licenseNumber" placeholder="请输入执业证号" />
                </el-form-item>
                <el-form-item label="所属律所" prop="lawFirm">
                  <el-input v-model="infoForm.lawFirm" placeholder="请输入所属律所" />
                </el-form-item>
                <el-form-item label="个人简介" prop="bio">
                  <el-input
                    v-model="infoForm.bio"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入个人简介"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="saving" @click="handleSaveInfo">
                    保存修改
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="修改密码" name="password">
              <el-form
                ref="passwordFormRef"
                :model="passwordForm"
                :rules="passwordRules"
                label-width="100px"
                class="info-form"
              >
                <el-form-item label="当前密码" prop="oldPassword">
                  <el-input
                    v-model="passwordForm.oldPassword"
                    type="password"
                    placeholder="请输入当前密码"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="新密码" prop="newPassword">
                  <el-input
                    v-model="passwordForm.newPassword"
                    type="password"
                    placeholder="请输入新密码"
                    show-password
                  />
                </el-form-item>
                <el-form-item label="确认密码" prop="confirmPassword">
                  <el-input
                    v-model="passwordForm.confirmPassword"
                    type="password"
                    placeholder="请再次输入新密码"
                    show-password
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="changingPassword" @click="handleChangePassword">
                    修改密码
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="通知设置" name="notification">
              <el-form label-width="120px" class="info-form">
                <el-form-item label="案件提醒">
                  <el-switch v-model="notificationSettings.caseReminder" />
                  <span class="setting-desc">案件重要节点提醒</span>
                </el-form-item>
                <el-form-item label="文书提醒">
                  <el-switch v-model="notificationSettings.documentReminder" />
                  <span class="setting-desc">文书到期提醒</span>
                </el-form-item>
                <el-form-item label="系统通知">
                  <el-switch v-model="notificationSettings.systemNotice" />
                  <span class="setting-desc">系统公告和更新通知</span>
                </el-form-item>
                <el-form-item label="邮件通知">
                  <el-switch v-model="notificationSettings.emailNotification" />
                  <span class="setting-desc">重要消息邮件提醒</span>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" :loading="savingNotification" @click="handleSaveNotification">
                    保存设置
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

const userStore = useUserStore()

const activeTab = ref('info')
const saving = ref(false)
const changingPassword = ref(false)
const savingNotification = ref(false)

const infoFormRef = ref<FormInstance>()
const passwordFormRef = ref<FormInstance>()

const userInfo = ref({
  username: 'lawyer001',
  name: '张律师',
  email: 'lawyer@example.com',
  phone: '13800138000',
  avatar: '',
  role: 'lawyer',
  department: '劳动法律师团队',
  licenseNumber: '13101202012345678',
  lawFirm: 'XX律师事务所',
  bio: '专注于劳动法领域，擅长处理劳动争议、工伤赔偿等案件。'
})

const userStats = ref({
  caseCount: 156,
  winRate: 78,
  documentCount: 324
})

const infoForm = reactive({
  name: '',
  email: '',
  phone: '',
  licenseNumber: '',
  lawFirm: '',
  bio: ''
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const notificationSettings = reactive({
  caseReminder: true,
  documentReminder: true,
  systemNotice: true,
  emailNotification: false
})

const infoRules: FormRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const passwordRules: FormRules = {
  oldPassword: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

function getRoleLabel(role: string) {
  const labels: Record<string, string> = {
    admin: '管理员',
    lawyer: '主办律师',
    assistant: '律师助理'
  }
  return labels[role] || '律师'
}

function handleAvatarSuccess(response: any) {
  if (response.success) {
    userInfo.value.avatar = response.data.url
    ElMessage.success('头像更新成功')
  }
}

async function handleSaveInfo() {
  const valid = await infoFormRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    await userStore.updateUserInfo(infoForm)
    ElMessage.success('保存成功')
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function handleChangePassword() {
  const valid = await passwordFormRef.value?.validate().catch(() => false)
  if (!valid) return

  changingPassword.value = true
  try {
    await userStore.changePassword(passwordForm.oldPassword, passwordForm.newPassword)
    ElMessage.success('密码修改成功')
    passwordFormRef.value?.resetFields()
  } catch (error: any) {
    ElMessage.error(error.message || '密码修改失败')
  } finally {
    changingPassword.value = false
  }
}

async function handleSaveNotification() {
  savingNotification.value = true
  try {
    // 保存通知设置
    await new Promise(resolve => setTimeout(resolve, 500))
    ElMessage.success('设置保存成功')
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    savingNotification.value = false
  }
}

onMounted(() => {
  // 初始化表单数据
  Object.assign(infoForm, {
    name: userInfo.value.name,
    email: userInfo.value.email,
    phone: userInfo.value.phone,
    licenseNumber: userInfo.value.licenseNumber,
    lawFirm: userInfo.value.lawFirm,
    bio: userInfo.value.bio
  })
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.profile-container {
  .profile-card {
    text-align: center;
    margin-bottom: $spacing-lg;

    .avatar-section {
      padding: $spacing-lg 0;

      .avatar-upload {
        margin-top: $spacing-sm;
      }
    }

    .user-info {
      h2 {
        margin: 0;
        font-size: $font-size-xl;
        color: $text-primary;
      }

      .user-role {
        margin: $spacing-xs 0;
        color: $primary-color;
        font-size: $font-size-sm;
      }

      .user-dept {
        margin: 0 0 $spacing-md;
        color: $text-secondary;
        font-size: $font-size-sm;
      }
    }

    .user-stats {
      display: flex;
      justify-content: space-around;
      padding-top: $spacing-md;
      border-top: 1px solid $border-lighter;

      .stat-item {
        text-align: center;

        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: $text-primary;
        }

        .stat-label {
          font-size: $font-size-xs;
          color: $text-secondary;
        }
      }
    }
  }

  .info-form {
    max-width: 600px;
    padding: $spacing-lg 0;

    .setting-desc {
      margin-left: $spacing-sm;
      color: $text-secondary;
      font-size: $font-size-sm;
    }
  }
}
</style>
