from flask import Flask, render_template, request, jsonify, send_file
import razorpay
import PyPDF2
import os
import json
import uuid

app = Flask(__name__)

# Razorpay Keys
RAZORPAY_KEY_ID = "rzp_live_Suu4ZjuuZINyry"
RAZORPAY_KEY_SECRET = "pV6iNCGzwAIgy33sIxfyEb1I"

# Pricing
BW_PRICE = 1.5
COLOR_PRICE = 10

UPLOAD_FOLDER = 'uploads'
JOBS_FOLDER = 'print_jobs'
JOBS_FILE = 'jobs.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(JOBS_FOLDER, exist_ok=True)

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

def load_jobs():
    if os.path.exists(JOBS_FILE):
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_jobs(jobs):
    with open(JOBS_FILE, 'w') as f:
        json.dump(jobs, f)

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
    amount = int(data['amount'] * 100)
    order = client.order.create({'amount': amount, 'currency': 'INR', 'payment_capture': 1})
    return jsonify(order)

@app.route('/save_print_job', methods=['POST'])
def save_print_job():
    file = request.files['pdf']
    copies = request.form.get('copies', 1)
    print_type = request.form.get('print_type', 'bw')
    payment_id = request.form.get('payment_id', '')

    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = os.path.join(JOBS_FOLDER, filename)
    file.save(filepath)

    jobs = load_jobs()
    job = {
        'id': str(uuid.uuid4()),
        'filename': filename,
        'copies': copies,
        'print_type': print_type,
        'payment_id': payment_id,
        'status': 'pending'
    }
    jobs.append(job)
    save_jobs(jobs)

    return jsonify({'status': 'saved', 'job_id': job['id']})

@app.route('/get_print_jobs', methods=['GET'])
def get_print_jobs():
    jobs = load_jobs()
    pending = [j for j in jobs if j['status'] == 'pending']
    return jsonify({'jobs': pending})

@app.route('/download_pdf/<job_id>', methods=['GET'])
def download_pdf(job_id):
    jobs = load_jobs()
    job = next((j for j in jobs if j['id'] == job_id), None)
    if job:
        filepath = os.path.join(JOBS_FOLDER, job['filename'])
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'not found'}), 404

@app.route('/mark_printed/<job_id>', methods=['POST'])
def mark_printed(job_id):
    jobs = load_jobs()
    for job in jobs:
        if job['id'] == job_id:
            job['status'] = 'printed'
    save_jobs(jobs)
    return jsonify({'status': 'updated'})

if __name__ == '__main__':
    app.run(debug=True)