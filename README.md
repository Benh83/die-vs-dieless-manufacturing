# Die vs. Dieless

**Does frontier manufacturing tech change the possible and optimal size of custom manufacturing businesses?**

- **Full disclosure** I started this project looking for how the Machina Labs RoboCraftsman impacts minimum efficient scale, but quickly found that the real advantage of the RoboCraftsman came from lowering break-even volume. While minimum efficient scale is important long-term, break-even volume is often the factor that determines the survival of micro manufacturing business. Rather than looking at the most efficient forms of production, this project chooses a very strange constraint: one employee. While in the past, a one-employee complex industrial production business would have been generally unadvisable, new developments have made it more appealing. Small businesses may not often create the frontier, but they create a form of bottom-up resilience, frugality, and independence that strengthens both competitors and local Polis.

This is an interactive cost model for a one-employee business that sells custom, complex three-dimensional sheet-metal construction products, like formed facade panels, sculpted canopies and curved louvers(designs that would require a progressive die). Every design is new, and, being custom, each sells only 1–10 units. The model compares two ways to make them:

- **Progressive / draw die:** a new die for every design, pressed at a host shop.
- **Dieless robotic forming** ([Machina Labs RoboCraftsman](https://machinalabs.ai)): no die. The part is formed incrementally from a CAD toolpath.

Every assumption is a slider. Moving one updates the average-cost (AC) and marginal-cost (MC) curves, the **minimum efficient scale** (where MC = AC), and the **break-even volume** (the fewest units a year that make the business profitable).

https://benh83.github.io/die-vs-dieless-manufacturing/

## Results at default assumptions (5 units per design, $9,000 per unit)

| Scenario | Route | Break-even units/yr | MES units/yr (MC = AC) | Min AC | Quote win rate |
|---|---|---|---|---|---|
| 1 · worst for Machina | Progressive die | 136 | 230 | $8,684 | 23% |
| 1 · worst for Machina | Machina | 28 | 274 | $4,632 | 35% |
| 2 · best for Machina | Progressive die | 160 | 209 | $8,864 | 21% |
| 2 · best for Machina | Machina | 23 | 321 | $3,752 | 40% |

**What the defaults show**

1. **Dieless forming cuts the minimum viable scale about 5×.** Break-even drops down from 136 to 28 units per year, even when the nearest RoboCraftsman is 1800 miles away. A die has a relatively high fixed cost for each design, so the Machina method is strictly better until number of designs begins to increase. Dieless forming turns most of that per-design cost into a per-unit cost. 
2. **It doesn't shrink the textbook MES.** For a one-person shop, the bottom of the AC curve sits where the employee runs out of hours. The person sets the MES, not the machine. The technology lowers the whole AC curve and moves break-even left, so the market opens up to a smaller size of firm, particularly with more complex designs.
3. **Batch size is the hinge.** As the demand for a design scales, RoboCraftsman becomes less cost effective. At 1-4 units, it's the only way a business could break even. Heterogeneity of product and experimentation unlock the real value for Robocraftsman, which has potential to reshape the types of manufacturing business that are even possible. 

## The model

`Q` = units sold per year, `n` = units per design, `D = Q / n` = designs won per year.

```
TC(Q) = Fixed + Acquisition(L) + Labor(H) + D·c_design + Q·c_unit

w  = w₀ · 0.5^(lead weeks / half-life)            slow lead times lose deals
L  = D / w                                       qualified leads needed
Acquisition(L) = c_L · [L + Lₛ/(γ+1) · (L/Lₛ)^(γ+1)]   marginal cost c_L·(1 + (L/Lₛ)^γ)
H  = L·h_quote + D·(h_design + h_coord) + Q·h_unit
Labor(H) = salary + max(0, H − capacity) · (salary/capacity) · premium

AC = TC/Q     MC = dTC/dQ     MES = argmin AC ⇔ MC = AC
```

**Why AC is U-shaped.** With only fixed costs and constant unit costs, AC falls forever and never meets MC. Two constraints of a small custom shop bend it back up:
- **Labor capacity.** One employee has about 1,900 productive hours a year. Overflow work goes to contractors at a premium.
- **Thin local demand.** Each extra qualified lead costs more than the last once the regional market is tapped. Slow lead times lower the win rate, so the same revenue takes more leads and more unpaid quoting hours.

**Per-design costs, die route:** die build, die engineering, tryout/first article, expected rework (probability of a design change × rework cost), storage/disposal, CMM inspection, press setup, die transport, and financing of die capital from order until the customer pays.

**Per-design costs, Machina route:** programming/first article, its financing, and evaluation trips.

**Per-unit costs:** steel blank ÷ material utilization, press or robot time, trim/finish/deburr, handling + freight × miles + crating.

**Annual fixed costs:** the one employee, base marketing, overhead, and, depending on the route, an owned press or supplier onboarding.

Outputs: break-even (lower and upper), MES, minimum AC, AC penalty at ½ MES (the classic Pratten/Scherer measure of the cost of being small), the output at which the employee's hours run out, and profit-maximizing output (MC = P).

## Scenarios

| | Scenario 1: worst case for Machina | Scenario 2: best case for Machina |
|---|---|---|
| Die route | Press host is local (25 mi) | Host is 1 hr away (60 mi), die must be trucked there |
| Machina route | Shipped 1,800 mi from the factory, crated, 3-wk lead time, remote back-and-forth, flights to inspect first articles | Forward-deployed cell 150 mi away, 1.5-wk lead time, short drives |

## Assumptions and sources

All values are **synthetic**. They're chosen to be plausible, not taken from any real company's books. I would love to update them with real data if given access to it, though. The full list with ranges is in [`assumptions.csv`](assumptions.csv).

- Mid-complexity progressive dies commonly quote $15k–50k; complex multi-stage dies $25k–150k+ ([Jennison](https://www.jennisoncorp.com/post/sheet-metal-stamping-costs-explained-what-really-drives-the-price), [ML Hardware](https://www.ml-hardware.com/news/industry-news/how-much-to-get-a-metal-part-made-the-complete.html)).
- Hidden die NRE: design engineering $3–5k, tryout $2–5k, storage $0–2k/yr ([DRA Metal](https://drametal.com/blog/sheet-metal-tooling-cost-guide/)).
- Dieless forming removes the per-design die and shortens lead time from months to days ([Machina Labs](https://machinalabs.ai/resources/advanced-manufacturing-incremental-sheet-metal-forming-with-robotics-and-ai)). **Machina does not publish part pricing.** The cell rate ($300/robot-hr), cycle time (6 hr/part) and programming fee ($3,500/design) are assumptions to challenge.
- Incremental forming trades tooling cost for longer cycle time ([RoboDK](https://robodk.com/blog/robotic-incremental-forming-savings/)).

## Limitations

- Large panels are usually drawn in line or transfer dies, not progressive dies. The die-cost slider covers any hard tooling.
- Price is held fixed. A shop with a large cost advantage would cut price, or competitors would adopt the process, which would pull price toward the dieless AC.
- Overflow contractors are assumed to be available at a constant premium, so profit-maximizing output can be unrealistically large.
- Installation, taxes, warranty and capacity limits at Machina aren't modeled.

## Extending it

`model.js` is self-contained and works in Node:

```js
const M = require('./model.js');
const v = M.defaults();          // every assumption; scenario-specific ones are {s1, s2}
v.n = 3;
const r = M.analyze(M.build(v, 's1', 'M'));   // 'T' = die, 'M' = Machina
console.log(r.be, r.mes, r.acMin);
```

To test another industry, swap in its per-design and per-unit costs. Examples: dieless composites tooling, 3-D-printed molds, CNC vs. casting. The same question applies: how far does removing the per-instance fixed cost lower the scale at which heterogeneous products become profitable?

## License

MIT
