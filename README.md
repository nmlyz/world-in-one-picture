# world-in-one-picture

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/nmlyz/world-in-one-picture/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/nmlyz/world-in-one-picture/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A single-file Python program that draws a newspaper front page summing up the world news of Sunday 22 November 2026 — the overnight missile attack on Ukraine, the missiles stopped over Riyadh, the market sell-off into correction, the EU budget fight, the boat disaster in Nigeria, Cyclone Akvan in India, Voyager 1 reaching one light-day from Earth, and the Amputee Football World Cup final — as one 1024x1024 PNG, drawn entirely with code (a hand-made bitmap font, no external assets) using only the Python standard library.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program writes `entry.png` to the output directory. It uses no network and is fully deterministic: every run produces the same bytes.
