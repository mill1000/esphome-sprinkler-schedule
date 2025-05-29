
#include "sprinkler_schedule.h"

#include "esphome/core/log.h"

namespace esphome {
namespace sprinkler_schedule {

static const char *const TAG = "sprinkler_schedule";

void SprinklerScheduleComponent::setup() {
}

void SprinklerScheduleComponent::loop() {
}

void SprinklerScheduleComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "Sprinkler Schedule:");
}


}  // namespace sprinkler_schedule
}  // namespace esphome