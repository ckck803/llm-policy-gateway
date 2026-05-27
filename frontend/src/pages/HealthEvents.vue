<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { AlertTriangleIcon, HeartPulseIcon, SearchIcon } from 'lucide-vue-next'
import AdminDataTable from '../components/common/AdminDataTable.vue'
import PaginationControls from '../components/common/PaginationControls.vue'
import { ModelHealthEvent, useApi } from '../composables/useApi'
import { usePagination } from '../composables/usePagination'

const api = useApi()
const events = ref<ModelHealthEvent[]>([])
const loading = ref(false)
const searchQuery = ref('')

const filteredEvents = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return events.value.filter((event) => {
    return (
      !query ||
      event.provider.toLowerCase().includes(query) ||
      event.model_name.toLowerCase().includes(query) ||
      event.rule_name.toLowerCase().includes(query) ||
      event.reason.toLowerCase().includes(query)
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
  paginatedItems: paginatedEvents
} = usePagination(filteredEvents)

async function loadEvents() {
  loading.value = true
  try {
    events.value = await api.getModelHealthEvents()
  } finally {
    loading.value = false
  }
}

function formatPercent(value: string | number) {
  const numericValue = Number(value || 0)
  const ratio = numericValue > 1 ? numericValue / 100 : numericValue
  return `${Math.round(ratio * 100)}%`
}

function formatDate(value: string) {
  return new Date(value).toLocaleString()
}

onMounted(loadEvents)
</script>

<template>
  <div class="p-6 lg:p-8">
    <div class="mb-6 flex items-center justify-between gap-4">
      <div>
        <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-indigo-400">Routing Guard</p>
        <h2 class="text-2xl font-bold text-zinc-100">Health Events</h2>
      </div>
    </div>

    <div class="mb-5 flex flex-wrap items-center gap-3">
      <div class="relative min-w-72 flex-1">
        <SearchIcon class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
        <input
          v-model="searchQuery"
          class="w-full rounded-lg border border-zinc-700 bg-zinc-800 py-2.5 pl-9 pr-4 text-sm text-zinc-200 placeholder-zinc-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"
          placeholder="Search model, rule, or reason..."
          type="text"
        />
      </div>
    </div>

    <AdminDataTable :loading="loading" :is-empty="filteredEvents.length === 0">
      <template #head>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Event</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Model</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Rule / Reason</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Metrics</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Created</th>
      </template>

      <template #empty>
        <HeartPulseIcon class="mx-auto mb-4 h-12 w-12 text-zinc-700" />
        <h3 class="mb-1 text-sm font-semibold text-zinc-300">No health events found</h3>
        <p class="text-sm text-zinc-600">Health transitions will appear here after a model is blocked or recovered.</p>
      </template>

      <tr v-for="event in paginatedEvents" :key="event.id" class="transition-colors hover:bg-zinc-800/30">
        <td class="whitespace-nowrap px-5 py-3.5">
          <span
            :class="[
              'inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-xs font-medium',
              event.event_type === 'triggered'
                ? 'border-red-500/20 bg-red-500/10 text-red-300'
                : 'border-emerald-500/20 bg-emerald-500/10 text-emerald-300'
            ]"
          >
            <AlertTriangleIcon v-if="event.event_type === 'triggered'" class="h-3 w-3" />
            <HeartPulseIcon v-else class="h-3 w-3" />
            {{ event.event_type }}
          </span>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5">
          <div class="font-medium text-zinc-200">{{ event.provider }}/{{ event.model_name }}</div>
          <div class="text-xs text-zinc-500">{{ event.status }}</div>
        </td>
        <td class="max-w-xl px-5 py-3.5">
          <div class="text-sm font-medium text-zinc-300">{{ event.rule_name || 'no rule' }}</div>
          <div class="truncate text-xs text-zinc-500">{{ event.reason }}</div>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">
          <div>{{ event.request_count }} req · {{ event.failures }} failures</div>
          <div class="text-xs text-zinc-500">{{ formatPercent(event.failure_rate) }} fail · avg {{ event.average_latency_ms }}ms</div>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">
          {{ formatDate(event.created_at) }}
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
  </div>
</template>
