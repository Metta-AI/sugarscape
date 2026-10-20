# Oremland–Laubenbacher landscape concordance

The published [Figure 8](https://www.jasss.org/17/2/6/Fig8-sugar-map.png) is a 300×300-pixel image with 6×6 pixels per model cell.
Its five dominant colors correspond to sugar capacities 0–4 under [Table 8](https://www.jasss.org/17/2/6.html).
The recovered 50×50 matrix matches all 2,500 cells of the retained NetLogo 5.3.1 and 6.1.1 Sugarscape maps.
The recovered text file is also byte-identical to both retained files, SHA-256 `cd9b4661c8813d3e268995676d5ba84394ee813986adb0d657dc9be4a1fab675`.

The comparison checks all eight rotations/reflections. Only the original file orientation matches exactly.
Cell capacities use the most frequent exact palette color within each 6×6 block.
Every cell has a unique winner; the smallest support is 10 pixels, with a minimum nine-pixel margin over another palette color.
The text labels contain antialiasing, including 40 non-gray pixels, which are excluded from exact palette counts.
An initial all-gray assertion failed on these label pixels; the final comparison counts full RGB colors instead.
No cell is filled from a neighboring cell or copied from the candidate NetLogo matrix.

| Capacity | Cell count |
| --- | ---: |
| 0 | 431 |
| 1 | 522 |
| 2 | 765 |
| 3 | 558 |
| 4 | 224 |

`result/cell-support.json` records the five palette counts for every cell.
`result/comparison.json` records the image and candidate file hashes, orientation comparisons, and scope.
`result/figure8-capacity.txt` contains the recovered matrix, with rows ordered from image top to bottom.

Reproduce using Python with NumPy and Pillow:

```sh
python compare.py /path/to/netlogo-5.3.1/sugar-map.txt \
  /path/to/netlogo-6.1.1/sugar-map.txt --output /path/to/fresh-result
```

This establishes the published capacity layout, not the identity of the author's original `.txt` file or execution environment.
The nearest-neighbor resampling convention, tax timing and negative-wealth handling, scaled agent classes, and original control schedules remain unresolved.
No simulation result or completed replication is claimed.

Figure attribution: Matthew Oremland and Reinhard Laubenbacher, *Optimization of Agent-Based Models: Scaling Methods and Heuristic Algorithms*, JASSS 17(2), 6 (2014), Figure 8, DOI 10.18564/jasss.2472.
