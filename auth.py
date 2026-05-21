def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    admin_password = "admin123"
    return query
