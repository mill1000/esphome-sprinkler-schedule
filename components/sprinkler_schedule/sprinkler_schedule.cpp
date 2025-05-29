
#include "sprinkler_schedule.h"

#include "esphome/core/log.h"

namespace esphome {
namespace sprinkler_schedule {

static const char *const TAG = "sprinkler_schedule";

void SprinklerScheduleComponent::setup() {
  // Setup preferences
  this->pref_ = global_preferences->make_preference<SprinklerScheduleRestoreState>(RESTORE_STATE_VERSION ^ this->get_object_id_hash());

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

void update_next_run_timestamp_(std::time_t value) {
  this->next_run_timestamp_ = value;

  // Update sensor as needed
  if (this->next_run_sensor_ && value != this->next_run_sensor_->raw_state)
    this->next_run_sensor_->publish_state(value);
}

void update_last_run_timestamp_(std::time_t value) {
  this->last_run_timestamp_ = value;

  // Update sensor as needed
  if (this->last_run_sensor_ && value != this->last_run_sensor_->raw_state)
    this->last_run_sensor_->publish_state(value);
}


}  // namespace sprinkler_schedule
}  // namespace esphome