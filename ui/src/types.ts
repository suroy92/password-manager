export interface Entry {
  id: string
  title: string
  username?: string
  password?: string | null
  url?: string
  notes?: string
  recovery_codes?: string[] | null
  created_at: string
  updated_at: string
  last_rotated_at?: string | null
}

export interface EntryIn {
  title: string
  username?: string
  password?: string
  url?: string
  notes?: string
  recovery_codes?: string[]
}
