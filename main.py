import os
from pathlib import Path


SECRET_SECTION = "meus_arquivos"
SECRET_MAIN_KEYS = ("main_py", "script_oculto")
SECRET_MAIN_ENV_KEYS = ("STREAMLIT_SECRET_MAIN_PY", "MAIN_PY_CODE", "SCRIPT_OCULTO")


def _load_from_streamlit_secrets() -> str:
    try:
        import streamlit as st
    except Exception:
        return ""

    for key in SECRET_MAIN_KEYS:
        try:
            code = str(st.secrets[SECRET_SECTION][key] or "")
        except Exception:
            continue

        if code.strip():
            return code

    return ""


def _load_from_toml_secrets() -> str:
    secrets_path = Path(__file__).resolve().parent / ".streamlit" / "secrets.toml"
    if not secrets_path.exists():
        return ""

    try:
        import tomllib

        with secrets_path.open("rb") as file:
            secrets_data = tomllib.load(file)
    except Exception:
        return ""

    section = secrets_data.get(SECRET_SECTION, {})
    for key in SECRET_MAIN_KEYS:
        code = str(section.get(key, "") or "")
        if code.strip():
            return code

    return ""


def _load_from_env() -> str:
    for key in SECRET_MAIN_ENV_KEYS:
        code = os.environ.get(key, "")
        if code.strip():
            return code

    return ""


def _run_secret_code(code: str) -> None:
    fake_file = str(Path(__file__).resolve())
    namespace = {
        "__name__": "__main__",
        "__file__": fake_file,
        "__package__": None,
        "__cached__": None,
    }
    exec(compile(code, fake_file, "exec"), namespace)


def main() -> None:
    code = _load_from_streamlit_secrets() or _load_from_toml_secrets() or _load_from_env()
    if not code.strip():
        raise RuntimeError(
            "Backend oculto nao configurado. Defina [meus_arquivos].main_py "
            "nos Secrets do Streamlit ou a variavel MAIN_PY_CODE localmente."
        )

    _run_secret_code(code)


if __name__ == "__main__":
    main()
