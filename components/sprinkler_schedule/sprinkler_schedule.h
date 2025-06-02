#pragma once

#include "esphome/components/button/button.h"
#include "esphome/components/datetime/time_entity.h"
#include "esphome/components/number/number.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/sprinkler/sprinkler.h"
#include "esphome/components/switch/switch.h"
#include "esphome/components/time/real_time_clock.h"
#include "esphome/core/component.h"
#include "esphome/core/time.h"

namespace esphome {
namespace sprinkler_schedule {

class SprinklerScheduleTime;
class ScheduleOnTimeTrigger;

constexpr uint32_t RESTORE_STATE_VERSION = 0xA1F0E60D;
struct SprinklerScheduleRestoreState {
  std::time_t last_run_timestamp;
  std::time_t next_run_timestamp;
} __attribute__((packed));

class SprinklerScheduleComponent : public Component {
  SUB_SWITCH(enable);

  SUB_SENSOR(last_run);
  SUB_SENSOR(next_run);
  SUB_SENSOR(estimated_duration);

  SUB_NUMBER(repetitions);
  SUB_NUMBER(frequency);

  SUB_BUTTON(run_now);
  SUB_BUTTON(run_tomorrow);
  SUB_BUTTON(delay);
  SUB_BUTTON(manual_run);
  SUB_BUTTON(reset);

 public:
  struct Valve {
    const sprinkler::SprinklerControllerSwitch* enable_switch;
    const sprinkler::SprinklerControllerNumber* duration_number;

    bool is_enabled() const { return (this->enable_switch == nullptr || this->enable_switch->state); }
    float get_duration_in_seconds() const { return duration_number->state * 60; }
  };

  SprinklerScheduleComponent(sprinkler::Sprinkler* controller,
                             time::RealTimeClock* clock,
                             SprinklerScheduleTime* start_time) : controller_(controller),
                                                                  clock_(clock),
                                                                  start_time_(start_time) {
  }

  void setup() override;
  void loop() override;
  void dump_config() override;

  void add_valve(const sprinkler::SprinklerControllerSwitch* enable_sw,
                 const sprinkler::SprinklerControllerNumber* duration_num) {
    this->valves_.push_back({enable_sw, duration_num});
  }

 protected:
  ESPPreferenceObject pref_;

  sprinkler::Sprinkler* controller_ = {nullptr};
  time::RealTimeClock* clock_ = {nullptr};  // TODO can't make const?
  SprinklerScheduleTime* start_time_ = {nullptr};
  ScheduleOnTimeTrigger* start_time_trigger_;

  std::time_t last_run_timestamp_;
  std::time_t next_run_timestamp_;

  std::vector<Valve> valves_;

  void on_start_time_();

  void update_timestamp_sensor_(sensor::Sensor* sensor, std::time_t time, bool ignore_enabled = false);
  void update_estimated_duration_sensor_();

  bool is_enabled_() const { return (this->enable_switch_ == nullptr || this->enable_switch_->state); }
  uint8_t get_cycle_repetitions_() const;

  void recalculate_next_run_();
  std::time_t calculate_next_run_(std::time_t from, uint32_t days) const;
  void run_(const ESPTime *now, bool update_timestamps = true);
};

class SprinklerScheduleTime : public datetime::TimeEntity {
 public:
  void set_initial_value(ESPTime initial_value) { this->initial_value_ = initial_value; }

  void setup() {
    // Attempt to load previous value from flash
    this->pref_ = global_preferences->make_preference<datetime::TimeEntityRestoreState>(this->get_object_id_hash());
    datetime::TimeEntityRestoreState temp = {};
    if (this->pref_.load(&temp)) {
      temp.apply(this);
      return;
    }

    // Use initial value if restore isn't successful
    this->hour_ = this->initial_value_.hour;
    this->minute_ = this->initial_value_.minute;
    this->second_ = this->initial_value_.second;
    this->publish_state();
  }

  void control(const datetime::TimeCall& call) override {
    // Update and publish state
    this->hour_ = call.get_hour().value_or(this->hour_);
    this->minute_ = call.get_minute().value_or(this->minute_);
    this->second_ = call.get_second().value_or(this->second_);
    this->publish_state();

    // Save value to flash for restore
    datetime::TimeEntityRestoreState temp = {
        .hour = this->hour_,
        .minute = this->minute_,
        .second = this->second_,
    };
    this->pref_.save(&temp);
  }

 protected:
  ESPPreferenceObject pref_;
  ESPTime initial_value_{};
};

class ScheduleOnTimeTrigger : public datetime::OnTimeTrigger {
 public:
  void set_on_time_callback(std::function<void()> callback) { this->on_time_ = callback; }

  void trigger() {
    // Call callback
    if (this->on_time_)
      this->on_time_();

    // Call original trigger in case user defined an automation
    OnTimeTrigger::trigger();
  };

 protected:
  std::function<void()> on_time_;
};

class SprinklerScheduleButton : public button::Button {
 public:
 protected:
  void press_action() {}  // Do nothing
};

}  // namespace sprinkler_schedule
}  // namespace esphome