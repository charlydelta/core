"""Constants for the Learning Sensor integration."""

from homeassistant.const import Platform

DOMAIN = "learning"
PLATFORMS = [Platform.BINARY_SENSOR]
ATTR_OBSERVATIONS = "observations"
ATTR_OCCURRED_OBSERVATION_ENTITIES = "occurred_observation_entities"
ATTR_CLASSIFICATION_SCORE = "classification_score"
ATTR_CLASSIFICATION_SCORE_THRESHOLD = "classification_score_threshold"

CONF_OBSERVATIONS = "observations"
CONF_TEMPLATE = "template"
CONF_NUMERIC_STATE = "numeric_state"
CONF_CLASSIFICATION_SCORE_THRESHOLD = "classification_score_threshold"

DEFAULT_NAME = "Learning Binary Sensor"
DEFAULT_CLASSIFICATION_SCORE_THRESHOLD = 0.5
