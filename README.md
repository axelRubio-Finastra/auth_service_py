# auth_service_py (FastAPI)

Este servicio ofrece:

- Registro de usuarios con verificacion por correo
- Inicio de sesion JWT
- Contraseñas encriptadas (bycrypt)
- Facilmente adaptable a PostgresSQL, MySQL, etc.

## Structure

auth_service/
│
├── .env
├── requirements.txt
├── README.md
├── test_main.py
│
└── app/
   ├── __init__.py
   ├── main.py
   ├── config.py
   ├── database.py
   ├── models.py
   ├── schemas.py
   ├── auth.py
   └── email_utils.py

## Como ejecutar

```bash
uvicorn app.main --reload

