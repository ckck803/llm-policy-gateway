<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import Dashboard from './pages/Dashboard.vue'
import Playground from './pages/Playground.vue'
import Models from './pages/Models.vue'
import RoutingLogs from './pages/RoutingLogs.vue'
import Policies from './pages/Policies.vue'
import ProviderCredentials from './pages/ProviderCredentials.vue'
import Users from './pages/Users.vue'
import Screens from './pages/Screens.vue'
import Login from './pages/Login.vue'
import {
  ActivityIcon,
  BotIcon,
  CpuIcon,
  KeyRoundIcon,
  LayoutDashboardIcon,
  LayoutIcon,
  LogOutIcon,
  MoonIcon,
  RouteIcon,
  SunIcon,
  TerminalIcon,
  UsersIcon
} from 'lucide-vue-next'
import { AppUser, clearAuthToken, getAuthToken, setAuthToken, useApi } from './composables/useApi'
import { useTheme } from './composables/useTheme'

const tabs = [
  { id: 'dashboard', label: 'Dashboard', component: Dashboard, group: 'service', icon: LayoutDashboardIcon },
  { id: 'playground', label: 'Playground', component: Playground, group: 'service', icon: TerminalIcon },
  { id: 'models', label: 'Models', component: Models, group: 'service', icon: CpuIcon },
  { id: 'policies', label: 'Policies', component: Policies, group: 'service', icon: RouteIcon },
  { id: 'credentials', label: 'Credentials', component: ProviderCredentials, group: 'service', icon: KeyRoundIcon },
  { id: 'logs', label: 'Routing Logs', component: RoutingLogs, group: 'service', icon: ActivityIcon },
  { id: 'users', label: 'Users', component: Users, group: 'admin', icon: UsersIcon },
  { id: 'screens', label: 'Screens', component: Screens, group: 'admin', icon: LayoutIcon }
] as const

const navGroups = [
  { id: 'service', label: 'Service' },
  { id: 'admin', label: 'Access Management' }
] as const

const { isDark, toggle: toggleTheme } = useTheme()
const api = useApi()
const currentUser = ref<AppUser | null>(null)
const authReady = ref(false)
const activeTab = ref<(typeof tabs)[number]['id']>('dashboard')
const visibleTabs = computed(() =>
  tabs.filter((tab) => currentUser.value?.allowed_screens.includes(tab.id) ?? false)
)
const visibleNavGroups = computed(() =>
  navGroups
    .map((group) => ({
      ...group,
      tabs: visibleTabs.value.filter((tab) => tab.group === group.id)
    }))
    .filter((group) => group.tabs.length > 0)
)
const activeComponent = computed(
  () =>
    visibleTabs.value.find((tab) => tab.id === activeTab.value)?.component ??
    visibleTabs.value[0]?.component ??
    Dashboard
)

async function loadMe() {
  try {
    currentUser.value = await api.getMe()
    if (!visibleTabs.value.some((tab) => tab.id === activeTab.value) && visibleTabs.value[0]) {
      activeTab.value = visibleTabs.value[0].id
    }
  } catch {
    clearAuthToken()
    currentUser.value = null
  } finally {
    authReady.value = true
  }
}

async function handleLoggedIn(token: string) {
  setAuthToken(token)
  await loadMe()
}

async function logout() {
  try {
    await api.logout()
  } catch {
    // ignore server logout failure
  }
  clearAuthToken()
  currentUser.value = null
}

onMounted(async () => {
  if (getAuthToken()) {
    await loadMe()
  } else {
    authReady.value = true
  }
})
</script>

<template>
  <Login v-if="authReady && !currentUser" @logged-in="handleLoggedIn" />

  <div v-else-if="authReady" class="flex min-h-screen bg-zinc-950">
    <!-- Sidebar -->
    <aside class="flex w-64 shrink-0 flex-col bg-sidebar border-r border-zinc-800/60">
      <!-- Logo -->
      <div class="flex items-center gap-3 px-5 py-5 border-b border-zinc-800/60">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
          <BotIcon class="h-4 w-4 text-white" />
        </div>
        <div>
          <p class="text-[10px] font-semibold uppercase tracking-widest text-zinc-500">LLM Gateway</p>
          <p class="text-sm font-semibold text-zinc-100 leading-tight">Routing Admin</p>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        <div v-for="group in visibleNavGroups" :key="group.id">
          <p class="mb-1 px-2 text-[10px] font-semibold uppercase tracking-widest text-zinc-600">
            {{ group.label }}
          </p>
          <div class="space-y-0.5">
            <button
              v-for="tab in group.tabs"
              :key="tab.id"
              :class="[
                'flex w-full items-center gap-3 rounded-md px-2.5 py-2 text-sm font-medium transition-all duration-150',
                activeTab === tab.id
                  ? 'bg-indigo-600/15 text-indigo-400 border border-indigo-500/20'
                  : 'text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-200 border border-transparent'
              ]"
              @click="activeTab = tab.id"
            >
              <component
                :is="tab.icon"
                :class="['h-4 w-4 shrink-0', activeTab === tab.id ? 'text-indigo-400' : 'text-zinc-500']"
              />
              {{ tab.label }}
            </button>
          </div>
        </div>
      </nav>

      <!-- User footer -->
      <div class="border-t border-zinc-800/60 p-3">
        <div class="flex items-center gap-3 rounded-lg p-2 hover:bg-zinc-800/50 transition-colors group">
          <div class="flex h-8 w-8 items-center justify-center rounded-full bg-zinc-700 shrink-0">
            <span class="text-xs font-semibold text-zinc-300 uppercase">
              {{ currentUser?.username?.charAt(0) ?? '?' }}
            </span>
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-zinc-200">{{ currentUser?.username }}</p>
            <p class="text-xs text-zinc-500">{{ currentUser?.is_staff ? 'Admin' : 'User' }}</p>
          </div>
          <button
            class="shrink-0 rounded p-1.5 text-zinc-500 hover:bg-zinc-700 hover:text-zinc-200 transition-colors"
            :title="isDark ? 'Switch to Light mode' : 'Switch to Dark mode'"
            type="button"
            @click="toggleTheme"
          >
            <SunIcon v-if="isDark" class="h-4 w-4" />
            <MoonIcon v-else class="h-4 w-4" />
          </button>
          <button
            class="shrink-0 rounded p-1.5 text-zinc-500 hover:bg-zinc-700 hover:text-zinc-200 transition-colors"
            title="Logout"
            type="button"
            @click="logout"
          >
            <LogOutIcon class="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 min-w-0 overflow-auto">
      <component :is="activeComponent" />
    </main>
  </div>

  <!-- Loading state -->
  <main v-else class="flex min-h-screen items-center justify-center bg-zinc-950">
    <div class="flex items-center gap-3 text-zinc-500">
      <div class="h-4 w-4 animate-spin rounded-full border-2 border-zinc-700 border-t-indigo-500"></div>
      <span class="text-sm">Loading...</span>
    </div>
  </main>
</template>
