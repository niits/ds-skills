# Third-Party Notices

This file records third-party material that was adapted or used as a technical reference.
It supplements the repository's MIT license and does not relicense third-party material.
Ordinary citations used to support technical claims remain in the relevant skill files.

## K-Dense AI Scientific Agent Skills

Source:
[K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills)
(formerly linked as `claude-scientific-skills`). Relevant upstream skills include
`hypothesis-generation` and `scientific-visualization`.

Repository areas: `skills/banking-hypothesis-generation/` and portions of
`skills/visualization/`.

Changes: rewritten, reorganized, and expanded for banking use cases, Databricks output,
visualization workflows, and this repository's reference-file structure.

MIT License

Copyright (c) 2025 K-Dense Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Orchestra Research AI Research Skills

Source:
[Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs),
especially `20-ml-paper-writing/academic-plotting`.

Repository area: portions of `skills/visualization/references/`.

Changes: selected chart patterns were rewritten, reorganized, and integrated into the
broader visualization workflow.

MIT License

Copyright (c) 2025 Claude AI Research Skills Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## plotnine

Source: [has2k1/plotnine](https://github.com/has2k1/plotnine) and
[plotnine documentation](https://plotnine.org/).

Repository areas: plotnine examples and guidance in `skills/visualization/`.

The repository uses plotnine's public API in examples and its documentation as a
technical reference. If any substantial plotnine code is incorporated, it is covered by
the following notice.

The MIT License (MIT)

Copyright (c) 2022 Hassan Kibirige

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Posit Cheatsheets

Source: [rstudio/cheatsheets](https://github.com/rstudio/cheatsheets).

License: [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
(`CC-BY-4.0`). Copyright remains with the respective cheatsheet authors and Posit.

Repository area: plotnine and grammar-of-graphics guidance in
`skills/visualization/references/`.

Changes: quick-reference concepts were selected, rewritten, reorganized, and adapted to
Python/plotnine and Databricks usage. This notice identifies the source, links the source
and license, and marks the material as modified. No upstream branding or endorsement is
claimed.

## Color Palettes and Accessibility References

`skills/visualization/assets/color_palettes.py`,
`skills/visualization/assets/swd_style.py`, and
`skills/visualization/references/color-palettes.md` include palette values or guidance
attributed to the following sources:

- Masataka Okabe and Kei Ito, "Color Universal Design (CUD) - How to make figures and
  presentations that are friendly to Colorblind people," 2002, modified 2008:
  https://jfly.uni-koeln.de/color/
- Bang Wong, "Points of View: Color blindness," *Nature Methods* 8, 441 (2011). The
  `WONG` name in the asset is retained as an alias for the Okabe-Ito colors, not as a
  claim that Wong created a distinct palette.
- Paul Tol, "Colour schemes," SRON Netherlands Institute for Space Research:
  https://personal.sron.nl/~pault/
- Cynthia Brewer, Mark Harrower, and The Pennsylvania State University, ColorBrewer 2.0:
  https://colorbrewer2.org/

The repository reproduces short hexadecimal palette lists and colormap identifiers for
interoperability and attribution. No ownership of the underlying named palettes is
claimed. These sources do not all publish their surrounding prose, figures, or websites
under the repository's MIT license; do not infer permission to copy those materials from
their citation here.

## Storytelling with Data

Reference: Cole Nussbaumer Knaflic, *Storytelling with Data: A Data Visualization Guide
for Business Professionals*, Wiley, 2015.

Repository areas: communication and decluttering guidance in
`skills/visualization/references/` and the independently implemented helper functions in
`skills/visualization/assets/swd_style.py`.

The book is an all-rights-reserved reference, not bundled licensed material. This
repository claims no license to reproduce its text, tables, or figures. Chart-design
methods were used as conceptual input for independently written instructions, examples,
and code.
