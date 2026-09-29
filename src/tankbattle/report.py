"""Turn a finished match's statistics into a three-panel matplotlib chart, as PNG bytes or a file.

Panels: cumulative damage over time, accuracy per player, and a log of every shot
(power vs. angle, filled when it hit). Uses matplotlib's object-oriented `Figure` rather
than `pyplot`, so it needs no window and is safe to call from a background thread.
"""

import io
from pathlib import Path

from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from tankbattle.stats import summarize

FIGURE_SIZE = (9.6, 3.6)  # inches; at 100 dpi that is 960 x 360 px, sized to fit the game window
DPI = 100
_BACKGROUND = "#f4f4f2"


def _escape(text: str) -> str:
    """Stop matplotlib treating a `$` in a player name as the start of math text."""
    return text.replace("$", r"\$")


def _color(info: dict) -> tuple[float, float, float]:
    r, g, b = info["color"]
    return r / 255, g / 255, b / 255


def _plot_damage_over_time(ax, match: dict) -> None:
    ax.set_title("Damage dealt over time")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Cumulative damage")
    end = max(match["duration_s"], 1.0)
    for key, info in match["players"].items():
        shots = [s for s in match["shots"] if s["player_id"] == int(key)]
        times, totals, total = [0.0], [0.0], 0.0
        for shot in shots:
            total += shot["damage_dealt"]
            times.append(shot["time_s"])
            totals.append(total)
        times.append(end)
        totals.append(total)
        color = _color(info)
        ax.step(times, totals, where="post", color=color, linewidth=2, label=_escape(info["name"]))
        ax.plot(
            [s["time_s"] for s in shots if s["hit"]],
            [t for t, s in zip(totals[1:], shots) if s["hit"]],
            "o",
            color=color,
            markersize=5,
        )
    ax.set_xlim(0, end)
    ax.set_ylim(bottom=0)
    ax.legend(fontsize=8, loc="upper left")


def _plot_accuracy(ax, match: dict) -> None:
    ax.set_title("Accuracy")
    ax.set_ylabel("Shots that hit (%)")
    ax.set_ylim(0, 118)  # headroom so the "hits/shots" label above a 100% bar isn't clipped
    ax.set_yticks(range(0, 101, 20))
    summary = summarize(match)
    for x, (key, info) in enumerate(match["players"].items()):
        stats = summary[int(key)]
        ax.bar(x, stats["accuracy"] * 100, color=_color(info), width=0.6)
        ax.text(x, stats["accuracy"] * 100 + 2, f"{stats['hits']}/{stats['shots']}", ha="center", fontsize=9)
    ax.set_xticks(range(len(match["players"])))
    ax.set_xticklabels([_escape(info["name"]) for info in match["players"].values()], fontsize=8)


def _plot_shot_log(ax, match: dict) -> None:
    ax.set_title("Every shot: aim vs. result")
    ax.set_xlabel("Power (%)")
    ax.set_ylabel("Angle (degrees)")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 180)
    for key, info in match["players"].items():
        color = _color(info)
        shots = [s for s in match["shots"] if s["player_id"] == int(key)]
        hits = [s for s in shots if s["hit"]]
        misses = [s for s in shots if not s["hit"]]
        ax.scatter(
            [s["power"] for s in hits],
            [s["angle"] for s in hits],
            s=[30 + 3 * s["damage_dealt"] for s in hits],
            color=color,
            edgecolor="black",
            linewidth=0.6,
        )
        ax.scatter([s["power"] for s in misses], [s["angle"] for s in misses], marker="x", color=color, s=28)
    ax.legend(
        handles=[
            Line2D(
                [], [], marker="o", linestyle="", color="gray", markeredgecolor="black", label="hit (size = damage)"
            ),
            Line2D([], [], marker="x", linestyle="", color="gray", label="miss"),
        ],
        fontsize=7,
        loc="lower left",
    )


def _title(match: dict) -> str:
    winner = match["players"].get(str(match["winner_id"]))
    result = f"{_escape(winner['name'])} won" if winner else "Draw"
    minutes, seconds = divmod(int(match["duration_s"]), 60)
    return f"{result}  -  {minutes}m {seconds:02d}s  -  {len(match['shots'])} shots fired"


def build_figure(match: dict) -> Figure:
    """Draw the three panels for one match and return the figure."""
    figure = Figure(figsize=FIGURE_SIZE, dpi=DPI, facecolor=_BACKGROUND)
    axes = figure.subplots(1, 3, gridspec_kw={"width_ratios": [1.3, 0.8, 1.2]})
    for ax in axes:
        ax.set_facecolor("white")
        ax.tick_params(labelsize=8)
        ax.title.set_fontsize(10)
        ax.xaxis.label.set_fontsize(8)
        ax.yaxis.label.set_fontsize(8)
        ax.grid(alpha=0.3)
    _plot_damage_over_time(axes[0], match)
    _plot_accuracy(axes[1], match)
    _plot_shot_log(axes[2], match)
    figure.suptitle(_title(match), fontsize=12, fontweight="bold")
    figure.tight_layout(rect=(0, 0, 1, 0.94))
    return figure


def build_report(match: dict) -> bytes:
    """Render the match chart and return it as PNG bytes."""
    buffer = io.BytesIO()
    build_figure(match).savefig(buffer, format="png", facecolor=_BACKGROUND)
    return buffer.getvalue()


def save_report(match: dict, path: str | Path) -> Path:
    """Render the match chart to a PNG file and return its path."""
    path = Path(path)
    path.write_bytes(build_report(match))
    return path
