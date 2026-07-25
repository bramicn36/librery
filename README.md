# Library Management System

A library management application with a **FastAPI** backend, **MySQL** database, and a simple **HTML** client.

## Project Structure

```
library-project/
├── main.py           # FastAPI application (all API endpoints)
├── database.py       # MySQL connection (PyMySQL)
├── requirements.txt  # Python dependencies
├── schema.sql        # Database table definitions
├── seed.sql          # Seed data (3 authors, 6 books, 3 loans)
├── docker-compose.yml
├── client/
│   ├── index.html    # HTML client
│   └── css/
│       └── style.css
└── README.md
```

## Prerequisites

- Python 3.10+
- Docker Desktop (for MySQL)

## Setup

### 1. Start MySQL with Docker

```bash
docker compose up -d
```

This creates the `library` database with:
- **User:** root
- **Password:** rootpass123
- **Port:** 3306

Tables and seed data are loaded automatically on first run via `schema.sql` and `seed.sql`.

**phpMyAdmin (web UI):** http://localhost:8081  
Login: user `root`, password `rootpass123`, then select database `library`.

If you need to reset the database manually (or fix credential mismatch from an older setup):

```bash
docker compose down -v
docker compose up -d
```

Or apply schema and seed manually:

```bash
docker exec -i library_mysql mysql -uroot -prootpass123 library < schema.sql
docker exec -i library_mysql mysql -uroot -prootpass123 library < seed.sql
```

### 2. Install Python Dependencies

```bash
pip install fastapi uvicorn pymysql
```

Or:

```bash
pip install -r requirements.txt
```

### 3. Start the Server

```bash
uvicorn main:app --reload
```

The API runs at **http://localhost:8000**

## API Endpoints

### Authors
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/authors` | Get all authors |
| POST | `/authors` | Add a new author |

### Books
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/books` | Get all books |
| GET | `/books/{id}` | Get a book by ID |
| POST | `/books?title=&author_id=&year=` | Add a new book |
| PUT | `/books/{id}` | Update a book |
| DELETE | `/books/{id}` | Delete a book |

### Loans
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/loans` | Get all loans |
| POST | `/loans` | Create a new loan |
| PUT | `/loans/{id}/return` | Mark a book as returned |

Interactive API docs: **http://localhost:8000/docs**

## HTML Client

1. Make sure the FastAPI server is running (`uvicorn main:app --reload`)
2. Open `client/index.html` directly in your browser

The client:
- Loads all books on page load via `fetch("http://localhost:8000/books")`
- Provides a form to add books (title, author, year)
- Shows **Available** / **On Loan** status for each book
- Includes a **Delete** button for each book

## Seed Data

| Table | Count | Details |
|-------|-------|---------|
| Authors | 3 | Jane Austen, Gabriel García Márquez, Haruki Murakami |
| Books | 6 | At least 2 books per author |
| Loans | 3 | 2 active loans, 1 returned |

## Before You Submit

- [ ] MySQL Docker container is running (`docker compose ps`)
- [ ] Server starts without errors (`uvicorn main:app --reload`)
- [ ] Swagger UI works at http://localhost:8000/docs
- [ ] HTML client loads books from the API
- [ ] Include `screenshot.png` showing the working client

## Screenshot

See `screenshot.png` in the project root for a preview of the working client.
