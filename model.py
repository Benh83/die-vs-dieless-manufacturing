"""
machina-industrial-scale-enablement / model.py

Question: how does dieless robotic forming (Machina Labs RoboCraftsman) change
the size of custom metal-fabrication firm that can break even, and be efficient,
with firm size measured in employees and in units produced per year?

Setting
-------
A small firm designs and sells custom, doubly curved (non-developable) aluminum
facade and canopy panels. Every order is a new geometry, built as a batch of
n identical units. Three ways to make each geometry:

  T  Tooled     - a draw die per geometry, pressed at a host shop
  H  Hand       - skilled employees form each panel over a CNC-milled buck
  M  Machina    - parts bought from a Machina RoboCraftsman factory

Notation
--------
  Q  units sold per year            n  units per design (batch size)
  D  designs won per year = Q / n   w  quote win rate (falls with lead time)
  L  qualified leads needed = D / w N  employees (owner included)

  hours(Q)  = L*h_quote + D*h_design + Q*h_unit
  capacity  = N * h_year * max(0.4, 1 - m*(N-1))   (coordination loss m per coworker)
  lead cost = c_L * [L + Ls/(g+1) * (L/Ls)^(g+1)]  (marginal c_L*(1+(L/Ls)^g))

  TC(Q, N)  = N*(salary + overhead per head) + fixed
              + D*c_design + Q*c_unit + lead cost          if hours(Q) <= capacity(N)

Short run: N fixed. AC and MC over Q up to capacity.
Long run:  the firm picks the smallest N that can do the hours.
           LRAC(Q) = TC(Q, N*(Q)) / Q.  MES = argmin LRAC.  Minimum viable
           firm = smallest Q (and its N) where price >= LRAC.

All numbers are synthetic and meant to be argued with. Pure Python, no
dependencies, so the same file runs in CPython and in the browser (Pyodide).
"""

import json
import math

VERSION = "2.0"

ROUTES = {
    "T": "Tooled (draw die)",
    "H": "Hand-formed",
    "M": "Machina",
}
ROUTE_ORDER = ["T", "H", "M"]

SCENARIOS = {
    "s1": "Worst case for Machina: parts ship from the Los Angeles factory",
    "s2": "Best case for Machina: hypothetical regional Machina factory",
}

N_MAX = 25          # largest headcount considered
Q_CAP = 6000        # hard ceiling on units/yr the model will search


def P(id, group, label, unit, lo, hi, step, default, route="all", hint=""):
    return dict(id=id, group=group, label=label, unit=unit, min=lo, max=hi,
                step=step, default=default, route=route, hint=hint)


