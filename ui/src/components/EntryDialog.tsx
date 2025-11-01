import * as React from 'react'
import Dialog from '@mui/material/Dialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import TextField from '@mui/material/TextField'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import { Entry, EntryIn } from '../types'
import { createEntry, getEntry, updateEntry } from '../api'
import PasswordGenDialog from './PasswordGenDialog'

export default function EntryDialog({ open, onClose, initial }:{ open: boolean, onClose: (changed:boolean)=>void, initial?: Entry }){
  const editing = !!initial
  const [title, setTitle] = React.useState(initial?.title ?? '')
  const [username, setUsername] = React.useState(initial?.username ?? '')
  const [password, setPassword] = React.useState<string>('')
  const [url, setUrl] = React.useState(initial?.url ?? '')
  const [notes, setNotes] = React.useState(initial?.notes ?? '')
  const [codes, setCodes] = React.useState<string>('')
  const [loading, setLoading] = React.useState(false)
  const [pwOpen, setPwOpen] = React.useState(false)

  React.useEffect(() => {
    setTitle(initial?.title ?? '')
    setUsername(initial?.username ?? '')
    setUrl(initial?.url ?? '')
    setNotes(initial?.notes ?? '')
    setPassword('')
    setCodes('')
  }, [initial, open])

  // Fetch sensitive fields when editing
  React.useEffect(() => {
    async function fetchSecrets(){
      if (open && initial?.id){
        const ent = await getEntry(initial.id, true)
        setPassword(ent.password || '')
        setCodes((ent.recovery_codes || []).join('\n'))
      }
    }
    fetchSecrets()
  }, [open, initial?.id])

  function toPayload(): EntryIn {
    const rc = codes.split(/\r?\n/).map(s => s.trim()).filter(Boolean)
    return {
      title,
      username: username || undefined,
      password: password || undefined,
      url: url || undefined,
      notes: notes || undefined,
      recovery_codes: rc.length ? rc : undefined,
    }
  }

  async function save(){
    setLoading(true)
    try {
      const payload = toPayload()
      if (editing && initial?.id){
        await updateEntry(initial.id, payload, false)
      } else {
        await createEntry(payload, false)
      }
      onClose(true)
    } catch (e) {
      console.error(e)
      onClose(false)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={()=>onClose(false)} fullWidth maxWidth="sm">
      <DialogTitle>{editing ? 'Edit entry' : 'New entry'}</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField label="Title" value={title} onChange={e=>setTitle(e.target.value)} required />
          <TextField label="Username / Email" value={username} onChange={e=>setUsername(e.target.value)} />
          <Stack direction="row" spacing={1}>
            <TextField fullWidth label="Password" type="text" value={password} onChange={e=>setPassword(e.target.value)} />
            <Button variant="outlined" onClick={()=>setPwOpen(true)}>Generate</Button>
          </Stack>
          <TextField label="URL" value={url} onChange={e=>setUrl(e.target.value)} />
          <TextField label="Notes" value={notes} onChange={e=>setNotes(e.target.value)} multiline minRows={2} />
          <TextField label="Recovery codes (one per line)" value={codes} onChange={e=>setCodes(e.target.value)} multiline minRows={3} />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={()=>onClose(false)}>Cancel</Button>
        <Button variant="contained" onClick={save} disabled={!title || loading}>{loading ? 'Saving...' : 'Save'}</Button>
      </DialogActions>
      <PasswordGenDialog open={pwOpen} onClose={()=>setPwOpen(false)} onPick={(pw)=>{ setPassword(pw); setPwOpen(false) }} />
    </Dialog>
  )
}
