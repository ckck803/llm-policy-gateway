<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { XIcon } from 'lucide-vue-next'
import { RecoveryStrategy, RecoveryStrategyPayload } from '../../composables/useApi'
import AppSelect from '../common/AppSelect.vue'

const props = defineProps<{ strategy: RecoveryStrategy | null }>()

const emit = defineEmits<{
  close: []
  save: [payload: RecoveryStrategyPayload]
  delete: [strategy: RecoveryStrategy]
}>()

const isEdit = computed(() => Boolean(props.strategy))

const form = reactive<RecoveryStrategyPayload>({
  strategy_id: '',
  name: '',
  description: '',
  trigger_event: 'validation_fail',
  action: 'strict_retry',
  retry_prompt: 'Return only valid JSON. Do not include markdown fences, prose, or comments.',
  max_retries: 1,
  target_tier: '',
  priority: 100,
  is_active: true
})

watch(
  () => props.strategy,
  (strategy) => {
    Object.assign(form, {
      strategy_id: strategy?.strategy_id ?? '',
      name: strategy?.name ?? '',
      description: strategy?.description ?? '',
      trigger_event: strategy?.trigger_event ?? 'validation_fail',
      action: strategy?.action ?? 'strict_retry',
      retry_prompt: strategy?.retry_prompt ?? 'Return only valid JSON. Do not include markdown fences, prose, or comments.',
      max_retries: strategy?.max_retries ?? 1,
      target_tier: strategy?.target_tier ?? '',
      priority: strategy?.priority ?? 100,
      is_active: strategy?.is_active ?? true
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
          <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-indigo-400">Recovery Strategy</p>
          <h3 class="text-lg font-semibold text-zinc-100">{{ isEdit ? 'Strategy Detail' : 'New Strategy' }}</h3>
        </div>
        <button class="rounded-lg p-1.5 text-zinc-500 transition-colors hover:bg-zinc-800 hover:text-zinc-200" type="button" @click="emit('close')">
          <XIcon class="h-5 w-5" />
        </button>
      </header>

      <form class="p-6" @submit.prevent="emit('save', form)">
        <div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2">
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Strategy ID</span>
            <input v-model.trim="form.strategy_id" required placeholder="S-01" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Priority</span>
            <input v-model.number="form.priority" min="1" required type="number" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block md:col-span-2">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Name</span>
            <input v-model.trim="form.name" required placeholder="Strict retry then fallback" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Trigger</span>
            <AppSelect v-model="form.trigger_event" :options="[
              { value: 'validation_fail', label: 'Validation failure' },
              { value: 'timeout', label: 'Timeout' },
              { value: 'api_fail', label: 'API failure' },
              { value: 'parse_fail', label: 'Parse failure' },
              { value: 'low_confidence', label: 'Low confidence' }
            ]" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Action</span>
            <AppSelect v-model="form.action" :options="[
              { value: 'strict_retry', label: 'Strict retry' },
              { value: 'fallback', label: 'Fallback' },
              { value: 'escalate', label: 'Escalate to tier' },
              { value: 'block', label: 'Block response' }
            ]" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Max retries</span>
            <input v-model.number="form.max_retries" min="0" required type="number" class="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50" />
          </label>
          <label class="block">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Escalation Tier</span>
            <AppSelect v-model="form.target_tier" :options="[
              { value: '', label: 'No tier target' },
              { value: 'advanced', label: 'Advanced' },
              { value: 'structured', label: 'Structured' },
              { value: 'long_context', label: 'Long Context' },
              { value: 'standard', label: 'Standard' },
              { value: 'lightweight', label: 'Lightweight' }
            ]" />
          </label>
          <label class="block md:col-span-2">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Retry prompt</span>
            <textarea v-model="form.retry_prompt" rows="3" class="w-full resize-none rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"></textarea>
          </label>
          <label class="block md:col-span-2">
            <span class="mb-1.5 block text-xs font-medium text-zinc-400">Description</span>
            <textarea v-model="form.description" rows="3" class="w-full resize-none rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-200 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/50"></textarea>
          </label>
          <label class="flex items-center gap-3 text-sm font-medium text-zinc-400">
            <input v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded border-zinc-600 bg-zinc-800 accent-indigo-500" />
            Active
          </label>
        </div>

        <footer class="flex items-center gap-3 border-t border-zinc-800 pt-4">
          <button v-if="strategy" class="rounded-lg border border-red-500/30 px-4 py-2 text-sm font-medium text-red-400 transition-colors hover:bg-red-500/10" type="button" @click="emit('delete', strategy)">
            Delete
          </button>
          <span class="flex-1"></span>
          <button class="rounded-lg border border-zinc-700 px-4 py-2 text-sm font-medium text-zinc-400 transition-colors hover:bg-zinc-800 hover:text-zinc-200" type="button" @click="emit('close')">
            Cancel
          </button>
          <button class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-500" type="submit">
            {{ isEdit ? 'Save Changes' : 'Create Strategy' }}
          </button>
        </footer>
      </form>
    </div>
  </div>
</template>
