<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import Dashboard from './pages/Dashboard.vue'
import Playground from './pages/Playground.vue'
import RoutingSimulator from './pages/RoutingSimulator.vue'
import Models from './pages/Models.vue'
import RoutingLogs from './pages/RoutingLogs.vue'
import Policies from './pages/Policies.vue'
import RoutingRules from './pages/RoutingRules.vue'
import ThresholdRules from './pages/ThresholdRules.vue'
import ValidationRules from './pages/ValidationRules.vue'
import RecoveryStrategies from './pages/RecoveryStrategies.vue'
import ProviderCredentials from './pages/ProviderCredentials.vue'
import UsageQuotas from './pages/UsageQuotas.vue'
import ModelHealthRules from './pages/ModelHealthRules.vue'
import HealthEvents from './pages/HealthEvents.vue'
import HealthOverrides from './pages/HealthOverrides.vue'
import Users from './pages/Users.vue'
import Screens from './pages/Screens.vue'
import SecuritySettings from './pages/SecuritySettings.vue'
import UserSessions from './pages/UserSessions.vue'
import AuditLogs from './pages/AuditLogs.vue'
import Login from './pages/Login.vue'
import {
  ActivityIcon,
  BotIcon,
  CheckSquareIcon,
  CpuIcon,
  KeyRoundIcon,
  GaugeIcon,
  HeartPulseIcon,
  HistoryIcon,
  ListChecksIcon,
  LayoutDashboardIcon,
  LayoutIcon,
  ListTreeIcon,
  LogOutIcon,
  MoonIcon,
  RepeatIcon,
  RouteIcon,
  SlidersHorizontalIcon,
  SunIcon,
  TerminalIcon,
  UsersIcon,
  XIcon
} from 'lucide-vue-next'
import { AppUser, LoginResponse, clearAuthToken, getAuthToken, setAuthToken, useApi } from './composables/useApi'
import { useTheme } from './composables/useTheme'

const tabs = [
  { id: 'dashboard', label: 'Dashboard', component: Dashboard, group: 'service', icon: LayoutDashboardIcon },
  { id: 'playground', label: 'Playground', component: Playground, group: 'service', icon: TerminalIcon },
  { id: 'simulator', label: 'Routing Simulator', component: RoutingSimulator, group: 'service', icon: ListChecksIcon },
  { id: 'models', label: 'Models', component: Models, group: 'service', icon: CpuIcon },
  { id: 'policies', label: 'Policies', component: Policies, group: 'service', icon: RouteIcon },
  { id: 'routing-rules', label: 'Routing Rules', component: RoutingRules, group: 'service', icon: ListTreeIcon },
  { id: 'threshold-rules', label: 'Threshold Rules', component: ThresholdRules, group: 'service', icon: SlidersHorizontalIcon },
  { id: 'validation-rules', label: 'Validation Rules', component: ValidationRules, group: 'service', icon: CheckSquareIcon },
  { id: 'recovery-strategies', label: 'Recovery Strategies', component: RecoveryStrategies, group: 'service', icon: RepeatIcon },
  { id: 'credentials', label: 'Credentials', component: ProviderCredentials, group: 'service', icon: KeyRoundIcon },
  { id: 'quotas', label: 'Usage Quotas', component: UsageQuotas, group: 'service', icon: GaugeIcon },
  { id: 'health-rules', label: 'Health Rules', component: ModelHealthRules, group: 'service', icon: HeartPulseIcon },
  { id: 'health-events', label: 'Health Events', component: HealthEvents, group: 'service', icon: HistoryIcon },
  { id: 'health-overrides', label: 'Health Overrides', component: HealthOverrides, group: 'service', icon: HeartPulseIcon },
  { id: 'logs', label: 'Routing Logs', component: RoutingLogs, group: 'service', icon: ActivityIcon },
  { id: 'users', label: 'Users', component: Users, group: 'admin', icon: UsersIcon },
  { id: 'screens', label: 'Screens', component: Screens, group: 'admin', icon: LayoutIcon },
  { id: 'security-settings', label: 'Security Settings', component: SecuritySettings, group: 'admin', icon: KeyRoundIcon },
  { id: 'sessions', label: 'User Sessions', component: UserSessions, group: 'admin', icon: ActivityIcon },
  { id: 'audit-logs', label: 'Audit Logs', component: AuditLogs, group: 'admin', icon: HistoryIcon }
] as const

