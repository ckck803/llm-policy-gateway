<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ActivityIcon, AlertTriangleIcon, ClockIcon, CpuIcon, DollarSignIcon, RotateCcwIcon } from 'lucide-vue-next'
import PaginationControls from '../components/common/PaginationControls.vue'
import { DashboardMetrics, useApi } from '../composables/useApi'
import { usePagination } from '../composables/usePagination'

const api = useApi()
const metrics = ref<DashboardMetrics | null>(null)
const loading = ref(true)
const period = ref('7d')
const customStartDate = ref('')
const customEndDate = ref('')
const recentLogs = computed(() => metrics.value?.recent_logs ?? [])
const {
  page,
  pageSize,
  pageSizeOptions,
  totalItems,
  totalPages,
  startItem,
  endItem,
  paginatedItems: paginatedRecentLogs
} = usePagination(recentLogs)

function formatUsd(value: string | number) {
  return `$${Number(value || 0).toFixed(6)}`
}

function formatPercent(value: number) {
  return `${Math.round((value || 0) * 100)}%`
}

function dateToInputValue(date: Date) {
  return date.toISOString().slice(0, 10)
}

function setDefaultCustomDates() {
  if (customStartDate.value && customEndDate.value) {
    return
  }
  const end = new Date()
  const start = new Date()
  start.setDate(end.getDate() - 6)
  customStartDate.value = dateToInputValue(start)
  customEndDate.value = dateToInputValue(end)
}

async function loadMetrics() {
  loading.value = true
  try {
    metrics.value = await api.getMetrics({
      period: period.value,
      startDate: period.value === 'custom' ? customStartDate.value : undefined,
      endDate: period.value === 'custom' ? customEndDate.value : undefined
    })
  } finally {
    loading.value = false
  }
}

watch(period, () => {
  if (period.value === 'custom') {
    setDefaultCustomDates()
    return
  }
  void loadMetrics()
})

onMounted(async () => {
  await loadMetrics()
})
</script>

