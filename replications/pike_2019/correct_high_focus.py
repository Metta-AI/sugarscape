"""Explicit experiment: reverse only the released high-focus comparison."""

import inspect
import textwrap

import organization

original_source = textwrap.dedent(inspect.getsource(organization.rules.step_high))
assert original_source.count("max(highest) > max(new)") == 1
corrected_source = original_source.replace(
    "max(highest) > max(new)", "max(highest) < max(new)"
)
namespace = {}
exec(  # noqa: S102 -- Compile the pinned author method with exactly one declared operator change.
    compile(corrected_source, "<corrected-high-focus>", "exec"),
    vars(organization),
    namespace,
)
organization.rules.step_high = namespace["step_high"]
