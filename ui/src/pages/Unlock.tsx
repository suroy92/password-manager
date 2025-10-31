import * as React from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'
import Container from '@mui/material/Container'
import Paper from '@mui/material/Paper'
import TextField from '@mui/material/TextField'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'

export default function Unlock() {
  const [pw, setPw] = React.useState('')
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const nav = useNavigate()

  async function submit() {
    setLoading(true); setError(null)
    try {
      await api.post('/unlock', { master_password: pw })
      nav('/vault')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Unlock failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="sm" sx={{ mt: 6 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>Unlock vault</Typography>
        <Stack spacing={2}>
          <TextField type="password" label="Master password" value={pw} onChange={(e) => setPw(e.target.value)} autoFocus />
          <Button variant="contained" onClick={submit} disabled={loading || !pw}>
            {loading ? 'Unlocking...' : 'Unlock'}
          </Button>
          {error && <Typography color="error">{error}</Typography>}
        </Stack>
      </Paper>
    </Container>
  )
}
