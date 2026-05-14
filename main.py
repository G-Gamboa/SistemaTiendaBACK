from contextlib import contextmanager
from typing import Any, Optional
import json
import os

import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="API Caja Tienda GT")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")


@contextmanager
def get_connection(dict_cursor: bool = False):
    cursor_factory = RealDictCursor if dict_cursor else None
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=cursor_factory)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


class Transaction(BaseModel):
    transaction_type: str
    sale_amount: Optional[float] = None
    received_amount: Optional[float] = None
    change_amount: Optional[float] = None
    money_in: dict[str, int] = {}
    money_out: dict[str, int] = {}
    notes: str = ""


@app.exception_handler(psycopg2.Error)
async def database_exception_handler(request: Any, exc: psycopg2.Error) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Error de base de datos"})


@app.get("/")
@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/inventory")
def get_inventory() -> dict[str, int]:
    with get_connection(dict_cursor=True) as conn:
        cur = conn.cursor()
        cur.execute("SELECT denomination, quantity FROM cash_inventory ORDER BY denomination DESC;")
        rows = cur.fetchall()
    return {str(row["denomination"]): row["quantity"] for row in rows}


@app.post("/api/transaction")
def process_transaction(t: Transaction) -> dict[str, str]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO transactions_log
                (transaction_type, sale_amount, received_amount, change_amount, money_in, money_out, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                t.transaction_type,
                t.sale_amount,
                t.received_amount,
                t.change_amount,
                json.dumps(t.money_in),
                json.dumps(t.money_out),
                t.notes,
            ),
        )
        for denom, qty in t.money_in.items():
            cur.execute(
                "UPDATE cash_inventory SET quantity = quantity + %s WHERE denomination = %s",
                (qty, denom),
            )
        for denom, qty in t.money_out.items():
            cur.execute(
                "UPDATE cash_inventory SET quantity = quantity - %s WHERE denomination = %s",
                (qty, denom),
            )
    return {"status": "success", "message": "Transacción registrada exitosamente"}


@app.get("/api/transactions")
def get_transactions() -> list[dict[str, Any]]:
    with get_connection(dict_cursor=True) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT transaction_type, sale_amount, received_amount, change_amount,
                   money_in, money_out, notes, created_at
            FROM transactions_log
            WHERE created_at >= NOW() - INTERVAL '30 days'
            ORDER BY created_at DESC
            """
        )
        rows = cur.fetchall()
    return [{**row, "created_at": row["created_at"].isoformat()} for row in rows]
