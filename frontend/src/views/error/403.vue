<template>
  <div class="error-page">
    <div class="error-content">
      <el-icon :size="120" color="#409eff"><WarningFilled /></el-icon>
      <h1>403</h1>
      <h2>无访问权限</h2>
      <p>抱歉，您没有权限访问此页面</p>
      <el-button type="primary" @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { WarningFilled } from '@element-plus/icons-vue'

const router = useRouter()

function goHome() {
  router.push('/dashboard')
}
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: $bg-page;
}

.error-content {
  text-align: center;

  h1 {
    margin: $spacing-lg 0 $spacing-sm;
    font-size: 72px;
    font-weight: 600;
    color: $text-primary;
  }

  h2 {
    margin: 0 0 $spacing-sm;
    font-size: 24px;
    color: $text-primary;
  }

  p {
    margin: 0 0 $spacing-lg;
    color: $text-secondary;
  }
}
</style>
