# Private BharatGen 10-case human review — do not publish raw output

The pretrained BharatGen experiment has already produced ten actual candidates
in the user's private Colab evidence ZIP. This script turns those records into a
**private, human-ratable** CSV, without copying output sentences into public
GitHub, the academic PDF or a shared Drive folder.

```bash
python scripts/review_bharatgen_evidence.py --create-from-zip /path/to/bharatgen-private-zip
```

Edit **private_research/bharatgen-human-review.csv**, which is gitignored.
Each candidate needs an independently reasoned 0/1/2 score for:

- **grammar**: 0 incorrect or broken, 1 partly improved, 2 grammatical;
- **meaning**: 0 changed essential meaning, 1 doubtful, 2 meaning preserved;
- **entities**: 0 names/times/facts altered, 1 unclear, 2 all constraints preserved;
- **unnecessary_edit**: 0 harmful needless edits, 1 cosmetic/some, 2 no harmful edits.

Enter a real reviewer identifier and short notes per row; incomplete scores fail.
If the only reviewer is the project author or an AI assistant, disclose that and
do not call the review **independent expert validation**.

For an aggregate-only, private summary:

```bash
python scripts/review_bharatgen_evidence.py --summarize private_research/bharatgen-human-review.csv
```

No generated Hindi sentences are printed in the aggregate. Scores on ten
self-authored sentences cannot establish broad model reliability. **Do not
upload the private review CSV, ZIP, screenshots or log to the public repo.**
Obtain BharatGen permission before sharing individual generated outputs publicly.
