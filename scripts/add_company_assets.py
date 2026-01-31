from __future__ import annotations

import re
import difflib
from pathlib import Path
from urllib.parse import urlparse


def _find_block(lines: list[str], marker: str) -> tuple[int, int]:
    start = None
    depth = 0
    for i, line in enumerate(lines):
        if start is None and marker in line and "{" in line:
            start = i
            depth += line.count("{") - line.count("}")
            continue
        if start is not None:
            depth += line.count("{") - line.count("}")
            if depth == 0:
                return start, i
    raise ValueError(f"Could not find block for {marker}")


def _detect_indent(lines: list[str], start: int, end: int) -> str:
    for i in range(start + 1, end):
        stripped = lines[i].lstrip("\t ")
        if stripped and not stripped.startswith("#"):
            return lines[i][: len(lines[i]) - len(stripped)]
    return "    "


def _upsert_dict_entry(file_path: Path, dict_name: str, key: str, value: str) -> bool:
    if not value:
        return False

    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    start, end = _find_block(lines, f"{dict_name} =")
    indent = _detect_indent(lines, start, end)

    key_pattern = re.compile(rf"^\s*[\"']{re.escape(key)}[\"']\s*:\s*[\"'].*?[\"']\s*,?\s*$")
    for i in range(start + 1, end):
        if key_pattern.match(lines[i]):
            lines[i] = f"{indent}\"{key}\": \"{value}\",\n"
            file_path.write_text("".join(lines), encoding="utf-8")
            return True

    lines.insert(end, f"{indent}\"{key}\": \"{value}\",\n")
    file_path.write_text("".join(lines), encoding="utf-8")
    return True


