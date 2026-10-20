"""Build explicitly parameterized reduced models from the qualified full model."""

import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("full_model", type=Path)
parser.add_argument("output", type=Path)
args = parser.parse_args()
model = args.full_model.read_text()
landscape = args.full_model.with_name("sugar-map.txt").read_bytes()
assert (
    hashlib.sha256(args.full_model.read_bytes()).hexdigest()
    == "1cc6ee9db0852ea2a071004aa31eb797a06131b434cffc82f697993057aca816"
)
assert (
    hashlib.sha256(landscape).hexdigest()
    == "cd9b4661c8813d3e268995676d5ba84394ee813986adb0d657dc9be4a1fab675"
)
capacities = [int(value) for value in landscape.split()]
assert len(capacities) == 2500 and set(capacities) == set(range(5))
args.output.mkdir(parents=True, exist_ok=False)
models = []
for width in [50, 40, 30, 20, 10, 5]:
    # Two common nearest-neighbor conventions, both exact at the original size.
    for mapping in ["pixel_centers", "aligned_endpoints"]:
        if mapping == "pixel_centers":
            indices = [(2 * index + 1) * 50 // (2 * width) for index in range(width)]
        else:
            # Round nonnegative source coordinates to nearest, with half ties up.
            indices = [
                (2 * index * 49 + width - 1) // (2 * (width - 1))
                for index in range(width)
            ]
        assert len(set(indices)) == width and min(indices) >= 0 and max(indices) < 50
        for rounding in ["nearest", "floor"]:
            name = f"{width}-{mapping}-{rounding}"
            output = args.output / name
            output.mkdir()
            population = 200 * width * width // 2500
            assert population * 2500 == 200 * width * width
            radii = list(range(1, 6)) if width == 50 else [1, 1, 1, 2, 2]
            if 10 < width < 50:
                radii[3:] = [
                    (vision * width + (25 if rounding == "nearest" else 0)) // 50
                    for vision in [4, 5]
                ]
            reduced = model
            if width != 50:
                replacements = {
                    "  vision-points   ;;": "  original-vision ;; unscaled class membership, with no extra random draw\n  vision-points   ;;",
                    "  resize-world 0 49 0 49": f"  resize-world 0 {width - 1} 0 {width - 1}",
                    "  set initial-population 200": f"  set initial-population {population}",
                    "  set vision random-in-range 1 5": "  set original-vision random-in-range 1 5\n  set vision item (original-vision - 1) "
                    + str(radii).replace(",", ""),
                    "      if vision > 3 [set category category + 2]": "      if original-vision > 3 [set category category + 2]",
                }
                for old, new in replacements.items():
                    assert reduced.count(old) == 1, old
                    reduced = reduced.replace(old, new)
            reduced_capacities = [
                capacities[y * 50 + x] for y in indices for x in indices
            ]
            if width == 50:
                assert indices == list(range(50)) and reduced == model
                reduced_landscape = landscape
            else:
                reduced_landscape = (
                    "\n".join(
                        " ".join(
                            str(value)
                            for value in reduced_capacities[y * width : (y + 1) * width]
                        )
                        for y in range(width)
                    )
                    + "\n"
                ).encode()
            (output / "oremland.nlogo").write_text(reduced)
            (output / "sugar-map.txt").write_bytes(reduced_landscape)
            models.append(
                {
                    "name": name,
                    "width": width,
                    "initial_population": population,
                    "mapping": mapping,
                    "rounding": rounding,
                    "source_indices": indices,
                    "radius_by_original_vision": radii,
                    "capacity_counts": {
                        str(value): reduced_capacities.count(value)
                        for value in range(5)
                    },
                    "model_sha256": hashlib.sha256(
                        (output / "oremland.nlogo").read_bytes()
                    ).hexdigest(),
                    "landscape_sha256": hashlib.sha256(reduced_landscape).hexdigest(),
                }
            )
protocol = {
    "source": "https://www.jasss.org/17/2/6.html sections 4.23–4.24 and Appendix B; dissertation PDF page 32 (printed 18)",
    "full_model_sha256": hashlib.sha256(args.full_model.read_bytes()).hexdigest(),
    "full_landscape_sha256": hashlib.sha256(landscape).hexdigest(),
    "builder_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "assumptions": [
        "Population scales with area at unchanged initial density 200/2500; the source says it scales but does not state its formula.",
        "Low original vision 1–3 maps to radius 1 in reduced models; original high vision 4–5 scales by n/50, with nearest or floor integer conversion.",
        "The paper explicitly assigns high vision 2 at widths 10 and 5. Other widths receive no additional clamp.",
        "Tax class is retained from unscaled vision, so shrinking a radius does not silently change the policy entry.",
        "The full-size model remains byte-identical; its original vision 1–5 is not collapsed to binary vision.",
        "Pixel-center and aligned-endpoint nearest-neighbor maps are declared alternatives, not recovered author settings.",
        "These alternatives are sensitivity cases, not an exhaustive resolution of all source ambiguity. No settings are selected based on published outcomes.",
    ],
    "models": models,
}
(args.output / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")
print(
    json.dumps(
        {
            "models": len(models),
            "distinct_model_landscape_pairs": len(
                {(row["model_sha256"], row["landscape_sha256"]) for row in models}
            ),
        }
    )
)
