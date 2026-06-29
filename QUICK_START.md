# ⚡ CogniData Quick Start Guide

Get up and running in 5 minutes!

---

## 🚀 One-Line Install & Run

```bash
git clone https://github.com/shivakumar0001/Cognidata_mainfinal.git && cd Cognidata_mainfinal/cognidata && powershell -ExecutionPolicy Bypass -File run.ps1
```

**That's it!** The script will:
1. Install backend dependencies
2. Install frontend dependencies  
3. Start backend on port 8000
4. Start frontend on port 5173
5. Open browser to http://localhost:5173

---

## 📋 Prerequisites

- ✅ Python 3.10+
- ✅ Node.js 18+
- ✅ Git

**Check versions:**
```bash
python --version  # Should be 3.10+
node --version    # Should be 18+
git --version     # Any recent version
```

---

## 🔑 First Login

```
URL: http://localhost:5173
Email: admin@cognidata.com
Password: admin123
```

**⚠️ Change password after first login!**

---

## 📤 Upload Your First Dataset

1. Click **Upload** in sidebar
2. Drag & drop your CSV/Excel/JSON file
3. Wait for upload (shows row/column count)
4. See preview in tabs below

**Supported:**
- CSV files (any encoding)
- Excel (.xlsx, .xls)
- JSON files
- Up to 200MB per file
- Multiple files at once

---

## 🤖 Ask AI Your First Question

1. Click **AI Analyst** in sidebar
2. Type: `"Show me a summary of the data"`
3. Get AI-generated insights in seconds

**Try asking:**
- "What are the key trends?"
- "Show me correlations"
- "Find any anomalies"
- "Create a sales forecast"
- "Cluster the customers"

---

## 📊 Generate Visualizations

1. Click **Dashboard** in sidebar
2. Auto-generated charts appear
3. Click any chart to expand
4. Change chart types with dropdown

**Available charts:**
- Bar, Line, Scatter, Pie
- Heatmap, Box, Violin
- Area, Polar, Radar
- And 6 more types!

---

## 🗺️ Create a Map

1. Upload dataset with location columns
2. Click **Maps** in sidebar
3. Choose map type:
   - Points map
   - Heatmap
   - Choropleth
   - 3D Globe

**Column names should include:**
- `latitude`, `lat`, `y`
- `longitude`, `lon`, `lng`, `x`

---

## 🔬 Run AutoML

1. Click **AutoML** in sidebar
2. Select target column
3. Choose task type (Classification/Regression)
4. Click **Train Model**
5. Get accuracy and feature importance

**Models included:**
- Random Forest
- Gradient Boosting
- Logistic Regression
- Support Vector Machine

---

## 📊 Advanced Analytics

**Clustering:**
1. Click **Advanced Analytics**
2. Go to Clustering tab
3. Set number of clusters
4. Click **Run Clustering**

**Time Series:**
1. Go to Time Series tab
2. Select date column
3. Get trends and forecasts

**Anomaly Detection:**
1. Go to Anomaly tab
2. Click **Detect Anomalies**
3. See outliers highlighted

---

## 👥 Create Workspace

1. Click **Workspaces** in sidebar
2. Click **+ New Workspace**
3. Enter name & description
4. Invite team members
5. Collaborate on datasets

---

## 📄 Generate Report

1. Click **Reports** in sidebar
2. Select charts to include
3. Add title and description
4. Click **Generate PDF**
5. Download branded report

---

## ⚙️ Configure API Key

For full AI features:

1. Get OpenAI API key from https://platform.openai.com
2. Create `cognidata/backend/.env`:
   ```env
   OPENAI_API_KEY=sk-your-key-here
   ```
3. Restart backend

---

## 🔧 Common Commands

**Start application:**
```bash
powershell -ExecutionPolicy Bypass -File cognidata/run.ps1
```

**Backend only:**
```bash
cd cognidata/backend
uvicorn app.main:app --reload
```

**Frontend only:**
```bash
cd cognidata/frontend
npm run dev
```

**Run tests:**
```bash
cd cognidata/backend
pytest -v
```

**Verify setup:**
```bash
powershell -ExecutionPolicy Bypass -File verify_setup.ps1
```

---

## 🆘 Quick Troubleshooting

**Upload fails?**
- Check file format (CSV/Excel/JSON only)
- Check file size (max 200MB)
- Check browser console (F12) for errors

