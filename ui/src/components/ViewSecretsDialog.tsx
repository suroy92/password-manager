import * as React from 'react'
import Dialog from '@mui/material/Dialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import TextField from '@mui/material/TextField'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import IconButton from '@mui/material/IconButton'
import InputAdornment from '@mui/material/InputAdornment'
import Tooltip from '@mui/material/Tooltip'
import Visibility from '@mui/icons-material/Visibility'
import VisibilityOff from '@mui/icons-material/VisibilityOff'
import ContentCopy from '@mui/icons-material/ContentCopy'
import Alert from '@mui/material/Alert'
import { getEntry } from '../api'
import type { Entry } from '../types'

export default function ViewSecretsDialog({
  open,
  entryId,
  title,
  onClose,
}: {
  open: boolean
  entryId: string | null
  title?: string
  onClose: () => void
}) {
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [item, setItem] = React.useState<Entry | null>(null)
  const [showPw, setShowPw] = React.useState(false)
  const [copied, setCopied] = React.useState<string | null>(null)

  React.useEffect(() => {
    async function load() {
      if (!open || !entryId) return
      setLoading(true)
      setError(null)
      setItem(null)
      setShowPw(false)
      try {
        const e = await getEntry(entryId, true)
        setItem(e)
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Failed to load secrets')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [open, entryId])

  async function copy(text: string, label: string) {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(label)
      setTimeout(() => setCopied(null), 1200)
    } catch (_e) {}
  }

  const pw = item?.password || ''

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>View secrets{title ? ` — ${title}` : ''}</DialogTitle>
      <DialogContent>
        {loading && (
          <Stack alignItems="center" sx={{ py: 4, opacity: 0.7, fontSize: 14 }}>
            Loading…
          </Stack>
        )}
        {!loading && error && <Alert severity="error" sx={{ mt: 1 }}>{error}</Alert>}
        {!loading && !error && item && (
          <Stack spacing={2} sx={{ mt: 1 }}>
            <TextField
              label="Password"
              type={showPw ? 'text' : 'password'}
              value={pw}
              InputProps={{
                readOnly: true,
                endAdornment: (
                  <InputAdornment position="end">
                    <Tooltip title={showPw ? 'Hide' : 'Show'}>
                      <IconButton onClick={() => setShowPw(v => !v)} edge="end">
                        {showPw ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={copied === 'pw' ? 'Copied!' : 'Copy'}>
                      <IconButton onClick={() => copy(pw, 'pw')} edge="end">
                        <ContentCopy />
                      </IconButton>
                    </Tooltip>
                  </InputAdornment>
                ),
              }}
            />
            <TextField
              label="Recovery codes"
              value={(item.recovery_codes || []).join('\n')}
              InputProps={{ readOnly: true }}
              multiline
              minRows={3}
            />
            <Stack direction="row" spacing={1}>
              <Button
                variant="outlined"
                onClick={() => copy((item.recovery_codes || []).join('\n'), 'codes')}
              >
                {copied === 'codes' ? 'Copied!' : 'Copy codes'}
              </Button>
            </Stack>
          </Stack>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  )
}
