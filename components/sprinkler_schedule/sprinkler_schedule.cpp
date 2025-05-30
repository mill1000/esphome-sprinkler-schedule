
#include "sprinkler_schedule.h"

#include "esphome/core/log.h"
#include "esphome/core/time.h"

namespace esphome {
namespace sprinkler_schedule {

static const char *const TAG = "sprinkler_schedule";

void SprinklerScheduleComponent::setup() {
  // Setup preferences
  this->pref_ = global_preferences->make_preference<SprinklerScheduleRestoreState>(RESTORE_STATE_VERSION ^ 0xFF00FF00); // TODO no hash for component?

  // Attempt to load previous state from flash
  SprinklerScheduleRestoreState restore_state = {};
  if (this->pref_.load(&restore_state)) {
    this->last_run_timestamp_ = restore_state.last_run_timestamp;
    this->next_run_timestamp_ = restore_state.next_run_timestamp;
  }
}

void SprinklerScheduleComponent::loop() {
}

void SprinklerScheduleComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "Sprinkler Schedule:");
}

void SprinklerScheduleComponent::update_next_run_timestamp_(std::time_t value) {
  this->next_run_timestamp_ = value;

  // Update sensor as needed
  if (this->next_run_sensor_ && value != this->next_run_sensor_->raw_state)
    this->next_run_sensor_->publish_state(value);
}

void SprinklerScheduleComponent::update_last_run_timestamp_(std::time_t value) {
  this->last_run_timestamp_ = value;

  // Update sensor as needed
  if (this->last_run_sensor_ && value != this->last_run_sensor_->raw_state)
    this->last_run_sensor_->publish_state(value);
}

void SprinklerScheduleComponent::update_estimated_duration_() {
  auto estimated_duration = 0;
  for (const auto &valve : this->valves_) {
    // Sum run duration of all enabled valves
    if (valve.enable_switch == nullptr || valve.enable_switch->state)
      estimated_duration += valve.duration_number->state;
  }

  // Apply repetitions
  estimated_duration *= this->get_cycle_repetitions_();

  // Update sensor as needed
  if (this->estimated_duration_sensor_ && estimated_duration != this->estimated_duration_sensor_->raw_state)
    this->estimated_duration_sensor_->publish_state(estimated_duration);
}

uint8_t SprinklerScheduleComponent::get_cycle_repetitions_() const {
  return this->repetitions_number_ == NULL ? 1 : this->repetitions_number_->state;
}


void SprinklerScheduleComponent::calculate_next_run_(std::time_t from, uint32_t days) {
  // Convert to local time and adjust for start time and days parameter
  struct tm *date = std::localtime(&from);
  date->tm_hour = start_time_->hour;
  date->tm_min = start_time_->minute;
  date->tm_sec = start_time_->second;
  date->tm_mday += days;

  // Update timestamp
  this->update_next_run_timestamp_(std::mktime(date));
}

void SprinklerScheduleComponent::run_() {
  // TODO controller must be in idle

  // Grab current time from clock
  const ESPTime &now = this->clock_->now();

  // Don't run if we're lacking a valid clock
  if (!now.is_valid())
    return;  // TODO set an error?

  // Copy schedule settings to controller
  for (uint8_t i = 0; i < this->valves_.size(); i++) {
    const auto& valve = this->valves_[i];

    // Copy valve enable switch state to the controller
    if (valve.enable_switch == nullptr || valve.enable_switch->state)
      controller_->enable_switch(i)->turn_on();
    else
      controller_->enable_switch(i)->turn_off();

    // Copy valve run duration to controller
    controller_->set_valve_run_duration(i, valve.duration_number->state);
  }

  // Copy repetitions to controller
  controller_->set_repeat(this->get_cycle_repetitions_() - 1);

  // Update last run timestamp
  this->update_last_run_timestamp_(now.timestamp);

  // Run the cycle
  controller_->start_full_cycle();

  // Calculate the next run time
  this->calculate_next_run_(now.timestamp, this->frequency_number_->state);
}

}  // namespace sprinkler_schedule
}  // namespace esphome