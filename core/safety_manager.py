import re
from utils.logger import get_logger


class SafetyManager:
    def __init__(self):
        self.logger = get_logger(__name__)
        
        self.injection_patterns = [
            r"(?i)\bignore\s+previous\s+instructions\b",
            r"(?i)\bignore\s+above\s+instructions\b",
            r"(?i)\bforget\s+all\s+(?:prior|previous)\s+instructions\b",
            r"(?i)\bdisregard\s+(?:all\s+)?previous\s+instructions\b",
            r"(?i)\breveal\s+(?:your\s+)?system\s+prompt\b",
            r"(?i)\breveal\s+(?:your\s+)?prompt\b",
            r"(?i)\bdecode\s+(?:the\s+)?system\s+prompt\b",
            r"(?i)\bprint\s+(?:your\s+)?system\s+prompt\b",
            r"(?i)\bshow\s+(?:your\s+)?system\s+prompt\b",
            r"(?i)\boutput\s+(?:your\s+)?system\s+prompt\b",
            r"(?i)\byou\s+are\s+now\s+in\s+developer\s+mode\b",
            r"(?i)\bact\s+as\s+an\s+unfiltered\b"
        ]

    def sanitize_input(self, text):
        self.logger.info("Sanitizing input text for potential prompt injection...")

        if not text or not isinstance(text, str):
            raise ValueError("Input text must be a non-empty string.")

        sanitized = text
        for pattern in self.injection_patterns:
            sanitized = re.sub(pattern, "", sanitized)

        sanitized = sanitized.lstrip(" .!?,-_")
        sanitized = sanitized.rstrip(" .,-_")

        if not sanitized.strip():
            self.logger.warning("Input text was empty after sanitization.")
            raise ValueError("Question was empty after sanitization.")

        return sanitized

    def sanitize_output(self, response_text):
        self.logger.info("Sanitizing LLM response output...")

        if not response_text or not isinstance(response_text, str):
            self.logger.warning("Empty response passed to sanitizer.")
            return ""

        # 1. Clean thinking blocks (<think>...</think> or unclosed <think>...)
        if "<think>" in response_text:
            if "</think>" in response_text:
                cleaned = re.sub(r"(?is)<think>.*?</think>", "", response_text)
            else:
                match = re.search(r"(?m)^(#{1,6}\s|\*\*|\d+\.\s|Definition|Solve|Consider|The\s|In\s|Based\s)", response_text)
                if match:
                    cleaned = response_text[match.start():]
                else:
                    cleaned = re.sub(r"(?is)^<think>.*?\n", "", response_text)
        else:
            cleaned = response_text

        cleaned = cleaned.strip()

        # 2. Clean any numbered reasoning steps (e.g. "1. **Analyze...", "2. **Scan...", "3. **Check...")
        reasoning_pattern = r"(?is)^(?:\d+\.\s*\*\*(?:Analyze|Scan|Check|Extract|User).*?\n\n|Here's a thinking process:.*?\n\n)"
        while re.match(reasoning_pattern, cleaned):
            cleaned = re.sub(reasoning_pattern, "", cleaned).strip()

        # 3. Remove standalone or trailing single-backslash lines
        cleaned = re.sub(r"^\s*\\+\s*$", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"(?<!\\)\\\s*$", "", cleaned, flags=re.MULTILINE)

        # 4. Recursively unbox any \boxed{content}
        while "\\boxed{" in cleaned:
            idx = cleaned.find("\\boxed{")
            depth = 1
            curr = idx + len("\\boxed{")
            while curr < len(cleaned) and depth > 0:
                if cleaned[curr] == "{":
                    depth += 1
                elif cleaned[curr] == "}":
                    depth -= 1
                curr += 1
            if depth == 0:
                inside = cleaned[idx + len("\\boxed{") : curr - 1]
                cleaned = cleaned[:idx] + " " + inside + " " + cleaned[curr:]
            else:
                break

        # 5. Convert brackets around LaTeX equations [ h_i(x)=0 ] into $$ ... $$
        latex_cmds = r"\\(?:mu|lambda|nabla|partial|frac|sum|int|infty|le|ge|cdot|begin|text|alpha|beta|gamma)"
        cleaned = re.sub(
            r"\[\s*(\\.*?" + latex_cmds + r".*?)\s*\]",
            lambda m: f"\n$$\n{m.group(1).strip()}\n$$\n",
            cleaned,
            flags=re.DOTALL
        )

        # 6. Wrap any unwrapped \begin{env} ... \end{env} in $$ ... $$
        cleaned = re.sub(
            r"(?<!\$\$)\s*(\\begin\{(?:aligned|cases|array|matrix|bmatrix|equation)\}.*?\\end\{(?:aligned|cases|array|matrix|bmatrix|equation)\})\s*(?!\$\$)",
            lambda m: f"\n$$\n{m.group(1).strip()}\n$$\n",
            cleaned,
            flags=re.DOTALL
        )

        return cleaned
