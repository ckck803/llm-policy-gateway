import { appEnv } from '../config/env'

const API_BASE = appEnv.apiBaseUrl
const TOKEN_KEY = 'llm-policy-gateway-token'

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setAuthToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearAuthToken() {
  localStorage.removeItem(TOKEN_KEY)
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken()
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Token ${token}` } : {}),
      ...(options.headers ?? {})
    },
    ...options
  })

  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = payload.error_message || payload.detail || 'Request failed'
    throw new Error(message)
  }
  return payload as T
}

export type LLMModel = {
  id: number
  provider: string
  name: string
  display_name: string
  model_tier: string
  provider_credential: number | null
  provider_credential_display_name: string | null
  health_status: string
  health_reason: string
  health_metrics: {
    provider: string
    model_name: string
    status: string
    reason: string
    rule_id: number | null
    rule_name: string
    request_count: number
    failures: number
    failure_rate: number
    average_latency_ms: number
    window_minutes: number | null
  }
  role: string
  quality_level: number
  speed_level: number
  cost_level: number
  privacy_level: string
  context_window: number
  input_token_price_per_1m: string
  output_token_price_per_1m: string
  average_latency_ms: number
  timeout_seconds: number
  is_active: boolean
}

export type LLMModelPayload = Omit<LLMModel, 'id' | 'provider_credential_display_name' | 'health_status' | 'health_reason' | 'health_metrics'>

export type RoutingPolicy = {
  id: number
  name: string
  display_name: string
  description: string
  priority_config: {
    quality_weight?: number
    speed_weight?: number
    cost_weight?: number
    context_weight?: number
    local_only?: boolean
    prefer_coding_models?: boolean
    prefer_reasoning_models?: boolean
    min_context_window?: number
    max_estimated_cost_usd?: string
    fallback_to_local_on_budget?: boolean
  }
  is_active: boolean
}

export type RoutingPolicyPayload = Omit<RoutingPolicy, 'id'>

export type RoutingRule = {
  id: number
  rule_id: string
  name: string
  description: string
  condition_key: string
  target_tier: string
  priority: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export type RoutingRulePayload = Omit<RoutingRule, 'id' | 'created_at' | 'updated_at'>

export type ThresholdRule = {
  id: number
  rule_id: string
  name: string
  description: string
  metric_key: string
  operator: string
  threshold_value: string
  action_on_trigger: string
  target_tier: string
  max_tokens: number | null
  priority: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export type ThresholdRulePayload = Omit<ThresholdRule, 'id' | 'created_at' | 'updated_at'>

export type ResponseValidationRule = {
  id: number
  rule_id: string
  name: string
  description: string
  recovery_strategy: number | null
  recovery_strategy_display_name: string | null
  condition_key: string
  validation_type: string
  action_on_fail: string
  retry_prompt: string
  max_retries: number
  target_tier: string
  priority: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export type ResponseValidationRulePayload = Omit<ResponseValidationRule, 'id' | 'recovery_strategy_display_name' | 'created_at' | 'updated_at'>

export type RecoveryStrategy = {
  id: number
  strategy_id: string
  name: string
  description: string
  trigger_event: string
  action: string
  retry_prompt: string
  max_retries: number
  target_tier: string
  priority: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export type RecoveryStrategyPayload = Omit<RecoveryStrategy, 'id' | 'created_at' | 'updated_at'>

export type ProviderCredential = {
  id: number
  provider: string
  display_name: string
  base_url: string
  access_token_masked: string
  last_used_at: string | null
  token_rotated_at: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export type ProviderCredentialPayload = Omit<ProviderCredential, 'id' | 'access_token_masked' | 'last_used_at' | 'token_rotated_at' | 'created_at' | 'updated_at'> & {
  access_token?: string
}

export type ProviderCredentialTestResult = {
  ok: boolean
  status_code: number | null
  message: string
}

export type ProviderModelCandidate = {
  name: string
  display_name: string
  context_window: number
  exists: boolean
}

export type ProviderModelPreview = {
  models: ProviderModelCandidate[]
}

export type ProviderModelImportResult = {
  imported: LLMModel[]
  skipped: string[]
}

export type UsageQuota = {
  id: number
  name: string
  user: number | null
  username: string | null
  provider: string
  monthly_request_limit: number | null
  monthly_cost_limit_usd: string | null
  period_start: string
  current_month_requests: number
  current_month_cost_usd: string
  request_usage_ratio: number | null
  cost_usage_ratio: number | null
  is_exceeded: boolean
  action_on_exceed: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export type UsageQuotaPayload = Omit<UsageQuota, 'id' | 'username' | 'period_start' | 'current_month_requests' | 'current_month_cost_usd' | 'request_usage_ratio' | 'cost_usage_ratio' | 'is_exceeded' | 'created_at' | 'updated_at'>

export type ModelHealthRule = {
  id: number
  name: string
  provider: string
  model_name: string
  window_minutes: number
  min_requests: number
  max_failure_rate_percent: string | null
  max_average_latency_ms: number | null
  action_on_trigger: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export type ModelHealthRulePayload = Omit<ModelHealthRule, 'id' | 'created_at' | 'updated_at'>

export type ModelHealthEvent = {
  id: number
  event_type: string
  provider: string
  model_name: string
  status: string
  rule: number | null
  rule_name: string
  reason: string
  request_count: number
  failures: number
  failure_rate: string | number
  average_latency_ms: number
  created_at: string
}

export type ModelHealthOverride = {
  id: number
  name: string
  provider: string
  model_name: string
  override_type: string
  reason: string
  expires_at: string | null
  is_active: boolean
  created_by: number | null
  created_by_username: string | null
  created_at: string
  updated_at: string
}

export type ModelHealthOverridePayload = Omit<ModelHealthOverride, 'id' | 'created_by' | 'created_by_username' | 'created_at' | 'updated_at'>

export type RoutingLog = {
  id: number
  username: string | null
  prompt_summary: string
  policy: string
  selected_provider: string
  selected_model: string
  routing_reason: string
  latency_ms: number
  estimated_tokens: number
  estimated_cost_usd: string
  response_text: string
  error_message: string
  validation_status: string
  validation_errors: string
  created_at: string
}

export type PaginatedResponse<T> = {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export type RoutingLogQuery = {
  page?: number
  pageSize?: number
  search?: string
  ordering?: string
}

export type DashboardMetrics = {
  total_requests: number
  average_latency_ms: number
  total_estimated_cost_usd: string
  local_routing_ratio: number
  estimated_cost_savings_percent: number
  failed_requests: number
  failure_rate: number
  fallback_attempts: number
  quota_blocks: number
  filter: {
    period: string
    start_date: string | null
    end_date: string | null
  }
  model_usage: Array<{ selected_provider: string; selected_model: string; count: number; estimated_cost_usd: string }>
  provider_usage: Array<{ selected_provider: string; count: number; estimated_cost_usd: string }>
  user_usage: Array<{ user__username: string | null; count: number; estimated_cost_usd: string }>
  policy_usage: Array<{ policy: string; count: number; estimated_cost_usd: string }>
  provider_health: Array<{ selected_provider: string; count: number; failures: number; failure_rate: number; average_latency_ms: number }>
  model_health: Array<{ selected_provider: string; selected_model: string; count: number; failures: number; failure_rate: number; average_latency_ms: number }>
  unhealthy_models: Array<{ provider: string; model_name: string; status: string; reason: string; rule_id: number | null; rule_name: string; request_count: number; failures: number; failure_rate: number; average_latency_ms: number; window_minutes: number | null }>
  recent_health_events: ModelHealthEvent[]
  recent_errors: Array<{
    id: number
    prompt_summary: string
    selected_provider: string
    selected_model: string
    error_message: string
    created_at: string
  }>
  recent_logs: RoutingLog[]
}

export type DashboardMetricsQuery = {
  period?: string
  startDate?: string
  endDate?: string
}

export type ChatResponse = RoutingLog & {
  analysis: {
    has_sensitive_data: boolean
    is_code: boolean
    is_structured_output: boolean
    is_long_context: boolean
    requires_reasoning: boolean
    estimated_tokens: number
  }
  matched_rules?: Array<{ rule_id: string; name: string; condition_key: string; target_tier: string; priority: number }>
  matched_threshold_rules?: Array<{ rule_id: string; name: string; metric_key: string; operator: string; threshold_value: string; action_on_trigger: string; target_tier: string; max_tokens: number | null; priority: number }>
  matched_validation_rules?: Array<{ rule_id: string; name: string; condition_key: string; validation_type: string; action_on_fail: string; recovery_strategy: number | null; recovery_strategy_display_name: string | null; max_retries: number; target_tier: string; priority: number }>
}

export type RoutingSimulationCandidate = {
  provider: string
  name: string
  model_tier: string
  display_name: string
  role: string
  privacy_level: string
  context_window: number
  input_token_price_per_1m: string
  output_token_price_per_1m: string
  average_latency_ms: number
  timeout_seconds: number
  estimated_input_cost_usd: string
  estimated_output_cost_usd: string
  estimated_total_cost_usd: string
  eligible: boolean
  rank: number | null
  score: number
  score_breakdown: {
    quality: number
    speed: number
    cost: number
    context: number
    privacy: number
    total: number
  }
  reasons: string[]
}

export type RoutingSimulationResponse = {
  policy: string
  selected_provider: string
  selected_model: string
  routing_reason: string
  analysis: ChatResponse['analysis']
  matched_rules: Array<{ rule_id: string; name: string; condition_key: string; target_tier: string; priority: number }>
  matched_threshold_rules: Array<{ rule_id: string; name: string; metric_key: string; operator: string; threshold_value: string; action_on_trigger: string; target_tier: string; max_tokens: number | null; priority: number }>
  matched_validation_rules: Array<{ rule_id: string; name: string; condition_key: string; validation_type: string; action_on_fail: string; recovery_strategy: number | null; recovery_strategy_display_name: string | null; max_retries: number; target_tier: string; priority: number }>
  candidates: RoutingSimulationCandidate[]
}

export type AppUser = {
  id: number
  username: string
  is_staff: boolean
  is_active: boolean
  allowed_screens: string[]
}

export type LoginResponse = {
  token: string
  user: AppUser
}

export type AppUserPayload = {
  username: string
  password?: string
  is_staff: boolean
  is_active: boolean
  allowed_screens: string[]
}

export type ScreenDefinition = {
  pk: number
  id: string
  label: string
  description: string
  sort_order: number
  is_active: boolean
}

export type ScreenDefinitionPayload = Omit<ScreenDefinition, 'pk'>

export type SecurityPolicy = {
  id: number
  max_sessions_user: number
  max_sessions_staff: number
  idle_timeout_minutes: number
  absolute_timeout_hours: number
  on_session_limit: string
  revoke_sessions_on_permission_change: boolean
  block_inactive_user_login: boolean
  updated_at: string
}

export type SecurityPolicyPayload = Omit<SecurityPolicy, 'id' | 'updated_at'>

export type UserSession = {
  id: number
  username: string
  ip_address: string | null
  user_agent: string
  login_at: string
  last_seen_at: string
  expires_at: string
  revoked_at: string | null
  logout_at: string | null
  status: string
  is_expired: boolean
}

export type AuditLog = {
  id: number
  actor: number | null
  actor_username: string | null
  action: string
  resource_type: string
  resource_id: string
  resource_name: string
  metadata: Record<string, unknown>
  ip_address: string | null
  user_agent: string
  created_at: string
}

export function useApi() {
  function buildQuery(params: Record<string, string | number | undefined>) {
    const query = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        query.set(key, String(value))
      }
    })
    const queryString = query.toString()
    return queryString ? `?${queryString}` : ''
  }

  return {
    login: (username: string, password: string) =>
      request<LoginResponse>('/api/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ username, password })
      }),
    getMe: () => request<AppUser>('/api/auth/me/'),
    logout: () =>
      request<Record<string, never>>('/api/auth/logout/', {
        method: 'POST'
      }),
    getUsers: () => request<AppUser[]>('/api/users/'),
    getScreens: () => request<ScreenDefinition[]>('/api/screens/'),
    createScreen: (payload: ScreenDefinitionPayload) =>
      request<ScreenDefinition>('/api/screens/', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    updateScreen: (pk: number, payload: Partial<ScreenDefinitionPayload>) =>
      request<ScreenDefinition>(`/api/screens/${pk}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      }),
    deleteScreen: (pk: number) =>
      request<Record<string, never>>(`/api/screens/${pk}/`, {
        method: 'DELETE'
      }),
    getSecurityPolicy: () => request<SecurityPolicy>('/api/security/policy/'),
    updateSecurityPolicy: (payload: Partial<SecurityPolicyPayload>) =>
      request<SecurityPolicy>('/api/security/policy/', {
        method: 'PATCH',
        body: JSON.stringify(payload)
      }),
    getUserSessions: () => request<UserSession[]>('/api/security/sessions/'),
    revokeUserSession: (id: number) =>
      request<UserSession>(`/api/security/sessions/${id}/revoke/`, {
        method: 'POST'
      }),
    getAuditLogs: () => request<AuditLog[]>('/api/security/audit-logs/'),
    createUser: (payload: AppUserPayload) =>
      request<AppUser>('/api/users/', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    updateUser: (id: number, payload: Partial<AppUserPayload>) =>
      request<AppUser>(`/api/users/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      }),
    deleteUser: (id: number) =>
      request<Record<string, never>>(`/api/users/${id}/`, {
        method: 'DELETE'
      }),
    getMetrics: (query: DashboardMetricsQuery = {}) =>
      request<DashboardMetrics>(
        `/api/dashboard/metrics/${buildQuery({
          period: query.period,
          start_date: query.startDate,
          end_date: query.endDate
        })}`
      ),
    getModels: () => request<LLMModel[]>('/api/models/'),
    createModel: (payload: LLMModelPayload) =>
      request<LLMModel>('/api/models/', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    updateModel: (id: number, payload: Partial<LLMModelPayload>) =>
      request<LLMModel>(`/api/models/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      }),
    deleteModel: (id: number) =>
      request<Record<string, never>>(`/api/models/${id}/`, {
        method: 'DELETE'
      }),
    getPolicies: () => request<RoutingPolicy[]>('/api/policies/'),
    createPolicy: (payload: RoutingPolicyPayload) =>
      request<RoutingPolicy>('/api/policies/', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    updatePolicy: (id: number, payload: Partial<RoutingPolicyPayload>) =>
      request<RoutingPolicy>(`/api/policies/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      }),
    deletePolicy: (id: number) =>
      request<Record<string, never>>(`/api/policies/${id}/`, {
        method: 'DELETE'
      }),
    getRoutingRules: () => request<RoutingRule[]>('/api/routing-rules/'),
    createRoutingRule: (payload: RoutingRulePayload) =>
      request<RoutingRule>('/api/routing-rules/', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    updateRoutingRule: (id: number, payload: Partial<RoutingRulePayload>) =>
      request<RoutingRule>(`/api/routing-rules/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      }),
    deleteRoutingRule: (id: number) =>
      request<Record<string, never>>(`/api/routing-rules/${id}/`, {
        method: 'DELETE'
      }),
    getThresholdRules: () => request<ThresholdRule[]>('/api/threshold-rules/'),
    createThresholdRule: (payload: ThresholdRulePayload) =>
      request<ThresholdRule>('/api/threshold-rules/', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    updateThresholdRule: (id: number, payload: Partial<ThresholdRulePayload>) =>
      request<ThresholdRule>(`/api/threshold-rules/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      }),
    deleteThresholdRule: (id: number) =>
      request<Record<string, never>>(`/api/threshold-rules/${id}/`, {
        method: 'DELETE'
      }),
    getValidationRules: () => request<ResponseValidationRule[]>('/api/validation-rules/'),
    createValidationRule: (payload: ResponseValidationRulePayload) =>
      request<ResponseValidationRule>('/api/validation-rules/', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    updateValidationRule: (id: number, payload: Partial<ResponseValidationRulePayload>) =>
      request<ResponseValidationRule>(`/api/validation-rules/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      }),
    deleteValidationRule: (id: number) =>
      request<Record<string, never>>(`/api/validation-rules/${id}/`, {
        method: 'DELETE'
      }),
    getRecoveryStrategies: () => request<RecoveryStrategy[]>('/api/recovery-strategies/'),
    createRecoveryStrategy: (payload: RecoveryStrategyPayload) =>
      request<RecoveryStrategy>('/api/recovery-strategies/', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    updateRecoveryStrategy: (id: number, payload: Partial<RecoveryStrategyPayload>) =>
      request<RecoveryStrategy>(`/api/recovery-strategies/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      }),
    deleteRecoveryStrategy: (id: number) =>
      request<Record<string, never>>(`/api/recovery-strategies/${id}/`, {
        method: 'DELETE'
      }),
    getProviderCredentials: () => request<ProviderCredential[]>('/api/provider-credentials/'),
    createProviderCredential: (payload: ProviderCredentialPayload) =>
      request<ProviderCredential>('/api/provider-credentials/', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    updateProviderCredential: (id: number, payload: Partial<ProviderCredentialPayload>) =>
      request<ProviderCredential>(`/api/provider-credentials/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      }),
    deleteProviderCredential: (id: number) =>
      request<Record<string, never>>(`/api/provider-credentials/${id}/`, {
        method: 'DELETE'
      }),
    testProviderCredential: (payload: Pick<ProviderCredentialPayload, 'provider' | 'base_url' | 'access_token'>) =>
      request<ProviderCredentialTestResult>('/api/provider-credentials/test/', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    previewProviderModels: (credentialId: number) =>
      request<ProviderModelPreview>(`/api/provider-credentials/${credentialId}/models/preview/`),
    importProviderModels: (credentialId: number, modelNames: string[]) =>
      request<ProviderModelImportResult>(`/api/provider-credentials/${credentialId}/models/import/`, {
        method: 'POST',
        body: JSON.stringify({ model_names: modelNames })
      }),
    getUsageQuotas: () => request<UsageQuota[]>('/api/usage-quotas/'),
    createUsageQuota: (payload: UsageQuotaPayload) =>
      request<UsageQuota>('/api/usage-quotas/', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    updateUsageQuota: (id: number, payload: Partial<UsageQuotaPayload>) =>
      request<UsageQuota>(`/api/usage-quotas/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      }),
    deleteUsageQuota: (id: number) =>
      request<Record<string, never>>(`/api/usage-quotas/${id}/`, {
        method: 'DELETE'
      }),
    getModelHealthRules: () => request<ModelHealthRule[]>('/api/model-health-rules/'),
    createModelHealthRule: (payload: ModelHealthRulePayload) =>
      request<ModelHealthRule>('/api/model-health-rules/', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    updateModelHealthRule: (id: number, payload: Partial<ModelHealthRulePayload>) =>
      request<ModelHealthRule>(`/api/model-health-rules/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      }),
    deleteModelHealthRule: (id: number) =>
      request<Record<string, never>>(`/api/model-health-rules/${id}/`, {
        method: 'DELETE'
      }),
    getModelHealthEvents: () => request<ModelHealthEvent[]>('/api/model-health-events/'),
    getModelHealthOverrides: () => request<ModelHealthOverride[]>('/api/model-health-overrides/'),
    createModelHealthOverride: (payload: ModelHealthOverridePayload) =>
      request<ModelHealthOverride>('/api/model-health-overrides/', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    updateModelHealthOverride: (id: number, payload: Partial<ModelHealthOverridePayload>) =>
      request<ModelHealthOverride>(`/api/model-health-overrides/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      }),
    deleteModelHealthOverride: (id: number) =>
      request<Record<string, never>>(`/api/model-health-overrides/${id}/`, {
        method: 'DELETE'
      }),
    getLogs: (query: RoutingLogQuery = {}) =>
      request<PaginatedResponse<RoutingLog>>(
        `/api/routing-logs/${buildQuery({
          page: query.page,
          page_size: query.pageSize,
          search: query.search,
          ordering: query.ordering
        })}`
      ),
    chat: (prompt: string, policy: string) =>
      request<ChatResponse>('/api/chat/', {
        method: 'POST',
        body: JSON.stringify({ prompt, policy })
      }),
    simulateRouting: (prompt: string, policy: string) =>
      request<RoutingSimulationResponse>('/api/routing-simulator/', {
        method: 'POST',
        body: JSON.stringify({ prompt, policy })
      })
  }
}
