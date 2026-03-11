# Crash Log Analyzer

Simple Android crash log analyzer built with Streamlit.

This tool helps developers and QA engineers extract useful information from crash logs, such as:

- Exception type
- First stack frame
- App-level stack frame
- File and line number
- Possible hints for debugging

The goal of this project is to provide a lightweight crash log analyzer that can help quickly identify potential root causes.

## Demo
https://crash-log-analyzer.streamlit.app

## Features

- Paste crash log into a text area
- Click **Analyze**
- Get quick structured output
- Basic local usage counter

## Supported patterns

Currently this tool is mainly designed for:

- Android / Java-style crash logs
- Common exceptions such as:
  - NullPointerException
  - IndexOutOfBoundsException
  - IllegalStateException
  - NumberFormatException
  - OutOfMemoryError
  - StackOverflowError

## Run locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the app

```bash
streamlit run app.py
```


### 3. Open in browser

```bash
Streamlit will usually open this local URL:

http://localhost:8501
```

# 🔗 Related Tools

You may also be interested in:

- Stack Trace Root Cause Finder :
  https://stack-trace-root-cause-finder.streamlit.app
- Logcat Error Filter : https://logcat-error-filter.streamlit.app/

These tools help developers debug logs more efficiently.
