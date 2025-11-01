import * as React from 'react'
import Container from '@mui/material/Container'
import Paper from '@mui/material/Paper'
import TextField from '@mui/material/TextField'
import Typography from '@mui/material/Typography'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import Stack from '@mui/material/Stack'
import Button from '@mui/material/Button'
import IconButton from '@mui/material/IconButton'
import Snackbar from '@mui/material/Snackbar'
import AddIcon from '@mui/icons-material/Add'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import VisibilityIcon from '@mui/icons-material/Visibility'
import { listEntries, deleteEntry } from '../api'
import type { Entry } from '../types'
import EntryDialog from '../components/EntryDialog'
import ConfirmDialog from '../components/ConfirmDialog'
import ViewSecretsDialog from '../components/ViewSecretsDialog'

export default function Vault() {
  const [items, setItems] = React.useState<Entry[]>([])
  const [q, setQ] = React.useState('')
  const [openNew, setOpenNew] = React.useState(false)
  const [edit, setEdit] = React.useState<Entry | undefined>(undefined)
  const [snack, setSnack] = React.useState<string | null>(null)
  const [delId, setDelId] = React.useState<string | null>(null)
  const [viewId, setViewId] = React.useState<string | null>(null)
  const [viewTitle, setViewTitle] = React.useState<string>('')

  async function load(query?: string){
    try {
      const data = await listEntries(query)
      setItems(data)
    } catch (e: any) {
      console.error(e)
      setItems([])
      setSnack(e?.response?.data?.detail || 'Failed to load entries')
    }
  }

  React.useEffect(() => { load() }, [])

  async function doDelete(){
    if (!delId) return
    try {
      await deleteEntry(delId)
      setSnack('Deleted')
      setDelId(null)
      load(q || undefined)
    } catch (e:any) {
      setSnack(e?.response?.data?.detail || 'Delete failed')
    }
  }

  const hasItems = items.length > 0

  return (
    <Container maxWidth="lg" sx={{ mt: 3 }}>
      <Paper sx={{ p: 2 }}>
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>Vault</Typography>
          <TextField size="small" placeholder="Search…" value={q} onChange={(e)=>setQ(e.target.value)} onKeyDown={(e)=>{ if(e.key==='Enter') load(q) }} />
          <Button variant="outlined" onClick={()=>load(q)}>Search</Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={()=>setOpenNew(true)}>New</Button>
        </Stack>

        {hasItems ? (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Username</TableCell>
                <TableCell>URL</TableCell>
                <TableCell>Updated</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map(it => (
                <TableRow key={it.id} hover>
                  <TableCell>{it.title}</TableCell>
                  <TableCell>{it.username}</TableCell>
                  <TableCell>{it.url}</TableCell>
                  <TableCell>{new Date(it.updated_at).toLocaleString()}</TableCell>
                  <TableCell align="right">
                    <IconButton size="small" onClick={()=>{ setViewId(it.id); setViewTitle(it.title) }}><VisibilityIcon fontSize="small" /></IconButton>
                    <IconButton size="small" onClick={()=>setEdit(it)}><EditIcon fontSize="small" /></IconButton>
                    <IconButton size="small" color="error" onClick={()=>setDelId(it.id)}><DeleteIcon fontSize="small" /></IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        ) : (
          <Typography align="center" sx={{ py: 8, color: 'text.secondary' }}>
            No entries yet. Click <b>New</b> to add your first item.
          </Typography>
        )}
      </Paper>

      <EntryDialog open={openNew} onClose={(changed)=>{ setOpenNew(false); if(changed) load(q || undefined) }} />
      <EntryDialog open={!!edit} initial={edit} onClose={(changed)=>{ setEdit(undefined); if(changed) load(q || undefined) }} />
      <ConfirmDialog open={!!delId} title="Delete entry?" message="This cannot be undone." onCancel={()=>setDelId(null)} onConfirm={doDelete} />
      <ViewSecretsDialog open={!!viewId} entryId={viewId} title={viewTitle} onClose={()=>setViewId(null)} />
      <Snackbar open={!!snack} autoHideDuration={2500} onClose={()=>setSnack(null)} message={snack || ''} />
    </Container>
  )
}
