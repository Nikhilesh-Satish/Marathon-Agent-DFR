
import os
import re
import hashlib
import google.generativeai as genai

class GeminiBatchGenerator:
    def __init__(self, model_name="models/gemini-1.5-pro"):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel(model_name)

    def _build_prompt(self, stage, files, architecture_text):
        file_list = ", ".join(files)
        return f"""
You are a code generator. The architecture is frozen and must not be changed.

Architecture:
{architecture_text}

Generate the following {stage} files in one response:
{file_list}

Output format:
--- FILE: <filename> ---
<code>
--- END FILE ---
"""

    def _split_files(self, response_text):
        pattern = r"--- FILE: (.*?) ---([\s\S]*?)--- END FILE ---"
        matches = re.findall(pattern, response_text)

        file_map = {}
        for filename, content in matches:
            file_map[filename.strip()] = content.strip()
        return file_map

    def _checksum(self, text):
        return hashlib.sha256(text.encode()).hexdigest()

    def generate_stage(self, stage, files, architecture_text, output_dir):
        prompt = self._build_prompt(stage, files, architecture_text)
        response = self.model.generate_content(prompt)
        text = response.text

        generated_files = self._split_files(text)

        checksums = {}
        for fname, code in generated_files.items():
            path = os.path.join(output_dir, fname)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            checksums[fname] = self._checksum(code)

        return generated_files, checksums
