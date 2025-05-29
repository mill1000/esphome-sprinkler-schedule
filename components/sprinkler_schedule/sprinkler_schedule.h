#pragma once

#include "esphome/core/component.h"
#include "esphome/components/sprinkler/sprinkler.h"

namespace esphome {
namespace sprinkler_schedule {

class SprinklerScheduleComponent : public Component {
 public:
  SprinklerScheduleComponent(sprinkler::Sprinkler* controller) : controller_(*controller) {}

  void setup() override;
  void loop() override;
  void dump_config() override;

 protected:
  sprinkler::Sprinkler& controller_;
};

}  // namespace sprinkler_schedule
}  // namespace esphome