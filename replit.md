# Engineering-and-Design

## Project Overview
A collection of Data Science and AI tools for engineering and design applications, centered on DCC (Document Control Center) management.

## Main Application
**Excel Explorer Pro** — A client-side web app for loading and analyzing Excel datasets with features including:
- Multi-level grouping and dynamic charting (Chart.js)
- AI-driven data insights (Google Gemini, OpenAI, DeepSeek)
- Excel import/export via SheetJS (xlsx.js)
- DCC register tracking (Submittals, RFIs)

## Tech Stack
- **Frontend:** Vanilla HTML/CSS/JavaScript (single-file app)
- **Backend/Processing:** Python 3, pandas, openpyxl, Jupyter Notebooks
- **CDN Libraries:** SheetJS, Chart.js, Google Fonts

## Project Layout
```
/
├── serve.py              # Python HTTP server entry point
├── dcc/                  # Main application directory
│   ├── Excel Explorer Pro working.html  # Main web app
│   ├── data/             # Sample Excel datasets
│   ├── publish/          # Release-ready versions
│   ├── dcc_mdl.py        # Python data processing script
│   └── *.ipynb           # Jupyter notebooks
└── README.md
```

## Running the App
- **Workflow:** "Start application" runs `python3 serve.py`
- **Port:** 5000
- **Entry point:** Serves `dcc/Excel Explorer Pro working.html` at `/`

## Deployment
- Target: autoscale
- Run command: `python3 serve.py`