PARAMS = [
    # ---------------------------------------------------------------- firm
    P("N", "Firm", "Employees (owner included)", "", 1, N_MAX, 1, 3,
      hint="Everyone on payroll. No contractors: hours beyond capacity are simply not available."),
    P("salary", "Firm", "Cost per employee, fully loaded", "$", 40000, 200000, 1000, 85000,
      hint="Salary, payroll tax and benefits. One blended rate for designers, estimators and craftspeople."),
    P("ohHead", "Firm", "Overhead per employee", "$", 0, 40000, 500, 9000,
      hint="Floor space, tools, software seats and insurance that grow with headcount."),
    P("hrsYear", "Firm", "Productive hours per employee per year", "hr", 1000, 2400, 50, 1850,
      hint="Hours actually spent on quoting, design, forming and handling."),
    P("mgmt", "Firm", "Coordination loss per additional coworker", "%", 0, 5, 0.25, 1.5,
      hint="Each extra person costs everyone this share of their hours in meetings and handoffs. The organizational source of diseconomies of scale."),
    P("fixOH", "Firm", "Fixed overhead (annual)", "$", 0, 150000, 1000, 30000,
      hint="Accounting, legal, general liability, office. Does not grow with headcount."),
    P("rate", "Firm", "Cost of capital", "%", 0, 30, 0.5, 10,
      hint="Charged on per-design outlays from order until the customer pays."),
    P("payTerms", "Firm", "Customer payment terms after delivery", "wk", 0, 16, 1, 6,
      hint="Net-30 to net-60 plus retainage is normal in construction."),

    # -------------------------------------------------------------- market
    P("price", "Market", "Price per panel", "$", 1000, 30000, 250, 7500,
      hint="4 x 10 ft doubly curved aluminum panel, supplied not installed. About $2,080/m² ($193/ft²)."),
    P("n", "Market", "Units per design (batch size)", "", 1, 25, 1, 5,
      hint="How many identical panels share one geometry. Freeform facades often run 1 to 6."),
    P("leadCost", "Market", "Marketing cost per qualified lead", "$", 0, 3000, 25, 400,
      hint="Bid boards, trade shows, sample panels, per architect or contractor who asks for a quote."),
    P("winBase", "Market", "Win rate if delivery were instant", "%", 5, 95, 1, 45,
      hint="Share of quotes that become orders before lead time is considered."),
    P("halfLife", "Market", "Lead time that halves the win rate", "wk", 1, 40, 1, 8,
      hint="Construction schedules punish slow suppliers."),
    P("leadSat", "Market", "Local market depth (leads/yr before lead cost doubles)", "", 20, 2000, 10, 200,
      hint="Custom facade work is regional and thin. The demand-side source of rising marginal cost."),
    P("gamma", "Market", "Market saturation curvature", "x", 1, 4, 0.5, 3,
      hint="How sharply lead cost climbs past market depth."),
    P("fixMkt", "Market", "Base marketing (annual)", "$", 0, 100000, 1000, 15000,
      hint="Website, portfolio photography, AIA and CSI memberships."),
    P("changeProb", "Market", "Chance the architect revises after tooling is made", "%", 0, 80, 1, 20,
      hint="A die absorbs a revision badly, a buck moderately, a toolpath cheaply."),

    # -------------------------------------------------------------- labor hours
    P("hrsQuote", "Hours", "Hours per quote (won or lost)", "hr", 0, 20, 0.5, 3),
    P("hrsUnit", "Hours", "Hours per unit: handling, QC, install coordination", "hr", 0, 10, 0.25, 2),
    P("hrsDesignT", "Hours", "Design hours per geometry", "hr", 0, 80, 1, 16, "T",
      "Geometry must be made die-formable: draw depth, addendum, springback."),
    P("hrsDesignH", "Hours", "Design hours per geometry", "hr", 0, 80, 1, 14, "H",
      "Buck model plus a forming plan for the craftspeople."),
    P("hrsDesignM", "Hours", "Design hours per geometry", "hr", 0, 80, 1, 10, "M",
      "CAD goes straight to toolpath with fewer formability constraints."),

    # -------------------------------------------------------------- material
    P("netMat", "Material", "Aluminum in the finished panel", "$", 20, 1500, 10, 210,
      hint="3.6 m² of 3 mm 5052 ≈ 29 kg at about $7/kg delivered."),
    P("coat", "Material", "Coating and packing per panel", "$", 0, 1500, 10, 250,
      hint="PVDF paint or anodize. Same for every route."),
    P("utilT", "Material", "Material utilization", "%", 30, 100, 1, 70, "T", "Binder and addendum trimmed after the draw."),
    P("utilH", "Material", "Material utilization", "%", 30, 100, 1, 80, "H", "Near-net blanks, trimmed by hand."),
    P("utilM", "Material", "Material utilization", "%", 30, 100, 1, 60, "M", "The clamping frame border is scrap."),

    # -------------------------------------------------------------- tooled
    P("dieCost", "Tooled", "Draw die per geometry", "$", 5000, 300000, 1000, 45000, "T",
      "Large 4 x 10 ft draw die. Soft zinc-alloy or epoxy $20k–60k; hardened steel $100k+."),
    P("dieEng", "Tooled", "Die design engineering", "$", 0, 30000, 500, 5000, "T", "Often left out of the die quote."),
    P("tryout", "Tooled", "Tryout and first article", "$", 0, 30000, 500, 4000, "T"),
    P("changeCost", "Tooled", "Die rework when the design changes", "%", 0, 100, 5, 30, "T", "Share of die cost."),
    P("dieStore", "Tooled", "Die storage or disposal", "$", 0, 5000, 50, 300, "T"),
    P("inspectT", "Tooled", "First-article inspection per geometry", "$", 0, 5000, 50, 600, "T"),
    P("setupHrs", "Tooled", "Press setup hours per job", "hr", 0, 16, 0.5, 4, "T"),
    P("runHrs", "Tooled", "Press hours per panel", "hr", 0.05, 3, 0.05, 0.4, "T"),
    P("pressRate", "Tooled", "Press host rate", "$", 50, 800, 5, 225, "T", "Large-bed press, per hour."),
    P("trimT", "Tooled", "5-axis laser trim per panel", "$", 0, 1000, 10, 180, "T"),

    # -------------------------------------------------------------- hand
    P("buckCost", "Hand-formed", "CNC-milled buck per geometry", "$", 0, 20000, 250, 3500, "H",
      "MDF or foam form the craftspeople shape the panel against."),
    P("hrsFormH", "Hand-formed", "Forming hours per panel", "hr", 5, 200, 1, 60, "H",
      "English wheel, stretching, planishing, weld repair. Coachbuilders spend 40–100+ hours on a hood-sized panel."),
    P("scrapH", "Hand-formed", "Rework or scrap rate", "%", 0, 50, 1, 15, "H",
      "Panels that miss the ±2 mm joint tolerance and are remade."),
    P("inspectH", "Hand-formed", "3-D scan per geometry", "$", 0, 5000, 50, 400, "H"),
    P("trimH", "Hand-formed", "Trim and edge prep per panel", "$", 0, 1000, 10, 120, "H"),
    P("equipH", "Hand-formed", "Forming shop (annual)", "$", 0, 150000, 1000, 30000, "H",
      "Wheels, power hammer, welders, extra floor space."),

    # -------------------------------------------------------------- machina
    P("mNRE", "Machina", "Programming and first article per geometry", "$", 0, 20000, 250, 3500, "M",
      "Toolpath, frame setup, first-part scan. Synthetic: Machina publishes no pricing."),
    P("mHrs", "Machina", "Robot hours per panel (form, scan, trim)", "hr", 0.5, 30, 0.5, 5, "M"),
    P("mRate", "Machina", "Cell rate per robot-hour", "$", 50, 1000, 10, 300, "M", "Including Machina's margin. Synthetic."),
    P("finishM", "Machina", "Surface finishing per panel", "$", 0, 1000, 10, 180, "M",
      "Stated finish is 125 µin Ra, so visible faces are blended before coating."),
    P("trimM", "Machina", "Residual deburr per panel", "$", 0, 500, 5, 25, "M"),

    # -------------------------------------------------------------- logistics
    P("shipBase", "Logistics", "Handling per shipped panel", "$", 0, 500, 5, 60),
    P("freight", "Logistics", "Freight per panel-mile", "$", 0.05, 2, 0.01, 0.35),
    P("milesH", "Logistics", "Miles: own shop to site", "mi", 0, 1000, 5, 40, "H"),

    # -------------------------------------------------------------- scenario-specific
    P("milesT", "Scenario", "Miles: die host to site", "mi", 0, 3000, 5, {"s1": 25, "s2": 60}, "T"),
    P("milesM", "Scenario", "Miles: Machina factory to site", "mi", 0, 3000, 10, {"s1": 1800, "s2": 150}, "M",
      "Worst case: the Los Angeles factory. Best case: a regional factory that does not exist yet."),
    P("crateM", "Scenario", "Crating per panel", "$", 0, 600, 10, {"s1": 150, "s2": 40}, "M"),
    P("leadT", "Scenario", "Lead time", "wk", 1, 30, 0.5, {"s1": 10, "s2": 10.5}, "T",
      "Die design, build, tryout and run."),
    P("leadH", "Scenario", "Lead time", "wk", 1, 30, 0.5, {"s1": 5, "s2": 5}, "H"),
    P("leadM", "Scenario", "Lead time", "wk", 0.5, 30, 0.5, {"s1": 2, "s2": 1}, "M",
      "Machina: first parts typically within a week of CAD. Worst case adds cross-country freight."),
    P("coordT", "Scenario", "Supplier coordination hours per geometry", "hr", 0, 40, 0.5, {"s1": 2, "s2": 5}, "T"),
    P("coordM", "Scenario", "Supplier coordination hours per geometry", "hr", 0, 40, 0.5, {"s1": 6, "s2": 2}, "M",
      "Remote reviews and time-zone delay versus a short drive."),
    P("tripsM", "Scenario", "Site visits to Machina per geometry", "", 0, 2, 0.05, {"s1": 0.25, "s2": 0.25}, "M"),
    P("tripCost", "Scenario", "Cost per visit", "$", 0, 5000, 50, {"s1": 1800, "s2": 200}, "M"),
    P("dieMove", "Scenario", "Die transport per geometry", "$", 0, 3000, 50, {"s1": 0, "s2": 300}, "T"),
    P("supplierM", "Scenario", "Supplier onboarding and audits (annual)", "$", 0, 50000, 500, {"s1": 6000, "s2": 3000}, "M"),
]

