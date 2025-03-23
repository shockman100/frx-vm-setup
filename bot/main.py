import asyncio
from modules.telegram_sender import send_telegram, read_secret


def get_secret_or_default(name: str, default: str) -> str:
    value = read_secret(name)
    return value if value else default


async def run():
    # Titkok beolvasása, de fallback értékekkel
    ib_host = get_secret_or_default("ib_host", "127.0.0.1")
    ib_port = int(get_secret_or_default("ib_port", "7497"))
    ib_client_id = int(get_secret_or_default("ib_client_id", "1"))

    # (Opcionálisan) beolvashatod ezeket is, ha szükséges lesz
    ib_username = read_secret("ib_username")
    ib_password = read_secret("ib_password")

    send_telegram(f"📡 Csatlakozás IB Gateway-hez ({ib_host}:{ib_port}, clientId={ib_client_id})...")

    try:
        # IDE jön majd az IB-kliens inicializálás pl.
        # ib = IB()
        # await ib.connect(ib_host, ib_port, clientId=ib_client_id)
        raise ConnectionRefusedError("Simulated IB connect fail")  # Tesztcélra

    except Exception as e:
        send_telegram(f"❌ Hiba: {e}")
        print(f"❌ Hiba: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except RuntimeError as e:
        if "event loop is already running" in str(e):
            print("❌ Az event loop már fut, próbálkozunk alternatív megoldással...")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(run())
        else:
            raise
