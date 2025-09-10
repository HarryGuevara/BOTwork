# JobBot — buscador y registrador de vacantes

Bot en Python que busca ofertas (RemoteOK, WWR y boards por empresa), filtra por palabras clave/condiciones, guarda en CSV y puede avisar por email/Telegram.

## Uso rápido
1) Revisa/ajusta `config.yaml`.
2) Instala dependencias:
   pip install -r requirements.txt
3) Ejecuta:
   python main.py --crawl
4) (Opcional) Notificaciones:
   python main.py --crawl --notify

### Marcar una postulación
python main.py --applied <JOB_ID>

**Nota:** Respeta los Términos de Uso de cada sitio.
