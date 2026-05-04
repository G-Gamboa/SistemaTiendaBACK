from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json

app = FastAPI(title="API Caja Tienda GT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

class Transaction(BaseModel):
    transaction_type: str
    sale_amount: float = None
    received_amount: float = None
    change_amount: float = None
    money_in: dict = {}
    money_out: dict = {}
    notes: str = ""

@app.get("/api/inventory")
def get_inventory():
    """Devuelve cuántos billetes y monedas hay actualmente en la caja."""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        cur.execute("SELECT denomination, quantity FROM cash_inventory ORDER BY denomination DESC;")
        rows = cur.fetchall()
        conn.close()
        
        return {str(row['denomination']): row['quantity'] for row in rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transaction")
def process_transaction(t: Transaction):
    """Guarda el log de la venta y actualiza las cantidades de billetes."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO transactions_log 
            (transaction_type, sale_amount, received_amount, change_amount, money_in, money_out, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (t.transaction_type, t.sale_amount, t.received_amount, t.change_amount, 
              json.dumps(t.money_in), json.dumps(t.money_out), t.notes))
        
        for denom, qty in t.money_in.items():
            cur.execute("UPDATE cash_inventory SET quantity = quantity + %s WHERE denomination = %s", (qty, denom))
            
        for denom, qty in t.money_out.items():
            cur.execute("UPDATE cash_inventory SET quantity = quantity - %s WHERE denomination = %s", (qty, denom))
            
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Transacción registrada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
@app.get("/health")
def health_check():
    """Endpoint de estado para confirmar que la API está viva."""
    return {
        "status": "ok", 
        "message": "API funcionando al 100%",
        "environment": "production"
    }

@app.get("/api/transactions")
def get_transactions():
    """Devuelve el historial de transacciones de los últimos 30 días para los reportes."""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cur = conn.cursor()
        # Traemos todo lo de los últimos 30 días
        cur.execute("""
            SELECT transaction_type, sale_amount, received_amount, change_amount, 
                   money_in, money_out, notes, created_at
            FROM transactions_log 
            WHERE created_at >= NOW() - INTERVAL '30 days'
            ORDER BY created_at DESC
        """)
        rows = cur.fetchall()
        conn.close()
        
        # Formatear la fecha para que el HTML la entienda
        for row in rows:
            row['created_at'] = row['created_at'].isoformat()
            
        return rows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))