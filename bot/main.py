from ib_insync import IB, Stock
from modules.telegram_sender import send_telegram, init_telegram_credentials, read_secret
import os

def run_bot():
    init_telegram_credentials()

    try:
        ib_host = "127.0.0.1"  # IP cím nem titkos
        ib_port = 7497  # Port nem titkos
        ib_client_id = int(read_secret("ib_client_id") or 1)
        ib_username = read_secret("ib_username")
        ib_password = read_secret("ib_password")

        if not ib_username or not ib_password:
            send_telegram("❌ Hiba: IB username vagy password hiányzik a titkos fájlból.")
            print("❌ Hiba: IB username vagy password hiányzik a titkos fájlból.")
            return

        print(f" Csatlakozás IB Gateway-hez ({ib_host}:{ib_port}, clientId={ib_client_id})...")
        ib = IB()
        ib.connect(ib_host, ib_port, clientId=ib_client_id, username=ib_username, password=ib_password)
        print("✅ Kapcsolódva Interactive Brokers-hez")

        stock = Stock('AAPL', 'SMART', 'USD')
        ib.qualifyContracts(stock)
        ticker = ib.reqMktData(stock)

        while True:
            ib.sleep(1)
            price = ticker.marketPrice()
            print(f"AAPL árfolyam: {price}")

            if price and price > 200:
                msg = f" Az AAPL árfolyam elérte a {price:.2f} USD-t!"
                print(msg)
                send_telegram(msg)
                break

        ib.disconnect()

    except Exception as e:
        send_telegram(f"❌ Hiba történt a botban: {e}")
        print(f"❌ Hiba: {e}")


if __name__ == "__main__":
    run_bot()
