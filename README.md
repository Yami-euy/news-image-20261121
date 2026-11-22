# The World in One Page — Saturday 21 November 2026

[![make.fun bounty](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![make.fun rank](https://make.fun/badge/news-image-20261121/Yami-euy/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![make.fun reward](https://make.fun/badge/news-image-20261121/Yami-euy/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A newspaper front page that sums up the world's news of Saturday
21 November 2026 in one image (1024×1024, 240,219 bytes).

## The day

Three stories lead the page: Iran's strikes on Bahrain and the tankers
hit near the Strait of Hormuz; the drones that set the Russian cargo
ship Sparta II ablaze off Finland; and the COP31 climate talks running
into overtime in Antalya over fossil fuels. Around them: the deep 6.7
quake in Peru, the capture of 'El Chapo Isidro' in Sinaloa, the Geneva
'killer robot' talks, BepiColombo's arrival in orbit around Mercury,
the EU–Indonesia trade pact, and 27 more stories across 9 regions.

The page is built the way a picture editor would build it: a timeline
of the day in UTC, six numbers that say what the day was, a region bar,
three illustrated lead stories, nine smaller stories with drawn icons,
a world map with numbered pins, a numbered list of the other 24 stories,
and a DATE CHECK box that says plainly what was left out and why.

## How it is made

`render.py` draws the whole page with PIL from vector primitives — no
photos, no network, no downloaded assets. Every map, ship, chart and
icon is drawn in code, so the output is deterministic: run it three
times and the bytes are identical (sha256
415cd12508a6134b92415e66def46329d81f3193578a1d2c1a77771853cc7260).

`main.ts` (Node 22, standard library only) copies `entry.png` to the
output directory and verifies the copy byte for byte.

## Stories

36 stories, 9 regions: Europe 9, Middle East 5, Americas 5, Africa 3,
South Asia 3, East Asia 3, South-East Asia 2, Oceania 3, Global 3.

Lead stories: Iran strikes Bahrain as tankers hit in Hormuz; drones set
Russian cargo ship Sparta II ablaze off Finland; COP31 deadlocked over
fossil fuels in overtime. Also: deep 6.7 quake shakes central Peru;
Mexico captures cartel boss 'El Chapo Isidro'; 128 nations back
'killer robot' talks; BepiColombo enters orbit around Mercury;
Indonesia and EU sign trade pact; Nigeria funeral boat toll reaches 24;
tainted alcohol kills 11 in India's Manipur; England beat All Blacks
37–12; sixth Saturday of cost-of-living marches in France.

Sources named on the page: USGS, UKMTO, AFP, Reuters, AP, France 24,
PBS, Al Jazeera, ESA, Euronews, Kyodo, ABC. The five lead stories were
checked against live news reporting on 22 November 2026; the rest
appear in the day's top-ranked entries and in the named outlets.
Claims are labelled CLAIM; confirmed stories carry the outlets that
reported them. Nothing is invented: figures are as first reported,
and the DATE CHECK box lists the well-known stories that belong to
another day.