def _get_background_options(file_path: Path) -> list[str]:
    content = file_path.read_text(encoding="utf-8")
    match = re.search(r"const\s+backgroundCombinations\s*=\s*\{([\s\S]*?)\};", content)
    if not match:
        return []
    body = match.group(1)
    keys = re.findall(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*:\s*\{", body, flags=re.MULTILINE)
    return keys


def _upsert_company_background(file_path: Path, key: str, background_key: str) -> bool:
    if not background_key:
        return False

    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    start, end = _find_block(lines, "const companyConfig")
    indent = _detect_indent(lines, start, end)

    key_pattern = re.compile(rf"^\s*[\"']?{re.escape(key)}[\"']?\s*:\s*backgroundCombinations\.[A-Za-z0-9_]+\s*,?\s*$")
    for i in range(start + 1, end):
        if key_pattern.match(lines[i]):
            lines[i] = f"{indent}\"{key}\": backgroundCombinations.{background_key},\n"
            file_path.write_text("".join(lines), encoding="utf-8")
            return True

    lines.insert(end, f"{indent}\"{key}\": backgroundCombinations.{background_key},\n")
    file_path.write_text("".join(lines), encoding="utf-8")
    return True


def _upsert_caps_exception(file_path: Path, company_key: str) -> bool:
    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    start = None
    end = None
    for i, line in enumerate(lines):
        if "exceptions = [" in line:
            start = i
            for j in range(i, len(lines)):
                if "]" in lines[j]:
                    end = j
                    break
            break

    if start is None or end is None:
        return False

    existing = "".join(lines[start:end + 1])
    if company_key.upper() in existing:
        return False

    insert_line = end
    indent = re.match(r"^(\s*)", lines[end]).group(1)
    lines.insert(insert_line, f"{indent}\"{company_key.upper()}\",\n")
    file_path.write_text("".join(lines), encoding="utf-8")
    return True


def _prompt(label: str, default: str | None = None) -> str:
    print()
    colored = _print_label(label)
    if default is None:
        return input(f"{colored}: ").strip()
    value = input(f"{colored} [{default}]: ").strip()
    return value or default


def _prompt_choice(label: str, options: list[str], default: str | None = None) -> str:
    if not options:
        return ""
    numbered = {str(i + 1): opt for i, opt in enumerate(options)}
    print()
    print(_print_label(label))
    for number, opt in numbered.items():
        print(f"  {number}) {opt}")
    print()
    if default and default in options:
        choice = _prompt("Pick a number", default=str(options.index(default) + 1))
    else:
        choice = _prompt("Pick a number")
    return numbered.get(choice.strip(), "")


def _get_existing_keys(file_path: Path, dict_name: str) -> list[str]:
    lines = file_path.read_text(encoding="utf-8").splitlines()
    start, end = _find_block(lines, f"{dict_name} =")
    keys = []
    for line in lines[start + 1 : end]:
        match = re.match(r"\s*[\"'](.+?)[\"']\s*:\s*", line)
        if match:
            keys.append(match.group(1))
    return keys


def _get_company_config_keys(file_path: Path) -> list[str]:
    content = file_path.read_text(encoding="utf-8")
    match = re.search(r"const\s+companyConfig\s*=\s*\{([\s\S]*?)\};", content)
    if not match:
        return []
    body = match.group(1)
    keys = []
    for line in body.splitlines():
        match_key = re.match(r"\s*[\"']?(.+?)[\"']?\s*:\s*backgroundCombinations\.", line)
        if match_key:
            keys.append(match_key.group(1))
    return keys


def _get_company_background_map(file_path: Path) -> dict[str, str]:
    content = file_path.read_text(encoding="utf-8")
    match = re.search(r"const\s+companyConfig\s*=\s*\{([\s\S]*?)\};", content)
    if not match:
        return {}
    body = match.group(1)
    mapping: dict[str, str] = {}
    for line in body.splitlines():
        match_key = re.match(r"\s*[\"']?(.+?)[\"']?\s*:\s*backgroundCombinations\.([A-Za-z0-9_]+)", line)
        if match_key:
            mapping[match_key.group(1)] = match_key.group(2)
    return mapping


def _get_category_map(file_path: Path) -> dict[str, str]:
    lines = file_path.read_text(encoding="utf-8").splitlines()
    start, end = _find_block(lines, "company_categories =")
    mapping: dict[str, str] = {}
    for line in lines[start + 1 : end]:
        match = re.match(r"\s*[\"'](.+?)[\"']\s*:\s*[\"'](.+?)[\"']", line)
        if match:
            mapping[match.group(1)] = match.group(2)
    return mapping


def _guess_from_existing(company_key: str, candidates: list[str]) -> str:
    if not candidates:
        return ""
    match = difflib.get_close_matches(company_key, candidates, n=1, cutoff=0.6)
    return match[0] if match else ""


def _print_error(message: str) -> None:
    red = "\x1b[31m"
    reset = "\x1b[0m"
    print(f"{red}{message}{reset}")


def _print_success(message: str) -> None:
    green = "\x1b[32m"
    reset = "\x1b[0m"
    print(f"{green}{message}{reset}")


def _print_label(label: str) -> str:
    blue = "\x1b[34m"
    reset = "\x1b[0m"
    return f"{blue}{label}{reset}"


def _is_valid_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _print_brandfetch_hint() -> None:
    print()
    print(_print_label("Asset source"))
    print("  Get logos/banners from: https://brandfetch.com/")
    print()


def _prompt_url(label: str, allow_empty: bool = True) -> str:
    while True:
        value = _prompt(label)
        if not value and allow_empty:
            return ""
        if _is_valid_url(value):
            return value
        _print_error("Invalid URL. Please enter a full http/https URL.")
        retry = _prompt("Try again? (y/n)", default="y").lower()
        if retry != "y":
            return ""


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    company_info = repo_root / "company_info"
    company_config = repo_root / "scripts" / "company-config.js"
    app_file = repo_root / "app.py"

    while True:
        _print_brandfetch_hint()

        existing_keys = set()
        existing_keys.update(_get_existing_keys(company_info / "company_logos.py", "company_logos"))
        existing_keys.update(_get_existing_keys(company_info / "company_banner.py", "company_banner"))
        existing_keys.update(_get_existing_keys(company_info / "circular_logos.py", "circular_logos"))
        existing_keys.update(_get_existing_keys(company_info / "company_link.py", "company_link"))
        existing_keys.update(_get_existing_keys(company_info / "company_categories.py", "company_categories"))
        existing_keys.update(_get_company_config_keys(company_config))

        while True:
            key = _prompt("Company name (used as key, will be lowercased)").lower()
            if not key:
                _print_error("Company name is required.")
                continue
            if key in existing_keys:
                _print_error(f"'{key}' already exists.")
                update = _prompt("Update existing entries? (y/n)", default="n").lower()
                if update == "y":
                    break
                retry = _prompt("Try another name? (y/n)", default="y").lower()
                if retry != "y":
                    return
                continue
            break

        logo_url = _prompt_url("Logo URL (leave blank to skip)")
        banner_url = _prompt_url("Banner URL (leave blank to skip)")
        circular_logo_url = _prompt_url("Circular logo URL (leave blank to skip)")
        website_url = _prompt_url("Website URL (leave blank to skip)")

        category_map = _get_category_map(company_info / "company_categories.py")
        background_map = _get_company_background_map(company_config)
        guess_source = _guess_from_existing(key, sorted(set(category_map) | set(background_map)))
        guessed_category = category_map.get(guess_source, "Technology")
        guessed_background = background_map.get(guess_source, "Blue")
        if guess_source:
            print()
            print(_print_label("Auto-guess"))
            print(f"  Based on: {guess_source}")
            print(f"  Category: {guessed_category}")
            print(f"  Background: {guessed_background}")

        category_options = [
            "Technology",
            "Finance",
            "Retail",
            "Entertainment",
            "Travel & Transport",
            "News & Media",
        ]
        category = _prompt_choice("Pick a category (1-6):", category_options, default=guessed_category)

        background_options = _get_background_options(company_config)
        background_key = _prompt_choice("Pick a background:", background_options, default=guessed_background)

        caps_choice = _prompt("Keep company name ALL CAPS in UI? (y/n)", default="n").lower()

        updates = []
        if _upsert_dict_entry(company_info / "company_logos.py", "company_logos", key, logo_url):
            updates.append("company_logos.py")
        if _upsert_dict_entry(company_info / "company_banner.py", "company_banner", key, banner_url):
            updates.append("company_banner.py")
        if _upsert_dict_entry(company_info / "circular_logos.py", "circular_logos", key, circular_logo_url):
            updates.append("circular_logos.py")
        if _upsert_dict_entry(company_info / "company_link.py", "company_link", key, website_url):
            updates.append("company_link.py")
        if _upsert_dict_entry(company_info / "company_categories.py", "company_categories", key, category):
            updates.append("company_categories.py")
        if _upsert_company_background(company_config, key, background_key):
            updates.append("scripts/company-config.js")
        if caps_choice == "y" and _upsert_caps_exception(app_file, key):
            updates.append("app.py")

        if updates:
            _print_success("Updated:")
            for item in updates:
                print(f"- {item}")
        else:
            _print_error("No changes applied.")

        again = _prompt("Do you want to add/update another company? (y/n)", default="n").lower()
        if again != "y":
            break


if __name__ == "__main__":
    main()
