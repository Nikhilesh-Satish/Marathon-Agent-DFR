import os
import json
import zipfile
import tempfile
import re

LANGUAGE_BY_EXTENSION = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "javascript",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "cpp",
    ".go": "go"
}

FUNCTION_PATTERNS = {
    "python": [
        r"def\s+{name}\s*\(.*\):([\s\S]*?)(?=\ndef|\Z)"
    ],
    "javascript": [
        r"function\s+{name}\s*\(.*\)\s*\{{([\s\S]*?)\}}",
        r"{name}\s*=\s*\(.*\)\s*=>\s*\{{([\s\S]*?)\}}"
    ],
    "java": [
        r"(public|private|protected)?\s+\w+\s+{name}\s*\(.*\)\s*\{{([\s\S]*?)\}}"
    ],
    "cpp": [
        r"\w+\s+{name}\s*\(.*\)\s*\{{([\s\S]*?)\}}"
    ],
    "go": [
        r"func\s+{name}\s*\(.*\)\s*\{{([\s\S]*?)\}}"
    ]
}

def extract_zip_if_needed(path):
    if zipfile.is_zipfile(path):
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        return temp_dir
    return path

def detect_language(filename):
    _, ext = os.path.splitext(filename)
    return LANGUAGE_BY_EXTENSION.get(ext)

def function_exists_with_body(func_name, filepath, language):
    if language not in FUNCTION_PATTERNS:
        return None, "unsupported language"

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    for pattern in FUNCTION_PATTERNS[language]:
        regex = re.compile(pattern.format(name=func_name), re.MULTILINE)
        match = regex.search(content)
        if match:
            body = match.group(1).strip()
            if body:
                return True, "function exists and has implementation"
            else:
                return False, "function exists but is empty"

    return False, "function does not exist"

def run_dfr(requirements_json, code_input, output_log):
    with open(requirements_json) as f:
        requirements = json.load(f)["requirements"]

    code_dir = extract_zip_if_needed(code_input)
    results = {req: {"status": "violated", "reason": "function does not exist"} for req in requirements}

    for root, _, files in os.walk(code_dir):
        for file in files:
            lang = detect_language(file)
            if not lang:
                continue

            filepath = os.path.join(root, file)
            for req in requirements:
                if results[req]["status"] == "satisfied":
                    continue

                exists, reason = function_exists_with_body(req, filepath, lang)
                if exists:
                    results[req] = {
                        "status": "satisfied",
                        "reason": reason,
                        "language": lang,
                        "file": filepath
                    }
                elif exists is False and "empty" in reason:
                    results[req] = {
                        "status": "violated",
                        "reason": reason,
                        "language": lang,
                        "file": filepath
                    }

    with open(output_log, "w") as f:
        json.dump(results, f, indent=2)

    print(f"DFR log written to {output_log}")
