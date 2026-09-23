/* Die vs. Dieless — cost model
 * A small shop sells custom, 3-D sheet-metal construction products.
 * Every design is a new "instance"; each instance is built in a batch of n units.
 * Q = units sold per year, D = Q / n designs won per year.
 *
 * TC(Q) = Fixed + Acquisition(L) + Labor(H) + D·c_design + Q·c_unit
 *   L  = D / w                          qualified leads needed (w = win rate)
 *   w  = w0 · 0.5^(lead weeks / half-life)   slow lead times lose deals
 *   Acquisition(L) = cL · (L + Ls/(γ+1)·(L/Ls)^(γ+1))   marginal lead cost cL·(1+(L/Ls)^γ)
 *   H  = L·h_quote + D·(h_design + h_coord) + Q·h_unit
 *   Labor(H) = salary + max(0, H − capacity) · (salary/capacity) · premium
 * AC = TC/Q, MC = dTC/dQ. MES = argmin AC (where MC = AC).
 */
(function (root) {
  const P = [
    // ---- Market & demand ----
    { id: 'price', g: 'Market & demand', label: 'Price per unit', unit: '$', min: 1000, max: 25000, step: 250, def: 9000, tech: 'both',
      hint: 'What a GC or architect pays per custom formed panel, uninstalled. Bespoke formed facade metal runs roughly $150–400/ft²; a 4×8 ft panel ≈ $4.8k–12.8k.' },
    { id: 'n', g: 'Market & demand', label: 'Units per design (batch size)', unit: '', min: 1, max: 25, step: 1, def: 5, tech: 'both',
      hint: 'How many identical units each custom design sells. Your stated range is 1–10.' },
    { id: 'leadCost', g: 'Market & demand', label: 'Marketing cost per qualified lead', unit: '$', min: 0, max: 3000, step: 25, def: 400, tech: 'both',
      hint: 'Ads, trade-show share, bid-board fees, sample parts — per architect/GC who asks for a quote.' },
    { id: 'winBase', g: 'Market & demand', label: 'Win rate if delivery were instant', unit: '%', min: 5, max: 95, step: 1, def: 45, tech: 'both',
      hint: 'Share of quotes that become orders before lead time is considered.' },
    { id: 'halfLife', g: 'Market & demand', label: 'Weeks of lead time that halve the win rate', unit: 'wk', min: 1, max: 40, step: 1, def: 8, tech: 'both',
      hint: 'Construction schedules punish slow suppliers. At 8 wk, an 8-week die lead time wins half as many jobs as instant delivery.' },
    { id: 'leadSat', g: 'Market & demand', label: 'Local market depth (leads/yr before lead cost doubles)', unit: '', min: 20, max: 2000, step: 10, def: 200, tech: 'both',
      hint: 'Custom construction demand is local and thin. Past this many leads a year, each extra lead costs twice as much — the demand-side source of rising marginal cost.' },
    { id: 'gamma', g: 'Market & demand', label: 'Market saturation curvature', unit: 'x', min: 1, max: 4, step: 0.5, def: 3, tech: 'both',
      hint: 'How sharply lead cost climbs past market depth. 1 = linear, 4 = a wall.' },
    { id: 'fixMkt', g: 'Market & demand', label: 'Base marketing (annual)', unit: '$', min: 0, max: 100000, step: 1000, def: 15000, tech: 'both',
      hint: 'Website, portfolio photography, AIA/CSI memberships — spent regardless of volume.' },

    // ---- Labor & overhead ----
    { id: 'salary', g: 'Labor & overhead', label: 'The one employee, fully loaded', unit: '$', min: 30000, max: 200000, step: 1000, def: 85000, tech: 'both',
      hint: 'Salary + payroll tax + benefits for the single designer/estimator/PM.' },
    { id: 'hrsCap', g: 'Labor & overhead', label: 'Productive hours per year', unit: 'hr', min: 1000, max: 2600, step: 50, def: 1900, tech: 'both',
      hint: 'Past this, work goes to contractors at a premium — the labor source of rising marginal cost.' },
    { id: 'premium', g: 'Labor & overhead', label: 'Contract labor premium', unit: 'x', min: 1, max: 3, step: 0.05, def: 1.5, tech: 'both',
      hint: 'Multiple of the employee’s hourly cost paid for overflow hours.' },
    { id: 'hrsQuote', g: 'Labor & overhead', label: 'Hours per quote (won or lost)', unit: 'hr', min: 0, max: 20, step: 0.5, def: 3, tech: 'both',
      hint: 'Time spent with customers who may not buy. Lower win rates multiply this.' },
    { id: 'hrsDesignT', g: 'Labor & overhead', label: 'Design/DFM hours per design — die', unit: 'hr', min: 0, max: 80, step: 1, def: 16, tech: 'T',
      hint: 'Geometry has to be made die-formable: draw depth, addendum, springback allowance.' },
    { id: 'hrsDesignM', g: 'Labor & overhead', label: 'Design hours per design — Machina', unit: 'hr', min: 0, max: 80, step: 1, def: 10, tech: 'M',
      hint: 'Fewer formability constraints; CAD goes straight to toolpath.' },
    { id: 'hrsUnit', g: 'Labor & overhead', label: 'Hours per unit (handling, QC, install coordination)', unit: 'hr', min: 0, max: 10, step: 0.25, def: 2, tech: 'both', hint: '' },
    { id: 'fixOH', g: 'Labor & overhead', label: 'Overhead (annual)', unit: '$', min: 0, max: 150000, step: 1000, def: 30000, tech: 'both',
      hint: 'Insurance, CAD/CAM seats, small office, accounting, legal.' },
    { id: 'rate', g: 'Labor & overhead', label: 'Cost of capital', unit: '%', min: 0, max: 30, step: 0.5, def: 10, tech: 'both',
      hint: 'Applied to per-design outlays (dies, programming fees) from order until the customer pays.' },
    { id: 'payTerms', g: 'Labor & overhead', label: 'Customer payment terms after delivery', unit: 'wk', min: 0, max: 16, step: 1, def: 6, tech: 'both',
      hint: 'Net-30 to net-60 is normal in construction; retainage stretches it further.' },

    // ---- Material ----
    { id: 'netMat', g: 'Material', label: 'Steel in the finished part', unit: '$', min: 20, max: 1500, step: 10, def: 180, tech: 'both',
      hint: '4×8 ft of 10-ga A1011 ≈ 180 lb; ~$1/lb cut-to-size delivered (synthetic).' },
    { id: 'utilT', g: 'Material', label: 'Material utilization — die', unit: '%', min: 30, max: 100, step: 1, def: 72, tech: 'T',
      hint: 'Binder/addendum trimmed off after the draw.' },
    { id: 'utilM', g: 'Material', label: 'Material utilization — Machina', unit: '%', min: 30, max: 100, step: 1, def: 62, tech: 'M',
      hint: 'Incremental forming clamps the sheet in a frame; the border is scrap.' },

    // ---- Die route ----
    { id: 'dieCost', g: 'Die route', label: 'Die build cost per design', unit: '$', min: 3000, max: 250000, step: 1000, def: 25000, tech: 'T',
      hint: 'Mid-complexity progressive/draw dies usually quote $15k–50k; complex multi-stage dies $25k–150k+.' },
    { id: 'dieEng', g: 'Die route', label: 'Die design engineering', unit: '$', min: 0, max: 30000, step: 500, def: 4000, tech: 'T',
      hint: 'Often left out of the die quote ($3–5k typical).' },
    { id: 'tryout', g: 'Die route', label: 'Tryout & first article', unit: '$', min: 0, max: 30000, step: 500, def: 3000, tech: 'T',
      hint: 'Tryout blanks, press time, adjustments ($2–5k typical).' },
    { id: 'changeProb', g: 'Die route', label: 'Chance the customer changes the design after die cut', unit: '%', min: 0, max: 80, step: 1, def: 20, tech: 'T',
      hint: 'Architects revise. A die can’t absorb it cheaply; a toolpath can.' },
    { id: 'changeCost', g: 'Die route', label: 'Die rework cost when that happens', unit: '%', min: 0, max: 100, step: 5, def: 30, tech: 'T', hint: 'Share of die build cost.' },
    { id: 'dieStore', g: 'Die route', label: 'Die storage / disposal per die', unit: '$', min: 0, max: 5000, step: 50, def: 250, tech: 'T',
      hint: 'One-off dies get stored “just in case” or scrapped. Either costs money.' },
    { id: 'inspectT', g: 'Die route', label: 'CMM inspection per design', unit: '$', min: 0, max: 5000, step: 50, def: 600, tech: 'T',
      hint: 'Machina scans in-cell; the die route pays for separate first-article inspection.' },
    { id: 'setupHrs', g: 'Die route', label: 'Press setup hours per job', unit: 'hr', min: 0, max: 16, step: 0.5, def: 3, tech: 'T', hint: '' },
    { id: 'runHrs', g: 'Die route', label: 'Press hours per unit', unit: 'hr', min: 0.02, max: 3, step: 0.02, def: 0.3, tech: 'T',
      hint: 'Large panels, multiple hits, manual handling.' },
    { id: 'trimT', g: 'Die route', label: 'Secondary trim & pierce per unit', unit: '$', min: 0, max: 1000, step: 10, def: 150, tech: 'T',
      hint: '5-axis laser trim or hand trim after drawing.' },

    // ---- Machina route ----
    { id: 'mNRE', g: 'Machina route', label: 'Programming & first article per design', unit: '$', min: 0, max: 20000, step: 250, def: 3500, tech: 'M',
      hint: 'Toolpath generation, frame setup, first-part scan. Synthetic — Machina does not publish pricing.' },
    { id: 'mHrs', g: 'Machina route', label: 'Robot hours per unit (form + scan + trim)', unit: 'hr', min: 0.5, max: 30, step: 0.5, def: 6, tech: 'M',
      hint: 'Incremental forming is slow: a large, deep 3-D part can take hours.' },
    { id: 'mRate', g: 'Machina route', label: 'Machina cell rate', unit: '$', min: 50, max: 1000, step: 10, def: 300, tech: 'M',
      hint: 'Per robot-hour, including Machina’s margin. Synthetic.' },
    { id: 'finishM', g: 'Machina route', label: 'Surface finishing per unit', unit: '$', min: 0, max: 1000, step: 10, def: 120, tech: 'M',
      hint: 'Architectural finishes may need tool-path marks sanded before coating.' },
    { id: 'trimM', g: 'Machina route', label: 'Residual deburr per unit', unit: '$', min: 0, max: 500, step: 5, def: 25, tech: 'M',
      hint: 'Trimming and drilling happen in the same cell.' },

    // ---- Logistics (shared rates) ----
    { id: 'shipBase', g: 'Logistics', label: 'Handling per shipped unit', unit: '$', min: 0, max: 500, step: 5, def: 60, tech: 'both', hint: '' },
    { id: 'freight', g: 'Logistics', label: 'Freight per unit-mile', unit: '$', min: 0.05, max: 2, step: 0.01, def: 0.35, tech: 'both',
      hint: 'Oversize crated panel moving LTL.' },

    // ---- Scenario-specific ----
    { id: 'milesT', g: 'Scenario', label: 'Miles: die host → customer', unit: 'mi', min: 0, max: 3000, step: 5, def: { s1: 25, s2: 60 }, tech: 'T', hint: '' },
    { id: 'milesM', g: 'Scenario', label: 'Miles: Machina factory → customer', unit: 'mi', min: 0, max: 3000, step: 10, def: { s1: 1800, s2: 150 }, tech: 'M',
      hint: 'Worst case: shipped from the LA-area factory. Best case: a forward-deployed cell nearby.' },
    { id: 'crateT', g: 'Scenario', label: 'Crating per unit — die', unit: '$', min: 0, max: 600, step: 10, def: { s1: 0, s2: 0 }, tech: 'T', hint: 'Local truck delivery needs none.' },
    { id: 'crateM', g: 'Scenario', label: 'Crating per unit — Machina', unit: '$', min: 0, max: 600, step: 10, def: { s1: 150, s2: 40 }, tech: 'M', hint: '' },
    { id: 'leadT', g: 'Scenario', label: 'Lead time to customer — die', unit: 'wk', min: 1, max: 30, step: 0.5, def: { s1: 8, s2: 9 }, tech: 'T',
      hint: 'Die design + build + tryout + run.' },
    { id: 'leadM', g: 'Scenario', label: 'Lead time to customer — Machina', unit: 'wk', min: 0.5, max: 30, step: 0.5, def: { s1: 3, s2: 1.5 }, tech: 'M',
      hint: 'Worst case adds freight transit, a queue behind defense work, and remote back-and-forth.' },
    { id: 'coordT', g: 'Scenario', label: 'Supplier coordination hours per design — die', unit: 'hr', min: 0, max: 40, step: 0.5, def: { s1: 2, s2: 5 }, tech: 'T',
      hint: 'Trips to the die shop and press host.' },
    { id: 'coordM', g: 'Scenario', label: 'Supplier coordination hours per design — Machina', unit: 'hr', min: 0, max: 40, step: 0.5, def: { s1: 6, s2: 2 }, tech: 'M',
      hint: 'Communication delay: time zones, remote reviews, waiting on scans.' },
    { id: 'tripsM', g: 'Scenario', label: 'Evaluation trips to Machina per design', unit: '', min: 0, max: 2, step: 0.05, def: { s1: 0.25, s2: 0.25 }, tech: 'M',
      hint: '0.25 = one visit every fourth design, to inspect first articles in person.' },
    { id: 'tripCost', g: 'Scenario', label: 'Cost per evaluation trip', unit: '$', min: 0, max: 5000, step: 50, def: { s1: 1800, s2: 200 }, tech: 'M',
      hint: 'Flight + hotel + a lost day, versus a short drive.' },
    { id: 'dieMove', g: 'Scenario', label: 'Die transport per design', unit: '$', min: 0, max: 3000, step: 50, def: { s1: 0, s2: 300 }, tech: 'T',
      hint: 'Trucking a heavy die to a press host an hour away.' },
    { id: 'pressRate', g: 'Scenario', label: 'Press host rate', unit: '$', min: 50, max: 600, step: 5, def: { s1: 175, s2: 175 }, tech: 'T',
      hint: 'Per press-hour at the shop hosting your die.' },
    { id: 'pressOwn', g: 'Scenario', label: 'Owned press (annual lease + upkeep)', unit: '$', min: 0, max: 250000, step: 5000, def: { s1: 0, s2: 0 }, tech: 'T',
      hint: 'Set above 0 to model owning the press instead of renting a host’s. Pair with a lower press rate.' },
    { id: 'supplierM', g: 'Scenario', label: 'Supplier onboarding & audits (annual) — Machina', unit: '$', min: 0, max: 50000, step: 500, def: { s1: 6000, s2: 3000 }, tech: 'M',
      hint: 'NDAs, quality audits, a new vendor’s paperwork.' },
  ];

  function defaults() {
    const v = {};
    for (const p of P) v[p.id] = typeof p.def === 'object' ? { ...p.def } : p.def;
    return v;
  }
  function get(v, id, scen) { const x = v[id]; return typeof x === 'object' ? x[scen] : x; }

  // Build cost functions for one technology in one scenario.
  function build(v, scen, tech) {
    const g = (id) => get(v, id, scen);
    const n = g('n');
    const lead = tech === 'T' ? g('leadT') : g('leadM');
    const w = (g('winBase') / 100) * Math.pow(0.5, lead / g('halfLife'));
    const cL = g('leadCost'), Ls = g('leadSat'), gam = g('gamma');
    const wage = g('salary') / g('hrsCap');
    const fin = (x) => x * (g('rate') / 100) * (lead + g('payTerms')) / 52;
    let perDesign, perDesignLog, perUnit, fixed, hDesign;
    const ship = g('shipBase') + g('freight') * (tech === 'T' ? g('milesT') : g('milesM')) + (tech === 'T' ? g('crateT') : g('crateM'));
    if (tech === 'T') {
      const die = g('dieCost');
      perDesign = die + g('dieEng') + g('tryout') + (g('changeProb') / 100) * (g('changeCost') / 100) * die
        + g('dieStore') + g('inspectT') + g('setupHrs') * g('pressRate') + fin(die + g('dieEng') + g('tryout'));
      perDesignLog = g('dieMove');
      perUnit = { material: g('netMat') / (g('utilT') / 100), process: g('runHrs') * g('pressRate'), finishing: g('trimT'), logistics: ship };
      fixed = g('fixMkt') + g('fixOH') + g('pressOwn');
      hDesign = g('hrsDesignT') + g('coordT');
    } else {
      perDesign = g('mNRE') + fin(g('mNRE'));
      perDesignLog = g('tripsM') * g('tripCost');
      perUnit = { material: g('netMat') / (g('utilM') / 100), process: g('mHrs') * g('mRate'), finishing: g('finishM') + g('trimM'), logistics: ship };
      fixed = g('fixMkt') + g('fixOH') + g('supplierM');
      hDesign = g('hrsDesignM') + g('coordM');
    }
    function parts(Q) {
      const D = Q / n, L = D / w;
      const acq = cL * (L + (Ls / (gam + 1)) * Math.pow(L / Ls, gam + 1));
      const H = L * g('hrsQuote') + D * hDesign + Q * g('hrsUnit');
      const labor = g('salary') + Math.max(0, H - g('hrsCap')) * wage * g('premium');
      return {
        tooling: D * perDesign,
        acquisition: acq,
        labor,
        material: Q * perUnit.material,
        process: Q * perUnit.process,
        finishing: Q * perUnit.finishing,
        logistics: Q * perUnit.logistics + D * perDesignLog,
        fixed,
        _H: H, _L: L, _D: D,
      };
    }
    const TC = (Q) => { const p = parts(Q); return p.tooling + p.acquisition + p.labor + p.material + p.process + p.finishing + p.logistics + p.fixed; };
    // Q at which the single employee's hours run out
    let lo = 0, hi = 1e6;
    if (parts(hi)._H < g('hrsCap')) lo = hi;
    for (let i = 0; i < 80 && hi - lo > 0.01; i++) { const m = (lo + hi) / 2; (parts(m)._H < g('hrsCap') ? (lo = m) : (hi = m)); }
    return { TC, parts, w, lead, n, price: g('price'), capQ: lo, perDesign: perDesign + perDesignLog, perUnit };
  }

  const QMAX = 8000;
  function analyze(m) {
    const P0 = m.price;
    const AC = (Q) => m.TC(Q) / Q;
    const MC = (Q) => { const h = Math.max(0.05, Q * 1e-4); return (m.TC(Q + h) - m.TC(Q - h)) / (2 * h); };
    const prof = (Q) => P0 * Q - m.TC(Q);
    // grid
    const N = 2500; let best = Infinity, bestQ = 1, pmax = -Infinity, pQ = 0;
    const grid = [];
    for (let i = 1; i <= N; i++) { const Q = QMAX * Math.pow(i / N, 2); grid.push(Q); }
    let be = null, beHi = null;
    for (let i = 0; i < grid.length; i++) {
      const Q = grid[i]; const a = AC(Q); if (a < best) { best = a; bestQ = Q; }
      const p = prof(Q); if (p > pmax) { pmax = p; pQ = Q; }
      if (i > 0) {
        const p0 = prof(grid[i - 1]);
        if (be === null && p0 < 0 && p >= 0) be = bis(prof, grid[i - 1], Q);
        if (be !== null && beHi === null && p0 >= 0 && p < 0) beHi = bis(prof, grid[i - 1], Q);
      }
    }
    if (be === null && prof(grid[0]) >= 0) be = grid[0];
    // refine MES with golden section around bestQ
    let a = Math.max(0.5, bestQ * 0.8), b = Math.min(QMAX, bestQ * 1.25);
    for (let k = 0; k < 60; k++) { const c = a + (b - a) * 0.382, d = a + (b - a) * 0.618; (AC(c) < AC(d) ? (b = d) : (a = c)); }
    const mes = (a + b) / 2; const acMin = AC(mes);
    const atEdge = mes > QMAX * 0.98;
    return {
      AC, MC, prof, mes, acMin, atEdge,
      penaltyHalf: AC(mes / 2) / acMin - 1,
      be, beHi, profitable: be !== null,
      qStar: pQ, piStar: pmax,
    };
  }
  function bis(f, a, b) { for (let i = 0; i < 60; i++) { const m = (a + b) / 2; (Math.sign(f(m)) === Math.sign(f(a)) ? (a = m) : (b = m)); } return (a + b) / 2; }

  const api = { PARAMS: P, defaults, get, build, analyze, QMAX };
  if (typeof module !== 'undefined') module.exports = api; else root.MESModel = api;
})(this);
