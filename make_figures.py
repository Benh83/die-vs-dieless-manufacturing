"""Regenerate the README figures and key numbers from model.py.
Usage:  python make_figures.py        (needs matplotlib)"""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import model

OUT = pathlib.Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)
COL = {"T": "#C2611F", "H": "#8A6FB0", "M": "#1F4FA3"}
INK, MUTED, GRID = "#0C0E10", "#6C757D", "#E8EBED"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": INK,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.spines.top": False, "axes.spines.right": False})


def style(ax, title, sub=None):
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color=INK, pad=26 if sub else 12)
    if sub:
        ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=9.5, color=MUTED, va="bottom")
    ax.set_axisbelow(True)


def spread(ys, gap):
    """Nudge label y positions (data units) apart so they don't overlap."""
    order = sorted(range(len(ys)), key=lambda i: ys[i])
    out = list(ys)
    for a, b in zip(order, order[1:]):
        if out[b] - out[a] < gap:
            out[b] = out[a] + gap
    return out


def end_labels(ax, items, x, gap):
    """items: list of (route, y). Draws colored-square + ink name just right of x."""
    ys = spread([y for _, y in items], gap)
    for (r, _), y in zip(items, ys):
        ax.annotate("\u25A0", (x, y), xytext=(6, 0), textcoords="offset points", color=COL[r],
                    va="center", fontsize=10, annotation_clip=False)
        ax.annotate(SHORT[r], (x, y), xytext=(18, 0), textcoords="offset points", color=INK,
                    va="center", fontsize=10, fontweight="bold", annotation_clip=False)


SHORT = {"T": "Tooled", "H": "Hand-formed", "M": "Machina"}


def firm_map(o, path):
    R = o["routes"]
    live = [r for r in model.ROUTE_ORDER if any(b["lo"] for b in R[r]["bands"])]
    dead = [r for r in model.ROUTE_ORDER if r not in live]
    last = max(b["N"] for r in live for b in R[r]["bands"] if b["lo"])
    rows = list(range(1, last + 1))
    lane, lg = 0.34, 0.08
    fig, ax = plt.subplots(figsize=(10, 0.36 * len(rows) + 1.9), dpi=150)
    for i in rows:
        for k, r in enumerate(live):
            b = R[r]["bands"][i - 1]
            if not b["lo"]:
                continue
            y = i + (k - (len(live) - 1) / 2) * (lane + lg)
            ax.barh(y, b["hi"] - b["lo"], left=b["lo"], height=lane, color=COL[r], lw=0)
            if b["at_cap"]:
                ax.plot([b["hi"], b["hi"]], [y - lane * 0.75, y + lane * 0.75], color=INK, lw=2, solid_capstyle="butt", zorder=4)
            ax.annotate(f"{b['lo']:,.0f}\u2013{b['hi']:,.0f}", (b["hi"], y), xytext=(6, 0), textcoords="offset points",
                        va="center", fontsize=7.5, color="#3B434A", family="DejaVu Sans Mono")
    for k, r in enumerate(live):
        l = R[r]["long"]
        if l["viable"]:
            y = l["mes_n"] + (k - (len(live) - 1) / 2) * (lane + lg)
            ax.plot(l["mes_q"], y, "o", ms=8, color=COL[r], mec="white", mew=1.5, zorder=3)
    ax.set_xscale("log")
    lo = min(b["lo"] for r in live for b in R[r]["bands"] if b["lo"])
    hi = max(b["hi"] for r in live for b in R[r]["bands"] if b["lo"])
    ax.set_xlim(lo * 0.8, hi * 1.9)
    ticks = [t for t in (20, 50, 100, 200, 500, 1000, 2000, 5000) if lo * 0.8 <= t <= hi * 1.9]
    ax.set_xticks(ticks)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_ylim(last + 0.7, 0.3)
    ax.set_yticks(rows)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=GRID, lw=1)
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Panels per year (log scale)")
    ax.set_ylabel("Employees")
    handles = [matplotlib.patches.Patch(color=COL[r], label=model.ROUTES[r]) for r in live]
    handles += [matplotlib.lines.Line2D([], [], color=INK, lw=2, marker="|", ms=10, ls="none", label="ran out of hours"),
                matplotlib.lines.Line2D([], [], marker="o", color="#3B434A", mec="white", ms=8, ls="none", label="minimum efficient scale")]
    handles += [matplotlib.patches.Patch(color=COL[r], label=f"{model.ROUTES[r]}: not profitable at any headcount") for r in dead]
    ax.legend(handles=handles, frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, fontsize=8.5,
              handlelength=1.4, columnspacing=1.6, borderaxespad=0.3)
    style(ax, "Where a firm can survive", None)
    ax.set_title("Where a firm can survive", loc="left", fontsize=13, fontweight="bold", color=INK, pad=44)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def lrac(o, price, path):
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    xmax = o["routes"]["M"]["lrac"]["q"][-1]
    ymax = max(price * 1.5, max(o["routes"][r]["long"]["lrac_min"] for r in model.ROUTE_ORDER) * 1.2)
    ends, labels = [], []
    for r in model.ROUTE_ORDER:
        L = o["routes"][r]["lrac"]
        ys = [y if y is not None else float("nan") for y in L["ac"]]
        ax.plot(L["q"], ys, color=COL[r], lw=2)
        last = [y for q, y in zip(L["q"], ys) if y == y and y <= ymax]
        if last:
            ends.append((r, last[-1]))
        l = o["routes"][r]["long"]
        ax.plot(l["mes_q"], l["lrac_min"], "o", ms=8, color=COL[r], mec="white", mew=1.5, zorder=4)
        labels.append((l["mes_q"], l["lrac_min"], f"MES {l['mes_q']:,.0f} \u00b7 ${l['lrac_min']:,.0f}"))
    for (x, y, t), r in zip(labels, model.ROUTE_ORDER):
        dy = -8 if r == "H" else -15   # hand label sits tight under its dot, clear of the Machina line
        ax.annotate(t, (x, y), xytext=(0, dy), va="top", textcoords="offset points", ha="center", fontsize=8.5,
                    fontweight="bold", color=INK, bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none", alpha=0.85))
    ax.axhline(price, color=INK, lw=1.2)
    ax.annotate(f"Price ${price:,.0f}", (0, price), xytext=(6, 4), textcoords="offset points", fontsize=9,
                fontweight="bold", color=INK, bbox=dict(boxstyle="square,pad=0.1", fc="white", ec="none"))
    ax.set_ylim(0, ymax)
    ax.set_xlim(0, xmax)
    end_labels(ax, ends, xmax, ymax * 0.045)
    ax.grid(axis="y", color=GRID, lw=1)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda y, _: f"${y/1000:.0f}k"))
    ax.set_xlabel("Panels per year")
    ax.set_ylabel("Long-run average cost per panel")
    style(ax, "Long-run average cost",
          "The firm hires the fewest people who can do the work; a route makes money below the price line. Dot = minimum efficient scale.")
    fig.tight_layout(); fig.subplots_adjust(right=0.86); fig.savefig(path); plt.close(fig)


