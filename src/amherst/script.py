import argparse
import base64
import webbrowser
from pathlib import Path

import uvicorn


def main():
    uvicorn.run('app:app', host="127.0.0.1", port=8000, log_level="info")
    argparser = argparse.ArgumentParser()
    argparser.add_argument("hire_name", type=str)
    args = argparser.parse_args()
    hire_name_encoded = base64.urlsafe_b64encode(args.hire_name.encode()).decode()
    adr = f"http://127.0.0.1:8000/hires/{hire_name_encoded}"
    webbrowser.open_new(adr)


if __name__ == "__main__":
    main()
