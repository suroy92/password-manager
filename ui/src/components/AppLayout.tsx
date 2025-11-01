import * as React from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import AppBar from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import Box from '@mui/material/Box'
import Stack from '@mui/material/Stack'

export default function AppLayout() {
  const nav = useNavigate()
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <AppBar position="static" color="transparent" sx={{ backdropFilter: 'blur(8px)', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1, cursor: 'pointer' }} onClick={() => nav('/')}>🔐 Password Manager</Typography>
          <Stack direction="row" spacing={1}>
            <Button color="inherit" onClick={() => nav('/vault')}>Vault</Button>
            <Button color="inherit" onClick={() => nav('/setup')}>Setup</Button>
          </Stack>
        </Toolbar>
      </AppBar>
      <Box component="main" sx={{ flex: 1, p: 2 }}>
        <Outlet />
      </Box>
    </Box>
  )
}
