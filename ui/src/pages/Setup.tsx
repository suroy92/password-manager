import * as React from 'react'
import { useNavigate } from 'react-router-dom'
import Container from '@mui/material/Container'
import Paper from '@mui/material/Paper'
import TextField from '@mui/material/TextField'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import Typography from '@mui/material/Typography'
import Snackbar from '@mui/material/Snackbar'
import { setupVault } from '../api'

export default function Setup(){
  const nav = useNavigate()
  const [pw1, setPw1] = React.useState('')
  const [pw2, setPw2] = React.useState('')
  const [loading, setLoading] = React.useState(false)
  const [snack, setSnack] = React.useState<string | null>(null)

  async function submit(){
    if (pw1 !== pw2){
      setSnack('Passwords do not match')
      return
    }
    setLoading(true)
    try {
      await setupVault(pw1)
      setSnack('Vault initialized. Please unlock now.')
      setTimeout(()=>nav('/'), 600)
    } catch (e:any) {
      setSnack(e?.response?.data?.detail || 'Setup failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="sm" sx={{ mt: 6 }}>
      <Paper sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>First-time Setup</Typography>
        <Stack spacing={2}>
          <TextField type="password" label="Master password" value={pw1} onChange={e=>setPw1(e.target.value)} autoFocus />
          <TextField type="password" label="Confirm password" value={pw2} onChange={e=>setPw2(e.target.value)} />
          <Button variant="contained" onClick={submit} disabled={loading || !pw1 || !pw2}>
            {loading ? 'Setting up...' : 'Initialize'}
          </Button>
          <Typography variant="body2" color="text.secondary">
            This will create a local vault database. You will unlock it with this master password.
          </Typography>
        </Stack>
      </Paper>
      <Snackbar open={!!snack} autoHideDuration={3000} onClose={()=>setSnack(null)} message={snack || ''} />
    </Container>
  )
}
