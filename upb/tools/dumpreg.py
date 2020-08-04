import asyncio
import argparse
import logging
from pprint import pformat
from upb import create_upb_connection

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='UPB Dump Registers')


parser.add_argument('--host', dest='host', type=str, default="127.0.0.1",
                    help='Host to connect to')

parser.add_argument('--port', dest='port', type=int, default=2101,
                    help='Port to connect to')

parser.add_argument('--network', dest='network', type=int,
                    help='Network device is on')

parser.add_argument('--device', dest='device', type=int,
                    help='Device to connect to')

parser.add_argument('--user', dest='username', type=str,
                    help='Username for pulseworx gateway')

parser.add_argument('--pass', dest='password', type=str,
                    help='Password for pulseworx gateway')

options = parser.parse_args()


async def main():
    loop = asyncio.get_event_loop()
    client = await create_upb_connection(
        host=options.host, port=options.port, logger=logger, loop=loop,
        username=options.username, password=options.password
        )
    device = client.get_device(options.network, options.device)
    await device.sync_registers()
    client.stop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())

    except KeyboardInterrupt:
        loop.close()
