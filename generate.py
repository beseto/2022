#!/usr/bin/env python3
import pandas as pd
import sys
from pathlib import Path
import yaml

keywords = [
    "",
    "Schizophrenia and related disorders",
    "Mood disorders",
    "Neurotic disorders and related disorders",
    "Personality disorders",
    "Epilepsy",
    "Dementia",
    "Behavioural syndromes associated with physiological disturbances and physical factors",
    "Organic and symptomatic mental disorders",
    "Substance abuse and dependence",
    "Mental disorders in childhood and adolescence",
    "Sleep disorders",
    "Mental retardation",
    "Mental disorders in old age",
    "Forensic psychiatry",
    "Mental health and welfare",
    "Medical education",
    "Psychopathology",
    "Neuropsychology",
    "Neurophysiology",
    "Psychopharmacology",
    "Neurochemistry",
    "Neuropathology",
    "Genetics and molecular genetics",
    "Epidemiology",
    "Community mental health services",
    "Emergency psychiatry",
    "Consultation-liaison psychiatry",
    "Psychiatric diagnosis",
    "Symptomatology",
    "Pharmacotherapy",
    "Psychotherapy",
    "Psychosocial therapy/psychoeducation",
    "ECT/TMS/neuromodulation",
    "Laboratory tests/biomarkers",
    "Neuroimaging",
    "Animal model/basic research",
    "Suicide prevention",
    "Occupational mental health",
    "Social psychiatry",
    "COVID-19",
    "AI",
    "Others",
]


def generate_program(tbl: pd.DataFrame):
    # pre-defined structures
    def get_entries(df: pd.DataFrame) -> list[dict[str, str]]:
        res: list[dict[str, str]] = []
        for row in df.to_dict("records"):
            item = {
                "name": row["Title"],
                "time_start": row["StartTime"].strftime("%-H:%M"),
                "time_end": row["EndTime"].strftime("%-H:%M"),
            }
            res.append(item)
        return res

    res = {
        "days": [
            {
                "name": "BESETO",
                "abbr": "BESETO",
                "date": "2022-11-13",
                "rooms": [
                    {
                        "name": "Main",
                        "talks": get_entries(tbl[tbl["Type"] != "Short Oral"]),
                    },
                    {
                        "name": "Room A",
                        "talks": get_entries(tbl[tbl["Room"] == "A"]),
                    },
                    {
                        "name": "Room B",
                        "talks": get_entries(tbl[tbl["Room"] == "B"]),
                    },
                    {
                        "name": "Room C",
                        "talks": get_entries(tbl[tbl["Room"] == "C"]),
                    },
                    {
                        "name": "Room D",
                        "talks": get_entries(tbl[tbl["Room"] == "D"]),
                    },
                    {
                        "name": "Room E",
                        "talks": get_entries(tbl[tbl["Room"] == "E"]),
                    },
                ],
            }
        ]
    }
    yaml.dump(res, open(Path(".") / "_data" / "program.yml", "w"), sort_keys=False)


def generate_talks(tbl: pd.DataFrame):
    content = """---
name: {Title}
speakers:
  - {Presenter}
categories:
  - {Type}
  - {Institution}
{cats}{links}
---

{Abstract}
"""

    for talk in tbl.to_dict("records"):
        cats = ""
        for kid in talk["KeywordIDs"].split(","):
            if kid != "":
                cats += f"  - {keywords[int(float(kid))]}\n"
        fname = (
            talk["Title"].lower().replace(" ", "_").replace("/", "_").replace(":", "_")
        )
        links = ""
        if talk["Type"] == "Short Oral":
            links = f"""links:
  - name: Slides
    file: dummy.pdf
"""
        # filename should be replaced with {fname}.{talk['SlideExt']}
        with open(Path(".") / "_talks" / f"{fname}.md", "w") as f:
            f.write(content.format(**talk, cats=cats, links=links))


def generate_persons(tbl: pd.DataFrame):
    content = """---
name: {name}
first_name: {fst}
last_name: {lst}
---

"""

    done_names = set()
    for talk in tbl.to_dict("records"):
        name = talk["Presenter"]
        if name.startswith("Mr."):
            name = " ".join(name.split(" ")[1:])
        fst, lst = name.split(" ")
        fname = name.lower().replace(" ", "_").replace("/", "_").replace(":", "_")
        with open(Path(".") / "_speakers" / f"{fname}.md", "w") as f:
            f.write(content.format(name=name, fst=fst, lst=lst))


def reset_all():
    for f in Path(".").glob("_speakers/*.md"):
        f.unlink()
    for f in Path(".").glob("_talks/*.md"):
        f.unlink()
    f = Path(".") / "_data" / "program.yml"
    if f.exists():
        f.unlink()


if __name__ == "__main__":
    df = pd.read_excel(sys.argv[1], dtype={"KeywordIDs": str, "Order": int})
    reset_all()
    generate_program(df)
    generate_talks(df)
    generate_persons(df)
