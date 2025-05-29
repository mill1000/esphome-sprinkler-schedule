#pragma once

#include "esphome/core/component.h"

namespace esphome {
namespace sprinkler_schedule {

class SprinklerScheduleComponent : public Component {
 public:
  void setup() override;
  void loop() override;
  void dump_config() override;

 protected:
};

}  // namespace sprinkler_schedule
}  // namespace esphome