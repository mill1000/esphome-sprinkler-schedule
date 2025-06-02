import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.codegen import Pvariable
from esphome.components import (button, datetime, number, sensor, sprinkler,
                                switch, time)
from esphome.components.sprinkler import (CONF_ENABLE_SWITCH,
                                          CONF_RUN_DURATION_NUMBER,
                                          CONF_VALVES,
                                          SprinklerControllerNumber,
                                          SprinklerControllerSwitch,
                                          validate_min_max)
from esphome.const import (CONF_HOUR, CONF_ID, CONF_INITIAL_VALUE,
                           CONF_MAX_VALUE, CONF_MIN_VALUE, CONF_MINUTE,
                           CONF_NAME, CONF_RESTORE_VALUE, CONF_SECOND,
                           CONF_SET_ACTION, CONF_STEP,
                           CONF_UNIT_OF_MEASUREMENT, DEVICE_CLASS_DURATION,
                           DEVICE_CLASS_TIMESTAMP, ENTITY_CATEGORY_CONFIG,
                           UNIT_MINUTE, UNIT_SECOND)

CODEOWNERS = ["@mill1000"]
DEPENDENCIES = ["sprinkler", "time"]
AUTO_LOAD = ["number", "switch", "datetime", "sensor"]

MULTI_CONF = True

CONF_CONTROLLER_ID = "controller_id"
CONF_TIME_ID = "time_id"
CONF_START_TIME = "start_time"
CONF_LAST_RUN = "last_run_sensor"
CONF_NEXT_RUN = "next_run_sensor"
CONF_ESTIMATED_DURATION = "estimated_duration_sensor"
CONF_FREQUENCY_NUMBER = "frequency_number"
CONF_REPETITIONS_NUMBER = "repetitions_number"
CONF_RUN_NOW_BUTTON = "run_now_button"
CONF_RUN_TOMORROW_BUTTON = "run_tomorrow_button"
CONF_DELAY_BUTTON = "delay_button"
CONF_MANUAL_RUN_BUTTON = "manual_run_button"


sprinkler_schedule_ns = cg.esphome_ns.namespace("sprinkler_schedule")
SprinklerScheduleComponent = sprinkler_schedule_ns.class_(
    "SprinklerScheduleComponent", cg.Component)

SprinklerScheduleTime = sprinkler_schedule_ns.class_(
    "SprinklerScheduleTime", datetime.TimeEntity, cg.Component)

SprinklerScheduleButton = sprinkler_schedule_ns.class_(
    "SprinklerScheduleButton", button.Button)

_BUTTON_SCHEMA = (
    cv.Schema(
        {
            cv.Optional(CONF_RUN_NOW_BUTTON): button.button_schema(
                SprinklerScheduleButton,
            ),
            cv.Optional(CONF_RUN_TOMORROW_BUTTON): button.button_schema(
                SprinklerScheduleButton,
            ),
            cv.Optional(CONF_DELAY_BUTTON): button.button_schema(
                SprinklerScheduleButton,
            ),
            cv.Optional(CONF_MANUAL_RUN_BUTTON): button.button_schema(
                SprinklerScheduleButton,
            ),
        }
    )
)

