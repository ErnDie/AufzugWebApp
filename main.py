#! /usr/bin/env python3
from typing import Dict

from aiohttp import web
import json
import asyncio
from crosslab.api_client import APIClient
from crosslab.soa_client.device_handler import DeviceHandler
from crosslab.soa_services.electrical import ElectricalConnectionService
from crosslab.soa_services.electrical.signal_interfaces.gpio import ConstractableGPIOInterface, GPIOInterface
from latency import Latency

interfaces: Dict[str, GPIOInterface] = dict()

sensor_names = [
    "FloorZero",
    "FloorOne",
    "FloorTwo",
    "FloorThree",
    "FloorFour",
    "FloorFive",
    "FloorSix",
    "FloorSeven",
    "FloorEight",
    "FloorNine",
    "FloorTen",
    "FloorEleven"
]


async def main_async():
    latency_calc = Latency()

    async def run_server():
        app = web.Application()
        app.router.add_route('GET', '/', handle_index)
        app.router.add_route('GET', '/zero', floorZero)
        app.router.add_route('GET', '/three', floorThree)
        app.router.add_route('GET', '/ten', floorTen)
        app.router.add_route('GET', '/measure', measurement)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8000)
        await site.start()

    async def handle_index(request):
        # Read the contents of the index.html file
        with open('index.html', 'r') as f:
            html_content = f.read()

        # Return the HTML content as the response
        return web.Response(text=html_content, content_type='text/html')

    async def floorZero(request):
        latency_calc.start()
        interfaces["FloorZero"].changeDriver("strongH")

    async def floorThree(request):
        latency_calc.start()
        interfaces["FloorThree"].changeDriver("strongH")

    async def floorTen(request):
        latency_calc.start()
        interfaces["FloorTen"].changeDriver("strongH")

    async def measurement(request):
        for i in range(0, 50):
            print(f"Iteration: {i}")
            latency_calc.start()
            if i % 2 == 0:
                interfaces["FloorThree"].changeDriver("strongH")
            else:
                interfaces["FloorTen"].changeDriver("strongH")
            await asyncio.sleep(5)

        await asyncio.sleep(3)
        latency_calc.calculateRTTJitter()
        latency_calc.calculateRTTMetrics()
        latency_calc.saveAsJSON()
        latency_calc.saveMetricsAsTxt()
        print("Measurement finished!")

    # read config from file
    with open("config.json", "r") as configfile:
        conf = json.load(configfile)

    # debug; delete for prod
    print(conf)
    deviceHandler = DeviceHandler()

    def newSensorInterface(interface):
        if isinstance(interface, GPIOInterface):
            name: str = interface.configuration["signals"]["gpio"]
            interfaces[name] = interface
            interface.on(
                "signalChange",
                lambda event: (
                    latency_calc.calculateLatency(),
                    latency_calc.printLatency()
                )
            )

    sensor_service = ElectricalConnectionService("electrical")
    sensor_interface = ConstractableGPIOInterface(sensor_names, "inout")
    sensor_service.addInterface(sensor_interface)
    sensor_service.on("newInterface", newSensorInterface)
    deviceHandler.add_service(sensor_service)

    url = conf["auth"]["deviceURL"]

    async with APIClient(url) as client:
        client.set_auth_token(conf["auth"]["deviceAuthToken"])
        # Create the HTTP server as a coroutine task
        server_task = asyncio.create_task(run_server())

        deviceHandlerTask = asyncio.create_task(
            deviceHandler.connect("{url}/devices/{did}".format(
                url=conf["auth"]["deviceURL"],
                did=conf["auth"]["deviceID"]
            ), client)
        )

        await asyncio.gather(server_task, deviceHandlerTask)


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
