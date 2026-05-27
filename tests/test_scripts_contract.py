from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_windows_scripts_cover_install_start_and_oracle_load():
    scripts = ROOT / "scripts" / "windows"
    expected = ["01_instalar.ps1", "02_iniciar_plataforma.ps1", "03_cargar_oracle.ps1"]
    for name in expected:
        assert (scripts / name).exists()

    start = (scripts / "02_iniciar_plataforma.ps1").read_text(encoding="utf-8")
    assert "docker compose up -d" in start
    assert "src.webapp.server" in start
    assert "http://localhost:8000" in start


def test_ubuntu_scripts_cover_install_start_and_oracle_load():
    scripts = ROOT / "scripts" / "ubuntu"
    expected = ["01_instalar.sh", "02_iniciar_plataforma.sh", "03_cargar_oracle.sh"]
    for name in expected:
        assert (scripts / name).exists()

    install = (scripts / "01_instalar.sh").read_text(encoding="utf-8")
    start = (scripts / "02_iniciar_plataforma.sh").read_text(encoding="utf-8")
    assert "docker.io" in install
    assert "docker-compose-plugin" in install
    assert "docker compose up -d" in start
    assert "src.webapp.server" in start
