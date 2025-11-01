import axios from 'axios'
import type { Entry, EntryIn } from './types'

export const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

export async function setupVault(master_password: string) {
  return api.post('/setup', { master_password })
}

export async function unlockVault(master_password: string) {
  return api.post('/unlock', { master_password })
}

export async function listEntries(q?: string) {
  const res = await api.get('/entries', { params: q ? { q } : undefined })
  return res.data.items as Entry[]
}

export async function getEntry(id: string, reveal = false) {
  const res = await api.get(`/entries/${id}`, { params: { reveal } })
  return res.data.item as Entry
}

export async function createEntry(payload: EntryIn, reveal = false) {
  const res = await api.post('/entries', payload, { params: { reveal } })
  return res.data.item as Entry
}

export async function updateEntry(id: string, payload: EntryIn, reveal = false) {
  const res = await api.put(`/entries/${id}`, payload, { params: { reveal } })
  return res.data.item as Entry
}

export async function deleteEntry(id: string) {
  await api.delete(`/entries/${id}`)
}

export async function generatePassword(options?: {
  length?: number
  upper?: boolean
  lower?: boolean
  digits?: boolean
  symbols?: boolean
  avoid_ambiguous?: boolean
}) {
  const res = await api.post('/password/generate', options ?? {})
  return res.data.password as string
}
