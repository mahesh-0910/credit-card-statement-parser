# 💳 Credit Card Statement Parser

A Flask web application that extracts key information from credit card statement PDFs using PyPDF2 and regex patterns.

## 🌟 Features

- 📄 **PDF Upload**: Drag & drop or browse to upload credit card statements
- 🔍 **Smart Extraction**: Automatically extracts 5 key data points:
  - Account Number (last 4 digits)
  - Statement Date
  - Total Balance/Amount Due
  - Payment Due Date
  - Minimum Payment Amount
- 🎨 **Beautiful UI**: Modern, responsive interface with purple gradient design
- ⚡ **Real-time Processing**: Instant results display
- 🔒 **Secure**: Files are processed and immediately deleted

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/credit-card-parser.git
   cd credit-card-parser
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
credit-card-parser/
├── app.py              # Flask application & PDF parser
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Frontend interface
├── uploads/           # Temporary upload folder (auto-created)
└── README.md          # This file
```

## 🛠️ Technologies Used

- **Backend**: Flask 3.0.0
- **PDF Processing**: PyPDF2 3.0.1
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Security**: Werkzeug 3.0.1


## 🔧 Configuration

### File Upload Limits
- Maximum file size: 16MB
- Allowed file types: PDF only

### Regex Patterns
The parser uses flexible regex patterns to extract data. To support additional statement formats, modify the patterns in `app.py`:
- `extract_account_number()`
- `extract_statement_date()`
- `extract_total_balance()`
- `extract_payment_due_date()`
- `extract_minimum_payment()`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author
**Mahesh Kumawat**

##  Acknowledgments

- Thanks to the Flask and PyPDF2 communities
- Inspired by the need to automate financial data extraction

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

⭐ If you find this project useful, please consider giving it a star!
