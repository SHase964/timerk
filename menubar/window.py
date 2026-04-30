import sys

import webview

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python window.py <url> [title] [width] [height]")
        sys.exit(1)

    url = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else "timerk"
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 640
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 540

    webview.create_window(title, url, width=width, height=height)
    webview.start()
