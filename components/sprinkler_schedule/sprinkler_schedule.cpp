
#include "sprinkler_schedule.h"

#include "esphome/core/log.h"
#include "esphome/core/time.h"

namespace esphome {
namespace sprinkler_schedule {

static const char *const TAG = "sprinkler_schedule";

void SprinklerScheduleComponent::setup() {
  // Setup preferences
  this->pref_ = global_preferences->make_preference<SprinklerScheduleRestoreState>(RESTORE_STATE_VERSION ^ 0xABCD1234);
  // this->last_run_sensor_->get_object_id_hash()
  // Attempt to load previous state from flash
  SprinklerScheduleRestoreState restore_state = {};
  if (this->pref_.load(&restore_state)) {
    this->last_run_timestamp_ = restore_state.last_run_timestamp;
    this->next_run_timestamp_ = restore_state.next_run_timestamp;
  }

  // Call start time setup manually
  this->start_time_->setup();

  // Add callback to start time which will recalculate the next run time
  this->start_time_->add_on_state_callback([this]() { this->recalculate_next_run_(); });

  // Setup schedule on time trigger
  this->start_time_trigger_ = new ScheduleOnTimeTrigger();
  this->start_time_trigger_->set_parent((datetime::TimeEntity *)this->start_time_);
  this->start_time_trigger_->set_on_time_callback([this]() { this->on_start_time_(); });

  // Add callback to frequency number which will recalculate the next run time
  this->frequency_number_->add_on_state_callback([this](float value) { this->recalculate_next_run_(); });

  // Add callback to enable switch to recalculate next run when enabled
  if (this->enable_switch_) {
    this->enable_switch_->add_on_state_callback([this](bool state) {
      if (state)
        this->recalculate_next_run_();
    });
  }

  // Add callbacks to buttons
  if (this->run_now_button_) {
    this->run_now_button_->add_on_press_callback([this]() {
      // Run schedule and update timestamps
      const auto &now = this->clock_->now();
      if (now.is_valid())
        this->run_(&now);
      else
        ESP_LOGW(TAG, "Clock is not valid. Run cancelled.");
    });
  }

  if (this->run_tomorrow_button_) {
    this->run_tomorrow_button_->add_on_press_callback([this]() {
      // Reschedule 1 day from now
      const auto &now = this->clock_->now();
      if (now.is_valid())
        this->next_run_timestamp_ = this->calculate_next_run_(now.timestamp, 1);
      else
        ESP_LOGW(TAG, "Clock is not valid. Run not scheduled for tomorrow.");
    });
  }

  if (this->delay_button_) {
    this->delay_button_->add_on_press_callback([this]() {
      // Add 1 day to next run
      this->next_run_timestamp_ += SECONDS_IN_DAY;
    });
  }

  if (this->manual_run_button_) {
    this->manual_run_button_->add_on_press_callback([this]() {
      // Run schedule without updating timestamps
      this->run_(nullptr, false);
    });
  }

  if (this->reset_button_) {
    this->reset_button_->add_on_press_callback([this]() {
      // Recalculate next run
      this->recalculate_next_run_();
    });
  }
}

void SprinklerScheduleComponent::loop() {
  // Update trigger
  this->start_time_trigger_->loop();

  // Publish any updated sensor states
  this->update_timestamp_sensor_(this->last_run_sensor_, this->last_run_timestamp_, true);
  this->update_timestamp_sensor_(this->next_run_sensor_, this->next_run_timestamp_);
  this->update_estimated_duration_sensor_();
}

void SprinklerScheduleComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "Sprinkler Schedule:");

  LOG_SWITCH("  ", "Enable Switch", this->enable_switch_);
  LOG_DATETIME_TIME("  ", "Start Time", this->start_time_);

  LOG_SENSOR("  ", "Last Run Sensor", this->last_run_sensor_);
  LOG_SENSOR("  ", "Next Run Sensor", this->next_run_sensor_);
  LOG_SENSOR("  ", "Estimated Duration Sensor", this->estimated_duration_sensor_);

  LOG_NUMBER("  ", "Frequency Number", this->frequency_number_);
  LOG_NUMBER("  ", "Repetitions Number", this->repetitions_number_);

  LOG_BUTTON("  ", "Run Now Button", this->run_now_button_);
  LOG_BUTTON("  ", "Run Tomorrow Button", this->run_tomorrow_button_);
  LOG_BUTTON("  ", "Delay Button", this->delay_button_);
  LOG_BUTTON("  ", "Manual Run Button", this->manual_run_button_);
  LOG_BUTTON("  ", "Reset Button", this->reset_button_);

  for (uint8_t i = 0; i < this->valves_.size(); i++) {
    const auto &valve = this->valves_[i];

    ESP_LOGCONFIG(TAG, "  Valve %d:", i);
    LOG_SWITCH("    ", "Enable Switch", (switch_::Switch *)valve.enable_switch);
    LOG_NUMBER("    ", "Run Duration Number", (number::Number *)valve.duration_number);
  }
}

