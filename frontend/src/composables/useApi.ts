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
  role: string
  quality_level: number
  speed_level: number
  cost_level: number
  privacy_level: string
  context_window: number
  is_active: boolean
}

export type LLMModelPayload = Omit<LLMModel, 'id'>

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
  }
  is_active: boolean
}

export type RoutingPolicyPayload = Omit<RoutingPolicy, 'id'>

export type ProviderCredential = {
  id: number
  provider: string
  display_name: string
  base_url: string
  access_token: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export type ProviderCredentialPayload = Omit<ProviderCredential, 'id' | 'created_at' | 'updated_at'>

export type RoutingLog = {
  id: number
  prompt_summary: string
  policy: string
  selected_provider: string
  selected_model: string
  routing_reason: string
  latency_ms: number
  estimated_tokens: number
  response_text: string
  error_message: string
  created_at: string
}

export type DashboardMetrics = {
  total_requests: number
  average_latency_ms: number
  local_routing_ratio: number
  estimated_cost_savings_percent: number
  model_usage: Array<{ selected_provider: string; selected_model: string; count: number }>
  policy_usage: Array<{ policy: string; count: number }>
  recent_logs: RoutingLog[]
}

export type ChatResponse = RoutingLog & {
  analysis: {
    has_sensitive_data: boolean
    is_code: boolean
    is_long_context: boolean
    requires_reasoning: boolean
    estimated_tokens: number
  }
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

export function useApi() {
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
    getMetrics: () => request<DashboardMetrics>('/api/dashboard/metrics/'),
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
    getLogs: () => request<RoutingLog[]>('/api/routing-logs/'),
    chat: (prompt: string, policy: string) =>
      request<ChatResponse>('/api/chat/', {
        method: 'POST',
        body: JSON.stringify({ prompt, policy })
      })
  }
}
