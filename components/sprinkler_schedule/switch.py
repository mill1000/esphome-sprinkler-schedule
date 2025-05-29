import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import switch
from esphome.components.sprinkler import (CONF_ENABLE_SWITCH,
                                          SprinklerControllerSwitch)
from esphome.const import CONF_NAME, ENTITY_CATEGORY_CONFIG

from . import CONF_SCHEDULE_ID, SprinklerScheduleComponent

DEPENDENCIES = ["sprinkler_schedule"]


CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(CONF_SCHEDULE_ID): cv.use_id(SprinklerScheduleComponent),
            cv.Optional(CONF_ENABLE_SWITCH): cv.maybe_simple_value(
                switch.switch_schema(
                    SprinklerControllerSwitch,
                    entity_category=ENTITY_CATEGORY_CONFIG,
                    default_restore_mode="RESTORE_DEFAULT_OFF",
                ),
                key=CONF_NAME,
            ),
        }
    )
)


async def to_code(config) -> None:

    schedule = await cg.get_variable(config[CONF_SCHEDULE_ID])

    if switch_config := config.get(CONF_ENABLE_SWITCH):
        sw = await switch.new_switch(switch_config)
        # await cg.register_parented(sw, config[CONF_SCHEDULE_ID]) # TODO?
        cg.add(schedule.set_enable_switch(sw))
