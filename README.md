# polyresearch

## Backend Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit the `.env` file and add your Gemini API key:
```
GEMINI_API_KEY=your_actual_api_key_here
```

5. Run the development server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`. You can view the interactive API documentation at `http://localhost:8000/docs`.