_SENSOR_SCHEMA = (
    cv.Schema(
        {
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


_NUMBER_SCHEMA = (
    cv.Schema(
        {
            cv.Required(CONF_FREQUENCY_NUMBER): cv.maybe_simple_value(
                number.number_schema(
                    SprinklerControllerNumber,
                    unit_of_measurement="d",
                    entity_category=ENTITY_CATEGORY_CONFIG
                )
                .extend(
                    {
                        cv.Optional(CONF_MIN_VALUE, default=1): cv.positive_int,
                        cv.Optional(CONF_MAX_VALUE, default=7): cv.positive_int,
                        cv.Optional(CONF_STEP, default=1): cv.positive_int,
                        cv.Optional(CONF_INITIAL_VALUE, default=2): cv.positive_int,
                        cv.Optional(CONF_RESTORE_VALUE, default=True): cv.boolean,
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
                    SprinklerControllerNumber,
                    entity_category=ENTITY_CATEGORY_CONFIG
                )
                .extend(
                    {
                        cv.Optional(CONF_MIN_VALUE, default=1): cv.positive_int,
                        cv.Optional(CONF_MAX_VALUE, default=5): cv.positive_int,
                        cv.Optional(CONF_STEP, default=1): cv.positive_int,
                        cv.Optional(CONF_INITIAL_VALUE, default=1): cv.positive_int,
                        cv.Optional(CONF_RESTORE_VALUE, default=True): cv.boolean,
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


_SWITCH_SCHEMA = (
    cv.Schema(
        {
            # TODO needs new name, conflicts with enable_switch in valves?
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
        # TODO should support run_duration too?
        cv.Required(CONF_RUN_DURATION_NUMBER): cv.maybe_simple_value(
            number.number_schema(
                SprinklerControllerNumber, entity_category=ENTITY_CATEGORY_CONFIG
            )
            .extend(
                {
                    cv.Optional(CONF_MIN_VALUE, default=1): cv.positive_int,
                    cv.Optional(CONF_MAX_VALUE, default=86400): cv.positive_int,
                    cv.Optional(CONF_STEP, default=1): cv.positive_int,
                    cv.Optional(CONF_INITIAL_VALUE, default=900): cv.positive_int,
                    cv.Optional(CONF_RESTORE_VALUE, default=True): cv.boolean,
                    cv.Optional(
                        CONF_UNIT_OF_MEASUREMENT, default=UNIT_SECOND
                    ): cv.one_of(UNIT_MINUTE, UNIT_SECOND, lower="True"),
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
            cv.Required(CONF_VALVES): cv.ensure_list(_VALVE_SCHEMA),
        }
    )
    .extend(_SENSOR_SCHEMA)
    .extend(_NUMBER_SCHEMA)
    .extend(_SWITCH_SCHEMA)
    .extend(_BUTTON_SCHEMA)
    .extend(cv.COMPONENT_SCHEMA)
)


async def _button_to_code(schedule, config) -> None:
    if button_config := config.get(CONF_MANUAL_RUN_BUTTON):
        but = await button.new_button(button_config)
        # await cg.register_component(but, button_config) # TODO?
        cg.add(schedule.set_manual_run_button(but))

    if button_config := config.get(CONF_RUN_NOW_BUTTON):
        but = await button.new_button(button_config)
        # await cg.register_component(but, button_config) # TODO?
        cg.add(schedule.set_run_now_button(but))

    if button_config := config.get(CONF_RUN_TOMORROW_BUTTON):
        but = await button.new_button(button_config)
        # await cg.register_component(but, button_config) # TODO?
        cg.add(schedule.set_run_tomorrow_button(but))

    if button_config := config.get(CONF_DELAY_BUTTON):
        but = await button.new_button(button_config)
        # await cg.register_component(but, button_config) # TODO?
        cg.add(schedule.set_delay_button(but))


async def _sensor_to_code(schedule, config) -> None:
    if sensor_config := config.get(CONF_LAST_RUN):
        sens = await sensor.new_sensor(sensor_config)
        cg.add(schedule.set_last_run_sensor(sens))

    if sensor_config := config.get(CONF_NEXT_RUN):
        sens = await sensor.new_sensor(sensor_config)
        cg.add(schedule.set_next_run_sensor(sens))

    if sensor_config := config.get(CONF_ESTIMATED_DURATION):
        sens = await sensor.new_sensor(sensor_config)
        cg.add(schedule.set_estimated_duration_sensor(sens))


async def _number_to_code(schedule, config) -> None:
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

        await cg.register_component(num, number_config)

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

        await cg.register_component(num, number_config)

        cg.add(schedule.set_repetitions_number(num))


async def _switch_to_code(schedule, config) -> None:
    if switch_config := config.get(CONF_ENABLE_SWITCH):
        sw = await switch.new_switch(switch_config)
        await cg.register_component(sw, switch_config)
        cg.add(schedule.set_enable_switch(sw))


async def _start_time_to_code(config) -> Pvariable:
    var = await datetime.new_datetime(config)

    if initial_value := config.get(CONF_INITIAL_VALUE):
        time_struct = cg.StructInitializer(
            cg.ESPTime,
            ("second", initial_value[CONF_SECOND]),
            ("minute", initial_value[CONF_MINUTE]),
            ("hour", initial_value[CONF_HOUR]),
        )
        cg.add(var.set_initial_value(time_struct))

    return var


async def to_code(config) -> None:
    controller_var = await cg.get_variable(config[CONF_CONTROLLER_ID])
    clock_var = await cg.get_variable(config[CONF_TIME_ID])

    start_time_var = await _start_time_to_code(config[CONF_START_TIME])

    schedule_var = cg.new_Pvariable(config[CONF_ID],
                                    controller_var,
                                    clock_var,
                                    start_time_var,
                                    )

    await cg.register_component(schedule_var, config)

    await _sensor_to_code(schedule_var, config)
    await _number_to_code(schedule_var, config)
    await _switch_to_code(schedule_var, config)
    await _button_to_code(schedule_var, config)

    for valve in config[CONF_VALVES]:
        if switch_config := valve[CONF_ENABLE_SWITCH]:
            enable_sw = await switch.new_switch(switch_config)
        else:
            enable_sw = cg.nullptr

        await cg.register_component(enable_sw, valve[CONF_ENABLE_SWITCH])

        number_config = valve[CONF_RUN_DURATION_NUMBER]
        duration_num = await number.new_number(
            number_config,
            min_value=number_config[CONF_MIN_VALUE],
            max_value=number_config[CONF_MAX_VALUE],
            step=number_config[CONF_STEP],
        )

        cg.add(duration_num.set_initial_value(
            number_config[CONF_INITIAL_VALUE]))
        cg.add(duration_num.set_restore_value(
            number_config[CONF_RESTORE_VALUE]))

        await cg.register_component(duration_num, number_config)

        cg.add(schedule_var.add_valve(enable_sw, duration_num))
