import requests

def get_session_cookie(username, password):
    """
    Logs in to the application and returns the session cookie.
    """
    login_url = "http://localhost:8000/login/auth"
    session = requests.Session()
    response = session.post(login_url, json={"username": username, "password": password})
    if response.status_code == 200:
        return session.cookies.get_dict()
    else:
        raise Exception(f"Login failed with status code {response.status_code}")