type TabId = (typeof tabs)[number]['id']

const navGroups = [
  { id: 'service', label: 'Service' },
  { id: 'admin', label: 'Access Management' }
] as const

const { isDark, toggle: toggleTheme } = useTheme()
const api = useApi()
const currentUser = ref<AppUser | null>(null)
const authReady = ref(false)
const activeTab = ref<TabId>('dashboard')
const openTabs = ref<TabId[]>(['dashboard'])
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
const openTabItems = computed(() =>
  openTabs.value
    .map((tabId) => visibleTabs.value.find((tab) => tab.id === tabId))
    .filter((tab): tab is (typeof tabs)[number] => Boolean(tab))
)

function syncOpenTabsWithAccess() {
  const allowedIds = visibleTabs.value.map((tab) => tab.id)
  openTabs.value = openTabs.value.filter((tabId) => allowedIds.includes(tabId))

  if (!openTabs.value.length && visibleTabs.value[0]) {
    openTabs.value = [visibleTabs.value[0].id]
  }

  if (!openTabs.value.includes(activeTab.value) && openTabs.value[0]) {
    activeTab.value = openTabs.value[0]
  }
}

function openWorkspaceTab(tabId: TabId) {
  if (!visibleTabs.value.some((tab) => tab.id === tabId)) {
    return
  }
  if (!openTabs.value.includes(tabId)) {
    openTabs.value.push(tabId)
  }
  activeTab.value = tabId
}

function closeWorkspaceTab(tabId: TabId) {
  if (openTabs.value.length <= 1) {
    return
  }

  const closingIndex = openTabs.value.indexOf(tabId)
  openTabs.value = openTabs.value.filter((id) => id !== tabId)

  if (activeTab.value === tabId) {
    const fallbackIndex = Math.max(0, closingIndex - 1)
    activeTab.value = openTabs.value[fallbackIndex] ?? openTabs.value[0]
  }
}

async function loadMe() {
  try {
    currentUser.value = await api.getMe()
    syncOpenTabsWithAccess()
  } catch {
    clearAuthToken()
    currentUser.value = null
  } finally {
    authReady.value = true
  }
}

function handleLoggedIn(response: LoginResponse) {
  setAuthToken(response.token)
  currentUser.value = response.user
  syncOpenTabsWithAccess()
  authReady.value = true
}

async function logout() {
  try {
    await api.logout()
  } catch {
    // ignore server logout failure
  }
  clearAuthToken()
  currentUser.value = null
  activeTab.value = 'dashboard'
  openTabs.value = ['dashboard']
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
              @click="openWorkspaceTab(tab.id)"
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
    <main class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <div class="flex min-h-12 shrink-0 items-end overflow-x-auto border-b border-zinc-800/60 bg-zinc-950 px-3 pt-2">
        <button
          v-for="tab in openTabItems"
          :key="tab.id"
          :class="[
            'group mr-1 flex h-10 min-w-36 max-w-56 items-center justify-between gap-3 rounded-t-lg border px-3 text-sm font-medium transition-colors',
            activeTab === tab.id
              ? 'border-zinc-700 border-b-zinc-900 bg-zinc-900 text-zinc-100'
              : 'border-transparent bg-transparent text-zinc-500 hover:bg-zinc-900/70 hover:text-zinc-200'
          ]"
          type="button"
          @click="activeTab = tab.id"
        >
          <span class="truncate">{{ tab.label }}</span>
          <span
            :class="[
              'rounded p-0.5 transition-colors',
              openTabItems.length <= 1
                ? 'cursor-default text-zinc-700'
                : 'text-zinc-500 hover:bg-zinc-800 hover:text-zinc-100'
            ]"
            role="button"
            tabindex="0"
            :title="openTabItems.length <= 1 ? 'Keep one tab open' : 'Close tab'"
            @click.stop="closeWorkspaceTab(tab.id)"
            @keydown.enter.stop.prevent="closeWorkspaceTab(tab.id)"
            @keydown.space.stop.prevent="closeWorkspaceTab(tab.id)"
          >
            <XIcon class="h-4 w-4" />
          </span>
        </button>
      </div>

      <div class="min-h-0 flex-1 overflow-auto">
        <component
          v-for="tab in openTabItems"
          :key="tab.id"
          :is="tab.component"
          v-show="activeTab === tab.id"
        />
      </div>
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
