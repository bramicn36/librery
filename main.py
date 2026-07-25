from datetime import date
from pathlib import Path
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from database import get_connection

# --- Schemas ---


class AuthorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    country: Optional[str] = Field(None, max_length=100)


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author_id: Optional[int] = None
    year: Optional[int] = Field(None, ge=1000, le=2100)
    available: Optional[bool] = None


class LoanCreate(BaseModel):
    book_id: int
    borrower: str = Field(..., min_length=1, max_length=100)


# --- Helpers ---


def as_bool(value: Any) -> bool:
    return bool(value)


# --- App ---

CLIENT_DIR = Path(__file__).resolve().parent / "client"

app = FastAPI(title="Library Management System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def serve_index():
    return FileResponse(CLIENT_DIR / "index.html")


app.mount("/static", StaticFiles(directory=CLIENT_DIR), name="static")


@app.get("/health")
def health_check():
    return {"status": "ok"}


# --- Authors ---


@app.get("/authors")
def get_authors():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM authors")
            return cursor.fetchall()
    finally:
        conn.close()


@app.post("/authors", status_code=status.HTTP_201_CREATED)
def create_author(author: AuthorCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO authors (name, country) VALUES (%s, %s)",
                (author.name, author.country),
            )
            conn.commit()
            cursor.execute("SELECT * FROM authors WHERE id = %s", (cursor.lastrowid,))
            return cursor.fetchone()
    finally:
        conn.close()


# --- Books ---


@app.get("/books")
def get_books():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM books")
            return cursor.fetchall()
    finally:
        conn.close()


@app.get("/books/{book_id}")
def get_book(book_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
            book = cursor.fetchone()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            return book
    finally:
        conn.close()


@app.post("/books")
def add_book(title: str, author_id: int, year: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO books (title, author_id, year) VALUES (%s, %s, %s)",
                (title, author_id, year),
            )
            conn.commit()
    finally:
        conn.close()
    return {"message": "Book added successfully"}


@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookUpdate):
    updates = book.model_dump(exclude_unset=True)
    if not updates:
        return get_book(book_id)

    if "author_id" in updates:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM authors WHERE id = %s", (updates["author_id"],))
                if not cursor.fetchone():
                    raise HTTPException(status_code=404, detail="Author not found")
        finally:
            conn.close()

    fields = ", ".join(f"{key} = %s" for key in updates)
    values = list(updates.values()) + [book_id]

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"UPDATE books SET {fields} WHERE id = %s", values)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Book not found")
            conn.commit()
            cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
            return cursor.fetchone()
    finally:
        conn.close()


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM books WHERE id = %s", (book_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Book not found")

            cursor.execute(
                """
                SELECT COUNT(*) AS cnt FROM loans
                WHERE book_id = %s AND return_date IS NULL
                """,
                (book_id,),
            )
            if cursor.fetchone()["cnt"] > 0:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot delete book with active loans",
                )

            cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
            conn.commit()
    finally:
        conn.close()


# --- Loans ---


@app.get("/loans")
def get_loans():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM loans")
            return cursor.fetchall()
    finally:
        conn.close()


@app.post("/loans", status_code=status.HTTP_201_CREATED)
def create_loan(loan: LoanCreate):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, available FROM books WHERE id = %s", (loan.book_id,))
            book = cursor.fetchone()
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            if not as_bool(book["available"]):
                raise HTTPException(status_code=400, detail="Book is not available")

            cursor.execute(
                """
                INSERT INTO loans (book_id, borrower, loan_date)
                VALUES (%s, %s, %s)
                """,
                (loan.book_id, loan.borrower, date.today()),
            )
            loan_id = cursor.lastrowid
            cursor.execute("UPDATE books SET available = FALSE WHERE id = %s", (loan.book_id,))
            conn.commit()
            cursor.execute("SELECT * FROM loans WHERE id = %s", (loan_id,))
            return cursor.fetchone()
    finally:
        conn.close()


@app.put("/loans/{loan_id}/return")
def return_loan(loan_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, book_id, return_date FROM loans WHERE id = %s",
                (loan_id,),
            )
            loan = cursor.fetchone()
            if not loan:
                raise HTTPException(status_code=404, detail="Loan not found")
            if loan["return_date"] is not None:
                raise HTTPException(status_code=400, detail="Loan already returned")

            cursor.execute(
                "UPDATE loans SET return_date = %s WHERE id = %s",
                (date.today(), loan_id),
            )
            cursor.execute("UPDATE books SET available = TRUE WHERE id = %s", (loan["book_id"],))
            conn.commit()
            cursor.execute("SELECT * FROM loans WHERE id = %s", (loan_id,))
            return cursor.fetchone()
    finally:
        conn.close()
