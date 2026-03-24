import re
import requests
import streamlit as st


FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSemB7XiPBrg_BJx3k_m0o_JHXfbhleKEdwu78vVOVidEByCdw/formResponse"

FIELD_TOOL_NAME = "entry.38392295"
FIELD_EVENT_TYPE = "entry.1467972143"
FIELD_INPUT_SOURCE = "entry.2139090681"
FIELD_NOTE = "entry.2065255547"


def is_keep_alive() -> bool:
    try:
        return str(st.query_params.get("keep_alive", "")).lower() in {"1", "true", "yes"}
    except Exception:
        return False


def track(tool_name: str, event_type: str, input_source: str = "none", note: str = "") -> None:
    if is_keep_alive():
        return

    data = {
        FIELD_TOOL_NAME: tool_name,
        FIELD_EVENT_TYPE: event_type,
        FIELD_INPUT_SOURCE: input_source,
        FIELD_NOTE: note,
    }

    try:
        requests.post(FORM_URL, data=data, timeout=5)
    except Exception:
        pass


TOOL_NAME = "Crash Log Analyzer"
TOOL_SLUG = "crash-log-analyzer"
TOOL_ICON = "🛠️"
TOOL_DESCRIPTION = "Paste your crash log below and click Analyze."

EXAMPLE_LOG = """java.lang.NullPointerException
    at com.example.app.MainActivity.onCreate(MainActivity.kt:42)
    at android.app.Activity.performCreate(Activity.java:8000)
    at android.app.Activity.performCreate(Activity.java:7984)
"""


def extract_exception(log_text: str) -> str:
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
    lines = log_text.splitlines()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("at "):
            return stripped

    return "Not found"


def extract_file_and_line(stack_frame: str) -> str:
    match = re.search(r"\(([^()]+:\d+)\)", stack_frame)
    if match:
        return match.group(1)

    return "Not found"


def extract_app_frame(log_text: str) -> str:
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


def detect_input_source(log_text: str) -> str:
    return "example" if log_text.strip() == EXAMPLE_LOG.strip() else "custom"


def is_qualified_custom_input(log_text: str, input_source: str) -> bool:
    return input_source == "custom" and len(log_text.strip()) > 20


st.set_page_config(page_title=TOOL_NAME, page_icon=TOOL_ICON, layout="centered")

st.title(f"{TOOL_ICON} {TOOL_NAME}")
st.caption(TOOL_DESCRIPTION)

if "tracked_visitor" not in st.session_state:
    track(TOOL_SLUG, "visitor")
    st.session_state["tracked_visitor"] = True

with st.expander("Example crash log"):
    st.code(EXAMPLE_LOG, language="text")

log = st.text_area("Crash Log", height=320, placeholder="Paste your crash log here...")

col1, col2 = st.columns([1, 1])

with col1:
    analyze_clicked = st.button("Analyze", use_container_width=True)

with col2:
    clear_clicked = st.button("Clear", use_container_width=True)

if clear_clicked:
    st.rerun()

if analyze_clicked:
    input_clean = log.strip()

    if not input_clean:
        st.warning("Please paste a crash log first.")
    else:
        input_source = detect_input_source(log)

        track(
            tool_name=TOOL_SLUG,
            event_type="click",
            input_source=input_source,
        )

        result = analyze_log(log)

        if is_qualified_custom_input(log, input_source):
            track(
                tool_name=TOOL_SLUG,
                event_type="qualified",
                input_source=input_source,
            )

        st.subheader("Analysis Result")
        st.markdown(f"**Exception Type:** `{result['exception']}`")
        st.markdown(f"**First Stack Frame:** `{result['first_frame']}`")
        st.markdown(f"**App-Level Frame:** `{result['app_frame']}`")
        st.markdown(f"**File / Line:** `{result['file_and_line']}`")
        st.markdown(f"**Possible Hint:** {result['hint']}")

st.caption("If this tool helped you, please ⭐ the GitHub repo.")