PARAM_INDEX = {p["id"]: p for p in PARAMS}


def defaults():
    return {p["id"]: (dict(p["default"]) if isinstance(p["default"], dict) else p["default"]) for p in PARAMS}


def _get(v, key, scen):
    x = v[key]
    return x[scen] if isinstance(x, dict) else x


class Route:
    """Cost structure of one production route in one scenario."""

    def __init__(self, v, scen, r):
        g = lambda k: float(_get(v, k, scen))
        self.r = r
        self.n = max(1.0, g("n"))
        self.price = g("price")
        lead = {"T": g("leadT"), "H": g("leadH"), "M": g("leadM")}[r]
        self.lead = lead
        self.w = g("winBase") / 100.0 * 0.5 ** (lead / g("halfLife"))
        self.cL, self.Ls, self.gam = g("leadCost"), g("leadSat"), g("gamma")
        self.h_quote, self.h_year, self.mgmt = g("hrsQuote"), g("hrsYear"), g("mgmt") / 100.0
        self.per_head = g("salary") + g("ohHead")
        chg = g("changeProb") / 100.0
        fin = lambda x: x * g("rate") / 100.0 * (lead + g("payTerms")) / 52.0
        ship = lambda miles, crate=0.0: g("shipBase") + g("freight") * miles + crate

        if r == "T":
            die = g("dieCost")
            nre = die + g("dieEng") + g("tryout")
            self.per_design = (nre + chg * g("changeCost") / 100.0 * die + g("dieStore") + g("inspectT")
                               + g("setupHrs") * g("pressRate") + fin(nre) + g("dieMove"))
            self.unit = dict(material=g("netMat") / (g("utilT") / 100.0) + g("coat"),
                             process=g("runHrs") * g("pressRate"),
                             finishing=g("trimT"),
                             logistics=ship(g("milesT")))
            self.h_design = g("hrsDesignT") + g("coordT")
            self.h_unit = g("hrsUnit")
            self.fixed = g("fixMkt") + g("fixOH")
        elif r == "H":
            s = g("scrapH") / 100.0
            buck = g("buckCost")
            self.per_design = buck + chg * 0.5 * buck + g("inspectH") + fin(buck)
            self.unit = dict(material=g("netMat") / (g("utilH") / 100.0) * (1 + s) + g("coat"),
                             process=0.0,  # the forming is done by employees: it shows up as payroll
                             finishing=g("trimH"),
                             logistics=ship(g("milesH")))
            self.h_design = g("hrsDesignH")
            self.h_unit = g("hrsUnit") + g("hrsFormH") * (1 + s)
            self.fixed = g("fixMkt") + g("fixOH") + g("equipH")
        else:
            nre = g("mNRE")
            self.per_design = nre + chg * 0.25 * nre + fin(nre) + g("tripsM") * g("tripCost")
            self.unit = dict(material=g("netMat") / (g("utilM") / 100.0) + g("coat"),
                             process=g("mHrs") * g("mRate"),
                             finishing=g("finishM") + g("trimM"),
                             logistics=ship(g("milesM"), g("crateM")))
            self.h_design = g("hrsDesignM") + g("coordM")
            self.h_unit = g("hrsUnit")
            self.fixed = g("fixMkt") + g("fixOH") + g("supplierM")
        self.c_unit = sum(self.unit.values())
        # hours per unit, all-in (quoting and design spread over the batch)
        self.h_per_q = self.h_quote / (self.n * self.w) + self.h_design / self.n + self.h_unit

    # ---- pieces
    def leads(self, Q):
        return Q / self.n / self.w

    def acquisition(self, Q):
        L = self.leads(Q)
        return self.cL * (L + self.Ls / (self.gam + 1.0) * (L / self.Ls) ** (self.gam + 1.0))

    def hours(self, Q):
        return Q * self.h_per_q

    def capacity(self, N):
        return N * self.h_year * max(0.4, 1.0 - self.mgmt * (N - 1))

    def q_cap(self, N):
        return self.capacity(N) / self.h_per_q

    def variable(self, Q):
        """All non-payroll, non-fixed cost of producing Q."""
        return Q / self.n * self.per_design + Q * self.c_unit + self.acquisition(Q)

    def payroll(self, N):
        return N * self.per_head

    def tc(self, Q, N):
        return self.variable(Q) + self.fixed + self.payroll(N)

    def mc(self, Q):
        h = max(1e-3, Q * 1e-4)
        return (self.variable(Q + h) - self.variable(max(1e-6, Q - h))) / (Q + h - max(1e-6, Q - h))

    def n_needed(self, Q):
        """Smallest headcount that can do the hours for Q, or None."""
        need = self.hours(Q)
        for N in range(1, N_MAX + 1):
            if self.capacity(N) >= need:
                return N
        return None

    def parts(self, Q, N):
        d = Q / self.n
        out = {
            "tooling": d * self.per_design,
            "marketing": self.acquisition(Q) + 0.0,
            "payroll": self.payroll(N),
            "material": Q * self.unit["material"],
            "process": Q * self.unit["process"],
            "finishing": Q * self.unit["finishing"],
            "logistics": Q * self.unit["logistics"],
            "fixed": self.fixed,
        }
        return out


