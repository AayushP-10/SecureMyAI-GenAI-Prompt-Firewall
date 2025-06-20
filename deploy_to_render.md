# 🚀 Quick Deploy to Render (5 Minutes)

## **Step 1: Push to GitHub**
```bash
git add .
git commit -m "Complete SecureMyAI with admin dashboard"
git push origin main
```

## **Step 2: Deploy on Render**
1. Go to [render.com](https://render.com) and sign up
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Fill in these settings:
   - **Name**: `securemyai`
   - **Environment**: `Python`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && streamlit run main_app.py --server.port $PORT --server.address 0.0.0.0`
   - **Plan**: `Free`

## **Step 3: Add API Keys**
In the **Environment** tab, add:
- `GROQ_API_KEY` = Your Groq API key
- `GOOGLE_API_KEY` = Your Google API key

## **Step 4: Deploy**
Click **"Create Web Service"** and wait 5-10 minutes.

## **Step 5: Get Your URL**
Your app will be live at: `https://securemyai.onrender.com`

## **Step 6: Test**
- Admin Login: `admin` / `admin123`
- Test prompt analysis
- Check admin dashboard

## **Step 7: Add to Resume**
```
SecureMyAI - GenAI Prompt Firewall
Live Demo: https://securemyai.onrender.com
```

**That's it! Your project is now public! 🎉** 