<template>
  <div class="p-6 lg:p-8">
    <!-- Page header -->
    <div class="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-indigo-400">Operations</p>
        <h2 class="text-2xl font-bold text-zinc-100">Dashboard</h2>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <label class="flex items-center gap-2 text-sm text-zinc-500">
          Period
          <select
            v-model="period"
            class="rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"
          >
            <option value="today">Today</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="all">All time</option>
            <option value="custom">Custom</option>
          </select>
        </label>

        <template v-if="period === 'custom'">
          <input
            v-model="customStartDate"
            class="rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"
            type="date"
          />
          <input
            v-model="customEndDate"
            class="rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"
            type="date"
          />
          <button
            class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="!customStartDate || !customEndDate || loading"
            type="button"
            @click="loadMetrics"
          >
            Apply
          </button>
        </template>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center gap-3 text-zinc-500">
      <div class="h-4 w-4 animate-spin rounded-full border-2 border-zinc-700 border-t-indigo-500"></div>
      <span class="text-sm">Loading metrics...</span>
    </div>

    <div v-else-if="metrics" class="space-y-6">
      <!-- Metric cards -->
      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <div class="mb-3 flex items-center justify-between">
            <span class="text-xs font-medium text-zinc-500">Total requests</span>
            <div class="rounded-md bg-indigo-600/10 p-1.5">
              <ActivityIcon class="h-3.5 w-3.5 text-indigo-400" />
            </div>
          </div>
          <p class="text-2xl font-bold text-zinc-100">{{ metrics.total_requests }}</p>
        </div>

        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <div class="mb-3 flex items-center justify-between">
            <span class="text-xs font-medium text-zinc-500">Avg latency</span>
            <div class="rounded-md bg-emerald-500/10 p-1.5">
              <ClockIcon class="h-3.5 w-3.5 text-emerald-400" />
            </div>
          </div>
          <p class="text-2xl font-bold text-zinc-100">{{ metrics.average_latency_ms }}<span class="ml-1 text-sm font-normal text-zinc-500">ms</span></p>
        </div>

        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <div class="mb-3 flex items-center justify-between">
            <span class="text-xs font-medium text-zinc-500">Local routing</span>
            <div class="rounded-md bg-amber-500/10 p-1.5">
              <CpuIcon class="h-3.5 w-3.5 text-amber-400" />
            </div>
          </div>
          <p class="text-2xl font-bold text-zinc-100">{{ Math.round(metrics.local_routing_ratio * 100) }}<span class="ml-0.5 text-sm font-normal text-zinc-500">%</span></p>
        </div>

        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <div class="mb-3 flex items-center justify-between">
            <span class="text-xs font-medium text-zinc-500">Est. cost</span>
            <div class="rounded-md bg-violet-500/10 p-1.5">
              <DollarSignIcon class="h-3.5 w-3.5 text-violet-400" />
            </div>
          </div>
          <p class="text-2xl font-bold text-zinc-100">{{ formatUsd(metrics.total_estimated_cost_usd) }}</p>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <div class="mb-3 flex items-center justify-between">
            <span class="text-xs font-medium text-zinc-500">Failed requests</span>
            <div class="rounded-md bg-red-500/10 p-1.5">
              <AlertTriangleIcon class="h-3.5 w-3.5 text-red-400" />
            </div>
          </div>
          <p class="text-2xl font-bold text-zinc-100">{{ metrics.failed_requests }}</p>
          <p class="mt-1 text-xs text-zinc-500">{{ formatPercent(metrics.failure_rate) }} failure rate</p>
        </div>

        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <div class="mb-3 flex items-center justify-between">
            <span class="text-xs font-medium text-zinc-500">Fallback events</span>
            <div class="rounded-md bg-sky-500/10 p-1.5">
              <RotateCcwIcon class="h-3.5 w-3.5 text-sky-400" />
            </div>
          </div>
          <p class="text-2xl font-bold text-zinc-100">{{ metrics.fallback_attempts }}</p>
          <p class="mt-1 text-xs text-zinc-500">requests with fallback attempts</p>
        </div>

        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <div class="mb-3 flex items-center justify-between">
            <span class="text-xs font-medium text-zinc-500">Quota blocks</span>
            <div class="rounded-md bg-amber-500/10 p-1.5">
              <AlertTriangleIcon class="h-3.5 w-3.5 text-amber-400" />
            </div>
          </div>
          <p class="text-2xl font-bold text-zinc-100">{{ metrics.quota_blocks }}</p>
          <p class="mt-1 text-xs text-zinc-500">blocked by monthly limits</p>
        </div>

        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <div class="mb-3 flex items-center justify-between">
            <span class="text-xs font-medium text-zinc-500">Healthy providers</span>
            <div class="rounded-md bg-emerald-500/10 p-1.5">
              <CpuIcon class="h-3.5 w-3.5 text-emerald-400" />
            </div>
          </div>
          <p class="text-2xl font-bold text-zinc-100">
            {{ metrics.provider_health.filter((provider) => provider.failures === 0).length }}
          </p>
          <p class="mt-1 text-xs text-zinc-500">of {{ metrics.provider_health.length }} active in period</p>
        </div>
      </div>

      <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
        <div class="mb-4 flex items-center justify-between gap-3">
          <h3 class="text-sm font-semibold text-zinc-200">Currently Unhealthy Models</h3>
          <span
            :class="[
              'rounded-md border px-2 py-0.5 text-xs font-medium',
              metrics.unhealthy_models.length
                ? 'border-red-500/20 bg-red-500/10 text-red-300'
                : 'border-emerald-500/20 bg-emerald-500/10 text-emerald-300'
            ]"
          >
            {{ metrics.unhealthy_models.length }} blocked
          </span>
        </div>
        <div class="space-y-2">
          <div
            v-for="model in metrics.unhealthy_models"
            :key="`${model.provider}-${model.model_name}`"
            class="rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2.5"
          >
            <div class="mb-1 flex items-center justify-between gap-3">
              <p class="truncate text-sm font-semibold text-red-300">{{ model.provider }}/{{ model.model_name }}</p>
              <span class="shrink-0 text-xs text-red-300/80">{{ formatPercent(model.failure_rate) }} fail</span>
            </div>
            <p class="text-xs text-red-200/80">{{ model.reason }}</p>
            <p class="mt-1 text-xs text-zinc-500">
              {{ model.request_count }} req · {{ model.failures }} failures · avg {{ model.average_latency_ms }}ms · {{ model.rule_name || 'no rule' }}
            </p>
          </div>
          <p v-if="!metrics.unhealthy_models.length" class="text-sm text-zinc-600">No model is currently blocked by health rules</p>
        </div>
      </div>

      <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
        <h3 class="mb-4 text-sm font-semibold text-zinc-200">Recent Health Events</h3>
        <div class="space-y-2">
          <div
            v-for="event in metrics.recent_health_events"
            :key="event.id"
            :class="[
              'rounded-lg border px-3 py-2.5',
              event.event_type === 'triggered'
                ? 'border-red-500/20 bg-red-500/10'
                : 'border-emerald-500/20 bg-emerald-500/10'
            ]"
          >
            <div class="mb-1 flex items-center justify-between gap-3">
              <p
                :class="[
                  'truncate text-sm font-semibold',
                  event.event_type === 'triggered' ? 'text-red-300' : 'text-emerald-300'
                ]"
              >
                {{ event.provider }}/{{ event.model_name }}
              </p>
              <span class="shrink-0 text-xs text-zinc-500">{{ new Date(event.created_at).toLocaleString() }}</span>
            </div>
            <p class="text-xs text-zinc-400">{{ event.event_type }} · {{ event.rule_name || 'no rule' }}</p>
            <p class="mt-1 truncate text-xs text-zinc-500">
              {{ formatPercent(Number(event.failure_rate)) }} fail · avg {{ event.average_latency_ms }}ms · {{ event.reason }}
            </p>
          </div>
          <p v-if="!metrics.recent_health_events?.length" class="text-sm text-zinc-600">No health transitions yet</p>
        </div>
      </div>

      <div class="grid gap-4 lg:grid-cols-2">
        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <h3 class="mb-4 text-sm font-semibold text-zinc-200">Provider Health</h3>
          <div class="space-y-2">
            <div
              v-for="provider in metrics.provider_health"
              :key="provider.selected_provider"
              class="grid grid-cols-[minmax(0,1fr)_auto] gap-3 rounded-lg bg-zinc-800/50 px-3 py-2.5"
            >
              <div class="min-w-0">
                <p class="truncate text-sm font-medium text-zinc-300">{{ provider.selected_provider }}</p>
                <p class="text-xs text-zinc-500">{{ provider.count }} req · avg {{ provider.average_latency_ms }}ms</p>
              </div>
              <div class="text-right">
                <p :class="['text-sm font-semibold', provider.failures ? 'text-red-400' : 'text-emerald-400']">
                  {{ formatPercent(provider.failure_rate) }}
                </p>
                <p class="text-xs text-zinc-500">{{ provider.failures }} failures</p>
              </div>
            </div>
            <p v-if="!metrics.provider_health?.length" class="text-sm text-zinc-600">No data yet</p>
          </div>
        </div>

        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <h3 class="mb-4 text-sm font-semibold text-zinc-200">Recent Errors</h3>
          <div class="space-y-2">
            <div
              v-for="error in metrics.recent_errors"
              :key="error.id"
              class="rounded-lg bg-red-500/10 px-3 py-2.5"
            >
              <div class="mb-1 flex items-center justify-between gap-3">
                <p class="truncate text-sm font-medium text-red-300">{{ error.selected_provider }}/{{ error.selected_model }}</p>
                <span class="shrink-0 text-xs text-red-400/70">{{ new Date(error.created_at).toLocaleString() }}</span>
              </div>
              <p class="truncate text-xs text-red-300/80">{{ error.error_message }}</p>
              <p class="mt-1 truncate text-xs text-zinc-500">{{ error.prompt_summary }}</p>
            </div>
            <p v-if="!metrics.recent_errors?.length" class="text-sm text-zinc-600">No recent errors</p>
          </div>
        </div>
      </div>

      <!-- Usage panels -->
      <div class="grid gap-4 lg:grid-cols-2">
        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <h3 class="mb-4 text-sm font-semibold text-zinc-200">Provider Usage</h3>
          <div class="space-y-2">
            <div
              v-for="provider in metrics.provider_usage"
              :key="provider.selected_provider"
              class="flex items-center justify-between rounded-lg bg-zinc-800/50 px-3 py-2.5"
            >
              <span class="text-sm text-zinc-300">{{ provider.selected_provider }}</span>
              <span class="text-xs text-zinc-400">{{ provider.count }} req / {{ formatUsd(provider.estimated_cost_usd) }}</span>
            </div>
            <p v-if="!metrics.provider_usage?.length" class="text-sm text-zinc-600">No data yet</p>
          </div>
        </div>

        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <h3 class="mb-4 text-sm font-semibold text-zinc-200">User Usage</h3>
          <div class="space-y-2">
            <div
              v-for="user in metrics.user_usage"
              :key="user.user__username || 'anonymous'"
              class="flex items-center justify-between rounded-lg bg-zinc-800/50 px-3 py-2.5"
            >
              <span class="text-sm text-zinc-300">{{ user.user__username || 'unknown' }}</span>
              <span class="text-xs text-zinc-400">{{ user.count }} req / {{ formatUsd(user.estimated_cost_usd) }}</span>
            </div>
            <p v-if="!metrics.user_usage?.length" class="text-sm text-zinc-600">No data yet</p>
          </div>
        </div>
      </div>

      <div class="grid gap-4 lg:grid-cols-2">
        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <h3 class="mb-4 text-sm font-semibold text-zinc-200">Model Usage</h3>
          <div class="space-y-2">
            <div
              v-for="model in metrics.model_usage"
              :key="`${model.selected_provider}-${model.selected_model}`"
              class="flex items-center justify-between rounded-lg bg-zinc-800/50 px-3 py-2.5"
            >
              <span class="text-sm text-zinc-300">{{ model.selected_provider }}/{{ model.selected_model }}</span>
              <span class="text-xs text-zinc-400">{{ model.count }} req / {{ formatUsd(model.estimated_cost_usd) }}</span>
            </div>
            <p v-if="!metrics.model_usage?.length" class="text-sm text-zinc-600">No data yet</p>
          </div>
        </div>

        <div class="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <h3 class="mb-4 text-sm font-semibold text-zinc-200">Policy Usage</h3>
          <div class="space-y-2">
            <div
              v-for="policy in metrics.policy_usage"
              :key="policy.policy"
              class="flex items-center justify-between rounded-lg bg-zinc-800/50 px-3 py-2.5"
            >
              <span class="text-sm text-zinc-300">{{ policy.policy }}</span>
              <span class="text-xs text-zinc-400">{{ policy.count }} req / {{ formatUsd(policy.estimated_cost_usd) }}</span>
            </div>
            <p v-if="!metrics.policy_usage?.length" class="text-sm text-zinc-600">No data yet</p>
          </div>
        </div>
      </div>

      <!-- Recent requests table -->
      <div class="rounded-xl border border-zinc-800 bg-zinc-900">
        <div class="border-b border-zinc-800 px-5 py-4">
          <h3 class="text-sm font-semibold text-zinc-200">Recent Requests</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full">
            <thead>
              <tr class="border-b border-zinc-800">
                <th class="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Prompt</th>
                <th class="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Policy</th>
                <th class="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Model</th>
                <th class="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">User</th>
                <th class="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Cost</th>
                <th class="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Latency</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-zinc-800/60">
              <tr v-for="log in paginatedRecentLogs" :key="log.id" class="hover:bg-zinc-800/30 transition-colors">
                <td class="max-w-xs truncate px-5 py-3.5 text-sm text-zinc-300">{{ log.prompt_summary }}</td>
                <td class="whitespace-nowrap px-5 py-3.5">
                  <span class="rounded-md bg-zinc-800 px-2 py-0.5 text-xs font-medium text-zinc-300">{{ log.policy }}</span>
                </td>
                <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">{{ log.selected_model }}</td>
                <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">{{ log.username || '-' }}</td>
                <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">{{ formatUsd(log.estimated_cost_usd) }}</td>
                <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">{{ log.latency_ms }}ms</td>
              </tr>
              <tr v-if="!metrics.recent_logs?.length">
                <td colspan="6" class="px-5 py-8 text-center text-sm text-zinc-600">No recent requests</td>
              </tr>
            </tbody>
          </table>
        </div>
        <PaginationControls
          v-if="metrics.recent_logs?.length"
          v-model:page="page"
          v-model:page-size="pageSize"
          :page-size-options="pageSizeOptions"
          :total-items="totalItems"
          :total-pages="totalPages"
          :start-item="startItem"
          :end-item="endItem"
        />
      </div>
    </div>
  </div>
</template>
