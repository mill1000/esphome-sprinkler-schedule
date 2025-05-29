import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import datetime, number, sprinkler, switch, time
from esphome.components.sprinkler import (CONF_ENABLE_SWITCH,
                                          CONF_RUN_DURATION_NUMBER,
                                          CONF_VALVES,
                                          SprinklerControllerNumber,
                                          SprinklerControllerSwitch,
                                          validate_min_max)
from esphome.const import (CONF_ID, CONF_INITIAL_VALUE, CONF_MAX_VALUE,
                           CONF_MIN_VALUE, CONF_NAME, CONF_RESTORE_VALUE,
                           CONF_SET_ACTION, CONF_STEP,
                           CONF_UNIT_OF_MEASUREMENT, ENTITY_CATEGORY_CONFIG,
                           UNIT_MINUTE, UNIT_SECOND)

CODEOWNERS = ["@mill1000"]
DEPENDENCIES = ["sprinkler"]

MULTI_CONF = True

CONF_CONTROLLER_ID = "controller_id"
CONF_TIME_ID = "time_id"
CONF_START_TIME = "start_time"
CONF_FREQUENCY_NUMBER = "frequency_number"
CONF_REPETITIONS_NUMBER = "repetitions_number"

sprinkler_schedule_ns = cg.esphome_ns.namespace("sprinkler_schedule")
SprinklerScheduleComponent = sprinkler_schedule_ns.class_(
    "SprinklerScheduleComponent", cg.Component)

SprinklerScheduleTime = sprinkler_schedule_ns.class_(
    "SprinklerScheduleTime", datetime.TimeEntity, cg.Component)


_VALVE_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_ENABLE_SWITCH): cv.maybe_simple_value(
            switch.switch_schema(
                SprinklerControllerSwitch,
                entity_category=ENTITY_CATEGORY_CONFIG,
                default_restore_mode="RESTORE_DEFAULT_OFF",
            ),
            key=CONF_NAME,
        ),
        cv.Optional(CONF_RUN_DURATION_NUMBER): cv.maybe_simple_value(
            number.number_schema(
                SprinklerControllerNumber, entity_category=ENTITY_CATEGORY_CONFIG
            )
            .extend(
                {
                    cv.Optional(CONF_INITIAL_VALUE, default=900): cv.positive_int,
                    cv.Optional(CONF_MAX_VALUE, default=86400): cv.positive_int,
                    cv.Optional(CONF_MIN_VALUE, default=1): cv.positive_int,
                    cv.Optional(CONF_RESTORE_VALUE, default=True): cv.boolean,
                    cv.Optional(CONF_STEP, default=1): cv.positive_int,
                    # cv.Optional(CONF_SET_ACTION): automation.validate_automation(
                    #     single=True
                    # ),
                    cv.Optional(
                        CONF_UNIT_OF_MEASUREMENT, default=UNIT_SECOND
                    ): cv.one_of(UNIT_MINUTE, UNIT_SECOND, lower="True"),
                }
            )
            .extend(cv.COMPONENT_SCHEMA),
            validate_min_max,
            key=CONF_NAME,
        ),
    }
)

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(SprinklerScheduleComponent),
            cv.GenerateID(CONF_CONTROLLER_ID): cv.use_id(sprinkler.Sprinkler),
            cv.GenerateID(CONF_TIME_ID): cv.use_id(time.RealTimeClock),
            cv.Required(CONF_START_TIME): cv.maybe_simple_value(
                datetime.time_schema(SprinklerScheduleTime).extend(
                    {
                        cv.Optional(CONF_INITIAL_VALUE): cv.date_time(
                            date=False, time=True
                        ),
                    }
                ),
                key=CONF_NAME,
            ),
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
                )
                .extend(cv.COMPONENT_SCHEMA),
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
                )
                .extend(cv.COMPONENT_SCHEMA),
                validate_min_max,
                key=CONF_NAME,
            ),
            cv.Optional(CONF_ENABLE_SWITCH): cv.maybe_simple_value(
                switch.switch_schema(
                    SprinklerControllerSwitch,
                    entity_category=ENTITY_CATEGORY_CONFIG,
                    default_restore_mode="RESTORE_DEFAULT_OFF",
                ),
                key=CONF_NAME,
            ),
            cv.Required(CONF_VALVES): cv.ensure_list(_VALVE_SCHEMA),
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
)


async def to_code(config) -> None:
    controller_var = await cg.get_variable(config[CONF_CONTROLLER_ID])

    var = cg.new_Pvariable(config[CONF_ID], controller_var)

    await cg.register_component(var, config)
