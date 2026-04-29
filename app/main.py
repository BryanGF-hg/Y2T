from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .db import Base, engine
from .routes.videos import router as videos_router

from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--remote-debugging-port=9222")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="YT Transcript Admin")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(videos_router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
  return templates.TemplateResponse(
      request,
      "index.html",
      {}
  )

