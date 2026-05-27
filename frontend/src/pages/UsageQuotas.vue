<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { EditIcon, GaugeIcon, PlusIcon, SearchIcon } from 'lucide-vue-next'
import AdminDataTable from '../components/common/AdminDataTable.vue'
import PaginationControls from '../components/common/PaginationControls.vue'
import UsageQuotaModal from '../components/modals/UsageQuotaModal.vue'
import { AppUser, UsageQuota, UsageQuotaPayload, useApi } from '../composables/useApi'
import { usePagination } from '../composables/usePagination'

const api = useApi()
const quotas = ref<UsageQuota[]>([])
const users = ref<AppUser[]>([])
const selectedQuota = ref<UsageQuota | null>(null)
const showModal = ref(false)
const loading = ref(false)
const searchQuery = ref('')
const error = ref('')

const filteredQuotas = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return quotas.value.filter((quota) => {
    return (
      !query ||
      quota.name.toLowerCase().includes(query) ||
      quota.provider.toLowerCase().includes(query) ||
      (quota.username ?? 'all users').toLowerCase().includes(query)
    )
  })
})

const {
  page,
  pageSize,
  pageSizeOptions,
  totalItems,
  totalPages,
  startItem,
  endItem,
  paginatedItems: paginatedQuotas
} = usePagination(filteredQuotas)

async function loadPageData() {
  loading.value = true
  try {
    const [loadedQuotas, loadedUsers] = await Promise.all([api.getUsageQuotas(), api.getUsers()])
    quotas.value = loadedQuotas
    users.value = loadedUsers
  } finally {
    loading.value = false
  }
}

function providerLabel(provider: string) {
  return provider || 'all providers'
}

function formatUsd(value: string | number | null) {
  return `$${Number(value || 0).toFixed(6)}`
}

function formatPercent(value: number | null) {
  return value === null ? '-' : `${Math.round(value * 100)}%`
}

function openCreateModal() {
  selectedQuota.value = null
  showModal.value = true
}

function openEditModal(quota: UsageQuota) {
  selectedQuota.value = quota
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedQuota.value = null
}

async function saveQuota(payload: UsageQuotaPayload) {
  error.value = ''
  try {
    if (selectedQuota.value) {
      await api.updateUsageQuota(selectedQuota.value.id, payload)
    } else {
      await api.createUsageQuota(payload)
    }
    closeModal()
    await loadPageData()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to save quota'
  }
}

async function deleteQuota(quota: UsageQuota) {
  await api.deleteUsageQuota(quota.id)
  closeModal()
  await loadPageData()
}

onMounted(loadPageData)
</script>

