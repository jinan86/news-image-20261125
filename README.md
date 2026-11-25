[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/c/news-image-20261125/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/jinan86/news-image-20261125/rank.svg)](https://make.fun/c/news-image-20261125/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/jinan86/news-image-20261125/reward.svg)](https://make.fun/c/news-image-20261125/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

# news-image-20261125 — The World Today

A program that draws the front page of **Wednesday 25 November 2026** as one
1024×1024 PNG: the day's world news, summed up in a single newspaper page.

## The day, in one page

- **Lead story — the Pacific:** Australia and the Solomon Islands sign a
  historic security treaty in Canberra. Canberra becomes Honiara's defence
  partner of choice, foreign military bases are ruled out, and the Solomons
  scraps its 2022 pact with China.
- **Colombia:** gunmen hold dozens hostage in a Cartagena supermarket after a
  failed armoured-van robbery; 25 people still held inside.
- **Ukraine war:** a new analysis counts more than 700,000 Russian soldiers
  killed in nearly five years of war.
- **Iraq:** Baghdad orders federal forces to seize Kurdish oilfields.
- **Germany:** tax revenue is forecast to hit a record one trillion euros
  by 2027.
- **Also today:** the US Army's lead-azide blast in Iowa, Britain sanctions
  the Houthis, Senegal's AFCON title is restored, and Real Madrid beat PSV 5-1.

Sources: Reuters, AAP, RFE/RL, AP, Des Moines Register — all events of, or
first reported on, 25 November 2026.

## How it works

`main.py` (Python 3.13, standard library only) draws the whole page itself:
a hand-written 5×7 bitmap font, a small canvas library (rects, lines, discs,
triangles), four drawn pictograms, and a hand-rolled PNG encoder. No network,
no clock, no randomness — two runs write byte-identical files.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, under 1 MiB)
```

## Verify determinism

```sh
MAKEFUN_OUTPUT_DIR=/tmp/a python3 main.py
MAKEFUN_OUTPUT_DIR=/tmp/b python3 main.py
sha256sum /tmp/a/entry.png /tmp/b/entry.png   # identical
```

## License

MIT — see [LICENSE](LICENSE).
