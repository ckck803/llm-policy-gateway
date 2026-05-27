<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { XIcon } from 'lucide-vue-next'
import { ModelHealthOverride, ModelHealthOverridePayload } from '../../composables/useApi'
import AppSelect from '../common/AppSelect.vue'

const props = defineProps<{
  override: ModelHealthOverride | null
}>()

const emit = defineEmits<{
  close: []
  save: [payload: ModelHealthOverridePayload]
  delete: [override: ModelHealthOverride]
}>()

const isEdit = computed(() => Boolean(props.override))

const form = reactive<ModelHealthOverridePayload>({
  name: '',
  provider: '',
  model_name: '',
  override_type: 'force_healthy',
  reason: '',
  expires_at: null,
  is_active: true
})

function toInputDateTime(value: string | null) {
  if (!value) {
    return ''
  }
  const date = new Date(value)
  const offsetDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
  return offsetDate.toISOString().slice(0, 16)
}

function toApiDateTime(value: string | null) {
  if (!value) {
    return null
  }
  return new Date(value).toISOString()
}

watch(
  () => props.override,
  (override) => {
    Object.assign(form, {
      name: override?.name ?? '',
      provider: override?.provider ?? '',
      model_name: override?.model_name ?? '',
      override_type: override?.override_type ?? 'force_healthy',
      reason: override?.reason ?? '',
      expires_at: toInputDateTime(override?.expires_at ?? null),
      is_active: override?.is_active ?? true
    })
  },
  { immediate: true }
)

function submit() {
  emit('save', {
    ...form,
    expires_at: toApiDateTime(form.expires_at)
  })
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm" @click="emit('close')">
    <div class="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl border border-zinc-800 bg-zinc-900 shadow-2xl animate-fade-in" @click.stop>
      <header class="flex items-center justify-between border-b border-zinc-800 px-6 py-5">
        <div>
          <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-indigo-400">Health Override</p>
          <h3 class="text-lg font-semibold text-zinc-100">{{ isEdit ? 'Override Detail' : 'New Override' }}</h3>
        </div>
        <button class="rounded-lg p-1.5 text-zinc-500 transition-colors hover:bg-zinc-800 hover:text-zinc-200" type="button" @click="emit('close')">
          <XIcon class="h-5 w-5" />
        </button>
      </header>

      <form class="p-6" @submit.prevent="submit">
        <div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2">
          <label class="block md:col-span-2">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Name</span>
            <input v-model.trim="form.name" required placeholder="Temporary OpenRouter recovery" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 placeholder-zinc-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Provider</span>
            <AppSelect v-model="form.provider" :options="[{ value: '', label: 'All providers' }, 'ollama', 'openai', 'gemini', 'openrouter']" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Model name</span>
            <input v-model.trim="form.model_name" placeholder="blank means all models" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 placeholder-zinc-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Override type</span>
            <AppSelect
              v-model="form.override_type"
              :options="[
                { value: 'force_healthy', label: 'Force healthy' },
                { value: 'force_unhealthy', label: 'Force unhealthy' }
              ]"
            />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Expires at</span>
            <input v-model="form.expires_at" type="datetime-local" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block md:col-span-2">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Reason</span>
            <textarea v-model.trim="form.reason" rows="3" placeholder="Why this override is needed" class="w-full resize-none rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 placeholder-zinc-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"></textarea>
          </label>
          <label class="flex items-center gap-3 text-sm font-medium text-zinc-400">
            <input v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded border-zinc-600 bg-zinc-800 accent-indigo-500" />
            Active
          </label>
        </div>

        <footer class="flex items-center gap-3 border-t border-zinc-800 pt-4">
          <button v-if="override" class="rounded-lg border border-red-500/30 px-4 py-2 text-sm font-medium text-red-400 transition-colors hover:bg-red-500/10" type="button" @click="emit('delete', override)">
            Delete
          </button>
          <span class="flex-1"></span>
          <button class="rounded-lg border border-zinc-700 px-4 py-2 text-sm font-medium text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-zinc-200" type="button" @click="emit('close')">
            Cancel
          </button>
          <button class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-500" type="submit">
            {{ isEdit ? 'Save Changes' : 'Create Override' }}
          </button>
        </footer>
      </form>
    </div>
  </div>
</template>
