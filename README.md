# The Passport Page of a Country That Isn't There

[![make.fun](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/stevewhy404/the-passport-page-of-a-countr-2-20261121-0318/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/stevewhy404/the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

A program that draws an invented passport spread for the **Republic of
Velmoria** — a country that does not exist — as `/output/entry.png`.

## The document

- **Left page — the data page.** Portrait of Mara Elin Ilsen, born
  12 FEB 1991 in Tarnwick; nationality Velmorian; issued 14 MAR 2024 by
  the Ministry of Passage, Tarnwick; expires 14 MAR 2034; document no.
  VL 4839201. The machine-readable zone carries real ICAO 9303 check
  digits.
- **Right page — visas and stamps.** One coherent trip, every stamp
  after the date of issue: out of Tarnwick 02 JUN 2024, into Dravnia
  03 JUN, out 18 JUN, into Caldoria 19 JUN, out 02 JUL, home to
  Tarnwick 02 JUL 2024.
- **The telling detail.** A red visa-condition stamp: *"VISA
  CONDITION 7 — NO CROSSING OF THE GREY PASS AFTER DUSK. — BORDER
  WARDEN, TARNWICK"*, with a handwritten note beneath it: *"Seen at
  the Grey Pass — 02 JUL 2024. M. Ilsen crossed on foot, before dusk."*

## Run it

```sh
python3 main.py   # writes /output/entry.png (1024x1024, PNG)
```

Python 3.13, Pillow only, no network. Deterministic: two runs produce
byte-identical output.
