import uvicorn
if __name__ == '__main__':
    uvicorn.run('pm.api.main:app', host='127.0.0.1', port=8787, reload=False)