def batch(o, path, cur):
    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=150)
    nmax = len(o["batch"]["M"])
    ends, notes = [], []
    ax.axvspan(cur - 0.5, cur + 0.5, color="#F3F4F5", zorder=0)
    for r in model.ROUTE_ORDER:
        rows = o["batch"][r]
        xs = [b["n"] for b in rows if b["min_q"]]
        ys = [b["min_q"] for b in rows if b["min_q"]]
        if not xs:
            notes.append(f"{model.ROUTES[r]} never breaks even")
            continue
        ax.plot(xs, ys, color=COL[r], lw=2, marker="o", ms=5, mec="white", mew=1)
        if xs[0] > 1:
            ax.annotate(f"{SHORT[r]} starts at {xs[0]}", (xs[0], ys[0]), xytext=(-6, 9), textcoords="offset points",
                        ha="left", fontsize=8.5, fontweight="bold", color=INK)
        ends.append((r, ys[-1]))
    ymax = max(y for r in model.ROUTE_ORDER for y in [b["min_q"] for b in o["batch"][r]] if y) * 1.15
    ax.set_ylim(0, ymax)
    ax.set_xlim(0.5, nmax + 0.5)
    ax.set_xticks(range(1, nmax + 1))
    end_labels(ax, ends, nmax + 0.5, ymax * 0.06)
    ax.grid(axis="y", color=GRID, lw=1)
    ax.set_xlabel("Panels per design")
    ax.set_ylabel("Break-even panels per year")
    style(ax, "Smallest viable firm by batch size",
          f"Lower is better. No line = that route cannot break even at that batch size. Shaded: default {cur} panels per design.")
    fig.tight_layout(); fig.subplots_adjust(right=0.86); fig.savefig(path); plt.close(fig)


if __name__ == "__main__":
    v = model.defaults()
    for s in model.SCENARIOS:
        o = model.compute({"scen": s})
        firm_map(o, OUT / f"firm_map_{s}.png")
        lrac(o, v["price"], OUT / f"lrac_{s}.png")
        batch(o, OUT / f"batch_{s}.png", v["n"])
    o = model.compute({"scen": "s1"})
    key = {s: {r: model.compute({"scen": s})["routes"][r]["long"] for r in model.ROUTE_ORDER} for s in model.SCENARIOS}
    key["batch_s1"] = {r: [(b["n"], b["min_q"], b["min_n"]) for b in o["batch"][r]] for r in model.ROUTE_ORDER}
    key["summary_s1"] = {r: o["routes"][r]["summary"] for r in model.ROUTE_ORDER}
    (OUT / "key_numbers.json").write_text(json.dumps(key, indent=1))
    print(model.summary_table())
    print("figures written to", OUT)
