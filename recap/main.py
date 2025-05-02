from flask import Flask, request, render_template, redirect
import requests

app = Flask(__name__)

SECRET_KEY = '6LfyISkrAAAAADG0qKVCoWF1vQzawIADYSiJmb6h'

@app.route('/')
def home():
    return open('index.html').read()

@app.route('/verify', methods=['POST'])
def verify():
    recaptcha_response = request.form['g-recaptcha-response']
    payload = {
        'secret': SECRET_KEY,
        'response': recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=payload)
    result = r.json()

    if result['success']:
        return render_template('success.html')  # ✅ Full HTML page shown
    else:
        return "<h2>CAPTCHA verification failed. Try again.</h2>"

if __name__ == "__main__":
    app.run(debug=True)
