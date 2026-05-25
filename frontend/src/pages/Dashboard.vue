<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ActivityIcon, ClockIcon, CpuIcon, TrendingUpIcon } from 'lucide-vue-next'
import { DashboardMetrics, useApi } from '../composables/useApi'

const api = useApi()
const metrics = ref<DashboardMetrics | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    metrics.value = await api.getMetrics()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="p-6 lg:p-8">
    <!-- Page header -->
    <div class="mb-8">
      <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-indigo-400">Operations</p>
      <h2 class="text-2xl font-bold text-zinc-100">Dashboard</h2>
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
            <span class="text-xs font-medium text-zinc-500">Est. savings</span>
            <div class="rounded-md bg-violet-500/10 p-1.5">
              <TrendingUpIcon class="h-3.5 w-3.5 text-violet-400" />
            </div>
          </div>
          <p class="text-2xl font-bold text-zinc-100">{{ metrics.estimated_cost_savings_percent }}<span class="ml-0.5 text-sm font-normal text-zinc-500">%</span></p>
        </div>
      </div>

      <!-- Usage panels -->
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
              <span class="rounded-md bg-zinc-700 px-2 py-0.5 text-xs font-semibold text-zinc-200">{{ model.count }}</span>
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
              <span class="rounded-md bg-zinc-700 px-2 py-0.5 text-xs font-semibold text-zinc-200">{{ policy.count }}</span>
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
                <th class="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Latency</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-zinc-800/60">
              <tr v-for="log in metrics.recent_logs" :key="log.id" class="hover:bg-zinc-800/30 transition-colors">
                <td class="max-w-xs truncate px-5 py-3.5 text-sm text-zinc-300">{{ log.prompt_summary }}</td>
                <td class="whitespace-nowrap px-5 py-3.5">
                  <span class="rounded-md bg-zinc-800 px-2 py-0.5 text-xs font-medium text-zinc-300">{{ log.policy }}</span>
                </td>
                <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">{{ log.selected_model }}</td>
                <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">{{ log.latency_ms }}ms</td>
              </tr>
              <tr v-if="!metrics.recent_logs?.length">
                <td colspan="4" class="px-5 py-8 text-center text-sm text-zinc-600">No recent requests</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
