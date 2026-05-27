<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { EditIcon, PlusIcon, SearchIcon, ServerIcon } from 'lucide-vue-next'
import AdminDataTable from '../components/common/AdminDataTable.vue'
import PaginationControls from '../components/common/PaginationControls.vue'
import ModelModal from '../components/modals/ModelModal.vue'
import AppSelect from '../components/common/AppSelect.vue'
import { LLMModel, LLMModelPayload, ProviderCredential, useApi } from '../composables/useApi'
import { usePagination } from '../composables/usePagination'

const api = useApi()
const models = ref<LLMModel[]>([])
const credentials = ref<ProviderCredential[]>([])
const selectedModel = ref<LLMModel | null>(null)
const showModal = ref(false)
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref<'all' | 'active' | 'inactive'>('all')
const error = ref('')

const filteredModels = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return models.value.filter((model) => {
    const matchesQuery =
      !query ||
      model.name.toLowerCase().includes(query) ||
      model.display_name.toLowerCase().includes(query) ||
      model.provider.toLowerCase().includes(query) ||
      model.model_tier.toLowerCase().includes(query) ||
      model.health_status.toLowerCase().includes(query) ||
      model.health_reason.toLowerCase().includes(query) ||
      model.role.toLowerCase().includes(query)
    const matchesStatus =
      statusFilter.value === 'all' ||
      (statusFilter.value === 'active' && model.is_active) ||
      (statusFilter.value === 'inactive' && !model.is_active)
    return matchesQuery && matchesStatus
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
  paginatedItems: paginatedModels
} = usePagination(filteredModels)

async function loadModels() {
  loading.value = true
  try {
    const [loadedModels, loadedCredentials] = await Promise.all([
      api.getModels(),
      api.getProviderCredentials()
    ])
    models.value = loadedModels
    credentials.value = loadedCredentials
  } finally {
    loading.value = false
  }
}

async function refreshCredentials() {
  credentials.value = await api.getProviderCredentials()
}

async function openCreateModal() {
  await refreshCredentials()
  selectedModel.value = null
  showModal.value = true
}

async function openEditModal(model: LLMModel) {
  await refreshCredentials()
  selectedModel.value = model
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedModel.value = null
}

async function saveModel(payload: LLMModelPayload) {
  error.value = ''
  try {
    if (selectedModel.value) {
      await api.updateModel(selectedModel.value.id, payload)
    } else {
      await api.createModel(payload)
    }
    closeModal()
    await loadModels()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to save model'
  }
}

async function disableModel(model: LLMModel) {
  await api.updateModel(model.id, { is_active: false })
  closeModal()
  await loadModels()
}

onMounted(loadModels)
</script>

<template>
  <div class="p-6 lg:p-8">
    <!-- Page header -->
    <div class="mb-6 flex items-center justify-between gap-4">
      <div>
        <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-indigo-400">Catalog</p>
        <h2 class="text-2xl font-bold text-zinc-100">Models</h2>
      </div>
      <button
        class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 transition hover:bg-indigo-500"
        type="button"
        @click="openCreateModal"
      >
        <PlusIcon class="h-4 w-4" />
        Add Model
      </button>
    </div>

    <!-- Filters -->
    <div class="mb-5 flex flex-wrap items-center gap-3">
      <div class="relative min-w-72 flex-1">
        <SearchIcon class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
        <input
          v-model="searchQuery"
          class="w-full rounded-lg border border-zinc-700 bg-zinc-800 py-2.5 pl-9 pr-4 text-sm text-zinc-200 placeholder-zinc-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"
          placeholder="Search model, provider, or role..."
          type="text"
        />
      </div>
      <AppSelect
        v-model="statusFilter"
        :options="[{ value: 'all', label: 'All status' }, { value: 'active', label: 'Active' }, { value: 'inactive', label: 'Inactive' }]"
      />
    </div>

    <!-- Error -->
    <div v-if="error" class="mb-4 rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2.5 text-sm text-red-400">
      {{ error }}
    </div>

    <AdminDataTable :loading="loading" :is-empty="filteredModels.length === 0">
      <template #head>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Model</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Tier</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Role</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Quality</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Speed</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Cost</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Token $/1M</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Latency</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Health</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Privacy</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Credential</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Status</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Action</th>
      </template>

      <template #empty>
        <ServerIcon class="mx-auto mb-4 h-12 w-12 text-zinc-700" />
        <h3 class="mb-1 text-sm font-semibold text-zinc-300">No models found</h3>
        <p class="mb-4 text-sm text-zinc-600">Add an Ollama, OpenAI, or Gemini model to start routing.</p>
        <button
          class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500"
          @click="openCreateModal"
        >
          Add Model
        </button>
      </template>

      <tr
        v-for="model in paginatedModels"
        :key="model.id"
        class="cursor-pointer transition-colors hover:bg-zinc-800/30"
        @click="openEditModal(model)"
      >
        <td class="whitespace-nowrap px-5 py-3.5">
          <div class="font-medium text-zinc-200">{{ model.display_name }}</div>
          <div class="text-xs text-zinc-500">{{ model.provider }}/{{ model.name }}</div>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5">
          <span class="rounded-md border border-sky-500/20 bg-sky-500/10 px-2 py-0.5 text-xs font-medium text-sky-300">
            {{ model.model_tier }}
          </span>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-300">{{ model.role }}</td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-300">{{ model.quality_level }}</td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-300">{{ model.speed_level }}</td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-300">{{ model.cost_level }}</td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-300">
          {{ model.input_token_price_per_1m }} / {{ model.output_token_price_per_1m }}
        </td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-300">
          {{ model.average_latency_ms || '-' }}ms
        </td>
        <td class="whitespace-nowrap px-5 py-3.5">
          <span
            :class="[
              'rounded-md border px-2 py-0.5 text-xs font-medium',
              model.health_status === 'unhealthy'
                ? 'border-red-500/20 bg-red-500/10 text-red-300'
                : 'border-emerald-500/20 bg-emerald-500/10 text-emerald-300'
            ]"
            :title="model.health_reason"
          >
            {{ model.health_status }}
          </span>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5">
          <span class="rounded-md bg-indigo-500/10 px-2 py-0.5 text-xs font-medium text-indigo-400 border border-indigo-500/20">
            {{ model.privacy_level }}
          </span>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-400">
          {{ model.provider_credential_display_name || '-' }}
        </td>
        <td class="whitespace-nowrap px-5 py-3.5">
          <span
            :class="[
              'rounded-md px-2 py-0.5 text-xs font-medium border',
              model.is_active
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-zinc-800 text-zinc-500 border-zinc-700'
            ]"
          >
            {{ model.is_active ? 'active' : 'inactive' }}
          </span>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5">
          <button
            class="rounded-md p-1.5 text-zinc-500 transition-colors hover:bg-zinc-700 hover:text-zinc-200"
            title="Edit"
            type="button"
            @click.stop="openEditModal(model)"
          >
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

    <ModelModal
      v-if="showModal"
      :model="selectedModel"
      :credentials="credentials"
      @close="closeModal"
      @disable="disableModel"
      @save="saveModel"
    />
  </div>
</template>
