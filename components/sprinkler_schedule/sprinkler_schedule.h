#pragma once

#include "esphome/components/datetime/time_entity.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/sprinkler/sprinkler.h"
#include "esphome/components/time/real_time_clock.h"
#include "esphome/core/component.h"
#include "esphome/core/time.h"

namespace esphome {
namespace sprinkler_schedule {

class SprinklerScheduleComponent : public Component {

  SUB_SENSOR(last_run);
  SUB_SENSOR(next_run);
  SUB_SENSOR(estimated_duration);

 public:
  SprinklerScheduleComponent(
      sprinkler::Sprinkler* controller,
      const time::RealTimeClock* clock,
      datetime::TimeEntity* start_time) : controller_(*controller), clock_(*clock), start_time_(*start_time) {}

  void setup() override;
  void loop() override;
  void dump_config() override;

 protected:
  sprinkler::Sprinkler& controller_;
  const time::RealTimeClock& clock_;
  datetime::TimeEntity& start_time_;
};

class SprinklerScheduleTime : public datetime::TimeEntity, public Component {
 public:
  void set_initial_value(ESPTime initial_value) { this->initial_value_ = initial_value; }

  void setup() {
    // Attempt to load previous value from flash
    this->pref_ = global_preferences->make_preference<datetime::TimeEntityRestoreState>(194434060U ^ this->get_object_id_hash());
    datetime::TimeEntityRestoreState temp = {};
    if (this->pref_.load(&temp)) {
      temp.apply(this);
      return;
    }

    // Set initial value if restore isn't successful
    ESPTime state = this->initial_value_;
    this->hour_ = state.hour;
    this->minute_ = state.minute;
    this->second_ = state.second;
    this->publish_state();
  }

  void control(const datetime::TimeCall& call) {
    // Update and publish state
    this->hour_ = call.get_hour().value_or(this->hour_);
    this->minute_ = call.get_minute().value_or(this->minute_);
    this->second_ = call.get_second().value_or(this->second_);
    this->publish_state();

    // Save value to flash for restore
    datetime::TimeEntityRestoreState temp = {};
    temp.hour = this->hour_;
    temp.minute = this->minute_;
    temp.second = this->second_;
    this->pref_.save(&temp);
  }

  // void dump_config() {
  //   LOG_DATETIME_TIME("", "Start Time", this);
  // }

 protected:
  ESPPreferenceObject pref_;
  ESPTime initial_value_{};
};

}  // namespace sprinkler_schedule
}  // namespace esphome