Programs to generate sector data for _Faster Than Light: Nomad_.
As of this writing, the format is somewhat idiosyncratic.
Conversion to <https://travellermap.com/make/poster> formats are for the
future.

## Usage

```
```

## TODO

- Run pylint or something similar on code.

- Add docstrings.

- Generate _Nomad_ planets?
  - Distinguish stars and planets?
  - Inputs:
    - Settlement Level (if not random)
    - Prevailing Technology Age
  - Outputs:
    - Trade Class
    - Physical Characteristic (fn of Trade Class & random roll)
    - Population (fn of Trade Class and random roll)
    - Technology Age (fn of Prevailing if given & random roll)
    - World Tag 1 (random)
    - World Tag 2 (random)
