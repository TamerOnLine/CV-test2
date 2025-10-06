import requests

API_BASE = "http://127.0.0.1:8000"

def generate_pdf(
    profile: dict,
    theme_name: str,
    layout_name: str | None,
    ui_lang: str,
    rtl_mode: bool,
) -> bytes:
    """
    Sends a POST request to generate a PDF using the specified profile and layout.

    Args:
        profile (dict): The profile data to include in the PDF.
        theme_name (str): The name of the theme to use.
        layout_name (str | None): The layout name or None for default.
        ui_lang (str): The UI language code.
        rtl_mode (bool): Whether to use right-to-left layout.

    Returns:
        bytes: The generated PDF content in binary form.

    Raises:
        HTTPError: If the request fails with a non-2xx response.
    """
    payload = {
        "theme_name": theme_name,
        "layout_name": layout_name,
        "ui_lang": ui_lang,
        "rtl_mode": rtl_mode,
        "profile": profile or {},
    }

    response = requests.post(f"{API_BASE}/generate-form-simple", json=payload, timeout=60)
    response.raise_for_status()
    return response.content
