from main import app


if __name__ == "__main__":
    # Run the same app object defined in main.py
    # This ensures local runs (python app.py / flask run) have all routes
    app.run(host="127.0.0.1", port=5000, debug=True)
