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
