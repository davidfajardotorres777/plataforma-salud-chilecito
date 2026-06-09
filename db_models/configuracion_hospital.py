from dataclasses import dataclass


@dataclass(slots=True)
class ConfiguracionHospital:
    nombre_hospital: str
    logo_url: str | None = None
    color_primario: str = "#0066cc"
    color_secundario: str = "#ffffff"
    mensaje_bienvenida: str | None = None
    requiere_derivacion: str = "N"
    tiempo_cancelacion_horas: int = 24
    id_configuracion: int | None = None
