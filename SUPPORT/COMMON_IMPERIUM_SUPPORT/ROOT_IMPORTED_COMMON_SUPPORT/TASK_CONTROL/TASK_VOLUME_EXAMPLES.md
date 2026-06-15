# Task Volume Examples V0.1

## SMALL example

- task_size_class: SMALL
- organ_count: 1
- checkpoint_required: false
- checkpoint_cadence: END_ONLY

## LARGE example

- task_size_class: LARGE
- organ_count: 4
- checkpoint_required: true
- checkpoint_cadence: PER_STAGE
- split_required_if includes mixed schema + runner + reporting planes

## MEGA example

- task_size_class: MEGA
- organ_count: 8
- checkpoint_required: true
- checkpoint_cadence: PER_STAGE
- continuation_protocol_required: true
- phases cover control docs, builders, validation, sweep, packaging
