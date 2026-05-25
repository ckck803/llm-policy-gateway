<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { EditIcon, PlusIcon, SearchIcon, ShieldCheckIcon } from 'lucide-vue-next'
import AdminDataTable from '../components/common/AdminDataTable.vue'
import ScreenModal from '../components/modals/ScreenModal.vue'
import { ScreenDefinition, ScreenDefinitionPayload, useApi } from '../composables/useApi'

const api = useApi()
const screens = ref<ScreenDefinition[]>([])
const selectedScreen = ref<ScreenDefinition | null>(null)
const showModal = ref(false)
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref<'all' | 'active' | 'inactive'>('all')
const error = ref('')

const filteredScreens = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return screens.value.filter((screen) => {
    const matchesQuery =
      !query ||
      screen.id.toLowerCase().includes(query) ||
      screen.label.toLowerCase().includes(query) ||
      screen.description.toLowerCase().includes(query)
    const matchesStatus =
      statusFilter.value === 'all' ||
      (statusFilter.value === 'active' && screen.is_active) ||
      (statusFilter.value === 'inactive' && !screen.is_active)
    return matchesQuery && matchesStatus
  })
})

async function loadScreens() {
  loading.value = true
  try {
    screens.value = await api.getScreens()
  } finally {
    loading.value = false
  }
}

function openCreateModal() {
  selectedScreen.value = null
  showModal.value = true
}

function openEditModal(screen: ScreenDefinition) {
  selectedScreen.value = screen
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedScreen.value = null
}

async function saveScreen(payload: ScreenDefinitionPayload) {
  error.value = ''
  try {
    if (selectedScreen.value) {
      await api.updateScreen(selectedScreen.value.pk, payload)
    } else {
      await api.createScreen(payload)
    }
    closeModal()
    await loadScreens()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to save screen'
  }
}

async function deleteScreen(screen: ScreenDefinition) {
  await api.deleteScreen(screen.pk)
  closeModal()
  await loadScreens()
}

onMounted(loadScreens)
</script>

<template>
  <div class="p-6 lg:p-8">
    <div class="mb-6 flex items-center justify-between gap-4">
      <div>
        <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-indigo-400">Permission</p>
        <h2 class="text-2xl font-bold text-zinc-100">Screens</h2>
      </div>
      <button
        class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 transition hover:bg-indigo-500"
        type="button"
        @click="openCreateModal"
      >
        <PlusIcon class="h-4 w-4" />
        Add Screen
      </button>
    </div>

    <div class="mb-5 flex flex-wrap items-center gap-3">
      <div class="relative min-w-72 flex-1">
        <SearchIcon class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
        <input
          v-model="searchQuery"
          class="w-full rounded-lg border border-zinc-700 bg-zinc-800 py-2.5 pl-9 pr-4 text-sm text-zinc-200 placeholder-zinc-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"
          placeholder="Search screen id, label, or description..."
          type="text"
        />
      </div>
      <select
        v-model="statusFilter"
        class="rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"
      >
        <option value="all">All status</option>
        <option value="active">Active</option>
        <option value="inactive">Inactive</option>
      </select>
    </div>

    <div v-if="error" class="mb-4 rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2.5 text-sm text-red-400">
      {{ error }}
    </div>

    <AdminDataTable :loading="loading" :is-empty="filteredScreens.length === 0">
      <template #head>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Screen</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Description</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Sort</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Status</th>
        <th class="px-5 py-3.5 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Action</th>
      </template>

      <template #empty>
        <ShieldCheckIcon class="mx-auto mb-4 h-12 w-12 text-zinc-700" />
        <h3 class="mb-1 text-sm font-semibold text-zinc-300">No screens found</h3>
        <button
          class="mt-3 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500"
          @click="openCreateModal"
        >
          Add Screen
        </button>
      </template>

      <tr
        v-for="screen in filteredScreens"
        :key="screen.pk"
        class="cursor-pointer transition-colors hover:bg-zinc-800/30"
        @click="openEditModal(screen)"
      >
        <td class="whitespace-nowrap px-5 py-3.5">
          <div class="font-medium text-zinc-200">{{ screen.label }}</div>
          <div class="text-xs text-zinc-500">{{ screen.id }}</div>
        </td>
        <td class="px-5 py-3.5 text-sm text-zinc-500">{{ screen.description || '-' }}</td>
        <td class="whitespace-nowrap px-5 py-3.5 text-sm text-zinc-300">{{ screen.sort_order }}</td>
        <td class="whitespace-nowrap px-5 py-3.5">
          <span
            :class="[
              'rounded-md px-2 py-0.5 text-xs font-medium border',
              screen.is_active
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                : 'bg-zinc-800 text-zinc-500 border-zinc-700'
            ]"
          >
            {{ screen.is_active ? 'active' : 'inactive' }}
          </span>
        </td>
        <td class="whitespace-nowrap px-5 py-3.5">
          <button
            class="rounded-md p-1.5 text-zinc-500 transition-colors hover:bg-zinc-700 hover:text-zinc-200"
            title="Edit"
            type="button"
            @click.stop="openEditModal(screen)"
          >
            <EditIcon class="h-4 w-4" />
          </button>
        </td>
      </tr>
    </AdminDataTable>

    <ScreenModal v-if="showModal" :screen="selectedScreen" @close="closeModal" @delete="deleteScreen" @save="saveScreen" />
  </div>
</template>
