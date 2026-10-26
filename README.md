<div align="center">

<img src="contrib-heatmap.svg" width="860" alt="GitHub contribution heatmap for evanyap7, cells dropping in on a diagonal wave">

<br>

<img src="contrib-skyline.svg" width="860" alt="The same year as a 3D skyline, one block per day">

</div>

<br>

<table align="center">
  <tr>
    <td width="440" valign="middle"><img src="evan-ascii.svg" width="440" alt="ASCII portrait of Evan"></td>
    <td width="420" valign="middle"><img src="info-card.svg" width="420" alt="About Evan"></td>
  </tr>
</table>

<div align="center">

<br>

<img src="now.svg" width="860" alt="now.txt">

</div>

<br>

## The same year, four more ways

<div align="center">

<img src="contrib-pulse.svg" width="860" alt="Weekly contribution totals as a line that draws itself">

<sub>**Pulse** · each week's total on one line, with the busiest week marked</sub>

<br><br>

<img src="contrib-ring.svg" width="860" alt="Contributions as concentric weekday rings swept by a clock hand">

<sub>**Ring** · weekdays are the rings, weeks are the spokes, a clock hand reveals the year</sub>

<br><br>

<img src="contrib-streak.svg" width="860" alt="The current streak traced day by day across the last twelve weeks">

<sub>**Streak** · the current run traced day by day, ending at the last day off</sub>

<br><br>

<img src="contrib-terminal.svg" width="860" alt="Contributions typed out as ASCII characters">

<sub>**Terminal** · every day scrambles, then settles on <code>. : + # @</code> by activity level</sub>

</div>

<br>

<details>
<summary>How this works</summary>

<br>

A profile README can't run JavaScript, so each view is a self-contained animated SVG generated from my own contribution data.

1. `scripts/fetch_contributions.py` reads the public contributions page and saves a small `data/contributions.json` (date, count, level for each day, plus streaks). No token needed, and the images never call GitHub themselves.
2. `scripts/render_heatmap_svg.py`, `render_skyline_svg.py` and `render_views_svg.py` turn that file into the six SVGs. Animation is plain CSS and SMIL: per-cell delays create the diagonal wave, the skyline's square-root heights stop one huge day flattening everything else, and each view plays once then holds the finished frame.
3. A GitHub Action (`.github/workflows/update-profile-art.yml`) re-runs all of it every six hours and commits the result as me, so the graphs stay current without anyone touching them.

Users with reduced-motion turned on get the finished frame immediately. Hover any cell for its exact count and date.

</details>
