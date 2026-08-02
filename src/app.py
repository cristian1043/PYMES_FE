from src import create_app

app = create_app('development')

if __name__ == '__main__':
    print("frontend corriendo en http://localhost:5001")
    app.run (debug=True, port=5001)
    
