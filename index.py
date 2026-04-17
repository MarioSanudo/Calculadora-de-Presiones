from src import app_creation
app=app_creation()

if __name__=="__main__":
    app.run(debug=app.config["DEBUG"], use_reloader=False)
