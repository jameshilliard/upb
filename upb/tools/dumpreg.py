import asyncio
import argparse
import logging
from upb import create_upb_connection

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='UPB Dump Registers')


parser.add_argument('--host', dest='host', type=str, default="127.0.0.1",
                    help='Host to connect to')

parser.add_argument('--port', dest='port', type=int, default=2101,
                    help='Port to connect to')

options = parser.parse_args()


async def main():
    client = await create_upb_connection(host=options.host, port=options.port, logger=logger)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    try:
        loop.run_forever()

    except KeyboardInterrupt:
        loop.close()
