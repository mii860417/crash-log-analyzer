# Crash Log Analyzer

A simple Streamlit tool to analyze crash logs.

This tool helps developers and QA engineers extract useful information from crash logs, such as:

- Exception type
- First stack frame
- App-level stack frame
- File and line number
- Possible hints for debugging

The goal of this project is to provide a lightweight crash log analyzer that can help quickly identify potential root causes.

## Demo


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
