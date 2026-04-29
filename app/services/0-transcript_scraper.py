import shutil
import re
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = Options()
options.add_argument("-profile")
options.add_argument("/home/hiro/.mozilla/firefox/abcd1234.default-release")


class TranscriptScrapeError(Exception):
    pass

def _clean_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    return text


def build_driver(headless: bool = True):
    gecko_path = shutil.which("geckodriver")
    if not gecko_path:
        raise TranscriptScrapeError(
            "geckodriver no encontrado. Instala con: sudo apt install geckodriver"
        )

    options = Options()
    if headless:
        options.add_argument("-headless")

    options.set_preference("intl.accept_languages", "es-ES,es")
    options.set_preference("media.volume_scale", "0.0")

    service = Service(gecko_path)
    return webdriver.Firefox(service=service, options=options)



def fetch_transcript_from_site(youtube_url: str, headless: bool = True, timeout: int = 40) -> dict:
    driver = build_driver(headless=headless)

    try:
        driver.get("https://youtubetotranscript.com/")
        wait = WebDriverWait(driver, timeout)

        # 1) input del link
        input_box = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
        )
        input_box.clear()
        input_box.send_keys(youtube_url)
        input_box.send_keys(Keys.ENTER)

        # 2) esperar textarea (NO el texto todavía)
        textarea = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "textarea"))
        )

        # 3) esperar a que el textarea tenga CONTENIDO
        def textarea_has_text(driver):
            value = textarea.get_attribute("value")
            return value and len(value.strip()) > 50

        wait.until(textarea_has_text)

        transcript_text = textarea.get_attribute("value")
        transcript_text = _clean_text(transcript_text)

        if not transcript_text:
            raise TranscriptScrapeError("Transcript vacío")

        # detectar CAPTCHA / error visual
        title = driver.title.lower()
        if "captcha" in title or "verify" in title:
            raise TranscriptScrapeError("CAPTCHA detectado")

        return {
            "title": driver.title,
            "transcript": transcript_text
        }

    finally:
        driver.quit()

