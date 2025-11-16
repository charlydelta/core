"""Sensor platform for Learning Sensor integration."""

from __future__ import annotations

import logging
import math
from typing import Any, NamedTuple

import voluptuous as vol

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ABOVE, CONF_BELOW, CONF_ENTITY_ID, CONF_PLATFORM
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_registry as er
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CONF_NUMERIC_STATE, CONF_P_GIVEN_F, CONF_P_GIVEN_T

_LOGGER = logging.getLogger(__name__)


def above_greater_than_below(config: dict[str, Any]) -> dict[str, Any]:
    """Validate above and below options.

    If the observation is of type/platform NUMERIC_STATE, then ensure that the
    value given for 'above' is not greater than that for 'below'. Also check
    that at least one of the two is specified.
    """
    if config[CONF_PLATFORM] == CONF_NUMERIC_STATE:
        above = config.get(CONF_ABOVE)
        below = config.get(CONF_BELOW)
        if above is None and below is None:
            _LOGGER.error(
                "For bayesian numeric state for entity: %s at least one of 'above' or 'below' must be specified",
                config[CONF_ENTITY_ID],
            )
            raise vol.Invalid("above_or_below")
        if above is not None and below is not None:
            if above > below:
                _LOGGER.error(
                    "For bayesian numeric state 'above' (%s) must be less than 'below' (%s)",
                    above,
                    below,
                )
                raise vol.Invalid("above_below")
    return config


NUMERIC_STATE_SCHEMA = vol.All(
    vol.Schema(
        {
            CONF_PLATFORM: CONF_NUMERIC_STATE,
            vol.Required(CONF_ENTITY_ID): cv.entity_id,
            vol.Optional(CONF_ABOVE): vol.Coerce(float),
            vol.Optional(CONF_BELOW): vol.Coerce(float),
            vol.Required(CONF_P_GIVEN_T): vol.Coerce(float),
            vol.Optional(CONF_P_GIVEN_F): vol.Coerce(float),
        },
        required=True,
    ),
    above_greater_than_below,
)


def no_overlapping(configs: list[dict]) -> list[dict]:
    """Validate that intervals are not overlapping.

    For a list of observations ensure that there are no overlapping intervals
    for NUMERIC_STATE observations for the same entity.
    """
    numeric_configs = [
        config for config in configs if config[CONF_PLATFORM] == CONF_NUMERIC_STATE
    ]
    if len(numeric_configs) < 2:
        return configs

    class NumericConfig(NamedTuple):
        above: float
        below: float

    d: dict[str, list[NumericConfig]] = {}
    for _, config in enumerate(numeric_configs):
        above = config.get(CONF_ABOVE, -math.inf)
        below = config.get(CONF_BELOW, math.inf)
        entity_id: str = str(config[CONF_ENTITY_ID])
        d.setdefault(entity_id, []).append(NumericConfig(above, below))

    for ent_id, intervals in d.items():
        intervals = sorted(intervals, key=lambda tup: tup.above)

        for i, tup in enumerate(intervals):
            if len(intervals) > i + 1 and tup.below > intervals[i + 1].above:
                _LOGGER.error(
                    "Ranges for bayesian numeric state entities must not overlap, but %s has overlapping ranges, above:%s, below:%s overlaps with above:%s, below:%s",
                    ent_id,
                    tup.above,
                    tup.below,
                    intervals[i + 1].above,
                    intervals[i + 1].below,
                )
                raise vol.Invalid(
                    "overlapping_ranges",
                )
    return configs


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Initialize Learning Sensor config entry."""
    registry = er.async_get(hass)
    # Validate + resolve entity registry id to entity_id
    entity_id = er.async_validate_entity_id(
        registry, config_entry.options[CONF_ENTITY_ID]
    )
    # TODO Optionally validate config entry options before creating entity
    name = config_entry.title
    unique_id = config_entry.entry_id

    async_add_entities([LearningBinarySensorEntity(unique_id, name, entity_id)])


class LearningBinarySensorEntity(BinarySensorEntity):
    """Learning Sensor."""

    def __init__(self, unique_id: str, name: str, wrapped_entity_id: str) -> None:
        """Initialize learning Sensor."""
        super().__init__()
        self._wrapped_entity_id = wrapped_entity_id
        self._attr_name = name
        self._attr_unique_id = unique_id
