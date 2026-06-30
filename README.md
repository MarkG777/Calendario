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
pip install -r requirements.txt
```

## Correr la app
```
python -m app.main
```

## Correr las pruebas
```
pytest
```

## Empaquetar (ejecutable independiente)
```
pip install pyinstaller
pyinstaller --onefile --windowed --name ControlDeCobros --clean --noconfirm --add-data "ui;ui" app/main.py
```
El ejecutable queda en `dist/ControlDeCobros.exe`. Al abrirlo, crea (o usa)
`cobros.db` en la misma carpeta donde está el `.exe`. El `.exe` es portable:
no requiere Python instalado, solo doble clic y funciona.

## Historial de versiones
Ver [CHANGELOG.md](CHANGELOG.md).

## Seguridad y privacidad
- Nunca subas al repositorio archivos `*.db`, `*.sqlite`, `.env` ni exportaciones
  con datos reales de deudores. Estos datos viven solo en la base de datos local
  del cliente.
