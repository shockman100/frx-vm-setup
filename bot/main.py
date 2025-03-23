import asyncio
from ib_insync import IB, Stock
from modules.telegram_sender import send_telegram, init_telegram_credentials, read_secret


async def run_bot():
    init_telegram_credentials()

    try:
        # Titkok olvasása a saját, működő függvényeddel
        ib_host = read_secret("ib_host") or "127.0.0.1"
        ib_port = int(read_secret("ib_port") or 7497)
        ib_client_id = int(read_secret("ib_client_id") or 1)

        print(f"📡 Csatlakozás IB Gateway-hez ({ib_host}:{ib_port}, clientId={ib_client_id})...")
        ib = IB()
        ib.connect(ib_host, ib_port, clientId=ib_client_id)
        print("✅ Kapcsolódva Interactive Brokers-hez")

        stock = Stock('AAPL', 'SMART', 'USD')
        ib.qualifyContracts(stock)
        ticker = ib.reqMktData(stock)

        while True:
            ib.sleep(1)
            price = ticker.marketPrice()
            print(f"AAPL árfolyam: {price}")

            if price and price > 200:
                msg = f"📈 Az AAPL árfolyam elérte a {price:.2f} USD-t!"
                print(msg)
                send_telegram(msg)
                break

        ib.disconnect()

    except Exception as e:
        send_telegram(f"❌ Hiba történt a botban: {e}")
        print(f"❌ Hiba: {e}")


if __name__ == "__main__":
    # A Te környezetedben működő, egyszerű és letesztelt asyncio indítás
    asyncio.run(run_bot())
