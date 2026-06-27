# Control de Cobros

Aplicación de escritorio para que un prestamista lleve el control de deudores,
préstamos, calendario de cobros, pagos y abonos parciales, y el rendimiento
real de su capital (TIR).

## Requisitos
- Python 3.12 o superior

## Instalación
```
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## Correr la app
```
python -m app.main
```
(Disponible a partir de la FASE 3 del desarrollo.)

## Correr las pruebas
```
pytest
```

## Empaquetar (ejecutable independiente)
```
pip install -e ".[build]"
python -m PyInstaller --name ControlDeCobros --onefile --windowed app/main.py
```
El ejecutable queda en `dist/ControlDeCobros.exe`. Al abrirlo, crea (o usa)
`cobros.db` en la misma carpeta donde está el `.exe` — no en la carpeta del
código fuente. `ControlDeCobros.spec` queda versionado para reproducir el
mismo empaquetado (por ejemplo, si más adelante se agrega un ícono).

## Historial de versiones
Ver [CHANGELOG.md](CHANGELOG.md).

## Seguridad y privacidad
- Nunca subas al repositorio archivos `*.db`, `*.sqlite`, `.env` ni exportaciones
  con datos reales de deudores. Estos datos viven solo en la base de datos local
  del cliente.
