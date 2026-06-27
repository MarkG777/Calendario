# Historial de versiones

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).

## [0.1.0] - 2026-06-25

### Agregado
- Andamiaje del proyecto: capas `domain/`, `data/`, `ui/`, `app/`, `tests/`,
  configuración de `pyproject.toml`, `.gitignore` y `README.md`.
- Dominio: entidades `Borrower`, `Loan`, `Installment`, `Payment`; generador
  del calendario de cuotas; cálculos de saldo pendiente, abonos parciales,
  detección de atraso, ganancia bruta y TIR. Todo el dinero usa `Decimal`.
- Persistencia: modelos SQLAlchemy y repositorios sobre SQLite, con
  serialización exacta de `Decimal` (sin pasar por `float`).
- UI mínima (PySide6): alta y listado de deudores, alta de préstamos con
  cuota calculada en vivo antes de guardar, calendario de cobros y registro
  de cobros/abonos.
- Dashboard: capital en la calle, cobranza esperada vs. real de la semana,
  morosidad de la cartera, ganancia proyectada vs. realizada, y TIR por
  préstamo y de la cartera.
- Empaquetado con PyInstaller: ejecutable independiente (`ControlDeCobros.exe`)
  que guarda la base de datos junto al `.exe`.
