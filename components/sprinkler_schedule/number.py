import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import number
from esphome.components.sprinkler import (SprinklerControllerNumber,
                                          validate_min_max)
from esphome.const import (CONF_INITIAL_VALUE, CONF_MAX_VALUE, CONF_MIN_VALUE,
                           CONF_NAME, CONF_RESTORE_VALUE, CONF_SET_ACTION,
                           CONF_STEP, ENTITY_CATEGORY_CONFIG)

from . import CONF_SCHEDULE_ID, SprinklerScheduleComponent

DEPENDENCIES = ["sprinkler_schedule"]

CONF_FREQUENCY_NUMBER = "frequency_number"
CONF_REPETITIONS_NUMBER = "repetitions_number"

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(CONF_SCHEDULE_ID): cv.use_id(SprinklerScheduleComponent),
            cv.Required(CONF_FREQUENCY_NUMBER): cv.maybe_simple_value(
                number.number_schema(
                    SprinklerControllerNumber, entity_category=ENTITY_CATEGORY_CONFIG
                )
                .extend(
                    {
                        cv.Optional(CONF_INITIAL_VALUE, default=2): cv.positive_int,
                        cv.Optional(CONF_MAX_VALUE, default=7): cv.positive_int,
                        cv.Optional(CONF_MIN_VALUE, default=1): cv.positive_int,
                        cv.Optional(CONF_RESTORE_VALUE, default=True): cv.boolean,
                        cv.Optional(CONF_STEP, default=1): cv.positive_int,
                        # cv.Optional(CONF_SET_ACTION): automation.validate_automation(
                        #     single=True
                        # ),
                    }
                ),
                validate_min_max,
                key=CONF_NAME,
            ),
            cv.Optional(CONF_REPETITIONS_NUMBER): cv.maybe_simple_value(
                number.number_schema(
                    SprinklerControllerNumber, entity_category=ENTITY_CATEGORY_CONFIG
                )
                .extend(
                    {
                        cv.Optional(CONF_INITIAL_VALUE, default=1): cv.positive_int,
                        cv.Optional(CONF_MAX_VALUE, default=5): cv.positive_int,
                        cv.Optional(CONF_MIN_VALUE, default=1): cv.positive_int,
                        cv.Optional(CONF_RESTORE_VALUE, default=True): cv.boolean,
                        cv.Optional(CONF_STEP, default=1): cv.positive_int,
                        # cv.Optional(CONF_SET_ACTION): automation.validate_automation(
                        #     single=True
                        # ),
                    }
                ),
                validate_min_max,
                key=CONF_NAME,
            ),
        }
    )
)


async def to_code(config) -> None:

    schedule = await cg.get_variable(config[CONF_SCHEDULE_ID])

    if number_config := config.get(CONF_FREQUENCY_NUMBER):
        num = await number.new_number(
            number_config,
            min_value=number_config[CONF_MIN_VALUE],
            max_value=number_config[CONF_MAX_VALUE],
            step=number_config[CONF_STEP],
        )

        cg.add(num.set_initial_value(number_config[CONF_INITIAL_VALUE]))
        cg.add(num.set_restore_value(number_config[CONF_RESTORE_VALUE]))

        # TODO?
        # if CONF_SET_ACTION in number_config:
        #     await automation.build_automation(
        #         num.get_set_trigger(),
        #         [(float, "x")],
        #         number_config[CONF_SET_ACTION],
        #     )

        # await cg.register_parented(sw, config[CONF_SCHEDULE_ID]) # TODO?
        cg.add(schedule.set_frequency_number(num))

    if number_config := config.get(CONF_REPETITIONS_NUMBER):
        num = await number.new_number(
            number_config,
            min_value=number_config[CONF_MIN_VALUE],
            max_value=number_config[CONF_MAX_VALUE],
            step=number_config[CONF_STEP],
        )
        
        cg.add(num.set_initial_value(number_config[CONF_INITIAL_VALUE]))
        cg.add(num.set_restore_value(number_config[CONF_RESTORE_VALUE]))

       # TODO?
        # if CONF_SET_ACTION in number_config:
        #     await automation.build_automation(
        #         num.get_set_trigger(),
        #         [(float, "x")],
        #         number_config[CONF_SET_ACTION],
        #     )

        # await cg.register_parented(sw, config[CONF_SCHEDULE_ID]) # TODO?
        cg.add(schedule.set_repititions_number(num))
