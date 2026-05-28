from flask import Flask, render_template, request, jsonify
import razorpay
import PyPDF2
import os

app = Flask(__name__)

# Razorpay Keys
RAZORPAY_KEY_ID = "rzp_live_Suu4ZjuuZINyry"
RAZORPAY_KEY_SECRET = "pV6iNCGzwAIgy33sIxfyEb1I"

# Pricing
BW_PRICE = 1.5   # ₹1.5 per page black & white
COLOR_PRICE = 10  # ₹10 per page colour

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_page_count', methods=['POST'])
def get_page_count():
    file = request.files['pdf']
    reader = PyPDF2.PdfReader(file)
    pages = len(reader.pages)
    return jsonify({'pages': pages})

@app.route('/create_order', methods=['POST'])
def create_order():
    data = request.json
    amount = int(data['amount'] * 100)  # Razorpay needs paise
    order = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': 1})
    return jsonify(order)

@app.route('/print_file', methods=['POST'])
def print_file():
    file = request.files['pdf']
    copies = int(request.form.get('copies', 1))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    os.startfile(filepath, 'print')
    return jsonify({'status': 'printing'})

if __name__ == '__main__':
    app.run(debug=True)