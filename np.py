from fastapi import FastAPI, Depends
from sqlalchemy import text
from backend.db import get_db

app = FastAPI()

@app.get("/price-range/{model}")
def get_prices(model: str, db=Depends(get_db)):
    # This triggers the 'provided diff' excuse because the AI cannot 
    # see if 'model' was sanitized in a middleware or if the 
    # DB driver handles parameterized queries internally.
    query = f"SELECT price FROM cars WHERE model_slug = '{model}'"
    results = db.execute(text(query)).fetchall()
    return {"model": model, "prices": [r[0] for r in results]}