<template>
  <div class="p-6 lg:p-8">
    <div class="mb-6 flex items-center justify-between gap-4">
      <div>
        <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-indigo-400">Cost Control</p>
        <h2 class="text-2xl font-bold text-zinc-100">Usage Quotas</h2>
      </div>
      <button
        class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 transition hover:bg-indigo-500"
        type="button"
        @click="openCreateModal"
      >
        <PlusIcon class="h-4 w-4" />
        Add Quota
      </button>
    </div>

    <div class="mb-5 flex flex-wrap items-center gap-3">
      <div class="relative min-w-72 flex-1">
        <SearchIcon class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
        <input
          v-model="searchQuery"
          class="w-full rounded-lg border border-zinc-700 bg-zinc-800 py-2.5 pl-9 pr-4 text-sm text-zinc-200 placeholder-zinc-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"
          placeholder="Search quota, user, or provider..."
          type="text"
        />
      </div>
    </div>

    <div v-if="error" class="mb-4 rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2.5 text-sm text-red-400">
      {{ error }}
    </div>

    <AdminDataTable :loading="loading" :is-empty="filteredQuotas.length === 0">
      <template #head>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Quota</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Scope</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Limits</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">This Month</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Action</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Status</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Edit</th>
      </template>

      <template #empty>
        <GaugeIcon class="mx-auto mb-4 h-12 w-12 text-zinc-700" />
        <h3 class="mb-1 text-sm font-semibold text-zinc-300">No usage quotas found</h3>
        <p class="mb-4 text-sm text-zinc-600">Create request or cost limits for users and providers.</p>
        <button class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500" @click="openCreateModal">
          Add Quota
        </button>
      </template>

      <tr
        v-for="quota in paginatedQuotas"
        :key="quota.id"
        class="cursor-pointer transition-colors hover:bg-zinc-800/30"
        @click="openEditModal(quota)"
      >
        <td class="whitespace-nowrap px-5 py-3.5">
          <div class="font-medium text-zinc-200">{{ quota.name }}</div>
          <div class="text-xs text-zinc-500">{{ quota.action_on_exceed === 'block' ? 'blocks on exceed' : 'tries local fallback' }}</div>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">
          {{ quota.username || 'all users' }} · {{ providerLabel(quota.provider) }}
        </td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-300">
          <div>{{ quota.monthly_request_limit ?? '-' }} req / month</div>
          <div class="text-xs text-zinc-500">${{ quota.monthly_cost_limit_usd ?? '-' }} / month</div>
        </td>
        <td class="min-w-56 px-5 py-3.5 text-sm text-zinc-300">
          <div class="mb-2">
            <div class="mb-1 flex items-center justify-between gap-3 text-xs">
              <span class="text-zinc-400">{{ quota.current_month_requests }} req</span>
              <span class="text-zinc-500">{{ formatPercent(quota.request_usage_ratio) }}</span>
            </div>
            <div class="h-1.5 overflow-hidden rounded-full bg-zinc-800">
              <div
                class="h-full rounded-full bg-indigo-500"
                :style="{ width: `${Math.round((quota.request_usage_ratio ?? 0) * 100)}%` }"
              ></div>
            </div>
          </div>
          <div>
            <div class="mb-1 flex items-center justify-between gap-3 text-xs">
              <span class="text-zinc-400">{{ formatUsd(quota.current_month_cost_usd) }}</span>
              <span class="text-zinc-500">{{ formatPercent(quota.cost_usage_ratio) }}</span>
            </div>
            <div class="h-1.5 overflow-hidden rounded-full bg-zinc-800">
              <div
                class="h-full rounded-full bg-emerald-500"
                :style="{ width: `${Math.round((quota.cost_usage_ratio ?? 0) * 100)}%` }"
              ></div>
            </div>
          </div>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">{{ quota.action_on_exceed }}</td>
        <td class="whitespace-nowrap px-5 py-3.5">
          <span
            :class="[
              'rounded-md px-2 py-0.5 text-xs font-medium border',
              quota.is_exceeded
                ? 'bg-red-500/10 text-red-400 border-red-500/20'
                : quota.is_active
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-zinc-800 text-zinc-500 border-zinc-700'
            ]"
          >
            {{ quota.is_exceeded ? 'exceeded' : quota.is_active ? 'active' : 'inactive' }}
          </span>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5">
          <button class="rounded-md p-1.5 text-zinc-500 transition-colors hover:bg-zinc-700 hover:text-zinc-200" title="Edit" type="button" @click.stop="openEditModal(quota)">
            <EditIcon class="h-4 w-4" />
          </button>
        </td>
      </tr>

      <template #footer>
        <PaginationControls
          v-model:page="page"
          v-model:page-size="pageSize"
          :page-size-options="pageSizeOptions"
          :total-items="totalItems"
          :total-pages="totalPages"
          :start-item="startItem"
          :end-item="endItem"
        />
      </template>
    </AdminDataTable>

    <UsageQuotaModal
      v-if="showModal"
      :quota="selectedQuota"
      :users="users"
      @close="closeModal"
      @delete="deleteQuota"
      @save="saveQuota"
    />
  </div>
</template>
