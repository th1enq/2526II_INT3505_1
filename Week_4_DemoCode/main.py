from app import create_app

app = create_app()

if __name__ == "__main__":
    print("Swagger UI available at: http://127.0.0.1:5001/docs/")
    app.run(debug=True, host="0.0.0.0", port=5001)
