<script setup lang="ts">
import { computed } from 'vue'
import { XIcon } from 'lucide-vue-next'
import { RoutingLog } from '../../composables/useApi'
import MarkdownViewer from '../common/MarkdownViewer.vue'

const props = defineProps<{
  log: RoutingLog
}>()

const emit = defineEmits<{
  close: []
}>()

const createdAt = computed(() => new Date(props.log.created_at).toLocaleString())

function formatUsd(value: string | number) {
  return `$${Number(value || 0).toFixed(6)}`
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm" @click="emit('close')">
    <div class="max-h-[90vh] w-full max-w-5xl overflow-y-auto rounded-xl border border-zinc-800 bg-zinc-900 shadow-2xl animate-fade-in" @click.stop>
      <header class="flex items-center justify-between border-b border-zinc-800 px-6 py-5">
        <div>
          <p class="mb-1 text-xs font-semibold uppercase tracking-widest text-indigo-400">Routing Log</p>
          <h3 class="text-lg font-semibold text-zinc-100">Request Detail</h3>
        </div>
        <button
          class="rounded-lg p-1.5 text-zinc-500 transition-colors hover:bg-zinc-800 hover:text-zinc-200"
          title="Close"
          type="button"
          @click="emit('close')"
        >
          <XIcon class="h-5 w-5" />
        </button>
      </header>

      <div class="space-y-5 p-6">
        <section class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <div class="rounded-lg border border-zinc-800 bg-zinc-800/50 p-3">
            <p class="mb-1 text-xs font-medium text-zinc-500">Policy</p>
            <p class="text-sm font-semibold text-zinc-200">{{ log.policy }}</p>
          </div>
          <div class="rounded-lg border border-zinc-800 bg-zinc-800/50 p-3">
            <p class="mb-1 text-xs font-medium text-zinc-500">Model</p>
            <p class="break-all text-sm font-semibold text-zinc-200">{{ log.selected_provider }}/{{ log.selected_model }}</p>
          </div>
          <div class="rounded-lg border border-zinc-800 bg-zinc-800/50 p-3">
            <p class="mb-1 text-xs font-medium text-zinc-500">Latency</p>
            <p class="text-sm font-semibold text-zinc-200">{{ log.latency_ms }}ms</p>
          </div>
          <div class="rounded-lg border border-zinc-800 bg-zinc-800/50 p-3">
            <p class="mb-1 text-xs font-medium text-zinc-500">Cost</p>
            <p class="text-sm font-semibold text-zinc-200">{{ formatUsd(log.estimated_cost_usd) }}</p>
          </div>
          <div class="rounded-lg border border-zinc-800 bg-zinc-800/50 p-3">
            <p class="mb-1 text-xs font-medium text-zinc-500">User</p>
            <p class="text-sm font-semibold text-zinc-200">{{ log.username || '-' }}</p>
          </div>
          <div class="rounded-lg border border-zinc-800 bg-zinc-800/50 p-3">
            <p class="mb-1 text-xs font-medium text-zinc-500">Estimated tokens</p>
            <p class="text-sm font-semibold text-zinc-200">{{ log.estimated_tokens }}</p>
          </div>
          <div class="rounded-lg border border-zinc-800 bg-zinc-800/50 p-3 md:col-span-2">
            <p class="mb-1 text-xs font-medium text-zinc-500">Created at</p>
            <p class="text-sm font-semibold text-zinc-200">{{ createdAt }}</p>
          </div>
        </section>

        <section>
          <h4 class="mb-2 text-sm font-semibold text-zinc-200">Prompt</h4>
          <div class="max-h-40 overflow-y-auto whitespace-pre-wrap rounded-lg border border-zinc-800 bg-zinc-800/40 p-4 text-sm leading-6 text-zinc-300">
            {{ log.prompt_summary || '-' }}
          </div>
        </section>

        <section>
          <h4 class="mb-2 text-sm font-semibold text-zinc-200">Routing Reason</h4>
          <div class="max-h-48 overflow-y-auto whitespace-pre-wrap rounded-lg border border-zinc-800 bg-zinc-800/40 p-4 text-sm leading-6 text-zinc-400">
            {{ log.routing_reason || '-' }}
          </div>
        </section>

        <section v-if="log.error_message">
          <h4 class="mb-2 text-sm font-semibold text-red-300">Error</h4>
          <div class="max-h-48 overflow-y-auto whitespace-pre-wrap rounded-lg border border-red-500/20 bg-red-500/10 p-4 text-sm leading-6 text-red-300">
            {{ log.error_message }}
          </div>
        </section>

        <section>
          <h4 class="mb-2 text-sm font-semibold text-zinc-200">Response</h4>
          <div class="max-h-80 overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-800/40 p-4 text-sm">
            <MarkdownViewer :content="log.response_text" empty-text="-" />
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
