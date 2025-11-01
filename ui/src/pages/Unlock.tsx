import * as React from 'react'
import { useNavigate } from 'react-router-dom'
import Container from '@mui/material/Container'
import Paper from '@mui/material/Paper'
import TextField from '@mui/material/TextField'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import Snackbar from '@mui/material/Snackbar'
import { unlockVault } from '../api'

export default function Unlock(){
  const [pw, setPw] = React.useState('')
  const [loading, setLoading] = React.useState(false)
  const [snack, setSnack] = React.useState<string | null>(null)
  const nav = useNavigate()

  async function submit(){
    setLoading(true); setSnack(null)
    try {
      await unlockVault(pw)
      nav('/vault')
    } catch (e:any) {
      setSnack(e?.response?.data?.detail || 'Unlock failed')
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
          <Typography variant="body2" color="text.secondary">
            First time here? Go to Setup from the top-right to initialize the vault.
          </Typography>
        </Stack>
      </Paper>
      <Snackbar open={!!snack} autoHideDuration={3000} onClose={()=>setSnack(null)} message={snack || ''} />
    </Container>
  )
}
