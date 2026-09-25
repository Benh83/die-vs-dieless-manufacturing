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


def style(ax, title):
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", color=INK, pad=12)
    ax.grid(axis="y", color=GRID, lw=1)
    ax.set_axisbelow(True)


def firm_map(o, path, n_show=15):
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=150)
    w = 0.24
    for k, r in enumerate(model.ROUTE_ORDER):
        for b in o["routes"][r]["bands"][:n_show]:
            if b["lo"] is None:
                continue
            x = b["N"] + (k - 1) * (w + 0.02)
            ax.bar(x, b["hi"] - b["lo"], bottom=b["lo"], width=w, color=COL[r],
                   label=model.ROUTES[r] if b["N"] == min(bb["N"] for bb in o["routes"][r]["bands"] if bb["lo"]) else None)
        l = o["routes"][r]["long"]
        if l["viable"] and l["mes_n"] <= n_show:
            ax.plot(l["mes_n"] + (k - 1) * (w + 0.02), l["mes_q"], "o", ms=8, color=COL[r], mec="white", mew=1.5)
    ax.set_yscale("log")
    ax.set_ylim(20, 3000)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda y, _: f"{y:,.0f}"))
    ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_yticks([20, 50, 100, 200, 500, 1000, 2000])
    if not any(b["lo"] for b in o["routes"]["T"]["bands"]):
        ax.text(0.99, 0.03, "Tooled (draw die): not viable at any headcount", transform=ax.transAxes,
                ha="right", color=COL["T"], fontsize=9)
    ax.set_xticks(range(1, n_show + 1))
    ax.set_xlabel("Employees")
    ax.set_ylabel("Panels per year (log)")
    style(ax, "Where a firm can survive: profitable output by headcount (dot = MES)")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def lrac(o, price, path):
    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=150)
    for r in model.ROUTE_ORDER:
        L = o["routes"][r]["lrac"]
        ax.plot(L["q"], [y if y is not None else float("nan") for y in L["ac"]], color=COL[r], lw=2, label=model.ROUTES[r])
        l = o["routes"][r]["long"]
        ax.plot(l["mes_q"], l["lrac_min"], "o", ms=8, color=COL[r], mec="white", mew=1.5)
    ax.axhline(price, color=INK, lw=1.2)
    ax.text(ax.get_xlim()[1] if False else L["q"][-1], price, f"  price ${price:,.0f}", va="bottom", ha="right", color=INK, fontsize=9)
    ax.set_ylim(0, price * 2.2)
    ax.set_xlim(0, L["q"][-1])
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda y, _: f"${y/1000:.0f}k"))
    ax.set_xlabel("Panels per year")
    ax.set_ylabel("Long-run average cost per panel")
    style(ax, "Long-run average cost (firm hires the fewest people who can do the work)")
    ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def batch(o, path):
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=150)
    rows = o["batch"]["M"]
    w = 0.26
    ymax = max(b["min_q"] for r in model.ROUTE_ORDER for b in o["batch"][r] if b["min_q"])
    for k, r in enumerate(model.ROUTE_ORDER):
        for b in o["batch"][r]:
            x = b["n"] + (k - 1) * (w + 0.02)
            if b["min_q"] is None:
                ax.bar(x, ymax * 1.05, width=w, color="none", edgecolor=COL[r], hatch="////", lw=0, alpha=0.35)
            else:
                ax.bar(x, b["min_q"], width=w, color=COL[r], label=model.ROUTES[r] if b is next(bb for bb in o["batch"][r] if bb["min_q"]) else None)
    ax.set_xticks([b["n"] for b in rows])
    ax.set_xlabel("Panels per design")
    ax.set_ylabel("Smallest viable panels per year")
    style(ax, "Smallest viable firm by batch size (hatched = never breaks even)")
    ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


if __name__ == "__main__":
    v = model.defaults()
    for s in model.SCENARIOS:
        o = model.compute({"scen": s})
        firm_map(o, OUT / f"firm_map_{s}.png")
        lrac(o, v["price"], OUT / f"lrac_{s}.png")
        batch(o, OUT / f"batch_{s}.png")
    o = model.compute({"scen": "s1"})
    key = {s: {r: model.compute({"scen": s})["routes"][r]["long"] for r in model.ROUTE_ORDER} for s in model.SCENARIOS}
    key["batch_s1"] = {r: [(b["n"], b["min_q"], b["min_n"]) for b in o["batch"][r]] for r in model.ROUTE_ORDER}
    key["summary_s1"] = {r: o["routes"][r]["summary"] for r in model.ROUTE_ORDER}
    (OUT / "key_numbers.json").write_text(json.dumps(key, indent=1))
    print(model.summary_table())
    print("figures written to", OUT)
