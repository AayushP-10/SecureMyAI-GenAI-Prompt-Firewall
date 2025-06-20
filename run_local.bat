@echo off
echo 🛡️ Starting SecureMyAI Locally...
echo ================================

cd backend

echo 📦 Installing dependencies...
pip install -r requirements.txt

echo 🚀 Starting Streamlit application...
echo.
echo 🌐 Application will be available at: http://localhost:8501
echo 🔐 Admin Login: admin / admin123
echo.
echo Press Ctrl+C to stop the application
echo.

python -m streamlit run main_app.py --server.port 8501 