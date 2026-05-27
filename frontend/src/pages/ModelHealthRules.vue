<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { EditIcon, HeartPulseIcon, PlusIcon, SearchIcon } from 'lucide-vue-next'
import AdminDataTable from '../components/common/AdminDataTable.vue'
import PaginationControls from '../components/common/PaginationControls.vue'
import ModelHealthRuleModal from '../components/modals/ModelHealthRuleModal.vue'
import { ModelHealthRule, ModelHealthRulePayload, useApi } from '../composables/useApi'
import { usePagination } from '../composables/usePagination'

const api = useApi()
const rules = ref<ModelHealthRule[]>([])
const selectedRule = ref<ModelHealthRule | null>(null)
const showModal = ref(false)
const loading = ref(false)
const searchQuery = ref('')
const error = ref('')

const filteredRules = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return rules.value.filter((rule) => {
    return (
      !query ||
      rule.name.toLowerCase().includes(query) ||
      rule.provider.toLowerCase().includes(query) ||
      rule.model_name.toLowerCase().includes(query)
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
  paginatedItems: paginatedRules
} = usePagination(filteredRules)

async function loadRules() {
  loading.value = true
  try {
    rules.value = await api.getModelHealthRules()
  } finally {
    loading.value = false
  }
}

function providerLabel(provider: string) {
  return provider || 'all providers'
}

function modelLabel(modelName: string) {
  return modelName || 'all models'
}

function openCreateModal() {
  selectedRule.value = null
  showModal.value = true
}

function openEditModal(rule: ModelHealthRule) {
  selectedRule.value = rule
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedRule.value = null
}

async function saveRule(payload: ModelHealthRulePayload) {
  error.value = ''
  try {
    if (selectedRule.value) {
      await api.updateModelHealthRule(selectedRule.value.id, payload)
    } else {
      await api.createModelHealthRule(payload)
    }
    closeModal()
    await loadRules()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to save health rule'
  }
}

async function deleteRule(rule: ModelHealthRule) {
  await api.deleteModelHealthRule(rule.id)
  closeModal()
  await loadRules()
}

onMounted(loadRules)
</script>

<template>
  <div class="p-6 lg:p-8">
    <div class="mb-6 flex items-center justify-between gap-4">
      <div>
        <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-indigo-400">Routing Guard</p>
        <h2 class="text-2xl font-bold text-zinc-100">Health Rules</h2>
      </div>
      <button
        class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 transition hover:bg-indigo-500"
        type="button"
        @click="openCreateModal"
      >
        <PlusIcon class="h-4 w-4" />
        Add Rule
      </button>
    </div>

    <div class="mb-5 flex flex-wrap items-center gap-3">
      <div class="relative min-w-72 flex-1">
        <SearchIcon class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
        <input
          v-model="searchQuery"
          class="w-full rounded-lg border border-zinc-700 bg-zinc-800 py-2.5 pl-9 pr-4 text-sm text-zinc-200 placeholder-zinc-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"
          placeholder="Search rule, provider, or model..."
          type="text"
        />
      </div>
    </div>

    <div v-if="error" class="mb-4 rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2.5 text-sm text-red-400">
      {{ error }}
    </div>

    <AdminDataTable :loading="loading" :is-empty="filteredRules.length === 0">
      <template #head>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Rule</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Scope</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Window</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Thresholds</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Status</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Edit</th>
      </template>

      <template #empty>
        <HeartPulseIcon class="mx-auto mb-4 h-12 w-12 text-zinc-700" />
        <h3 class="mb-1 text-sm font-semibold text-zinc-300">No health rules found</h3>
        <p class="mb-4 text-sm text-zinc-600">Create failure or latency guards for routing candidates.</p>
        <button class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500" @click="openCreateModal">
          Add Rule
        </button>
      </template>

      <tr
        v-for="rule in paginatedRules"
        :key="rule.id"
        class="cursor-pointer transition-colors hover:bg-zinc-800/30"
        @click="openEditModal(rule)"
      >
        <td class="whitespace-nowrap px-5 py-3.5">
          <div class="font-medium text-zinc-200">{{ rule.name }}</div>
          <div class="text-xs text-zinc-500">{{ rule.action_on_trigger === 'exclude' ? 'excludes unhealthy candidates' : rule.action_on_trigger }}</div>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">
          {{ providerLabel(rule.provider) }} · {{ modelLabel(rule.model_name) }}
        </td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-300">
          <div>{{ rule.window_minutes }} min</div>
          <div class="text-xs text-zinc-500">min {{ rule.min_requests }} requests</div>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-300">
          <div>fail {{ rule.max_failure_rate_percent ?? '-' }}%</div>
          <div class="text-xs text-zinc-500">latency {{ rule.max_average_latency_ms ?? '-' }}ms</div>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5">
          <span
            :class="[
              'rounded-md px-2 py-0.5 text-xs font-medium border',
              rule.is_active
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-zinc-800 text-zinc-500 border-zinc-700'
            ]"
          >
            {{ rule.is_active ? 'active' : 'inactive' }}
          </span>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5">
          <button class="rounded-md p-1.5 text-zinc-500 transition-colors hover:bg-zinc-700 hover:text-zinc-200" title="Edit" type="button" @click.stop="openEditModal(rule)">
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

    <ModelHealthRuleModal
      v-if="showModal"
      :rule="selectedRule"
      @close="closeModal"
      @delete="deleteRule"
      @save="saveRule"
    />
  </div>
</template>
