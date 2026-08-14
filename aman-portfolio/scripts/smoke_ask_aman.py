"""Optional live Ask Aman smoke test.

This script is intentionally excluded from automated tests. It sends one real
request only when run manually with ``--live``.
"""

from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main() -> int:
    parser = argparse.ArgumentParser(description="Send one optional live Ask Aman request.")
    parser.add_argument("--live", action="store_true", help="Required acknowledgement before sending a request.")
    parser.add_argument("--url", default="http://127.0.0.1:8000/api/ask", help="Ask Aman endpoint URL.")
    parser.add_argument("--question", default="What AI skills does Aman use?", help="Question to send (maximum 300 characters).")
    args = parser.parse_args()

    if not args.live:
        print("No request sent. Re-run with --live to perform the optional smoke test.")
        return 0
    if len(args.question) > 300:
        print("Question must be 300 characters or fewer.", file=sys.stderr)
        return 2

    request = Request(
        args.url,
        data=json.dumps({"question": args.question, "history": []}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=20) as response:  # nosec B310 - URL is chosen explicitly by the operator
            print(response.read().decode("utf-8"))
            return 0
    except HTTPError as error:
        print(error.read().decode("utf-8", errors="replace"), file=sys.stderr)
        return 1
    except URLError as error:
        print(f"Smoke test could not reach the endpoint: {error.reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
