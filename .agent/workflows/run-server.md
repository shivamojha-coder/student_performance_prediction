# Run Server Workflow

## Steps to start the Student Performance Prediction Platform

### 1. Create virtual environment
```bash
python -m venv venv
```

### 2. Activate virtual environment
**Windows:**
```bash
venv\Scripts\activate
```
**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate synthetic dataset (optional - existing dataset used by default)
```bash
python generate_dataset.py
```

### 5. Train ML model
```bash
python train_model.py
```

### 6. Initialize database
```bash
python -c "from app import app, init_db; app.app_context().push(); init_db()"
```

### 7. Run Flask development server
```bash
python app.py
```

Server will be available at: **http://localhost:5000**

### Default Credentials
- **Admin:** admin@edupredict.com / admin123
- **Student:** Register via /register page
