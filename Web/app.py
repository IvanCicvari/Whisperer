from flask import Flask, render_template
from routes import register_blueprints

app = Flask(__name__)  # ✅ Make sure this is defined before any blueprint imports

app.config["UPLOAD_FOLDER"] = "Web/data/uploads"
app.config["OUTPUT_FOLDER"] = "Web/data/output"
app.config["TEMP_FOLDER"] = "Web/data/temp"

register_blueprints(app)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
