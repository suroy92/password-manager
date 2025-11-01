import * as React from 'react'
import Dialog from '@mui/material/Dialog'
import DialogTitle from '@mui/material/DialogTitle'
import DialogContent from '@mui/material/DialogContent'
import DialogActions from '@mui/material/DialogActions'
import TextField from '@mui/material/TextField'
import Button from '@mui/material/Button'
import Stack from '@mui/material/Stack'
import Checkbox from '@mui/material/Checkbox'
import FormControlLabel from '@mui/material/FormControlLabel'
import { generatePassword } from '../api'

export default function PasswordGenDialog({ open, onClose, onPick }:{ open: boolean, onClose: ()=>void, onPick: (pw:string)=>void }){
  const [length, setLength] = React.useState(20)
  const [upper, setUpper] = React.useState(true)
  const [lower, setLower] = React.useState(true)
  const [digits, setDigits] = React.useState(true)
  const [symbols, setSymbols] = React.useState(true)
  const [avoid, setAvoid] = React.useState(true)
  const [result, setResult] = React.useState('')

  async function gen(){
    const pw = await generatePassword({ length, upper, lower, digits, symbols, avoid_ambiguous: avoid })
    setResult(pw)
  }

  function pick(){
    if(result) onPick(result)
  }

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Generate secure password</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField type="number" label="Length" value={length} onChange={e=>setLength(parseInt(e.target.value||'0',10))} inputProps={{ min:8, max:128 }} />
          <Stack direction="row" spacing={2} flexWrap="wrap">
            <FormControlLabel control={<Checkbox checked={upper} onChange={e=>setUpper(e.target.checked)} />} label="Uppercase" />
            <FormControlLabel control={<Checkbox checked={lower} onChange={e=>setLower(e.target.checked)} />} label="Lowercase" />
            <FormControlLabel control={<Checkbox checked={digits} onChange={e=>setDigits(e.target.checked)} />} label="Digits" />
            <FormControlLabel control={<Checkbox checked={symbols} onChange={e=>setSymbols(e.target.checked)} />} label="Symbols" />
            <FormControlLabel control={<Checkbox checked={avoid} onChange={e=>setAvoid(e.target.checked)} />} label="Avoid ambiguous" />
          </Stack>
          <TextField label="Result" value={result} InputProps={{ readOnly: true }} />
          <Button variant="outlined" onClick={gen}>Generate</Button>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button variant="contained" onClick={pick} disabled={!result}>Use password</Button>
      </DialogActions>
    </Dialog>
  )
}
