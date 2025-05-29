import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import (DEVICE_CLASS_DURATION, DEVICE_CLASS_TIMESTAMP,
                           UNIT_SECOND)

from . import CONF_SCHEDULE_ID, SprinklerScheduleComponent

DEPENDENCIES = ["sprinkler_schedule"]

CONF_LAST_RUN = "last_run"
CONF_NEXT_RUN = "next_run"
CONF_ESTIMATED_DURATION = "estimated_duration"


CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(CONF_SCHEDULE_ID): cv.use_id(SprinklerScheduleComponent),
            cv.Optional(CONF_LAST_RUN): sensor.sensor_schema(
                accuracy_decimals=0,
                device_class=DEVICE_CLASS_TIMESTAMP,
            ),
            cv.Optional(CONF_NEXT_RUN): sensor.sensor_schema(
                accuracy_decimals=0,
                device_class=DEVICE_CLASS_TIMESTAMP,
            ),
            cv.Optional(CONF_ESTIMATED_DURATION): sensor.sensor_schema(
                unit_of_measurement=UNIT_SECOND,
                accuracy_decimals=0,
                device_class=DEVICE_CLASS_DURATION,
            ),
        }
    )
)


async def to_code(config) -> None:

    schedule = await cg.get_variable(config[CONF_SCHEDULE_ID])

    if sensor_config := config.get(CONF_LAST_RUN):
        sens = await sensor.new_sensor(sensor_config)
        cg.add(schedule.set_last_run_sensor(sens))

    if sensor_config := config.get(CONF_NEXT_RUN):
        sens = await sensor.new_sensor(sensor_config)
        cg.add(schedule.set_next_run_sensor(sens))

    if sensor_config := config.get(CONF_ESTIMATED_DURATION):
        sens = await sensor.new_sensor(sensor_config)
        cg.add(schedule.set_estimated_duration_sensor(sens))
