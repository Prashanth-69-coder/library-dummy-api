from fastapi import FastAPI
import sqlite3

app = FastAPI()

@app.post("/signup")
def signup(username,password):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?,?)", (username,password))
    conn.commit()
    conn.close()
    return {"message": "User created successfully"}

@app.get("/login")
def login(username,password):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
    user = c.fetchone()
    if user:
        c.execute("UPDATE users SET is_flag = 1 WHERE username=? AND password=?", (username, password))
        conn.commit()
        conn.close()
        return {"message": "User logged in successfully"}
    else:
        return {"message": "Invalid username or password"}
    
@app.get("/logout")
def logout(username,password):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT is_flag FROM users WHERE username=? AND password=?", (username,password))
    user = c.fetchone()
    if user:
        if user[0] == 1:
            c.execute("UPDATE users SET is_flag = 0 WHERE username=? AND password=?", (username,password))
            conn.commit()
            conn.close()
            return {"message": "User logged out successfully"}
        else:
            conn.close()
            return {"message": "User is not logged in"}
    else:
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
    if user:
        if user[0] == 1:
            if int(count) == 1:
                c.execute("SELECT copies FROM books WHERE id=?", (book_id,))
                copies = c.fetchone()
                if copies and copies[0] > 0:
                    c.execute("UPDATE books SET copies = copies - 1 WHERE id=?", (book_id,))
                    c.execute("SELECT books FROM users WHERE id=?", (user_id,))
                    books = c.fetchone()
                    current_books = books[0] if books and books[0] else ""
                    if current_books == "":
                        new_books = "$" + str(book_id)
                    else:
                        new_books = current_books + "$" + str(book_id)
                    c.execute("UPDATE users SET books = ? WHERE id=?", (new_books, user_id))
                    conn.commit()
                    conn.close()
                    return {"message": "Book borrowed successfully"}
                else:
                    return {"message": "No copies available"}
            else:
                return {"message": "We don't accept more than one copy"}
        else:
            return {"message": "User is not logged in"}
    else:
        return {"message": "Invalid user id"}

    
                        
@app.post("/book/submit")
def book_submit(user_id, book_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT is_flag FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    if user:
        if user[0] == 1:
            c.execute("SELECT books FROM users WHERE id=?", (user_id,))
            books = c.fetchone()
            books_str = books[0] if books and books[0] else ""
            if f"${book_id}" in books_str:
                updated_books = books_str.replace(f"${book_id}", "")
                c.execute("UPDATE books SET copies = copies + 1 WHERE id=?", (book_id,))
                c.execute("UPDATE users SET books = ? WHERE id=?", (updated_books, user_id))
                conn.commit()
                conn.close()
                return {"message": "Book returned successfully"}
            else:
                conn.close()
                return {"message": "Book not found in user's library"}
        else:
            conn.close()
            return {"message": "User is not logged in"}
    else:
        conn.close()
        return {"message": "Invalid user id"}


@app.get("/book/borrowed_details")
def borrowed_details(user_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("SELECT is_flag FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    if user:
        if user[0] == 1:
            c.execute("SELECT books FROM users WHERE id=?", (user_id,))
            books = c.fetchone()
            l = []
            count = 0
            if books[0]!= "":
                books_str = books[0]
                books_list = books_str.split("$")
                for book in books_list:
                    if book.strip() != "":
                        count += 1
                        l.append(book)
                return {"borrowed_books": l, "total_borrowed": count}
            else:
                return {"borrowed_books": 0}
        else:
            return {"message": "User is not logged in"}
    else:
        return {"message": "Invalid user id"}