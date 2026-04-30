<template>
  <div class="main-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="logo">
        <el-icon v-if="isCollapsed" :size="24"><Briefcase /></el-icon>
        <template v-else>
          <el-icon :size="28"><Briefcase /></el-icon>
          <span class="logo-text">律师AI助手</span>
        </template>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :collapse-transition="false"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>

        <el-sub-menu index="case">
          <template #title>
            <el-icon><Briefcase /></el-icon>
            <span>案件管理</span>
          </template>
          <el-menu-item index="/case/list">
            <el-icon><List /></el-icon>
            <template #title>案件列表</template>
          </el-menu-item>
          <el-menu-item index="/case/create">
            <el-icon><Plus /></el-icon>
            <template #title>创建案件</template>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="document">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>文书中心</span>
          </template>
          <el-menu-item index="/document/list">
            <el-icon><List /></el-icon>
            <template #title>文书列表</template>
          </el-menu-item>
          <el-menu-item index="/document/template">
            <el-icon><Tickets /></el-icon>
            <template #title>文书模板</template>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/chat">
          <el-icon><ChatDotSquare /></el-icon>
          <template #title>智能咨询</template>
        </el-menu-item>

        <el-sub-menu index="knowledge">
          <template #title>
            <el-icon><Collection /></el-icon>
            <span>知识库</span>
          </template>
          <el-menu-item index="/knowledge/list">
            <el-icon><List /></el-icon>
            <template #title>知识列表</template>
          </el-menu-item>
          <el-menu-item index="/knowledge/law">
            <el-icon><Notebook /></el-icon>
            <template #title>法规库</template>
          </el-menu-item>
          <el-menu-item index="/knowledge/case">
            <el-icon><Files /></el-icon>
            <template #title>案例库</template>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/calculator">
          <el-icon><Calculator /></el-icon>
          <template #title>赔偿计算</template>
        </el-menu-item>

        <el-menu-item index="/statistics">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>数据统计</template>
        </el-menu-item>

        <el-sub-menu index="user">
          <template #title>
            <el-icon><User /></el-icon>
            <span>用户中心</span>
          </template>
          <el-menu-item index="/user/profile">
            <el-icon><UserFilled /></el-icon>
            <template #title>个人中心</template>
          </el-menu-item>
          <el-menu-item v-if="isAdmin" index="/user/management">
            <el-icon><Avatar /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </aside>

    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶部导航 -->
      <header class="header">
        <div class="header-left">
          <el-icon
            class="collapse-btn"
            :size="20"
            @click="toggleCollapse"
          >
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- AI助手快捷入口 -->
          <el-tooltip content="智能咨询" placement="bottom">
            <el-badge :value="unreadCount" :hidden="!unreadCount" class="item">
              <el-button text @click="openChat">
                <el-icon :size="20"><ChatDotSquare /></el-icon>
              </el-button>
            </el-badge>
          </el-tooltip>

          <!-- 消息通知 -->
          <el-tooltip content="消息通知" placement="bottom">
            <el-badge :value="notificationCount" :hidden="!notificationCount" class="item">
              <el-button text>
                <el-icon :size="20"><Bell /></el-icon>
              </el-button>
            </el-badge>
          </el-tooltip>

          <!-- 用户下拉菜单 -->
          <el-dropdown @command="handleCommand">
            <div class="user-dropdown">
              <el-avatar :size="32" :src="userAvatar">
                <el-icon><UserFilled /></el-icon>
              </el-avatar>
              <span class="username">{{ username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  系统设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <keep-alive :include="cachedViews">
              <component :is="Component" />
            </keep-alive>
          </transition>
        </router-view>
      </main>

      <!-- 页脚 -->
      <footer class="footer">
        <span>律师AI助手 &copy; {{ currentYear }}</span>
        <span class="divider">|</span>
        <span>专业劳动法律师智能助手</span>
      </footer>
    </div>

    <!-- AI助手悬浮窗 -->
    <div v-if="showChatFloat" class="chat-float" :class="{ expanded: chatExpanded }">
      <div class="chat-float-header">
        <span>智能咨询助手</span>
        <el-button-group>
          <el-button text size="small" @click="chatExpanded = !chatExpanded">
            <el-icon><FullScreen v-if="!chatExpanded" /><Close v-else /></el-icon>
          </el-button>
          <el-button text size="small" @click="showChatFloat = false">
            <el-icon><Close /></el-icon>
          </el-button>
        </el-button-group>
      </div>
      <div class="chat-float-content">
        <ChatWidget />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  House,
  Briefcase,
  Document,
  ChatDotSquare,
  Collection,
  Calculator,
  DataAnalysis,
  User,
  UserFilled,
  Avatar,
  List,
  Tickets,
  Notebook,
  Files,
  Plus,
  Fold,
  Expand,
  Bell,
  ArrowDown,
  Setting,
  SwitchButton,
  Close,
  FullScreen,
} from '@element-plus/icons-vue'

// 路由
const route = useRoute()
const router = useRouter()

// Store
const userStore = useUserStore()

// 状态
const isCollapsed = ref(false)
const showChatFloat = ref(false)
const chatExpanded = ref(false)
const cachedViews = ref(['Dashboard', 'CaseList', 'DocumentList'])

// 计算属性
const activeMenu = computed(() => route.path)
const username = computed(() => userStore.userInfo?.name || userStore.userInfo?.username || '用户')
const userAvatar = computed(() => userStore.userInfo?.avatar || '')
const isAdmin = computed(() => userStore.userInfo?.role === 'admin')
const unreadCount = ref(0)
const notificationCount = ref(0)
const currentYear = computed(() => new Date().getFullYear())

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    path: item.path,
    title: item.meta.title as string
  }))
})

