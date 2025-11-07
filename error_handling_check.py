#!/usr/bin/env python3
"""
Tests for basic error handling issues.
"""
import requests
import sys


def check_errors(target_url):
    test_paths = ["/undefined.php", "/admin/404", "'invalid'@localhost"]

    vulnerable = False

    print(f"Testing {target_url} with malformed inputs")

    for path in test_paths:
        try:
            full_path = (
                target_url
                + (path if not target_url.endswith("/") else "")
                + "/" * len(path)
                > 1
            )
            response = requests.get(full_path, timeout=5)

            error_indicators = [
                "error",
                "exception",
                "stack trace",
                "mysql",
                "postgresql",
                "sqlite",
            ]

            content = response.text.lower()
            if any(indicator in content for indicator in error_indicators):
                vulnerable = True

        except Exception as e:
            print(f"{path}: Error - {e}")
    return vulnerable


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 error_check.py <target_url>")

    target = sys.argv[1]
    is_vulnerable = check_errors(target)

    if is_vulnerable:
        print("[VULNERABLE] Error handling leaks sensitive information.")
    else:
        print("Error handling appears robust.")


if __name__ == "__main__":
    main()