def _grid(qmax, pts):
    return [max(0.25, qmax * (i / pts) ** 1.6) for i in range(1, pts + 1)]


def _bisect(f, a, b, it=50):
    fa = f(a)
    for _ in range(it):
        m = 0.5 * (a + b)
        fm = f(m)
        if (fm >= 0) == (fa >= 0):
            a, fa = m, fm
        else:
            b = m
    return 0.5 * (a + b)


def long_run(rt, pts=500):
    """Long-run analysis: firm picks the cheapest feasible headcount at each Q."""
    qmax = min(Q_CAP, rt.q_cap(N_MAX))
    grid = _grid(qmax, pts)
    rows = []
    for Q in grid:
        N = rt.n_needed(Q)
        if N is None:
            continue
        tc = rt.tc(Q, N)
        rows.append((Q, N, tc / Q, rt.price * Q - tc))
    if not rows:
        return None
    # MES: minimum of LRAC
    mes = min(rows, key=lambda r: r[2])
    # minimum viable firm: first Q with profit >= 0
    first = None
    for i, r in enumerate(rows):
        if r[3] >= 0:
            if i > 0:
                N = r[1]
                q = _bisect(lambda x: rt.price * x - rt.tc(x, N), max(0.25, rows[i - 1][0]), r[0])
                if rt.n_needed(q) != N:  # step in headcount inside the interval
                    q = r[0]
                first = (q, N)
            else:
                first = (r[0], r[1])
            break
    last = None
    if first:
        for r in reversed(rows):
            if r[3] >= 0:
                last = (r[0], r[1])
                break
    best = max(rows, key=lambda r: r[3])
    half = min(rows, key=lambda r: abs(r[0] - mes[0] / 2))
    near = [r for r in rows if r[2] <= mes[2] * 1.05]
    return {
        "eff_lo_q": near[0][0], "eff_hi_q": near[-1][0], "eff_lo_n": near[0][1], "eff_hi_n": near[-1][1],
        "mes_q": mes[0], "mes_n": mes[1], "lrac_min": mes[2],
        "penalty_half": half[2] / mes[2] - 1.0,
        "viable": first is not None,
        "min_q": first[0] if first else None, "min_n": first[1] if first else None,
        "max_q": last[0] if last else None, "max_n": last[1] if last else None,
        "pmax_q": best[0], "pmax_n": best[1], "pmax": best[3],
        "q_limit": qmax,
    }


