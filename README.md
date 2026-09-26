# machina-industrial-scale-enablement

**Live model:** https://benh83.github.io/machina-industrial-scale-enablement/
 
I have a background in quantitative economics, civics, and the liberal arts, and I'm trying to dig into interesting developments in hard tech where these three things collide. 

The mission of Machina Labs "is to democratize manufacturing. Distributed factories full of Robocraftsmen that can turn almost any idea, no matter how complex, into something real for anybody." I want to understand how this process of democratization might play out. While much of Machina's current business is with larger firms, as they gain capacity, the radical change in cost structure and production process created by Robocraftsman can allow new forms of firms to emerge at the margins. 

## The question

How does dieless robotic sheet-metal forming (Machina Labs' RoboCraftsman) change the size of custom metal-fabrication firm that can break even, and be efficient? Firm size is measured two ways: **employees** and **units produced per year**.

Understanding impact to potential firm size is important because it can help to translate the impacts of new tech into business terms. Machina cuts out massive fixed costs from both hand-formed and tooled production for micro-runs of complex sheet metal products. Every firm can do more with less, but minimum efficient scale and break even help us quantify the sort of firms that Machina can attract into the market that couldn't exist with hand-formed and tooled production. 

## Test case

The test product is a custom **doubly curved aluminum facade or canopy panel**:

- 4 × 10 ft, 3 mm 5052 aluminum, PVDF-coated.
- Sold at **$7,500** per panel, about $2,080 per m².
- Every order is a new geometry. Each geometry sells **5 panels** by default (slider: 1–25).

Doubly curved panels are the right test because they cannot be made on a press brake or roll former: the surface bends in two directions at once, like a saddle or a dome. Without Machina, the options are a die, a form built for that geometry, or many skilled hours.

Machina has been extremely effective in defense and aerospace, but I wanted to choose a non-defense for this industry analysis because ITAR and AS9100 add complexity that I don't understand well enough to factor in, but I assume that they would make it difficult for a micro-supplier to enter the market. Maybe Machina's controlled environment would allow small defense and aerospace competitors to emerge, but architectural applications have much more precedent of small firms succeeding. 

The model compares three ways to make each geometry:

| Route | What the firm does | Where the forming cost shows up |
|---|---|---|
| **Tooled** | Buys a draw die for each geometry, then pays a host shop to press the panels | Per design (the die) |
| **Hand-formed** | Its own employees form each panel over a CNC-milled buck | Headcount (about 60 hours per panel) |
| **Machina** | Designs, sells and manages the job; Machina forms, scans and trims the panels | Per panel (robot time) plus a small per-design programming fee |

## Headline results (default assumptions)

Scenario 1 ships parts from Machina's Los Angeles factory. Scenario 2 assumes a hypothetical regional Machina factory 150 miles away.

| Scenario | Route | Smallest viable firm | Minimum efficient scale (MES) | Near-efficient range (within 5% of lowest cost) | Lowest avg cost | Panels per employee-year | Quote win rate |
|---|---|---|---|---|---|---|---|
| 1 | Tooled | **Never viable** | 
| 1 | Hand-formed | **47 panels, 2 emp** | 155 panels, 7 emp | 71–259 panels, 3–13 emp | $6,618 | 24 | 29% |
| 1 | Machina | **44 panels, 1 emp** | 271 panels, 1 emp | 188–670 panels, 1–3 emp | $4,747 | 273 | 38% |
| 2 | Tooled | **Never viable** | 
| 2 | Hand-formed | **47 panels, 2 emp** | 155 panels, 7 emp | 71–259 panels, 3–13 emp | $6,618 | 24 | 29% |
| 2 | Machina | **35 panels, 1 emp** | 314 panels, 1 emp | 218–622 panels, 1–2 emp | $3,880 | 316 | 41% |

"Smallest viable firm" is the lowest output, and the headcount at that output, where price covers long-run average cost. MES is the output with the lowest long-run average cost. Tooled never gets its cost below the $7,500 price.

![Firm-size map](figures/firm_map_s1.png)

![Long-run average cost](figures/lrac_s1.png)

![Smallest viable firm by batch size](figures/batch_s1.png)

## the numbers say

**1. At 1–10 panels per design, particularly for products cheaper than most of what Machina produces, dies aren't really their competitor.**
With my assumptions, a die costs **$60,162 per design**: a $45k die plus engineering, tryout, expected rework, storage, inspection, setup and financing. which adds up to about **$12,000 per panel** at 5 panels per design, well above the $7,500 price. The die route only breaks even once each design repeats **11+ times** (147 panels a year at 11 per design). The incumbent for small-scale bespoke work at this scale is skilled hand forming.

While RoboCraftsman has a significant price advantage over the other two options, the speed of iteration as opposed to a die, and the reduction of intensive manual labor both make that price advantage come with benefits rather than non-financial costs. 

**2. Machina lowers the smallest viable firm to one person.**
The smallest viable firm enabled by Machina is **1 employee selling 44 panels a year** (~9 designs), or 35 panels with a forward deployed Robocraftsman/regional Machina factory. While a 2-person hand forming firm needs only a few more panels to break even, the potential for a one person industrial production firm to make products of such complexity is novel. Speculation about the one-person unicorn is usually concentrated in the software world, but so dramatically increasing the manufacturing capability of a one person firm may prove to be more important than we know. 

**3. A one person firm out-produces 12+ hand-formers, and per-employee production goes through the roof with RoboCraftsman  .**
All-in labor per panel is **6.8 hours for Machina versus 75.9 for hand forming**. That's **273 vs. 24 panels per employee-year, about 11×**. The hand-forming method worked not because of how efficient it was, but because of how inflexible and expensive die creation is. 

A lean, Robocraftsman-enabled firm, the firm is mainly design, sales and project management, and can be profitable at a wide range of outputs.


**4. The efficient firm shrinks in headcount and grows in output.**

| Route | MES | Near-efficient range |
|---|---|---|
| Hand-formed | 155 panels with **7 employees** | 3–13 employees |
| Machina | 271 panels with **1 employee** | 1–3 employees, up to 670 panels |

Lowest average cost falls **28%** ($6,618 → $4,747). With a regional factory it falls **41%** ($3,880).

**5. Distance to the Machina factory matters less than expected.**
Going from 1,800 miles to 150 miles only lowers the smallest viable Robocraftsman-utilizing firm from 44 to 35 panels a year. I made the choice to put this in here because I'm partial to short supply chains, but transport is so small relative to other costs that it doesn't change much at a firm level.

The biggest benefits to the distributed factories that Machina seems to be planning would be the ability to iterate on designs more quickly in person, and the eco-system of physical-world creativity that would almost inevitably emerge. 

**6. The market limits growth, not the technology.**

The largest profitable Machina firm makes about **1,430 panels with 6 employees**. Past that, winning more work in a thin regional construction market costs more than the work earns. Profit peaks at just over 900 panels with 4 employees. While the market limits this use case, other high-growth use cases will emerge that haven't yet been economically worthwhile. 


## Key assumptions

All values are **synthetic**. I couldn't find much info online on Machina pricing, so I will reach out soon and find out more. I could be totally off here, but the potential for custom auto panels and emerging applications means that construction applications are in the realm of possibility, even if they don't make up much of Machina's current work. The full list with ranges is in [`assumptions.csv`](assumptions.csv).

| Assumption | Default | Basis |
|---|---|---|
| Price per panel | $7,500 | About $2,080/m² for bespoke doubly curved aluminum, supplied only |
| Panels per design | 5 | Freeform facades often run 1–6 panels per geometry |
| Cost per employee (fully loaded) | $85,000 + $9,000 per-head overhead | One blended rate |
| Productive hours per employee | 1,850 / yr | |
| Coordination loss | 1.5% of hours per additional coworker | Organizational diseconomy of scale |
| Draw die per geometry | $45,000 (+$5k engineering, +$4k tryout) | Soft dies $20–60k, hardened $100k+ |
| Hand-forming hours per panel | 60 hr, plus 15% rework | Coachbuilders: 40–100+ hr for a hood-sized panel |
| CNC-milled buck per geometry | $3,500 | |
| Machina programming / first article | $3,500 per geometry | **Synthetic** |
| Machina robot time | 5 hr × $300/hr per panel | **Synthetic** |
| Machina surface finishing | $180 per panel | Stated finish 125 µin Ra |
| Lead time: tooled / hand / Machina | 10 / 5 / 2 wk (Machina 1 wk in scenario 2) | Machina: first parts typically within a week |
| Win rate halves every | 8 weeks of lead time | Construction schedules punish slow suppliers |
| Local market depth | 200 leads/yr before lead cost doubles | Thin regional market for bespoke facades |

## Method

**Notation:**
- `Q` = panels per year, `n` = panels per design, `D = Q/n` = designs per year.
- `w` = quote win rate, which falls with lead time. `L = D/w` = qualified leads needed.
- `N` = employees, owner included.

```
hours(Q)    = L·h_quote + D·h_design + Q·h_unit
capacity(N) = N · h_year · (1 − m·(N−1))
TC(Q, N)    = N·(salary + overhead per head) + fixed + D·c_design + Q·c_unit + lead cost(L)
              feasible only if hours(Q) ≤ capacity(N)        (no contractors)

Short run: N fixed.        AC = TC/Q,  MC = dTC/dQ
Long run:  N*(Q) = fewest employees that can do the hours
           LRAC(Q) = TC(Q, N*(Q)) / Q
           MES = argmin LRAC;  smallest viable firm = min Q with price ≥ LRAC
```

Long-run average cost jumps at each hire because headcount is a discrete variable. It rises at large scale for two reasons: coordination loss as the small team grows, and a thin regional market where each extra lead costs more than the last. Both of these factors would diminish if a firm were explicitly seeking to structure for a national market and scale, but I am approaching this analysis focused on local businesses in the model of a machine shop for a new era. 

## Limitations

- Price is held fixed. Over time, competition, or wider adoption of the technology, would push it toward the lowest average cost.
- There is one blended wage. Skilled panel formers are scarce and would cost more, which would make the hand-formed route look worse.
- Machina's capacity limits and job-queue priority (it also serves defense customers) aren't modeled, primarily because I have no idea. I would assume that the scenario modeled here would be possible in a few years after Machina builds up more capacity, and can service non mission-critical firms. I doubt that Machina would currently enter into this relatively lower-priority industry, but the technical capability Machina creates makes this sort of application a possible next step. 
- Installation, warranty, taxes and working-capital limits beyond per-design financing are excluded.


## Running it

- **In the browser:** `index.html` runs `model.py` itself, via [Pyodide](https://pyodide.org). The first load takes a few seconds.
- **Locally:** run `python -m http.server`, then open `http://localhost:8000`.
- **From the command line:** `python model.py` prints the results table. `python model.py --json` prints the full output. `python model.py --csv` rewrites `assumptions.csv`.
- **Figures:** `python make_figures.py` (needs matplotlib) regenerates `figures/`.
- **After editing `model.py`:** run `python build.py` to refresh the copy embedded in `index.html`, which is used when the page is opened as a local file.

## Sources

- [Machina Labs: Capabilities](https://machinalabs.ai/capabilities)
- [Machina Labs: Automotive](https://machinalabs.ai/applications/automotive)
- [Machina Labs: NASA toroidal tank case study](https://machinalabs.ai/resources/nasa-toroidal-tank-case-study)
- [Business Wire: Machina Labs raises $124 million (Feb 2026)](https://www.businesswire.com/news/home/20260204756837/en/Machina-Labs-Raises-$124-Million-to-Scale-Manufacturing-Infrastructure-for-Defense-and-Advanced-Mobility)
- [Defense One: the Air Force and Machina parts replacement](https://www.defenseone.com/technology/2024/04/air-force-help-startup-quietly-revolutionizing-parts-replacement/395430/)
- [Dongdaemun Design Plaza double-curved panel study](https://wyzrs.com/post/journal-paper)
- [Shao-Yi: automotive stamping die costs, body-panel lines $0.5–1M+](https://www.shao-yi.com/cost-of-automotive-stamping-dies)
- [Jennison: stamping die costs](https://www.jennisoncorp.com/post/sheet-metal-stamping-costs-explained-what-really-drives-the-price)
- [DRA Metal: hidden tooling costs](https://drametal.com/blog/sheet-metal-tooling-cost-guide/)

---

_Independent analysis. Not affiliated with or endorsed by Machina Labs. RoboCraftsman is a trademark of its owner._
