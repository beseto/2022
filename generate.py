#!/usr/bin/env python3
import pandas as pd
import sys
from pathlib import Path
import yaml

type_map = {
    "Symposium 1": "Symposium 1: Neuroscience and Biological Psychiatry",
    "Symposium 2": "Symposium 2: Emotion, Cognition, and Behavior",
    "Symposium 3": "Symposium 3: Stress and Social Psychiatry",
}

keywords = [
    "",
    "Schizophrenia and related disorders",
    "Mood disorders",
    "Neurotic disorders",
    "Personality disorders",
    "Epilepsy",
    "Dementia",
    "Behavioral syndromes associated w/ physical factors",
    "Organic/symptomatic disorders",
    "Substance abuse/dependence",
    "Childhood & adolescence",
    "Sleep disorders",
    "Mental retardation",
    "Mental disorders in old age",
    "Forensic psychiatry",
    "Mental health & welfare",
    "Medical education",
    "Psychopathology",
    "Neuropsychology",
    "Neurophysiology",
    "Psychopharmacology",
    "Neurochemistry",
    "Neuropathology",
    "Genetics & molecular genetics",
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


PREDEFINED_ENTRIES = [
    {"name": "Sign in on Zoom", "time_start": "8:30", "time_end": "9:00"},
    {"name": "Opening", "time_start": "9:00", "time_end": "9:10"},
    {"name": "Discussion 1", "time_start": "10:10", "time_end": "10:30"},
    {"name": "Discussion 2", "time_start": "11:35", "time_end": "11:55"},
    {"name": "Lunch break", "time_start": "11:55", "time_end": "13:00"},
    {"name": "Short Oral Presentations", "time_start": "13:00", "time_end": "14:30"},
    {"name": "Discussion 3", "time_start": "16:40", "time_end": "17:00"},
    {"name": "Closing", "time_start": "17:00", "time_end": "17:10"},
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

    def sort_entries(entries: list[dict[str, str]]) -> list[dict[str, str]]:
        return sorted(entries, key=lambda x: list(map(int, x["time_start"].split(":"))))

    res = {
        "days": [
            {
                "name": "Main Sessions",
                "abbr": "Main",
                "date": "2022-11-13",
                "rooms": [
                    {
                        "name": "Main",
                        "talks": sort_entries(
                            get_entries(tbl[tbl["Type"] != "Short Oral"])
                            + PREDEFINED_ENTRIES
                        ),
                    },
                ],
            },
            {
                "name": "Short Oral Sessions",
                "abbr": "ShortOral",
                "date": "2022-11-13",
                "rooms": [
                    {
                        "name": "Room A",
                        "talks": sort_entries(get_entries(tbl[tbl["Room"] == "A"])),
                    },
                    {
                        "name": "Room B",
                        "talks": sort_entries(get_entries(tbl[tbl["Room"] == "B"])),
                    },
                    {
                        "name": "Room C",
                        "talks": sort_entries(get_entries(tbl[tbl["Room"] == "C"])),
                    },
                    {
                        "name": "Room D",
                        "talks": sort_entries(get_entries(tbl[tbl["Room"] == "D"])),
                    },
                    {
                        "name": "Room E",
                        "talks": sort_entries(get_entries(tbl[tbl["Room"] == "E"])),
                    },
                ],
            },
        ]
    }
    yaml.dump(res, open(Path(".") / "_data" / "program.yml", "w"), sort_keys=False)


def generate_talks(tbl: pd.DataFrame):
    content = """---
name: "{Title}"
speakers:
{presenters}
categories:
  - "{Type}"
  - "{Institution}"
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
        #        if talk["Type"] == "Short Oral":
        #            links = f"""links:
        #  - name: Slides
        #    file: dummy.pdf
        # """
        # filename should be replaced with {fname}.{talk['SlideExt']}
        presenters = "\n".join(
            '  - "{}"'.format(name.strip()) for name in talk["Presenter"].split("&")
        )
        with open(Path(".") / "_talks" / f"{fname}.md", "w") as f:
            f.write(
                content.format(**talk, cats=cats, links=links, presenters=presenters)
            )


def generate_predefs():
    for item in PREDEFINED_ENTRIES:
        with open(
            Path(".")
            / "_talks"
            / f"{item['name'].lower().replace(' ', '_').replace('#','')}.md",
            "w",
        ) as f:
            typ = (
                type_map[item["name"].replace("Discussion", "Symposium")]
                if item["name"].startswith("Discussion")
                else "Other"
            )
            f.write(f"---\nname: {item['name']}\ncategories:\n  - \"{typ}\"\n---\n")


def generate_persons(tbl: pd.DataFrame):
    content = """---
name: "{name}"
first_name: "{fst}"
last_name: "{lst}"
---

"""

    done_names: set[str] = set()
    for talk in tbl.to_dict("records"):
        for name in talk["Presenter"].split("&"):
            name = name.strip()
            if name in done_names:
                continue
            done_names.add(name)
            if name.startswith("Mr."):
                name = " ".join(name.split(" ")[1:])
            parts = name.split(" ")
            fst, lst = " ".join(parts[:-1]), parts[-1]
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
    df["KeywordIDs"] = df["KeywordIDs"].apply(
        lambda x: ",".join(str(int(float(e))) for e in x.split(","))
        if isinstance(x, str)
        else str(int(x))
        if not pd.isna(x)
        else ""
    )
    df["Type"] = df["Type"].replace(type_map)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    reset_all()
    generate_program(df)
    generate_talks(df)
    generate_persons(df)
    generate_predefs()
