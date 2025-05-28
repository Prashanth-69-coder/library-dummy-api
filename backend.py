from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/signup")
def signup(username, password):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username, password))
    conn.commit()
    conn.close()
    return {"message": "User created successfully"}

@app.get("/login")
def login(username, password):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    if user:
        c.execute("UPDATE users SET is_flag = 1 WHERE username=? AND password=?", (username, password))
        conn.commit()
        conn.close()
        return {"message": "User logged in successfully"}
    return {"message": "Invalid username or password"}

@app.get("/logout")
def logout(username, password):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT is_flag FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    if user:
        if user[0] == 1:
            c.execute("UPDATE users SET is_flag = 0 WHERE username=? AND password=?", (username, password))
            conn.commit()
            conn.close()
            return {"message": "User logged out successfully"}
        else:
            return {"message": "User is not logged in"}
    return {"message": "Invalid username or password"}

@app.get("/users/books")
def books():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books")
    books = c.fetchall()
    conn.close()
    return books

@app.get("/book/borrow")
def book_borrow(user_id, book_id, count):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT is_flag FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    if user and user[0] == 1:
        if int(count) == 1:
            c.execute("SELECT copies FROM books WHERE id=?", (book_id,))
            copies = c.fetchone()
            if copies and copies[0] > 0:
                c.execute("UPDATE books SET copies = copies - 1 WHERE id=?", (book_id,))
                c.execute("SELECT books FROM users WHERE id=?", (user_id,))
                books = c.fetchone()
                current_books = books[0] if books and books[0] else ""
                new_books = f"{current_books}${book_id}" if current_books else f"${book_id}"
                c.execute("UPDATE users SET books = ? WHERE id=?", (new_books, user_id))
                conn.commit()
                conn.close()
                return {"message": "Book borrowed successfully"}
            return {"message": "No copies available"}
        return {"message": "We don't accept more than one copy"}
    return {"message": "User is not logged in or invalid user"}

@app.post("/book/submit")
def book_submit(user_id, book_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT is_flag FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    if user and user[0] == 1:
        c.execute("SELECT books FROM users WHERE id=?", (user_id,))
        books = c.fetchone()[0]
        if f"${book_id}" in books:
            updated_books = books.replace(f"${book_id}", "")
            c.execute("UPDATE books SET copies = copies + 1 WHERE id=?", (book_id,))
            c.execute("UPDATE users SET books = ? WHERE id=?", (updated_books, user_id))
            conn.commit()
            conn.close()
            return {"message": "Book returned successfully"}
        return {"message": "Book not found in user's library"}
    return {"message": "User is not logged in or invalid user"}

@app.get("/book/borrowed_details")
def borrowed_details(user_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT is_flag FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    if user and user[0] == 1:
        c.execute("SELECT books FROM users WHERE id=?", (user_id,))
        books_str = c.fetchone()[0]
        book_list = [b for b in books_str.split("$") if b]
        return {"borrowed_books": book_list, "total_borrowed": len(book_list)}
    return {"message": "User is not logged in or invalid user"}
