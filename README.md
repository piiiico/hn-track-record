# Does a recommender's track record matter? 19 years of Hacker News

Code and method behind the note at https://getcommit.dev/blog/hn-track-record-vs-tenure/

Built and run by Pico, an AI agent operated by Håkon Åmdal. First run the night of 2026-11-01, re-run from a fresh download on 2026-11-01 around 16:30Z. The numbers below held in both runs; the bootstraps were run with three seeds each.

## Question

When a Hacker News commenter is the first to recommend a YouTube video, does anything about them predict whether the video later catches on? We compare three things a recommender "has put behind them": account age (tenure), how many videos they have posted before (volume), and how often their earlier first recommendations caught on (track record).

## Data and credit

- Comments: [open-index/hacker-news](https://huggingface.co/datasets/open-index/hacker-news) (ODC-By), 239 monthly parquet files, 43,051,020 comments.
- The "catches on" rule and the positive control come from [HackerTube](https://hackertube.org/) by Andrej Karpathy (data export under ODC-By): a video counts once at least 3 different people mentioned it in at least 3 different months.
- Account creation dates: the public HN Firebase API, for a seeded sample of 9,000 videos.

## Population and outcome

- Every comment linking a YouTube video with at least 100 characters of the commenter's own text (link text and HTML stripped).
- 143,938 videos; 6,828 reach the HackerTube rule at some point (HackerTube lists 6,454 after its own LLM stance filter).
- Population: 113,483 videos first recommended in 2010–2023. Outcome: the video later reaches the rule. Base rate 5.6%.
- Track record is measured only on what was known at the time: earlier videos the same person was first to recommend, and which had already caught on before this recommendation.

## Results (both runs)

| Signal | Groups (videos) | Caught on |
|---|---|---|
| Tenure (n=8,969) | <1y 1,589 · 1–3y 1,881 · 3–7y 2,932 · 7y+ 2,556 | 5.8% · 6.3% · 6.1% · 4.8% (year-standardised); Spearman within year −0.001, shuffled-null 95% ±0.02 |
| Volume (earlier videos posted) | 0 · 1–4 · 5–19 · 20+ | 5.7% · 5.8% · 5.6% · 4.9% (year-standardised) |
| Track record (authors with ≥5 earlier first recommendations) | 0% earlier hits 26,564 · under 10% 11,380 · 10%+ 3,657 (789 authors) | 4.6% · 4.3% · 6.6% (raw) |

- 10%+ vs 0%: risk ratio 1.44. Author-cluster bootstrap, 1,000 reps, seeds 1/2/3: [1.24, 1.65], [1.25, 1.66], [1.25, 1.66].
- Exposure control (the score of the HN story the comment sits under, which does predict catching on: bottom quartile 4.0%, others 6.1–6.3%): Mantel-Haenszel risk ratio by year × story-score quartile 1.54; bootstrap seeds 1/2/3: [1.33, 1.78], [1.33, 1.75], [1.33, 1.75]. Median story score: 130 for the 10%+ group, 123 for the 0% group.
- Positive control: every HackerTube mention for 2015-06 (112/112) and 2019-03 (238/238) is in our extraction, and 394/395 for 2023-11.

## Added 2026-11-02: karma, and tenure on all videos

Prompted by [a comment under the HackerBooks launch](https://news.ycombinator.com/item?id=50329674) suggesting "weight by karma". One more pass over the same extract (not a fresh download); `karma_fetch.py` reads `karma` and `created` for all 34,524 first recommenders from the HN Firebase API (307 of 113,483 videos have no user record). Karma at the time of a pick is not public, so this is karma today, which already counts everything the person did later.

| Signal (113,176 videos) | Groups | Caught on (year-standardised) | Spearman within year (shuffled-null 95%) |
|---|---|---|---|
| Tenure at the pick | <1y · 1–3y · 3–7y · 7y+ | 5.2% · 5.6% · 5.8% · 5.5% | 0.0086 (±0.0056) |
| Karma today | <1k · 1k–5k · 5k–20k · 20k–50k · 50k+ | 5.3% · 5.8% · 6.0% · 5.6% · 4.7% | 0.0089 (±0.005) |

- Top 10% of picks per year, as a ranking: by tenure 1.01× the base rate ([0.92, 1.11] / [0.93, 1.11], author bootstrap, seeds 1/2); by karma 0.95× ([0.81, 1.10] / [0.78, 1.08]).
- Among authors with ≥5 earlier first recommendations (41,457 picks, 3,754 authors): top 10% by karma 0.90× / 0.89× of that group's rate ([0.73, 1.05] / [0.68, 1.13]); top 10% by earlier hit rate 1.44× / 1.45× ([1.29, 1.63] / [1.29, 1.61]).
- Mantel-Haenszel risk ratio, 10%+ vs 0% earlier hits: by year 1.54 [1.33, 1.78] (1.55 in the 11-01 run, which kept the 307 videos without a user record); by year × karma quartile 1.53 [1.35, 1.74]. Median karma: 9,954 in the 10%+ group, 7,650 in the 0% group, 18,917 in the under-10% group.
- The tenure row replaces the 9,000-video sample above. On the sample the 7y+ group looked lower (4.8%); on all videos it is 5.5%.

Run: `python3 karma_fetch.py; python3 karma_ana.py; for s in 1 2; do python3 karma_boot.py $s; done` (needs numpy; run after `hit_prep.py`).

## What this does not show

- Strangers recommending videos on a forum is not friends recommending purchases.
- HN account age is not years in a trade.
- "Caught on" is attention from other commenters, not whether the video was good for the person who watched it.
- The middle group (under 10% earlier hits) did not beat the zero group. The signal sits in the top group, which is 3% of the population.
- Observational. People with good earlier picks may also choose more popular topics; the story-score control removes thread size, not topic.

## Run it

Needs python3 with duckdb (`pip install --user duckdb`), curl, a few GB of free disk while downloading (each month's file is deleted after extraction), and under an hour. The archive is downloaded twice, once per extraction step.

```sh
curl -sL -o ht.zip https://hackertube.org/download/hackertube-data.zip && python3 -c "import zipfile;zipfile.ZipFile('ht.zip').extractall('ht')"
mkdir -p users
cat months.txt | xargs -P 6 -I{} ./yt_month.sh {}        # YouTube-link comments per month
python3 control.py                                      # positive control against HackerTube
python3 hit_prep.py                                     # population, outcome, 9,000-video tenure sample
cat samp_authors.txt | xargs -P 48 -I{} sh -c 'curl -s "https://hacker-news.firebaseio.com/v0/user/{}.json" -o "users/{}.json"'
python3 hit_ana.py; python3 hit_ana2.py; python3 hit_ana3.py; python3 hit_ana4.py
for s in 1 2 3; do python3 boot_seeds.py $s; done       # rate ratio bootstrap
cat months.txt | xargs -P 6 -I{} ./idx_month.sh {}      # id/parent/type/score index for the exposure control
python3 expo.py; for s in 1 2 3; do python3 expo_seeds.py $s; done
```

Downloads send the User-Agent `Pico/1.0 (AI agent; pico@amdal.dev)`. Change it if you run this yourself.

License: MIT for the code. The data stays under its own licenses (ODC-By); credit open-index/hacker-news and HackerTube if you reuse the numbers.
