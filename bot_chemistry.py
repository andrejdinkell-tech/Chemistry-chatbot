from fastapi import FastAPI
from pydantic import BaseModel
from chempy import Substance
import re

app = FastAPI()

class ChatRequest(BaseModel):
    message: str


def extract_formula(text: str):
    match = re.search(r'([A-Z][a-z]?\d*)+', text.replace(" ", ""))
    return match.group(0) if match else None


def extract_number(pattern, text):
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None


def solve(text: str):
    text = text.replace(",", ".")
    formula = extract_formula(text)

    if not formula:
        return "Не вижу формулу."

    try:
        substance = Substance.from_formula(formula)
        M = float(substance.mass)
    except:
        return "Ошибка в формуле."

    if "молярн" in text.lower():
        return f"Молярная масса {formula} = {M:.3f} г/моль"

    n = extract_number(r'(\d+\.?\d*)\s*моль', text)
    if n:
        return f"m = n × M = {n} × {M:.3f} = {n*M:.3f} г"

    m_val = extract_number(r'(\d+\.?\d*)\s*г', text)
    if m_val:
        return f"n = m / M = {m_val} / {M:.3f} = {m_val/M:.3f} моль"

    return "Тип задачи не распознан."


@app.post("/chat")
async def chat(req: ChatRequest):
    reply = solve(req.message)
    return {"reply": reply}