void SprinklerScheduleComponent::on_start_time_() {
  // Ignore if disabled
  if (!this->is_enabled_())
    return;

  // Grab current time from clock
  const ESPTime &now = this->clock_->now();

  // Ignore if clock is invalid or no run is scheduled
  if (!now.is_valid() || this->next_run_timestamp_ == 0) {
    ESP_LOGW(TAG, "Clock not valid or no run scheduled.");
    return;
  }

  // Return early if it's not time to run
  if (now.timestamp < this->next_run_timestamp_)
    return;

  // Run if controller is idle
  if (!this->is_controller_busy_())
    this->run_(&now);

  // Otherwise controller is busy, handle according to conflict resolution
  if (this->conflict_resolution_ == SKIP) {
    ESP_LOGI(TAG, "Controller is busy. Run skipped.");

    // Re-calculate next run if skipping
    this->next_run_timestamp_ = this->calculate_next_run_(now.timestamp, this->frequency_number_->state);
  } else if (this->conflict_resolution_ == QUEUE) {
    // Delay run by the time remaining in the current operation to the next 5 minute interval
    auto remaining = this->controller_->time_remaining_current_operation();

    // If paused, current operation doesn't have a value so default to 5 minutes
    auto delay_time = remaining.has_value() ? remaining.value() + 60 : 300;

    // Round to next 5 minute interval
    delay_time = 300 * std::ceil((float)delay_time / 300);

    ESP_LOGI(TAG, "Controller is busy. Run delayed for %d seconds.");

    this->next_run_timestamp_ += delay_time;
  }
}

void SprinklerScheduleComponent::update_timestamp_sensor_(sensor::Sensor *sensor, std::time_t time, bool ignore_enabled) {
  // Only update sensor if it exists
  if (sensor == nullptr)
    return;

  // Publish NAN/Unknown if schedule is disabled or value is not set
  float new_value = ((ignore_enabled || this->is_enabled_()) && time > 0) ? time : NAN;
  float old_value = sensor->raw_state;

  // Don't publish if both values are NAN
  if (isnan(new_value) && isnan(old_value))
    return;

  // Publish state if necessary
  if (new_value != old_value)
    sensor->publish_state(new_value);
}

void SprinklerScheduleComponent::update_estimated_duration_sensor_() {
  if (this->estimated_duration_sensor_ == nullptr)
    return;

  // Sum run duration of all enabled valves
  auto estimated_duration = 0;
  for (const auto &valve : this->valves_) {
    if (valve.is_enabled())
      estimated_duration += valve.get_duration_in_seconds();
  }

  // Apply repetitions
  estimated_duration *= this->get_cycle_repetitions_();

  // Update sensor as needed
  if (estimated_duration != this->estimated_duration_sensor_->raw_state)
    this->estimated_duration_sensor_->publish_state(estimated_duration);
}

uint8_t SprinklerScheduleComponent::get_cycle_repetitions_() const {
  return this->repetitions_number_ == NULL ? 1 : this->repetitions_number_->state;
}

void SprinklerScheduleComponent::recalculate_next_run_() {
  // Grab current time from clock
  const ESPTime &now = this->clock_->now();

  // Don't run if we're lacking a valid clock
  if (!now.is_valid()) {
    ESP_LOGW(TAG, "Clock is not valid. Failed to recalculate next run time.");
    return;  // TODO set an error?
  }

  // Use previous run if set, otherwise use current time
  auto from_time = this->last_run_timestamp_ ? this->last_run_timestamp_ : now.timestamp;

  // Calculate the next run time
  auto next = this->calculate_next_run_(from_time, this->frequency_number_->state);

  // If next run is in the past, schedule for tomorrow
  if (next < now.timestamp) {
    ESP_LOGI(TAG, "Calculated next run is in the past. Scheduling for tomorrow.");
    next = this->calculate_next_run_(now.timestamp, 1);
  }

  this->next_run_timestamp_ = next;
}

std::time_t SprinklerScheduleComponent::calculate_next_run_(std::time_t from, uint32_t days) const {
  // Convert to local time and adjust for start time and days parameter
  struct tm *date = std::localtime(&from);
  date->tm_hour = this->start_time_->hour;
  date->tm_min = this->start_time_->minute;
  date->tm_sec = this->start_time_->second;
  date->tm_mday += days;

  // Convert to timestamp
  return std::mktime(date);
}

void SprinklerScheduleComponent::run_(const ESPTime *now, bool update_timestamps) {
  // Don't start if controller is busy or in standby
  if (this->is_controller_busy_() || this->controller_->standby()) {
    ESP_LOGW(TAG, "Controller is busy or in standby. Run cancelled.");
    return;
  }

  // Copy schedule settings to controller
  for (uint8_t i = 0; i < this->valves_.size(); i++) {
    const auto &valve = this->valves_[i];

    // Copy valve enable switch state to the controller
    if (valve.is_enabled())
      this->controller_->enable_switch(i)->turn_on();
    else
      this->controller_->enable_switch(i)->turn_off();

    // Copy valve run duration to controller
    this->controller_->set_valve_run_duration(i, valve.get_duration_in_seconds());
  }

  // Copy repetitions to controller
  this->controller_->set_repeat(this->get_cycle_repetitions_() - 1);

  // Update last run timestamp
  if (update_timestamps)
    this->last_run_timestamp_ = now->timestamp;

  // Run the cycle
  this->controller_->start_full_cycle();

  // Calculate the next run time
  if (update_timestamps)
    this->next_run_timestamp_ = this->calculate_next_run_(now->timestamp, this->frequency_number_->state);
}

}  // namespace sprinkler_schedule
}  // namespace esphome