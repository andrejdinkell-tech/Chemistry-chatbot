from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chempy import Substance
import re

app = FastAPI()

# Чтобы index.html мог отправлять запросы
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str


# -------- ЛОГИКА --------

def extract_formula(text: str):
    match = re.search(r'([A-Z][a-z]?\d*)+', text.replace(" ", ""))
    return match.group(0) if match else None


def extract_number(pattern, text):
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None


def solve(text: str):
    text = text.replace(",", ".")
    text_lower = text.lower()

    formula = extract_formula(text)
    if not formula:
        return " Не вижу химическую формулу."

    try:
        substance = Substance.from_formula(formula)
        M = float(substance.mass)
    except:
        return "Ошибка в формуле."

  
    if "молярн" in text_lower:
        return f"Молярная масса {formula} = {M:.3f} г/моль"

   
    n = extract_number(r'(\d+\.?\d*)\s*моль', text)
    if n is not None:
        m = n * M
        return f"m = n × M = {n} × {M:.3f} = {m:.3f} г"

    
    m_val = extract_number(r'(\d+\.?\d*)\s*г', text)
    if m_val is not None:
        n = m_val / M
        return f"n = m / M = {m_val} / {M:.3f} = {n:.3f} моль"

    
    V = extract_number(r'(\d+\.?\d*)\s*л', text)
    if n is not None and V is not None:
        c = n / V
        return f"c = n / V = {n} / {V} = {c:.3f} моль/л"

    return "⚠ Тип задачи не распознан."


# -------- API --------

@app.post("/chat")
async def chat(req: ChatRequest):
    reply = solve(req.message)
    return {"reply": reply}


@app.get("/")
async def root():
    return {"status": "Chemistry site работает 🚀"}