**Backend won't start?**
```bash
cd cognidata/backend
pip install -r requirements.txt
```

**Frontend won't start?**
```bash
cd cognidata/frontend
npm install
```

**Port already in use?**
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <number> /F

# Kill process on port 5173
netstat -ano | findstr :5173
taskkill /PID <number> /F
```

**Can't log in?**
```bash
# Reset database
cd cognidata/backend
del cognidata.db
python -m app.seed
# Login: admin@cognidata.com / admin123
```

---

## 📚 Full Documentation

- **README.md** - Complete guide
- **FIXES_APPLIED.md** - Recent fixes
- **TROUBLESHOOTING.md** - Detailed troubleshooting
- **DEPLOYMENT_SUMMARY.md** - Deployment info
- **API Docs** - http://localhost:8000/docs

---

## 🎯 Feature Checklist

Try these features:

- [ ] Upload a dataset
- [ ] Ask AI a question
- [ ] Generate visualizations
- [ ] Create a map
- [ ] Run clustering
- [ ] Train ML model
- [ ] Create workspace
- [ ] Generate PDF report
- [ ] Set up 2FA
- [ ] Create alert
- [ ] Use SQL Agent
- [ ] Build RAG knowledge base

---

## 🌐 URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Health Check | http://localhost:8000/health |

---

## 🔐 Security Checklist

- [ ] Change default password
- [ ] Set strong SECRET_KEY in .env
- [ ] Add OPENAI_API_KEY to .env
- [ ] Never commit .env to git
- [ ] Enable 2FA for admin account
- [ ] Use HTTPS in production
- [ ] Set up firewall rules
- [ ] Regular database backups

---

## 💡 Pro Tips

1. **Multiple datasets**: Upload multiple files, switch between them
2. **Keyboard shortcuts**: Ctrl+K for quick search (if implemented)
3. **Export charts**: Right-click chart → Save as PNG
4. **Custom SQL**: Use SQL Agent for complex queries
5. **Batch upload**: Select multiple files at once
6. **Theme**: Toggle dark/light mode in Settings
7. **Streaming**: AI responses stream in real-time
8. **Memory**: AI remembers conversation context

---

## 📊 Example Datasets

Try with these sample datasets:

**Sales Data:**
```csv
date,region,product,revenue,quantity
2024-01-01,North,Widget,1000,50
2024-01-02,South,Gadget,1500,75
```

**Location Data:**
```csv
name,latitude,longitude,value
Store A,40.7128,-74.0060,100
Store B,34.0522,-118.2437,150
```

**Time Series:**
```csv
date,value
2024-01-01,100
2024-01-02,105
2024-01-03,110
```

---

## 🎓 Learning Path

1. **Day 1**: Upload data, explore dashboard
2. **Day 2**: Ask AI questions, generate charts
3. **Day 3**: Try maps and geospatial features
4. **Day 4**: Run ML models and clustering
5. **Day 5**: Create workspace, invite team
6. **Week 2**: Build custom reports and alerts
7. **Week 3**: Use API, build integrations

---

## 🚀 Deploy to Production

**Quick deploy with Docker:**
```bash
# Coming soon - Docker Compose setup
docker-compose up -d
```

**Cloud platforms:**
- AWS: EC2 + RDS + S3
- Azure: App Service + Azure SQL
- GCP: Cloud Run + Cloud SQL

See **DEPLOYMENT_SUMMARY.md** for details.

---

## 📞 Get Help

1. Check **TROUBLESHOOTING.md**
2. Search GitHub Issues
3. Check API docs
4. Ask in Discussions
5. Open new Issue with details

---

## ⭐ Key Features

- 🔐 Secure authentication (JWT, OAuth, 2FA)
- 📤 Smart dataset upload (CSV, Excel, JSON)
- 🤖 AI-powered analysis (GPT-4)
- 📊 16 chart types
- 🗺️ Interactive maps
- 🔬 AutoML & explainability
- 👥 Team workspaces
- 📄 PDF reports
- 🔔 Alerts & monitoring
- 💻 Developer API

---

**Repository**: https://github.com/shivakumar0001/Cognidata_mainfinal

**Status**: ✅ Production Ready

**Get started now!** ⚡

---

*Happy analyzing! 🎉*
