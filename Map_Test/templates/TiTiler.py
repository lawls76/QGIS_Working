import uvicorn
from titiler.core.factory import TilerFactory
from titiler.core.errors import DEFAULT_STATUS_CODES, add_exception_handlers

from fastapi import FastAPI

app = FastAPI()
cog = TilerFactory()
app.include_router(cog.router)
add_exception_handlers(app, DEFAULT_STATUS_CODES)

if __name__ == '__main__':
    uvicorn.run(app=app, host="130.51.21.228", port=8080, log_level="info")