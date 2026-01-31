const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface RequestOptions extends RequestInit {
  token?: string
}

export async function apiCall<T>(
  endpoint: string,
  options: RequestOptions = {},
): Promise<T> {
  const { token, ...fetchOptions } = options
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...fetchOptions.headers,
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...fetchOptions,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(error.detail || error.message || 'Request failed')
  }

  return response.json()
}

export async function uploadFile(file: File, token: string): Promise<string> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_URL}/api/upload/`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  })

  if (!response.ok) {
    throw new Error('Upload failed')
  }

  const data = await response.json()
  return data.url
}

export function getWebSocketUrl(path: string): string {
  const wsProtocol = process.env.NEXT_PUBLIC_API_URL?.startsWith('https')
    ? 'wss'
    : 'ws'
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const cleanUrl = baseUrl.replace(/^https?:\/\//, '')
  return `${wsProtocol}://${cleanUrl}${path}`
}
