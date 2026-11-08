"""Genera `dist-demo/`: la interfaz con el modo demo activado, lista para publicar como sitio estatico.

    python scripts/build_demo.py
    npx vercel dist-demo --prod     # o arrastra la carpeta a cualquier hosting estatico
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "src" / "agentic_research" / "app" / "web"
OUT = ROOT / "dist-demo"


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(WEB, OUT)
    (OUT / "config.js").write_text("window.DEMO_MODE = true;\n", encoding="utf-8")
    print(f"Demo generada en {OUT}")


if __name__ == "__main__":
    main()
