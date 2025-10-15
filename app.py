from flask import Flask, render_template, request, jsonify
import PyPDF2
import re
import os
from werkzeug.utils import secure_filename
import json
import traceback

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

class CreditCardParser:
    """Parser to extract key data points from credit card statements"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text = ""
        self.extracted_data = {}
        
    def extract_text_from_pdf(self) -> str:
        """Extract all text content from the PDF"""
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                self.text = text
                return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def extract_account_number(self):
        """Extract credit card account number (last 4 digits)"""
        patterns = [
            # Kotak format: XXXX-XXXX-XXXX-2827
            r'Account\s+Number[\s:]+[X\-]+(\d{4})',
            r'Account[\s:]+[X\-]+(\d{4})',
            # General patterns
            r'(?:Account|Card)\s*(?:Number|No\.?)[\s:]*[X*]{12}(\d{4})',
            r'[X*]{12}(\d{4})',
            r'ending\s+in\s+(\d{4})',
            r'xxxx\s*xxxx\s*xxxx\s*(\d{4})',
            r'Card\s+ending\s+(\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def extract_statement_date(self):
        """Extract statement date or billing cycle"""
        patterns = [
            # Kotak format: "02 Sep 2025 - 01 Oct 2025" - extract the end date
            r'Statement\s+Period[\s:]+\d{1,2}\s+\w+\s+\d{4}\s*-\s*(\d{1,2}\s+\w+\s+\d{4})',
            # General patterns
            r'Statement\s+Date[\s:]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Billing\s+(?:Cycle|Period)[\s:]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Statement\s+Period[\s:]+.*?to\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Closing\s+Date[\s:]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def extract_total_balance(self):
        """Extract total balance or amount due"""
        patterns = [
            # Kotak format: "Total Due: n8,450.75" or "New Balance n8,450.75"
            r'(?:Total\s+Due|New\s+Balance|Total\s+Outstanding)[\s:]+n\s*([\d,]+\.\d{2})',
            # General patterns with various currency symbols
            r'(?:Total\s+Balance|New\s+Balance|Current\s+Balance)[\s:]+[\$₹n]?\s*([\d,]+\.\d{2})',
            r'Amount\s+Due[\s:]+[\$₹n]?\s*([\d,]+\.\d{2})',
            r'Outstanding\s+Balance[\s:]+[\$₹n]?\s*([\d,]+\.\d{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                return float(amount)
        return None
    
    def extract_payment_due_date(self):
        """Extract payment due date"""
        patterns = [
            # Kotak format: "Payment Due Date\n16 Oct 2025" (newline between label and date)
            r'Payment\s+Due\s+Date[\s\n]+(\d{1,2}\s+\w+\s+\d{4})',
            # General patterns
            r'Due\s+Date[\s:]+(\d{1,2}\s+\w+\s+\d{4})',
            r'Payment\s+Due\s+Date[\s:]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Due\s+Date[\s:]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'Pay\s+by[\s:]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def extract_minimum_payment(self):
        """Extract minimum payment amount"""
        patterns = [
            # Kotak format: "Minimum Due: n1,200.00"
            r'Minimum\s+Due[\s:]+n\s*([\d,]+\.\d{2})',
            # General patterns
            r'Minimum\s+(?:Payment|Due)[\s:]+[\$₹n]?\s*([\d,]+\.\d{2})',
            r'Minimum\s+Amount\s+Due[\s:]+[\$₹n]?\s*([\d,]+\.\d{2})',
            r'Min\.\s+Payment[\s:]+[\$₹n]?\s*([\d,]+\.\d{2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                return float(amount)
        return None
    
    def parse(self):
        """Main parsing method - extracts all 5 key data points"""
        self.extract_text_from_pdf()
        
        self.extracted_data = {
            "account_last_4_digits": self.extract_account_number(),
            "statement_date": self.extract_statement_date(),
            "total_balance": self.extract_total_balance(),
            "payment_due_date": self.extract_payment_due_date(),
            "minimum_payment": self.extract_minimum_payment()
        }
        
        return self.extracted_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type
        if not (file and allowed_file(file.filename)):
            return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        print(f"📁 Saving file to: {filepath}")
        file.save(filepath)
        print(f"✅ File saved successfully!")
        
        # Parse the PDF
        print(f"🔍 Starting to parse PDF...")
        parser = CreditCardParser(filepath)
        results = parser.parse()
        
        print(f"📊 Extraction Results:")
        print(f"   Account: {results['account_last_4_digits']}")
        print(f"   Statement Date: {results['statement_date']}")
        print(f"   Balance: {results['total_balance']}")
        print(f"   Due Date: {results['payment_due_date']}")
        print(f"   Min Payment: {results['minimum_payment']}")
        
        # Clean up the uploaded file
        os.remove(filepath)
        print(f"🗑️ Cleaned up temporary file")
        
        return jsonify({
            'success': True,
            'data': results,
            'filename': filename
        })
    
    except Exception as e:
        # Print full error traceback
        print(f"❌ ERROR OCCURRED:")
        print(traceback.format_exc())
        
        # Clean up on error
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)