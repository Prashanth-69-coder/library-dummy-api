import streamlit as st
import requests

BASE_URL = "http://localhost:8000"  

def signup(username, password):
    response = requests.post(f"{BASE_URL}/signup", params={"username": username, "password": password})
    return response.json()

def login(username, password):
    response = requests.get(f"{BASE_URL}/login", params={"username": username, "password": password})
    return response.json()

def logout(username, password):
    response = requests.get(f"{BASE_URL}/logout", params={"username": username, "password": password})
    return response.json()

def get_books():
    response = requests.get(f"{BASE_URL}/users/books")
    return response.json()

def borrow_book(user_id, book_id, count=1):
    response = requests.get(f"{BASE_URL}/book/borrow", params={"user_id": user_id, "book_id": book_id, "count": count})
    return response.json()

def submit_book(user_id, book_id):
    response = requests.post(f"{BASE_URL}/book/submit", params={"user_id": user_id, "book_id": book_id})
    return response.json()

def borrowed_details(user_id):
    response = requests.get(f"{BASE_URL}/book/borrowed_details", params={"user_id": user_id})
    return response.json()

# --- Streamlit UI ---

st.title("Library Management System")

menu = ["Sign Up", "Login", "View Books", "Borrow Book", "Return Book", "Borrowed Details", "Logout"]
choice = st.sidebar.selectbox("Menu", menu)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = {}

if choice == "Sign Up":
    st.subheader("Create a new user")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Sign Up"):
        result = signup(username, password)
        st.success(result.get("message", "Error"))

elif choice == "Login":
    st.subheader("Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type='password', key="login_pass")
    if st.button("Login"):
        result = login(username, password)
        if result.get("message") == "User logged in successfully":
            st.session_state.logged_in = True
            st.session_state.user = {"username": username, "password": password}
            st.success("Logged in!")
        else:
            st.error(result.get("message"))

elif choice == "Logout":
    st.subheader("Logout")

    username = st.text_input("Username for logout")
    password = st.text_input("Password for logout", type='password')

    if st.button("Logout"):
        if username and password:
            result = logout(username, password)
            if "successfully" in result.get("message", ""):
                st.session_state.logged_in = False
                st.session_state.user = {}
                st.success(result.get("message"))
            else:
                st.error(result.get("message"))
        else:
            st.warning("Please enter username and password to logout.")


elif choice == "View Books":
    st.subheader("Available Books")
    books = get_books()
    if books:
        for book in books:
            st.write(f"ID: {book[0]}, Title: {book[1]}, Copies: {book[2]}")
    else:
        st.write("No books available.")

elif choice == "Borrow Book":
    if st.session_state.logged_in:
        st.subheader("Borrow a Book")
        user_id = st.number_input("Enter your user ID", min_value=1)
        book_id = st.number_input("Enter Book ID to borrow", min_value=1)
        count = st.number_input("Count (only 1 accepted)", value=1, min_value=1, max_value=1)
        if st.button("Borrow"):
            result = borrow_book(user_id, book_id, count)
            if "successfully" in result.get("message", ""):
                st.success(result.get("message"))
            else:
                st.error(result.get("message"))
    else:
        st.info("Please login to borrow books.")

elif choice == "Return Book":
    if st.session_state.logged_in:
        st.subheader("Return a Book")
        user_id = st.number_input("Enter your user ID", min_value=1, key="return_user_id")
        book_id = st.number_input("Enter Book ID to return", min_value=1, key="return_book_id")
        if st.button("Return"):
            result = submit_book(user_id, book_id)
            if "successfully" in result.get("message", ""):
                st.success(result.get("message"))
            else:
                st.error(result.get("message"))
    else:
        st.info("Please login to return books.")

elif choice == "Borrowed Details":
    if st.session_state.logged_in:
        st.subheader("Borrowed Books Details")
        user_id = st.number_input("Enter your user ID", min_value=1, key="details_user_id")
        if st.button("Show Details"):
            result = borrowed_details(user_id)
            if "borrowed_books" in result:
                st.write(f"Total Borrowed: {result.get('total_borrowed', 0)}")
                st.write("Books:", result.get("borrowed_books", []))
            else:
                st.error(result.get("message"))
    else:
        st.info("Please login to view borrowed books.")
