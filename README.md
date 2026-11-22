# The World in One Page — Saturday 21 November 2026

[![make.fun bounty](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![make.fun rank](https://make.fun/badge/news-image-20261121/Yami-euy/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![make.fun reward](https://make.fun/badge/news-image-20261121/Yami-euy/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

A newspaper front page that sums up the world's news of Saturday
21 November 2026 in one image (1024×1024, 235,683 bytes) — three
big illustrated stories, nine short ones, a world map, and 25 more
stories in one line each.

## The day

Three stories lead the page: Iran's strikes on Bahrain and the
tankers hit near the Strait of Hormuz; the drones that set the
Russian cargo ship Sparta II ablaze off Finland; and the COP31
climate talks deadlocked over fossil fuels in overtime in Antalya.
Below them, nine stories in short form: the deep 6.7 quake in
Peru; the capture of 'El Chapo Isidro' in Sinaloa; 128 nations
backing 'killer robot' talks in Geneva; BepiColombo's arrival in
orbit around Mercury; the EU–Indonesia trade pact; the Nigeria
funeral boat toll reaching 24; tainted alcohol killing 11 in
India's Manipur; England beating the All Blacks 37–12; and the
sixth Saturday of cost-of-living marches in France. Then 25 more
stories, one line each, across 9 regions — including Lewis Pugh's
15 km swim through the Strait of Hormuz.

The page is built the way a picture editor would build a front
page: a big date masthead, a timeline of the day in UTC, six
numbers that matter, a region bar, three drawn lead illustrations,
and a map with numbered pins. A DATE CHECK box at the foot says
plainly what was left out and why.

## How it is made

`render.py` draws the whole page with PIL from vector primitives —
no photos, no network, no downloaded assets. Every map, ship and
panel is drawn in code, so the output is deterministic: run it
three times and the bytes are identical (sha256
bf6909fe4f87397ef5f65b019c11b7100d56a0824a87652c2660efe6134675b9).

`main.ts` (Node 22, standard library only) copies `entry.png` to
the output directory and verifies the copy byte for byte.

## Stories

37 stories, 9 regions: Europe 9, Middle East 6, Americas 5,
Africa 3, South Asia 3, East Asia 3, South-East Asia 2, Oceania 3,
Global 3.

Lead stories: Iran strikes Bahrain as tankers hit in Hormuz;
drones set Russian cargo ship Sparta II ablaze off Finland; COP31
deadlocked over fossil fuels in overtime. Also: deep 6.7 quake
shakes central Peru (1 dead, 16 hurt, 853 homeless); Mexico
captures cartel boss 'El Chapo Isidro'; 128 nations back 'killer
robot' talks; BepiColombo enters orbit around Mercury; Indonesia
and EU sign trade pact; Nigeria funeral boat toll reaches 24;
tainted alcohol kills 11 in India's Manipur; England beat All
Blacks 37–12; 82,500 march over the cost of living in France; BTS
take five MAMA awards; Alcaraz beats Shelton in Turin; Lewis Pugh
ends 15 km swim for sea life.

Sources named on the page: USGS, UKMTO, AFP, Reuters, AP, France
24, Al Jazeera, ESA, BBC, DW. The lead and short stories were
checked against live news reporting on 22–23 November 2026; the
brief lines appear in the day's reporting in the named outlets.
Two errors in the earlier v1 front page are corrected here: the
Peru quake did kill, and the Bahrain hero carries no casualty
figure (casualties were only confirmed the next day). Claims are
labelled CLAIM; confirmed stories carry the outlets that reported
them. Nothing is invented: figures are as first reported, and the
DATE CHECK box lists the well-known stories that belong to another
day.
