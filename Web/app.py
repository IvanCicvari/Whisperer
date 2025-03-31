from flask import Flask, render_template
from pathlib import Path
from routes import register_blueprints  

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "Web/data/uploads"
app.config["OUTPUT_FOLDER"] = "Web/data/output"
app.config["TEMP_FOLDER"] = "Web/data/temp"


register_blueprints(app)  

# === Serve HTML frontend ===
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