// 方法
function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value
}

function openChat() {
  showChatFloat.value = true
  chatExpanded.value = false
}

function handleCommand(command: string) {
  switch (command) {
    case 'profile':
      router.push('/user/profile')
      break
    case 'settings':
      router.push('/user/settings')
      break
    case 'logout':
      handleLogout()
      break
  }
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    userStore.logout()
    ElMessage.success('已退出登录')
  } catch {
    // 用户取消
  }
}

// 初始化
onMounted(() => {
  userStore.initFromCookie()
})
</script>

<style scoped lang="scss">
@import '@/styles/variables.scss';

.main-layout {
  display: flex;
  height: 100vh;
  width: 100%;
}

.sidebar {
  width: $sidebar-width;
  height: 100vh;
  background: linear-gradient(180deg, #1e3a5f 0%, #152a45 100%);
  transition: width $transition-duration $transition-timing;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  &.collapsed {
    width: $sidebar-collapsed-width;
  }
}

.logo {
  height: $header-height;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);

  .logo-text {
    white-space: nowrap;
  }
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background: transparent !important;

  &:not(.el-menu--collapse) {
    width: $sidebar-width;
  }

  :deep(.el-menu-item),
  :deep(.el-sub-menu__title) {
    color: rgba(255, 255, 255, 0.7);
    height: 48px;
    line-height: 48px;

    &:hover {
      background-color: rgba(255, 255, 255, 0.1) !important;
      color: #fff;
    }
  }

  :deep(.el-menu-item.is-active) {
    background-color: rgba($primary-color, 0.2) !important;
    color: #fff;
    border-right: 3px solid $primary-color;
  }

  :deep(.el-sub-menu.is-active > .el-sub-menu__title) {
    color: #fff;
  }

  :deep(.el-menu) {
    background: transparent !important;
  }
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: $bg-page;
}

.header {
  height: $header-height;
  background: $bg-color;
  box-shadow: $box-shadow-light;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $spacing-md;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: $spacing-md;

  .collapse-btn {
    cursor: pointer;
    color: $text-secondary;
    transition: color $transition-timing;

    &:hover {
      color: $primary-color;
    }
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: $spacing-md;

  .item {
    margin-right: $spacing-sm;
  }
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;

  .username {
    font-size: $font-size-base;
    color: $text-primary;
  }
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: $spacing-md;
}

.footer {
  height: $footer-height;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: $bg-color;
  border-top: 1px solid $border-lighter;
  font-size: $font-size-xs;
  color: $text-secondary;

  .divider {
    color: $border-color;
  }
}

// AI助手悬浮窗
.chat-float {
  position: fixed;
  right: 20px;
  bottom: 20px;
  width: 380px;
  height: 500px;
  background: $bg-color;
  border-radius: $border-radius-large;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: $z-index-modal;
  transition: all $transition-duration $transition-timing;

  &.expanded {
    width: 600px;
    height: 80vh;
  }
}

.chat-float-header {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $spacing-md;
  background: linear-gradient(90deg, $primary-color 0%, $primary-dark-color 100%);
  color: #fff;
  font-weight: 500;
}

.chat-float-content {
  flex: 1;
  overflow: hidden;
}

// 响应式
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    z-index: $z-index-modal;
    transform: translateX(-100%);

    &.collapsed {
      transform: translateX(0);
      width: $sidebar-width;
    }
  }

  .chat-float {
    width: 100%;
    height: 100%;
    right: 0;
    bottom: 0;
    border-radius: 0;

    &.expanded {
      width: 100%;
      height: 100%;
    }
  }
}
</style>
