# Wi-Fi Security Suite

A desktop application for inspecting and auditing Wi-Fi networks and saved
profiles. Use it only with networks and devices you own or are explicitly
authorized to assess.

## Requirements

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/)

## Install and run

Install the application and its development dependencies:

```bash
uv sync --extra dev
```

Launch the desktop application:

```bash
uv run wifisec
```

The `wifisec` command is provided by the project package. You can also start
the application with `uv run python main.py`.

## Application features

The desktop interface includes:

- A dashboard
- Wi-Fi network scanning
- Saved-profile and password auditing
- Network assessment
- Password auditing tools
- Application settings

Some operations depend on the operating system, permissions, wireless adapter,
and optional system tools. The application reports capabilities and errors
through its interface; consult the relevant system-tool documentation for
platform-specific setup.

## Project layout

| Path | Purpose |
| --- | --- |
| `main.py` | Python entry point for the desktop application |
| `wifisec/ui/` | Main window, navigation, workers, theme, and feature pages |
| `wifisec/core/` | Scanning, assessment, capture, password auditing, and tool integration |
| `wifisec/services/` | Settings, update, and administrative services |
| `data/settings.json` | Default application settings |
| `tools/` | Bundled supporting tools and resources |
| `tests/` | Automated tests |
| `pyproject.toml` | Package metadata, dependencies, and command configuration |

## Development checks

Run the test suite and lint checks with:

```bash
uv run pytest
uv run ruff check .
```

## Contact

For bug reports, improvements, or suggestions:

- Email: <misheentrixie@trixiemisheen.site>
- WhatsApp: <http://wa.me/+254791915925>
- Instagram: <https://instagram.com/trixiemisheen>
- Telegram: <https://t.me/Trixie_Misheen>
