# 🛡️ SecureMyAI - GenAI Prompt Firewall

A comprehensive **Streamlit + Python-based GenAI prompt firewall** that protects sensitive information before it reaches Large Language Models (LLMs). Built with security-first principles and designed for production use.
Live Demo: https://securemyai.onrender.com/

## 🎯 Features

### ✅ **Local Filtering & Redaction**
- **Regex-based PII Detection:** Automatically detects emails, phone numbers, SSNs, credit cards, IP addresses, and more
- **Keyword-based Filtering:** Identifies high-risk and medium-risk keywords
- **Smart Redaction:** Replaces sensitive patterns with `[REDACTED]` placeholders
- **Risk Classification:** Three-tier risk assessment (low/medium/high)

### ✅ **Multi-LLM Support**
- **Groq (Mixtral):** Fast, cost-effective inference
- **Google Gemini 2.5:** Advanced reasoning capabilities
- **Extensible Architecture:** Easy to add more LLM providers

### ✅ **Comprehensive Logging**
- **Audit Trail:** Complete logging of all prompt analyses
- **CSV & JSON Export:** Structured data for analysis
- **Statistics Dashboard:** Real-time metrics and insights
- **Search & Filter:** Advanced prompt history viewer

### ✅ **Admin Dashboard & RBAC**
- **Role-Based Access Control:** Secure admin authentication
- **User Management:** Create, delete, and manage admin users
- **Security Monitoring:** Real-time threat detection and metrics
- **System Administration:** Configuration and settings management
- **Audit Logs:** Comprehensive activity tracking and export

### ✅ **Production Ready**
- **Docker Support:** Fully containerized deployment
- **Docker Compose:** Easy local development and testing
- **Render Deployment:** One-click cloud deployment
- **Security Focused:** No sensitive data leaves your control
- **Scalable Architecture:** Built for enterprise use

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Firewall      │    │   LLM APIs      │
│   Frontend      │───▶│   Engine        │───▶│   (Groq/Gemini) │
│                 │    │                 │    │                 │
│ • Prompt Input  │    │ • PII Detection │    │ • Response      │
│ • Risk Display  │    │ • Redaction     │    │ • Processing    │
│ • History View  │    │ • Logging       │    │                 │
│ • Admin Panel   │    │ • Auth System   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Log Storage   │
                       │                 │
                       │ • CSV Files     │
                       │ • JSON Files    │
                       │ • Statistics    │
                       │ • Admin Config  │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ OR Docker
- API keys for Groq and/or Google Gemini

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/SecureMyAI.git
   cd SecureMyAI
   ```

2. **Set up environment variables**
   ```bash
   # Create .env file in the root directory
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Build and run with Docker Compose**
   ```bash
   # Build the image
   docker-compose build
   
   # Start the application
   docker-compose up -d
   ```

4. **Access the application**
   - Open http://localhost:8501
   - **Admin Login:** `admin` / `admin123`
   - Start analyzing prompts!

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/SecureMyAI.git
   cd SecureMyAI/backend
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run main_app.py
   ```

5. **Access the application**
   - Open http://localhost:8501
   - **Admin Login:** `admin` / `admin123`
   - Start analyzing prompts!

## 🐳 Docker Management

### Using Docker Compose (Recommended)

```bash
# Build the application
docker-compose build

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Restart the application
docker-compose restart

# Check status
docker-compose ps
```

### Using Management Scripts

**Linux/Mac:**
```bash
# Make script executable
chmod +x docker-commands.sh

# Use the script
./docker-commands.sh up      # Start application
./docker-commands.sh down    # Stop application
./docker-commands.sh logs    # View logs
./docker-commands.sh status  # Check status
```

**Windows:**
```cmd
# Use the batch script
docker-commands.bat up      # Start application
docker-commands.bat down    # Stop application
docker-commands.bat logs    # View logs
docker-commands.bat status  # Check status
```

### Manual Docker Commands

```bash
# Build image
docker build -t securemyai ./backend

# Run container
docker run -p 8501:8501 --env-file .env securemyai

