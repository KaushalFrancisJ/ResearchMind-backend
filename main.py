import time
import uvicorn


def main():
    while True:
        try:
            uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, reload_delay=1.0)
        except Exception as e:
            print(f"Server crashed: {e}. Retrying in 2s...")
            time.sleep(2)


if __name__ == "__main__":
    main()
