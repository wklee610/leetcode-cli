from leetcli.utils.language import LEETCODE_LANGUAGES

LANG_FILE_EXT = {
    "Python3": "py",
    "C": "c",
    "C++": "cpp",
    "Java": "java",
    "Kotlin": "kt",
    "JavaScript": "js",
    "TypeScript": "ts",
    "Go": "go",
    "C#": "cs",
    "Swift": "swift",
    "Rust": "rs",
    "Ruby": "rb",
    "PHP": "php",
    "Dart": "dart",
    "Scala": "scala",
    "Elixir": "ex",
    "Erlang": "erl",
    "Racket": "rkt",
}

def _create_markdown_file(
    data,
    content_text,
    ac_rate
):
    try:
        safe_title = data['title'].replace(" ", "_").replace("/", "_")
        md_filename = f"{data['questionFrontendId']}_{safe_title}.md"

        md_text = f"# {data['title']} (ID: {data['questionFrontendId']})\n\n"
        md_text += f"**Difficulty:** {data['difficulty']}\n\n"
        md_text += f"**Acceptance:** {ac_rate}\n\n"
        md_text += "## Problem Description\n\n"
        md_text += content_text + "\n\n"

        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(md_text)

    except Exception as e:
        raise e

def _create_code_file(
    data,
    language
):
    lang_key = language.strip().lower()
    try:
        if lang_key not in LEETCODE_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {language}\n"
                f"Available options: {', '.join(sorted(set(LEETCODE_LANGUAGES.values())))}"
            )
        lang_std = LEETCODE_LANGUAGES[lang_key]
        template = next(
            (c['code'] for c in data['codeSnippets'] if c['lang'] == f'{lang_std}'), None
        )
        if template is None:
            raise ValueError(
                f"No code snippet available for language: {language}\n"
                f"Available options: {', '.join(sorted({c['lang'] for c in data['codeSnippets']}))}"
            )
        safe_title = data['title'].replace(" ", "_").replace("/", "_")
        filename = f"{data['questionFrontendId']}_{safe_title}.{LANG_FILE_EXT[lang_std]}"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(template)

    except Exception as e:
        raise e
    

def _get_code_str(
    filename
) -> str:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
        
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filename}")
    
    except Exception as e:
        raise RuntimeError(f"Failed to read file {filename}: {e}")