# Run with volume mounts for persistence
docker run -p 8501:8501 \
  -v $(pwd)/backend/logs:/app/logs \
  -v $(pwd)/backend/admin_config.json:/app/admin_config.json \
  --env-file .env securemyai
```

## 🔐 Admin Features

### Default Admin Credentials
- **Username:** `admin`
- **Password:** `admin123`
- **Role:** `super_admin`

### Admin Dashboard Features
- **📊 System Overview:** Real-time metrics and charts
- **👥 User Management:** Create and manage admin users
- **🔒 Security Monitoring:** Track high-risk prompts and threats
- **📝 Audit Logs:** View and export activity logs
- **⚙️ System Settings:** Configuration management
- **❓ Help & Documentation:** Comprehensive guides

### User Management
- Create new admin users with different roles
- Delete existing users (except default admin)
- Change passwords securely
- Monitor user activity and login attempts

## 🌐 Cloud Deployment

### Render (Recommended)

1. **Fork this repository** to your GitHub account

2. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Create a new Web Service
   - Connect your GitHub repository

3. **Configure environment variables**
   - Add your API keys in Render's environment variables section
   - Set `GROQ_API_KEY` and/or `GOOGLE_API_KEY`

4. **Deploy**
   - Render will automatically detect the `render.yaml` configuration
   - Your app will be live at `https://your-app-name.onrender.com`

### Other Platforms

The application can be deployed to any platform that supports Docker:
- **Heroku:** Use Docker containers
- **Railway:** Similar to Render deployment
- **AWS/GCP/Azure:** Use Docker containers with managed services

## 📊 Usage Guide

### 1. **Prompt Analysis**
- Enter your prompt in the text area
- Select your preferred LLM (Groq or Gemini)
- Click "Analyze Prompt"
- View detailed security analysis and LLM response

### 2. **Security Features**
- **High Risk:** Prompts are completely blocked
- **Medium Risk:** Sensitive content is redacted before sending to LLM
- **Low Risk:** Prompts are sent directly to LLM

### 3. **Prompt History**
- Navigate to "Prompt History" in the sidebar
- View statistics and filter by risk level, model, or search terms
- Expand entries to see detailed analysis

### 4. **Admin Dashboard**
- Login with admin credentials
- Access comprehensive system monitoring
- Manage users and system settings
- Export audit logs for compliance

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# LLM API Keys
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Customize logging
LOG_DIR=logs
```

### Docker Environment Variables

The Docker setup automatically loads environment variables from:
- `.env` file in the root directory
- Docker Compose environment section
- Runtime environment variables

### Customizing Filters

Edit `backend/app/firewall/filters.py` to:
- Add new PII patterns
- Modify keyword lists
- Adjust risk thresholds

### Customizing Redaction

Edit `backend/app/firewall/redactor.py` to:
- Add new redaction patterns
- Modify placeholder text
- Change redaction logic

## 📈 Monitoring & Analytics

### Log Files
- **CSV Logs:** `backend/logs/prompt_log.csv`
- **JSON Logs:** `backend/logs/prompt_log.json`
- **Admin Config:** `backend/admin_config.json`

### Key Metrics
- Total prompts analyzed
- Risk level distribution
- Blocked vs. redacted prompts
- Processing times
- Model usage statistics
- Admin user activity

## 🔒 Security Features

### Data Protection
- **No Data Storage:** Sensitive data is never stored permanently
- **Local Processing:** All analysis happens on your infrastructure
- **Redaction:** Sensitive patterns are replaced before LLM calls
- **Audit Trail:** Complete logging for compliance

### Authentication & Authorization
- **Role-Based Access Control:** Secure admin authentication
- **Session Management:** Automatic timeout and validation
- **Account Lockout:** Protection against brute force attacks
- **Password Security:** SHA-256 hashing

### Risk Detection
- **PII Patterns:** Email, phone, SSN, credit card, IP address
- **Sensitive Keywords:** Password, API key, token, secret
- **Context Analysis:** Risk assessment based on content

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- **Streamlit** for the amazing web framework
- **Groq** for fast LLM inference
- **Google Gemini** for advanced AI capabilities
- **Render** for seamless deployment

## 📞 Support

- **Email:** ayushappatil@gmail.com

---
