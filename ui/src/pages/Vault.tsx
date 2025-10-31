import * as React from 'react'
import api from '../api'
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

interface Entry {
  id: string
  title: string
  username?: string
  url?: string
  notes?: string
  updated_at?: string
}

export default function Vault() {
  const [items, setItems] = React.useState<Entry[]>([])
  const [q, setQ] = React.useState('')

  async function load() {
    const res = await api.get('/entries', { params: q ? { q } : undefined })
    setItems(res.data.items || [])
  }

  React.useEffect(() => { load() }, [])

  return (
    <Container maxWidth="md" sx={{ mt: 3 }}>
      <Paper sx={{ p: 2 }}>
        <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>Vault</Typography>
          <TextField size="small" placeholder="Search…" value={q} onChange={(e)=>setQ(e.target.value)} />
          <Button variant="outlined" onClick={load}>Search</Button>
        </Stack>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Username</TableCell>
              <TableCell>URL</TableCell>
              <TableCell>Updated</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {items.map(it => (
              <TableRow key={it.id} hover>
                <TableCell>{it.title}</TableCell>
                <TableCell>{it.username}</TableCell>
                <TableCell>{it.url}</TableCell>
                <TableCell>{it.updated_at}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Container>
  )
}
