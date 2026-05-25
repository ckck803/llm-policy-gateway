<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RoutingLog, useApi } from '../composables/useApi'

const api = useApi()
const logs = ref<RoutingLog[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    logs.value = await api.getLogs()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="p-6 lg:p-8">
    <!-- Page header -->
    <div class="mb-8">
      <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-indigo-400">Audit Trail</p>
      <h2 class="text-2xl font-bold text-zinc-100">Routing Logs</h2>
    </div>

    <div class="rounded-xl border border-zinc-800 bg-zinc-900">
      <div v-if="loading" class="flex items-center justify-center py-16 gap-3 text-zinc-500">
        <div class="h-4 w-4 animate-spin rounded-full border-2 border-zinc-700 border-t-indigo-500"></div>
        <span class="text-sm">Loading logs...</span>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full">
          <thead>
            <tr class="border-b border-zinc-800">
              <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Prompt</th>
              <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Policy</th>
              <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Model</th>
              <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Latency</th>
              <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Reason</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-zinc-800/60">
            <tr v-for="log in logs" :key="log.id" class="hover:bg-zinc-800/30 transition-colors">
              <td class="max-w-xs truncate px-5 py-3.5 text-sm text-zinc-300">{{ log.prompt_summary }}</td>
              <td class="whitespace-nowrap px-5 py-3.5">
                <span class="rounded-md bg-zinc-800 px-2 py-0.5 text-xs font-medium text-zinc-300">{{ log.policy }}</span>
              </td>
              <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">{{ log.selected_provider }}/{{ log.selected_model }}</td>
              <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">{{ log.latency_ms }}ms</td>
              <td class="px-5 py-3.5 text-sm text-zinc-500 max-w-xs truncate">{{ log.routing_reason }}</td>
            </tr>
            <tr v-if="!logs.length">
              <td colspan="5" class="px-5 py-16 text-center text-sm text-zinc-600">No routing logs yet</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
