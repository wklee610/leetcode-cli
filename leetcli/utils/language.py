import os

LEETCODE_LANGUAGES = {
    # --- Python ---
    "py": "Python3",
    "python": "Python3",
    "python3": "Python3",

    # --- C / C++ ---
    "c": "C",
    "cpp": "C++",
    "c++": "C++",
    "cc": "C++",
    "cxx": "C++",

    # --- Java ---
    "java": "Java",
    "kotlin": "Kotlin",
    "kt": "Kotlin",

    # --- JavaScript / TypeScript ---
    "js": "JavaScript",
    "javascript": "JavaScript",
    "node": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",

    # --- Go / Golang ---
    "go": "Go",
    "golang": "Go",

    # --- C# ---
    "csharp": "C#",
    "cs": "C#",
    "c#": "C#",

    # --- Swift ---
    "swift": "Swift",

    # --- Rust ---
    "rust": "Rust",
    "rs": "Rust",

    # --- Ruby ---
    "ruby": "Ruby",
    "rb": "Ruby",

    # --- PHP ---
    "php": "PHP",

    # --- Dart ---
    "dart": "Dart",

    # --- Scala ---
    "scala": "Scala",

    # --- Elixir ---
    "elixir": "Elixir",
    "ex": "Elixir",

    # --- Erlang ---
    "erlang": "Erlang",
    "erl": "Erlang",

    # --- Racket ---
    "racket": "Racket",
    "rkt": "Racket",
}

LANG_CONVERT = {
    "Python3": "python3",
    "Go": "golang",
    "Java": "java",
    "C++": "cpp",
    "Python": "python3",
    "JavaScript": "javascript",
    "TypeScript": "typescript",
    "C#": "csharp",
    "C": "c",
    "Kotlin": "kotlin",
    "Swift": "swift",
    "Rust": "rust",
    "Ruby": "ruby",
    "PHP": "php",
    "Dart": "dart",
    "Scala": "scala",
    "Elixir": "elixir",
    "Erlang": "erlang",
    "Racket": "racket",
}


def _detect_language(filename_or_ext: str) -> str:
    """Detect language from file or extension and convert to desired key."""
    if os.path.isfile(filename_or_ext) or os.path.splitext(filename_or_ext)[1]:
        ext = os.path.splitext(filename_or_ext)[1]
        if ext.startswith("."):
            ext = ext[1:]
        lang_key = ext.lower()
    else:
        lang_key = filename_or_ext.lower().lstrip(".")

    if lang_key not in LEETCODE_LANGUAGES:
        raise ValueError(
            f"Unsupported language or extension: {filename_or_ext}\n"
            f"Available options: {', '.join(sorted(set(LEETCODE_LANGUAGES.values())))}"
        )

    leetcode_lang = LEETCODE_LANGUAGES[lang_key]
    return LANG_CONVERT.get(leetcode_lang, leetcode_lang)