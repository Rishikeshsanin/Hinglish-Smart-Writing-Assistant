"""No real BharatGen output here: synthetic fixtures validate private review workflow."""
from __future__ import annotations
import csv
import json
import zipfile
import pytest
from scripts import review_bharatgen_evidence as review


def make_fixture(tmp_path):
    path=tmp_path/"private-example.zip"
    lines=[json.dumps({"event":"generation","case_id":f"H{i:02}",
                       "input":f"टेस्ट {i}","candidate":f"सुधार {i}",
                       "runtime_candidate_ok":True},ensure_ascii=False)
           for i in range(1,11)]
    with zipfile.ZipFile(path,"w") as bundle:
        bundle.writestr("ten-cases.jsonl","\n".join(lines))
    return path


def test_human_review_template_keeps_private_outputs_outside_public_path(monkeypatch,tmp_path):
    monkeypatch.setattr(review,"SAFE",tmp_path/"private_research")
    incoming=make_fixture(tmp_path)
    output=review.SAFE/"review.csv"
    assert review.build_private_review(incoming,output)==10
    with output.open(encoding="utf-8") as fh:
        rows=list(csv.DictReader(fh))
    assert rows[0]["candidate_hindi"]=="सुधार 1"
    assert not rows[0]["meaning_0_2"]
    assert not rows[0]["reviewer"]
    assert not (tmp_path/"docs"/"review.csv").exists()


def test_review_does_not_accept_unrated_or_anonymous_scores(monkeypatch,tmp_path):
    monkeypatch.setattr(review,"SAFE",tmp_path/"private_research")
    review.SAFE.mkdir()
    incoming=make_fixture(tmp_path)
    output=review.SAFE/"review.csv"
    review.build_private_review(incoming,output)
    with pytest.raises(ValueError,match="reviewer"):
        review.aggregate_review(output)
    rows=list(csv.DictReader(output.open(encoding="utf-8")))
    for row in rows:
        row.update(reviewer="human",grammar_0_2="2",meaning_0_2="2",
                   entities_0_2="2",unnecessary_edit_0_2="2")
    with output.open("w",encoding="utf-8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=review.FIELDS)
        writer.writeheader();writer.writerows(rows)
    aggregate=review.aggregate_review(output)
    assert aggregate["acceptable_meaning_and_entities_count"]==10
    assert "candidate_hindi" not in aggregate