def viability_by_headcount(rt, pts=500):
    """For each N: range of Q (within capacity) where profit with exactly N employees >= 0."""
    out = []
    for N in range(1, N_MAX + 1):
        cap = min(Q_CAP, rt.q_cap(N))
        grid = _grid(cap, pts // 2)
        lo = hi = None
        for Q in grid:
            if rt.price * Q - rt.tc(Q, N) >= 0:
                if lo is None:
                    lo = Q
                hi = Q
        out.append({"N": N, "lo": lo, "hi": hi, "cap": cap,
                    "at_cap": hi is not None and hi >= cap * 0.995})
    return out


def short_run(rt, N, xmax, pts=220):
    cap = rt.q_cap(N)
    top = min(cap, xmax)
    grid = [top * i / pts for i in range(1, pts + 1)]
    ac = [rt.tc(q, N) / q for q in grid]
    mc = [rt.mc(q) for q in grid]
    # break-even with this N
    lo = hi = None
    f = lambda q: rt.price * q - rt.tc(q, N)
    prev = None
    for q in grid:
        s = f(q) >= 0
        if prev is not None and s and not prev[1] and lo is None:
            lo = _bisect(f, prev[0], q)
        if prev is not None and not s and prev[1] and lo is not None and hi is None:
            hi = _bisect(f, prev[0], q)
        prev = (q, s)
    if lo is None and grid and f(grid[0]) >= 0:
        lo = grid[0]
    # short-run MES: argmin AC within capacity
    i = min(range(len(ac)), key=lambda k: ac[k])
    sr_min_q, sr_min_ac = grid[i], ac[i]
    interior = sr_min_q < top * 0.99
    return {"q": grid, "ac": ac, "mc": mc, "cap": cap, "be_lo": lo, "be_hi": hi,
            "sr_min_q": sr_min_q, "sr_min_ac": sr_min_ac, "interior": interior,
            "capped_by_chart": cap > xmax}


def _route_summary(rt):
    return {"w": rt.w, "lead": rt.lead, "per_design": rt.per_design, "c_unit": rt.c_unit,
            "unit": rt.unit, "h_per_q": rt.h_per_q, "units_per_employee": rt.h_year / rt.h_per_q,
            "fixed": rt.fixed}


def compute(state):
    """Everything the page needs, for one set of assumptions."""
    v = defaults()
    for k, x in state.get("v", {}).items():
        if k in v:
            v[k] = x
    scen = state.get("scen", "s1")
    N = int(_get(v, "N", scen))
    out = {"version": VERSION, "scen": scen, "N": N, "routes": {}, "cases": {}, "batch": {}}

    rts = {r: Route(v, scen, r) for r in ROUTE_ORDER}
    lr = {r: long_run(rts[r]) for r in ROUTE_ORDER}

    # chart ranges
    marks = []
    for r in ROUTE_ORDER:
        if lr[r]:
            marks += [lr[r]["mes_q"]] + ([lr[r]["min_q"]] if lr[r]["min_q"] else [])
    x_lr = min(Q_CAP, max(60.0, 1.35 * max(marks or [100.0])))
    x_sr = min(Q_CAP, max(40.0, 1.08 * max(rts[r].q_cap(N) for r in ROUTE_ORDER)))
    x_sr = min(x_sr, max(80.0, 2.5 * max([lr[r]["mes_q"] for r in ROUTE_ORDER if lr[r]] or [100.0])))

    lr_grid = [x_lr * (i / 240) for i in range(1, 241)]
    for r in ROUTE_ORDER:
        rt = rts[r]
        lrac = []
        nstar = []
        for q in lr_grid:
            n_ = rt.n_needed(q)
            lrac.append(rt.tc(q, n_) / q if n_ else None)
            nstar.append(n_)
        out["routes"][r] = {
            "name": ROUTES[r],
            "summary": _route_summary(rt),
            "long": lr[r],
            "lrac": {"q": lr_grid, "ac": lrac, "n": nstar},
            "short": short_run(rt, N, x_sr),
            "bands": viability_by_headcount(rt),
        }

    # both scenarios, long run
    for s in SCENARIOS:
        out["cases"][s] = {}
        for r in ROUTE_ORDER:
            rt = rts[r] if s == scen else Route(v, s, r)
            l = lr[r] if s == scen else long_run(rt, 300)
            out["cases"][s][r] = {"long": l, "w": rt.w, "n": rt.n}

    # minimum viable firm by batch size (long run)
    n_hi = max(20, int(_get(v, "n", scen)))
    for r in ROUTE_ORDER:
        rows = []
        for nn in range(1, n_hi + 1):
            vv = dict(v)
            vv["n"] = nn
            l = long_run(Route(vv, scen, r), 240)
            rows.append({"n": nn, "min_q": l["min_q"] if l else None, "min_n": l["min_n"] if l else None,
                         "mes_q": l["mes_q"] if l else None})
        out["batch"][r] = rows

    # cost breakdown at a chosen volume
    q_eval = float(state.get("q_eval", 100))
    br = {}
    for r in ROUTE_ORDER:
        rt = rts[r]
        need = rt.n_needed(q_eval)
        n_use = max(N, need or N)
        br[r] = {"parts": rt.parts(q_eval, n_use), "n_used": n_use, "n_needed": need,
                 "feasible_at_N": rt.q_cap(N) >= q_eval}
    out["breakdown"] = {"q": q_eval, "routes": br}
    return out


def compute_json(state_json):
    return json.dumps(compute(json.loads(state_json)))


def meta_json():
    return json.dumps({"params": PARAMS, "routes": ROUTES, "route_order": ROUTE_ORDER,
                       "scenarios": SCENARIOS, "n_max": N_MAX, "version": VERSION})


# ------------------------------------------------------------------ CLI
def _fmt(x, money=False):
    if x is None:
        return "never"
    return ("$" if money else "") + f"{x:,.0f}"


def summary_table(v=None):
    v = v or defaults()
    lines = ["| Scenario | Route | Min viable units/yr | Employees at min | Designs/yr at min | "
             "MES units/yr | Employees at MES | Min LRAC | Units per employee | Quote win rate |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for s in SCENARIOS:
        for r in ROUTE_ORDER:
            rt = Route(v, s, r)
            l = long_run(rt)
            lines.append("| {} | {} | {} | {} | {} | {} | {} | {} | {:.0f} | {:.0f}% |".format(
                s, ROUTES[r], _fmt(l["min_q"]), l["min_n"] or "—",
                f"{l['min_q'] / rt.n:.1f}" if l["min_q"] else "—",
                _fmt(l["mes_q"]), l["mes_n"], _fmt(l["lrac_min"], True),
                rt.h_year / rt.h_per_q, rt.w * 100))
    return "\n".join(lines)


def assumptions_csv(path):
    import csv
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "group", "label", "unit", "route", "default_s1", "default_s2", "min", "max", "note"])
        for p in PARAMS:
            d = p["default"] if isinstance(p["default"], dict) else {"s1": p["default"], "s2": p["default"]}
            w.writerow([p["id"], p["group"], p["label"], p["unit"],
                        {"all": "all", "T": "tooled", "H": "hand", "M": "machina"}[p["route"]],
                        d["s1"], d["s2"], p["min"], p["max"], p["hint"]])


if __name__ == "__main__":
    import sys
    if "--json" in sys.argv:
        print(json.dumps(compute({"scen": "s1"}), indent=1))
    elif "--csv" in sys.argv:
        assumptions_csv("assumptions.csv")
        print("wrote assumptions.csv")
    else:
        print(summary_table())
