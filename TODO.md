- Don't show mixer elements that aren't in use. Instead, have a separate button
  for adding inputs to be mixed.
  Adding or removing a mixer input should destroy the corresponding widgets in
  the GUI, as well as setting up the routing in ALSA. This will mean all inputs
  can be listed as stereo or mono, but the user can decide which way to route
  it arbitrarily.

- Add README

- Show startup errors in GUI as well as via `logger.error`

- Use decibels (requires adding support in pyalsaaudio)

- Don't allow routing directly from inputs (other than PCM) - use a mix
  instead. No technical reason for this but it's not really a useful use case
  and having all the extra menu entries makes it annoying to select sources for
  each output.

- Identify headphone/line outputs from the ALSA mixer names

- Support aliases for input names
