## Double Band Filter Plugin

![match_either_band](https://github.com/jacobmarks/double-band-filter-plugin/assets/12500356/5e51740b-f528-40ea-acb1-f66358b69aaa)

This plugin provides an operator to filter a float-valued field on two ranges
simultaneously.

Choose a field from the drop-down, and then specify two ranges. The operator
will return all samples where the field value is in the first range or the
second range. Behind the scenes, this is implemented using FiftyOne
ViewExpressions and the `match()` method.

## Installation

```shell
fiftyone plugins download https://github.com/jacobmarks/double-band-filter-plugin/
```

## Operators

### `match_either_band`

Filter a float-valued field on two ranges simultaneously. The operator will
return all samples where the field value is in the first range or the second
range.
