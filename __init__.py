"""Double Band Filter plugin.

This plugin provides an operator to filter a float-valued field on two ranges
simultaneously.
|
"""

import json

from bson import json_util

import fiftyone as fo
import fiftyone.operators as foo
from fiftyone.operators import types
from fiftyone import ViewField as F


def serialize_view(view):
    return json.loads(json_util.dumps(view._serialize()))


def _get_float_fields(dataset):
    return list(dataset.get_field_schema(ftype=fo.FloatField).keys())


def _filter_view(view, left_min, left_max, right_min, right_max, field):
    left_cond = (F(field) > left_min) & (F(field) < left_max)
    right_cond = (F(field) > right_min) & (F(field) < right_max)
    return view.match(left_cond | right_cond)


class MatchEitherBand(foo.Operator):
    @property
    def config(self):
        _config = foo.OperatorConfig(
            name="match_either_band",
            label="Double Band Filter: filter a float-valued field on two ranges simultaneously",
            dynamic=True,
        )
        _config.icon = "/assets/icon.svg"
        return _config

    def resolve_input(self, ctx):
        inputs = types.Object()
        form_view = types.View(
            label="Double Band Filter: filter a float-valued field on two ranges simultaneously"
        )

        float_fields = _get_float_fields(ctx.dataset)
        if len(float_fields) == 0:

            inputs.view(
                "warning",
                types.Warning(
                    label="No float-valued fields found in dataset",
                    description="Message description",
                ),
            )
            return types.Property(inputs, view=form_view)

        field_choices = types.RadioGroup()

        for ff in float_fields:
            field_choices.add_choice(ff, label=ff)

        inputs.enum(
            "field",
            field_choices.values(),
            label="Float-valued field to filter",
            description="Select a float-valued field to filter",
            view=types.DropdownView(),
            required=True,
        )

        field = ctx.params.get("field", None)
        if field:
            min, max = ctx.view.bounds(field)
        else:
            min, max = 0, 1

        obj = types.Object()
        obj.float(
            "left_min",
            label="Left Min",
            description="Minimum value for left band",
            view=types.FieldView(space=3),
        )
        obj.float(
            "left_max",
            label="Left Max",
            description="Maximum value for left band",
            required=True,
            view=types.FieldView(space=3),
        )
        obj.float(
            "right_min",
            label="Right Min",
            description="Minimum value for right band",
            required=True,
            view=types.FieldView(space=3),
        )
        obj.float(
            "right_max",
            label="Right Max",
            description="Maximum value for right band",
            required=True,
            view=types.FieldView(space=3),
        )
        inputs.define_property("range_bounds", obj)

        range_bounds = ctx.params.get("range_bounds", {})

        left_min = range_bounds.get("left_min", None)
        left_max = range_bounds.get("left_max", None)
        right_min = range_bounds.get("right_min", None)
        right_max = range_bounds.get("right_max", None)

        if left_min and min and left_min < min:
            inputs.view(
                "error",
                types.Error(
                    label="Out of bounds: Left",
                    description="Left Min is out of bounds",
                ),
            )

        elif left_min and left_max and left_min > left_max:
            inputs.view(
                "error",
                types.Error(
                    label="Empty Left Band",
                    description="Left Min is greater than Left Max",
                ),
            )

        elif right_max and max and right_max > max:
            inputs.view(
                "error",
                types.Error(
                    label="Out of bounds: Right",
                    description="Right Max is out of bounds",
                ),
            )

        elif right_min and right_max and right_min > right_max:
            inputs.view(
                "error",
                types.Error(
                    label="Empty Right Band",
                    description="Right Min is greater than Right Max",
                ),
            )

        elif left_max and right_min and left_max > right_min:
            inputs.view(
                "error",
                types.Error(
                    label="Overlapping Bands",
                    description="Left Max is greater than Right Min",
                ),
            )

        return types.Property(inputs, view=form_view)

    def execute(self, ctx):
        field = ctx.params.get("field", None)
        range_bounds = ctx.params.get("range_bounds", {})

        left_min = range_bounds.get("left_min", None)
        left_max = range_bounds.get("left_max", None)
        right_min = range_bounds.get("right_min", None)
        right_max = range_bounds.get("right_max", None)

        view = _filter_view(
            ctx.view, left_min, left_max, right_min, right_max, field
        )
        ctx.trigger(
            "set_view",
            params=dict(view=serialize_view(view)),
        )


def register(plugin):
    plugin.register(MatchEitherBand)
