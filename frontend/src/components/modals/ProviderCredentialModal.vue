<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { XIcon } from 'lucide-vue-next'
import { ProviderCredential, ProviderCredentialPayload } from '../../composables/useApi'

const props = defineProps<{
  credential: ProviderCredential | null
}>()

const emit = defineEmits<{
  close: []
  save: [payload: ProviderCredentialPayload]
  delete: [credential: ProviderCredential]
}>()

const isEdit = computed(() => Boolean(props.credential))

const form = reactive<ProviderCredentialPayload>({
  provider: 'openai',
  display_name: '',
  base_url: '',
  access_token: '',
  is_active: true
})

watch(
  () => props.credential,
  (credential) => {
    Object.assign(form, {
      provider: credential?.provider ?? 'openai',
      display_name: credential?.display_name ?? '',
      base_url: credential?.base_url ?? '',
      access_token: credential?.access_token ?? '',
      is_active: credential?.is_active ?? true
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
          <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-indigo-400">Provider Credential</p>
          <h3 class="text-lg font-semibold text-zinc-100">{{ isEdit ? 'Credential Detail' : 'New Credential' }}</h3>
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
              <option value="openai">openai</option>
              <option value="gemini">gemini</option>
              <option value="openrouter">openrouter</option>
            </select>
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Display name</span>
            <input v-model="form.display_name" required placeholder="OpenAI Production" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 placeholder-zinc-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block md:col-span-2">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Base URL</span>
            <input v-model="form.base_url" required placeholder="https://openrouter.ai/api/v1" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 placeholder-zinc-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block md:col-span-2">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Access Token</span>
            <input v-model="form.access_token" required type="password" placeholder="API key or access token" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 placeholder-zinc-600 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="flex items-center gap-3 text-sm font-medium text-zinc-400">
            <input v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded border-zinc-600 bg-zinc-800 accent-indigo-500" />
            Active
          </label>
        </div>

        <footer class="flex items-center gap-3 border-t border-zinc-800 pt-4">
          <button
            v-if="credential"
            class="rounded-lg border border-red-500/30 px-4 py-2 text-sm font-medium text-red-400 transition-colors hover:bg-red-500/10"
            type="button"
            @click="emit('delete', credential)"
          >
            Delete
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
            {{ isEdit ? 'Save Changes' : 'Create Credential' }}
          </button>
        </footer>
      </form>
    </div>
  </div>
</template>
