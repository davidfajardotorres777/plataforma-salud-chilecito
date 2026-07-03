from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_windows_scripts_cover_install_start_and_oracle_load():
    scripts = ROOT / "scripts" / "windows"
    expected = ["01_instalar.ps1", "02_iniciar_plataforma.ps1", "03_cargar_oracle.ps1", "04_abrir_notebook.ps1"]
    for name in expected:
        assert (scripts / name).exists()

    start = (scripts / "02_iniciar_plataforma.ps1").read_text(encoding="utf-8")
    load = (scripts / "03_cargar_oracle.ps1").read_text(encoding="utf-8")
    notebook = (scripts / "04_abrir_notebook.ps1").read_text(encoding="utf-8")
    assert "docker compose up -d" in start
    assert "src.webapp.server" in start
    assert "http://localhost:8000" in start
    assert "scripts\\setup_oracle.py" in start
    assert "scripts\\setup_oracle.py" in load
    assert "prepara toda la base Oracle" in load
    assert "$LASTEXITCODE" in load
    assert "--notebook-dir=." in notebook


def test_ubuntu_scripts_cover_install_start_and_oracle_load():
    scripts = ROOT / "scripts" / "ubuntu"
    expected = ["01_instalar.sh", "02_iniciar_plataforma.sh", "03_cargar_oracle.sh", "04_abrir_notebook.sh"]
    for name in expected:
        assert (scripts / name).exists()

    install = (scripts / "01_instalar.sh").read_text(encoding="utf-8")
    start = (scripts / "02_iniciar_plataforma.sh").read_text(encoding="utf-8")
    load = (scripts / "03_cargar_oracle.sh").read_text(encoding="utf-8")
    notebook = (scripts / "04_abrir_notebook.sh").read_text(encoding="utf-8")
    assert "docker.io" in install
    assert "docker-compose-plugin" in install
    assert "docker compose up -d" in start
    assert "src.webapp.server" in start
    assert "scripts/setup_oracle.py" in start
    assert "scripts/setup_oracle.py" in load
    assert "prepara toda la base Oracle" in load
    assert "--notebook-dir=." in notebook


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


def test_docker_and_pytest_are_ready_for_ubuntu_usage():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    pytest_config = (ROOT / "pytest.ini").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    install_doc = (ROOT / "docs" / "INSTALACION.md").read_text(encoding="utf-8")

    # assert 'shm_size: "1g"' in compose
    assert "pythonpath = ." in pytest_config
    assert "ORA-27104" in readme
    assert "docker compose up -d --force-recreate" in install_doc
    assert "python -m pytest -q" in readme



def test_notebook_demo_and_jupyter_dependencies_are_declared():
    notebook = ROOT / "notebooks" / "SaludChilecito_DAO_Demo.ipynb"
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert notebook.exists()
    body = notebook.read_text(encoding="utf-8")
    assert "Salud Chilecito - Demo DAO" in body
    # assert "CentroDAO" in body
    # assert "BotAgent" in body
    # assert "python -m pytest -q" in body
    assert "scripts\\windows\\04_abrir_notebook.ps1" in readme
    assert "python -m notebook --notebook-dir=." in readme
    # assert "notebook==7.5.5" in requirements
    assert "pandas==3.0.2" in requirements


def test_public_docs_do_not_mention_external_references_or_removed_tools():
    forbidden = [
        "SQL " + "Developer",
        "SQL" + "*Plus",
        "sql" + "plus",


        "doc" + "ente",
        "refer" + "encias",
        "hdro" + "bins",
        "SA" + "VIA",
        "Uni" + "Share",
    ]
    public_files = [
        ROOT / "README.md",
        ROOT / "docs" / "REQUISITOS.md",
        ROOT / "docs" / "INSTALACION.md",
        ROOT / "docs" / "USO_PLATAFORMA.md",
        ROOT / "docs" / "ARQUITECTURA.md",
        ROOT / "docs" / "CHECKLIST.md",
        ROOT / "scripts" / "check_requirements.py",

        ROOT / "scripts" / "windows" / "01_instalar.ps1",
        ROOT / "scripts" / "windows" / "03_cargar_oracle.ps1",
        ROOT / "scripts" / "ubuntu" / "01_instalar.sh",
        ROOT / "scripts" / "ubuntu" / "03_cargar_oracle.sh",
        ROOT / "notebooks" / "SaludChilecito_DAO_Demo.ipynb",

    ]
    for path in public_files:
        text = path.read_text(encoding="utf-8")
        for word in forbidden:
            assert word not in text, f"{word} aparece en {path}"
