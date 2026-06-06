import streamlit as st
import sqlite3
import random
import string

# ==========================
# DATABASE SETUP
# ==========================
conn = sqlite3.connect("passwords.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    website TEXT NOT NULL,
    username TEXT,
    password TEXT NOT NULL
)
""")
conn.commit()

# ==========================
# PASSWORD GENERATOR
# ==========================
def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return ''.join(random.choice(chars) for _ in range(length))

# ==========================
# PASSWORD STRENGTH CHECKER
# ==========================
def password_strength(password):
    score = 0

    if len(password) >= 8:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()" for c in password):
        score += 1

    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    else:
        return "Strong"

# ==========================
# UI
# ==========================
st.set_page_config(
    page_title="Password Manager",
    page_icon="🔐",
    layout="centered"
)

st.title("🔐 Password Manager")
st.write("Generate and store your passwords securely.")

menu = st.sidebar.selectbox(
    "Select Option",
    ["Generate Password", "Save Password", "View Passwords"]
)

# ==========================
# GENERATE PASSWORD
# ==========================
if menu == "Generate Password":

    st.subheader("Generate Password")

    length = st.slider(
        "Password Length",
        min_value=8,
        max_value=32,
        value=12
    )

    if st.button("Generate"):
        pwd = generate_password(length)

        st.success("Password Generated Successfully")
        st.code(pwd)

        strength = password_strength(pwd)

        if strength == "Weak":
            st.error(f"Strength: {strength}")
        elif strength == "Medium":
            st.warning(f"Strength: {strength}")
        else:
            st.success(f"Strength: {strength}")

# ==========================
# SAVE PASSWORD
# ==========================
elif menu == "Save Password":

    st.subheader("Save Password")

    website = st.text_input("Website")

    username = st.text_input("Username / Email")

    password = st.text_input(
        "Password",
        type="password"
    )

    if password:
        strength = password_strength(password)
        st.info(f"Password Strength: {strength}")

    if st.button("Save Password"):

        if website and password:

            cursor.execute(
                """
                INSERT INTO passwords
                (website, username, password)
                VALUES (?, ?, ?)
                """,
                (website, username, password)
            )

            conn.commit()

            st.success("Password Saved Successfully!")

        else:
            st.error("Website and Password are required.")

# ==========================
# VIEW PASSWORDS
# ==========================
elif menu == "View Passwords":

    st.subheader("Saved Passwords")

    cursor.execute(
        "SELECT id, website, username, password FROM passwords"
    )

    data = cursor.fetchall()

    if data:

        for row in data:

            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(f"🌐 Website: {row[1]}")
                st.write(f"👤 Username: {row[2]}")
                st.code(row[3])

            with col2:

                if st.button(
                    "Delete",
                    key=row[0]
                ):
                    cursor.execute(
                        "DELETE FROM passwords WHERE id=?",
                        (row[0],)
                    )
                    conn.commit()
                    st.rerun()

            st.divider()

    else:
        st.info("No passwords saved yet.")