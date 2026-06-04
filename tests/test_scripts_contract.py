from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_windows_scripts_cover_install_start_and_oracle_load():
    scripts = ROOT / "scripts" / "windows"
    expected = ["01_instalar.ps1", "02_iniciar_plataforma.ps1", "03_cargar_oracle.ps1"]
    for name in expected:
        assert (scripts / name).exists()

    start = (scripts / "02_iniciar_plataforma.ps1").read_text(encoding="utf-8")
    load = (scripts / "03_cargar_oracle.ps1").read_text(encoding="utf-8")
    assert "docker compose up -d" in start
    assert "src.webapp.server" in start
    assert "http://localhost:8000" in start
    assert "scripts\\setup_oracle.py" in start
    assert "scripts\\setup_oracle.py" in load
    assert "No requiere SQL Developer ni SQL*Plus" in load


def test_ubuntu_scripts_cover_install_start_and_oracle_load():
    scripts = ROOT / "scripts" / "ubuntu"
    expected = ["01_instalar.sh", "02_iniciar_plataforma.sh", "03_cargar_oracle.sh"]
    for name in expected:
        assert (scripts / name).exists()

    install = (scripts / "01_instalar.sh").read_text(encoding="utf-8")
    start = (scripts / "02_iniciar_plataforma.sh").read_text(encoding="utf-8")
    load = (scripts / "03_cargar_oracle.sh").read_text(encoding="utf-8")
    assert "docker.io" in install
    assert "docker-compose-plugin" in install
    assert "SQL Developer no es obligatorio" in install
    assert "docker compose up -d" in start
    assert "src.webapp.server" in start
    assert "scripts/setup_oracle.py" in start
    assert "scripts/setup_oracle.py" in load
    assert "No requiere SQL Developer ni SQL*Plus" in load


def test_requirements_document_declares_official_links_and_terminal_commands():
    doc = (ROOT / "docs" / "REQUISITOS.md").read_text(encoding="utf-8")
    assert "https://gitforwindows.org/" in doc
    assert "https://www.python.org/downloads/windows/" in doc
    assert "https://www.docker.com/products/docker-desktop/" in doc
    assert "python3 -m venv .venv" in doc
    assert "source .venv/bin/activate" in doc
    assert "sudo apt install -y git python3 python3-venv python3-pip docker.io docker-compose-plugin" in doc
    assert "notebook==7.5.5" in doc
    assert "pandas==3.0.2" in doc


def test_requirements_checker_script_exists():
    script = (ROOT / "scripts" / "check_requirements.py").read_text(encoding="utf-8")
    assert "Docker Compose" in script
    assert "Jupyter Notebook" in script
    assert "gitforwindows.org" in script


def test_oracle_setup_script_replaces_manual_sqlplus_flow():
    script = (ROOT / "scripts" / "setup_oracle.py").read_text(encoding="utf-8")
    assert "preparacion automatica Oracle" in script
    assert "ensure_tablespace" in script
    assert "run_schema_files" in script
    assert "No hace falta abrir SQL Developer ni SQL*Plus" in script


def test_notebook_demo_and_jupyter_dependencies_are_declared():
    notebook = ROOT / "notebooks" / "SaludChilecito_DAO_Demo.ipynb"
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert notebook.exists()
    body = notebook.read_text(encoding="utf-8")
    assert "Salud Chilecito - Demo DAO" in body
    assert "CentroDAO" in body
    assert "BotAgent" in body
    assert "jupyter notebook notebooks/SaludChilecito_DAO_Demo.ipynb" in readme
    assert "notebook==7.5.5" in requirements
    assert "pandas==3.0.2" in requirements
