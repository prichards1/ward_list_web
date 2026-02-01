from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Ward List Quiz - Web Edition</h1><p>Server is running!</p>"

if __name__ == '__main__':
    app.run(debug=True)