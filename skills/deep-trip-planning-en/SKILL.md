---
name: deep-trip-planning-en
description: "Build or audit a multi-day travel itinerary that is usable on the ground: date-specific verification, explicit decision thresholds, transit routing, and booking deadlines. Use for trip planning, itinerary reviews, lodging/transit tradeoffs, and travel budgets; do not use for ordinary work or project scheduling."
license: MIT
compatibility: Requires network access for current-source verification and python3 to run the shared date/holiday checker in the sibling deep-trip-planning skill. Install the Python holidays package when prompted.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/../deep-trip-planning/scripts/*)
---

# Deep Trip Planning

The goal is not a handsome list of places. It is an itinerary that still works when its reader is jet-lagged, carrying luggage, and unable to research another option.

Two failures cause most bad plans: information was checked only for existence rather than for the planned date and hour, and decisions were never closed. This workflow fixes both.

## Workflow

### Before step 0: destination not chosen

If the user asks where to go rather than how to visit a named place, do not invent a day-by-day plan. Use their travel style to offer **three candidates**, each with concrete tradeoffs: seasonal conditions, budget band, visa-checking complexity for their nationality, and flight/connection burden. Point to official immigration sources; never declare that a traveler does or does not need a visa from memory. Once they choose, start step 0.

### Step 0: lock hard constraints

Record booked lodging (address, check-in/out, cancellation deadline, all-in cost), fixed transport, travelers, must-do and no-go items, and constraints such as mobility, dietary needs, motion sickness, children, or older travelers.

Run `${CLAUDE_SKILL_DIR}/../deep-trip-planning/scripts/trip_dates.py <country-code> <start-date> <end-date>`; **never calculate weekdays mentally**. It checks the clock against network time before reporting weekdays, holidays, and long weekends. Then check whether dates are in the past and whether the user's “weekend” or other weekday assumptions match the calendar. Ask before continuing if they do not.

Set a daily origin: the nearest lodging station in a city, the lodging plus parking constraints on a road trip, or one origin per city on a multi-city trip. If lodging is undecided, read `references/lodging-decisions.md` before routing anything.

### Step 0.5: turn taste into numbers

Ask or infer—and label any assumption—the desired daily pace, food's importance, queue tolerance, shopping weight, budget posture, and appetite for pre-booking. Put numbers in the plan: “leave after X minutes,” “N reservation meals,” and a defined buffer. Preferences are dials, not defaults.

### Step 1: choose anchor days and swap rules

Give weather- or season-dependent activities a primary day, preferably a working day away from long weekends, plus explicit swap rules. “Check the weather” is not a rule; “make the first decision on the 16th, final decision on the 17th, and change the ticket first” is.

### Step 2: route each day and preserve a cut layer

For each day, make a time-to-action table, an order that does not double back, items that must remain versus can be dropped, a concrete weather fallback, and an unallocated buffer for transfers, exits, parking, and fatigue.

**Arrival and departure days are not for hard commitments.** On arrival day, do not schedule a non-refundable meal, minute-perfect golden hour, or the trip's only must-do after landing. Leave room for immigration, bags, delays, and jet lag; across time zones, start with a light walk, food, and sleep. On departure day, back-solve from the current airline, airport, and operator requirements. Put only discardable activities before it—tax refund, car return, lockers, and last shopping are not “quick stops.”

### Step 3: verify every planned place

Read `references/verification.md`. Check the planned weekday, opening window, closures, public holidays and long weekends, rule changes taking effect during the trip, the actual forecast window for seasonal events, and local crowding events.

### Step 4: make every transit leg actionable

Read `references/transit-and-maps.md`. For public transit, give line, transfer station, duration, fare, and operational trap. For driving, give route, driving time, parking, tolls, and road constraints. Default to individual tickets; buy a pass only when the written arithmetic wins.

### Steps 5–7: maps, budget, and deadline table

Read `references/transit-and-maps.md` for the three-layer map workflow, and `references/budget-and-customs.md` for budget and customs. Identify the one uncapped budget category—usually shopping—and set tiers plus a hard ceiling. Put ticket releases, cancellation cutoffs, booking windows, registrations, and rechecks into a dated table.

### Step 8: pre-delivery self-review

Compare every day with step 0's hard constraints and step 0.5's preference numbers. Then run the eight itinerary-review checks below against your own draft. Include the results at the end of the delivery; do not silently perform the review.

## Rules that apply throughout

⚠ **Opening hours, closure days, prices and fares, travel times and transfer counts, reservation rules and availability windows, public holidays, and the current prediction window for seasonal events need a source checked in this planning session.** Treat remembered training data as stale. If you cannot cite a source, do not state the number; write “recheck X days before departure” and where to do it. An honest gap is better than a confident error.

⚠ All numeric examples are placeholders. Use the traveler's stated preferences, not the planner's.

- Give every queue a walk-away threshold and a named alternative.
- Provide candidates without turning them into a checklist; the traveler goes to one, not all.
- Reservations are a choice between flexibility and certainty. Make their routing cost visible.
- Back-solve golden-hour plans. If the math fails, change the transport before accepting a late arrival.
- For an A/B choice, set a switching threshold first. If it is not met, close the decision explicitly.
- A costlier route is worth naming when it protects the day's only irreplaceable window; state what the extra cost buys.

## Sources and writing

Use social posts for lived experience and official pages for hard facts. A map is useful for distance and exits, not for future operating status. Do not buy booking or guiding services through social media.

Use `assets/planning-templates.md` for the Markdown outline, daily template, countdown, packing method, and emergency card. Adapt it to the trip; do not make up facts merely to fill cells. Give a conclusion before its reasons, attach a condition to every recommendation, and edit an existing itinerary in place rather than creating a competing copy.

## Review an existing itinerary

Check, in order:

1. Internal time conflicts.
2. Unnecessary detours.
3. Golden-hour plans that fail when back-solved.
4. Missing weekday, holiday, or policy verification.
5. Unexplained gaps.
6. Arrival/departure days with no fallback.
7. Seasonal expectations that do not match dates.
8. Obvious overload or contradiction, such as 12 cities in 10 days. Explain why, offer a usable alternative, then continue with the user's decision. Flag it; do not block, demand confirmation, or keep arguing.

When you find a problem, provide a replacement, not just a warning.

## References

- `references/verification.md` — use in step 3.
- `references/transit-and-maps.md` — use in steps 4–5.
- `references/lodging-decisions.md` — use when comparing lodging.
- `references/budget-and-customs.md` — use in step 6.
- `references/entry-and-health.md` — use after choosing a destination and before booking; it never authorizes a direct visa conclusion.
- `assets/planning-templates.md` — use when writing the final plan.
