import os
import re
import streamlit as st


st.set_page_config(page_title="Crash Log Analyzer", page_icon="🛠️", layout="centered")


def track_usage() -> int:
    """
    Track how many times the Analyze button has been clicked.
    Stores the count in a local text file.

    Note:
        On Streamlit Cloud, local file storage may reset if the app restarts.
        This is acceptable for MVP testing, but not for long-term analytics.
    """
    usage_file = "usage.txt"

    if not os.path.exists(usage_file):
        with open(usage_file, "w", encoding="utf-8") as f:
            f.write("0")

    with open(usage_file, "r", encoding="utf-8") as f:
        raw = f.read().strip()
        count = int(raw) if raw.isdigit() else 0

    count += 1

    with open(usage_file, "w", encoding="utf-8") as f:
        f.write(str(count))

    return count


def extract_exception(log_text: str) -> str:
    """
    Extract common exception types from crash logs.
    """
    patterns = [
        r"([A-Za-z0-9_$.]+Exception)",
        r"([A-Za-z0-9_$.]+Error)",
        r"FATAL EXCEPTION:\s*(.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, log_text)
        if match:
            return match.group(1).strip()

    return "Unknown"


def extract_stack_frame(log_text: str) -> str:
    """
    Extract the first stack frame line.
    Common Java / Android format:
        at com.example.app.MainActivity.onCreate(MainActivity.kt:42)
    """
    lines = log_text.splitlines()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("at "):
            return stripped

    return "Not found"


def extract_file_and_line(stack_frame: str) -> str:
    """
    Extract file name and line number from a stack frame.
    Example:
        at com.example.app.MainActivity.onCreate(MainActivity.kt:42)
    -> MainActivity.kt:42
    """
    match = re.search(r"\(([^()]+:\d+)\)", stack_frame)
    if match:
        return match.group(1)

    return "Not found"


def extract_app_frame(log_text: str) -> str:
    """
    Try to find an app-level stack frame rather than system/framework frames.
    This is a simple heuristic: skip common Android/Java/system packages.
    """
    lines = log_text.splitlines()
    excluded_prefixes = (
        "at android.",
        "at java.",
        "at javax.",
        "at kotlin.",
        "at sun.",
        "at dalvik.",
        "at com.android.",
    )

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("at ") and not stripped.startswith(excluded_prefixes):
            return stripped

    return "Not found"


def get_hint(exception: str) -> str:
    """
    Provide a simple rule-based hint based on exception type.
    """
    hints = {
        "NullPointerException": "Object reference might be null. Check initialization and nullable handling.",
        "IndexOutOfBoundsException": "Check list or array boundaries before access.",
        "ArrayIndexOutOfBoundsException": "Check array index boundaries before access.",
        "IllegalStateException": "Object may be in an invalid state. Check lifecycle or call order.",
        "IllegalArgumentException": "A method may be receiving an invalid argument.",
        "NumberFormatException": "Input string may not be a valid number. Validate before parsing.",
        "ClassCastException": "An object may be cast to an incompatible type.",
        "OutOfMemoryError": "Memory usage may be too high. Check large objects, bitmaps, or leaks.",
        "StackOverflowError": "There may be unintended recursion or an endlessly repeated call path.",
        "Unknown": "No suggestion available. Review the stack trace and locate the first app-level frame.",
    }

    simple_name = exception.split(".")[-1]
    return hints.get(simple_name, "No suggestion available. Review the stack trace for the first app-level frame.")


def analyze_log(log_text: str) -> dict:
    """
    Run the full analysis and return structured results.
    """
    exception = extract_exception(log_text)
    first_frame = extract_stack_frame(log_text)
    app_frame = extract_app_frame(log_text)
    file_and_line = extract_file_and_line(app_frame if app_frame != "Not found" else first_frame)
    hint = get_hint(exception)

    return {
        "exception": exception,
        "first_frame": first_frame,
        "app_frame": app_frame,
        "file_and_line": file_and_line,
        "hint": hint,
    }


st.title("🛠️ Crash Log Analyzer")
st.caption("Paste your crash log below and click Analyze.")

example_log = """java.lang.NullPointerException
    at com.example.app.MainActivity.onCreate(MainActivity.kt:42)
    at android.app.Activity.performCreate(Activity.java:8000)
    at android.app.Activity.performCreate(Activity.java:7984)
"""

with st.expander("Example crash log"):
    st.code(example_log, language="text")

log = st.text_area("Crash Log", height=320, placeholder="Paste your crash log here...")


col1, col2 = st.columns([1, 1])

with col1:
    analyze_clicked = st.button("Analyze", use_container_width=True)

with col2:
    clear_clicked = st.button("Clear", use_container_width=True)

if clear_clicked:
    st.rerun()

if analyze_clicked:
    if not log.strip():
        st.warning("Please paste a crash log first.")
    else:
        usage_count = track_usage()
        result = analyze_log(log)

        st.subheader("Analysis Result")

        st.markdown(f"**Exception Type:** `{result['exception']}`")
        st.markdown(f"**First Stack Frame:** `{result['first_frame']}`")
        st.markdown(f"**App-Level Frame:** `{result['app_frame']}`")
        st.markdown(f"**File / Line:** `{result['file_and_line']}`")
        st.markdown(f"**Possible Hint:** {result['hint']}")

        st.divider()
        st.caption(f"Total analyses: {usage_count}")