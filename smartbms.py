import sys
from datetime import datetime, timezone
import argparse
import asyncio
from bms import BMS
import dataclasses
import logging
import json

logger = logging.getLogger("signalk-123smartbms-usb")


@dataclasses.dataclass
class ComInstance:
    id: str
    port: str
    bms: BMS


async def monitor(config):
    instances = []
    loop = asyncio.get_running_loop()

    for device in config["devices"]:
        bms = BMS(loop, device["port"])
        await bms.connect()
        com = ComInstance(device["id"], device["port"], bms)
        instances.append(com)

    while True:
        for instance in instances:
            delta = {
                "updates": [{
                    "source": {
                        "label": "123/Smart BMS",
                        "type": "USB",
                        "src": instance.port,
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', "Z"),
                    "values": [
			{"path":
                        f"electrical.batteries.{instance.id}.voltage", "value": instance.bms.pack_voltage},
			{"path":
                        f"electrical.batteries.{instance.id}.current", "value": instance.bms.pack_current},
			{"path":
                        f"electrical.batteries.{instance.id}.capacity.stateOfCharge", "value": instance.bms.soc},
			{"path":
                        f"electrical.batteries.{instance.id}.capacity.nominal", "value": instance.bms.pack_capacityNominal},
			{"path":
                        f"electrical.batteries.{instance.id}.lowestCellVoltage", "value": instance.bms.lowest_cell_voltage},
			{"path":
                        f"electrical.batteries.{instance.id}.highestCellVoltage", "value": instance.bms.highest_cell_voltage},
			{"path":
                        f"electrical.batteries.{instance.id}.highestCellVoltageNum", "value": instance.bms.highest_cell_voltage_num},
			{"path":
                        f"electrical.batteries.{instance.id}.temperature", "value": instance.bms.highest_cell_temperature},
			{"path":
                        f"electrical.batteries.{instance.id}.temperatureNum", "value": instance.bms.highest_cell_temperature_num},
			{"path":
                        f"electrical.batteries.{instance.id}.allowedToCharge", "value": instance.bms.allowed_to_charge},
			{"path":
                        f"electrical.batteries.{instance.id}.allowedToDischarge", "value": instance.bms.allowed_to_discharge},
			{"path":
                        f"electrical.batteries.{instance.id}.capacity.remaining", "value": instance.bms.energy_stored},
			{"path":
                        f"electrical.batteries.{instance.id}.communicationError", "value": 
                                instance.bms.cell_communication_error
                                or instance.bms.serial_communication_error
                        },
                    ],
                }]
            }

            logger.info(delta)
            print(json.dumps(delta))
            sys.stdout.flush()

        await asyncio.sleep(3)


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--verbose", "-v", action="store_true", help="Increase the verbosity"
    )
    args = p.parse_args()

    logging.basicConfig(
        stream=sys.stderr, level=logging.DEBUG if args.verbose else logging.WARNING
    )

    logging.debug("Waiting for config...")
    config = json.loads(input())
    logging.info("Configured: %s", json.dumps(config))
    asyncio.run(monitor(config))


if __name__ == "__main__":
    main()
