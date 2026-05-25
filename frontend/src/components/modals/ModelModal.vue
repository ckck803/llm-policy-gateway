<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { XIcon } from 'lucide-vue-next'
import { LLMModel, LLMModelPayload } from '../../composables/useApi'

const props = defineProps<{
  model: LLMModel | null
}>()

const emit = defineEmits<{
  close: []
  save: [payload: LLMModelPayload]
  disable: [model: LLMModel]
}>()

const isEdit = computed(() => Boolean(props.model))

const form = reactive<LLMModelPayload>({
  provider: 'ollama',
  name: '',
  display_name: '',
  role: 'general',
  quality_level: 3,
  speed_level: 3,
  cost_level: 1,
  privacy_level: 'local',
  context_window: 8192,
  is_active: true
})

watch(
  () => props.model,
  (model) => {
    Object.assign(form, {
      provider: model?.provider ?? 'ollama',
      name: model?.name ?? '',
      display_name: model?.display_name ?? '',
      role: model?.role ?? 'general',
      quality_level: model?.quality_level ?? 3,
      speed_level: model?.speed_level ?? 3,
      cost_level: model?.cost_level ?? 1,
      privacy_level: model?.privacy_level ?? 'local',
      context_window: model?.context_window ?? 8192,
      is_active: model?.is_active ?? true
    })
  },
  { immediate: true }
)
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm" @click="emit('close')">
    <div class="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl border border-zinc-800 bg-zinc-900 shadow-2xl animate-fade-in" @click.stop>
      <header class="flex items-center justify-between border-b border-zinc-800 px-6 py-5">
        <div>
          <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-indigo-400">Model Catalog</p>
          <h3 class="text-lg font-semibold text-zinc-100">{{ isEdit ? 'Model Detail' : 'New Model' }}</h3>
        </div>
        <button
          class="rounded-lg p-1.5 text-zinc-500 transition-colors hover:bg-zinc-800 hover:text-zinc-200"
          type="button"
          @click="emit('close')"
        >
          <XIcon class="h-5 w-5" />
        </button>
      </header>

      <form class="p-6" @submit.prevent="emit('save', form)">
        <div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2">
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Provider</span>
            <select v-model="form.provider" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50">
              <option value="ollama">ollama</option>
              <option value="openai">openai</option>
              <option value="gemini">gemini</option>
              <option value="openrouter">openrouter</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Role</span>
            <select v-model="form.role" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50">
              <option value="general">general</option>
              <option value="coding">coding</option>
              <option value="reasoning">reasoning</option>
              <option value="summary">summary</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Model name</span>
            <input v-model="form.name" required placeholder="openai/gpt-4.1-mini" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 placeholder-zinc-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Display name</span>
            <input v-model="form.display_name" required placeholder="Llama 3.1 8B" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 placeholder-zinc-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Quality level</span>
            <input v-model.number="form.quality_level" min="1" max="5" type="number" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Speed level</span>
            <input v-model.number="form.speed_level" min="1" max="5" type="number" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Cost level</span>
            <input v-model.number="form.cost_level" min="1" max="5" type="number" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Context window</span>
            <input v-model.number="form.context_window" min="1" type="number" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Privacy</span>
            <select v-model="form.privacy_level" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50">
              <option value="local">local</option>
              <option value="external">external</option>
            </select>
          </label>
          <label class="flex items-center gap-3 pt-6 text-sm font-medium text-zinc-400">
            <input v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded border-zinc-600 bg-zinc-800 accent-indigo-500" />
            Active
          </label>
        </div>

        <footer class="flex items-center gap-3 border-t border-zinc-800 pt-4">
          <button
            v-if="model && model.is_active"
            class="rounded-lg border border-red-500/30 px-4 py-2 text-sm font-medium text-red-400 transition-colors hover:bg-red-500/10"
            type="button"
            @click="emit('disable', model)"
          >
            Disable
          </button>
          <span class="flex-1"></span>
          <button
            class="rounded-lg border border-zinc-700 px-4 py-2 text-sm font-medium text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-zinc-200"
            type="button"
            @click="emit('close')"
          >
            Cancel
          </button>
          <button class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-500" type="submit">
            {{ isEdit ? 'Save Changes' : 'Create Model' }}
          </button>
        </footer>
      </form>
    </div>
  </div>
</template>
