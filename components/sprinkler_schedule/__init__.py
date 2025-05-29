import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID

CODEOWNERS = ["@mill1000"]
DEPENDENCIES = ["sprinkler"]

MULTI_CONF = True

sprinkler_schedule_ns = cg.esphome_ns.namespace("sprinkler_schedule")
SprinklerScheduleComponent = sprinkler_schedule_ns.class_(
    "SprinklerScheduleComponent", cg.Component)

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(SprinklerScheduleComponent),
        }
    )
    .extend(cv.COMPONENT_SCHEMA)
)


async def to_code(config) -> None:
    var = cg.new_Pvariable(config[CONF_ID])

    await cg.register_component(var, config)
