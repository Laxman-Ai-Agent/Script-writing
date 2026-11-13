# How GPS works
- 31 operational satellites (nominal constellation 24) — https://en.wikipedia.org/wiki/Global_Positioning_System — medium (gps.gov page 404'd; count changes over time, say "about 30")
- Orbit altitude ~20,200 km (medium Earth orbit), 2 orbits per sidereal day — https://www.nasa.gov/directorates/somd/space-communications-navigation-program/gps/ and Wikipedia — high
- Each satellite carries redundant atomic clocks; ground control segment tracks them — NASA URL above — high
- Each satellite broadcasts its own position and time at regular intervals — NASA URL above — high
- Receiver computes how long signal took to arrive -> distance (signal travel time x speed of light) — NASA URL above — high
- Receiver needs >=4 satellites: 3 position coordinates + receiver's own clock error; so cheap receiver clock is fine — https://en.wikipedia.org/wiki/Global_Positioning_System — high
- Positioning by intersecting distance spheres = trilateration (not triangulation) — standard theory, term not on NASA page — medium
- Relativity: satellite clocks run ~38 microseconds/day faster (special ~-7, general ~+45) — https://www.astronomy.ohio-state.edu/pogge.1/Ast162/Unit5/gps — high
- Uncorrected, position errors grow ~10 km per day (fix wrong within ~2 minutes) — https://www.astronomy.ohio-state.edu/pogge.1/Ast162/Unit5/gps — medium (single academic source; 38 us x c = ~11 km, consistent)
- GPS is receive-only; phone does not transmit anything to satellites — https://en.wikipedia.org/wiki/Global_Positioning_System — high
- Smartphone accuracy ~4.9 m (16 ft) radius in open sky, worse near buildings/trees — https://www.gps.gov/systems/gps/performance/accuracy/ (via search snippet; page itself 404'd on fetch) — medium
- Time accuracy ~10 nanoseconds, position meter-level — NASA URL above — high
## Angle
- GPS is really a clock system: satellites broadcast time, and distance is just time x speed of light. 1 nanosecond error = ~30 cm. Einstein's relativity is built into the design.
- Misconception: GPS satellites do not track or "know" your phone; they only broadcast, and your phone does all the math. Also: "triangulation" with angles is wrong, it is timing-based distances.
- Caveat: the ~10 km/day figure is a rule-of-thumb; one forum argues a common clock offset would be absorbed by the 4th satellite, but per-satellite drift isn't. Keep claim as "errors would build up to kilometers daily".
