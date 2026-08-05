"""
generate_sample_data.py — synthetic OhioT1DM-format data for smoke-testing the pipeline.

The OhioT1DM dataset cannot be redistributed (it requires a Data Use Agreement
with the University of North Carolina at Charlotte). This script generates
FULLY SYNTHETIC files that follow the same XML schema, so that anyone can run
the pipeline end to end and verify that it executes.

The values are simulated. They are NOT patient data and must NOT be used to
reproduce or interpret any result reported in the paper. To reproduce the
reported results, request the real dataset and point the configuration at it.

Usage:
    python S.GenerateSampleData.py --out ./sample_data --days 5
    python S.GenerateSampleData.py --out ./sample_data --ids 559 588

NOTE: the parser assigns CSV column names by the position of each child element,
not by its tag name, so the order of the <basis_*> blocks below must match the
real files exactly (heart_rate, gsr, skin_temperature, air_temperature, steps,
sleep). Reordering them silently mislabels the output columns.
"""

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

SEED = 20260801
IDS = [540, 544, 552, 559, 563, 567, 570, 575, 584, 588, 591, 596]
START = datetime(2030, 1, 7, 0, 0, 0)          # obviously-synthetic future date
TS = "%d-%m-%Y %H:%M:%S"

MEALS = [("Breakfast", 8, 45), ("Lunch", 13, 60), ("Dinner", 19, 70), ("Snack", 16, 20)]


def fmt(dt):
    return dt.strftime(TS)


def simulate_day(rng, day_start):
    """One day of 5-minute CGM readings with meal excursions and a dawn rise."""
    readings, meals, boluses = [], [], []

    events = []
    for name, hour, carbs in MEALS:
        if name == "Snack" and rng.random() < 0.5:
            continue
        jitter = rng.randint(-40, 40)
        t = day_start + timedelta(hours=hour, minutes=jitter)
        c = max(5, int(rng.gauss(carbs, carbs * 0.25)))
        events.append((t, name, c))

    bg = rng.gauss(130, 15)
    for step in range(288):                      # 24 h at 5-min resolution
        t = day_start + timedelta(minutes=5 * step)
        hour = t.hour + t.minute / 60

        # slow drift back toward target, plus a dawn-phenomenon bump
        bg += (120 - bg) * 0.02
        if 4 <= hour <= 8:
            bg += 0.35
        bg += rng.gauss(0, 2.5)

        # post-meal excursion: rise over ~1 h, decay over ~3 h
        for mt, _, carbs in events:
            dt_min = (t - mt).total_seconds() / 60
            if 0 <= dt_min <= 240:
                amp = carbs * 1.4
                bg += amp * (0.045 if dt_min < 60 else -0.012)

        bg = min(max(bg, 45), 380)
        readings.append((t, int(round(bg))))

    for mt, name, carbs in events:
        meals.append((mt, name, carbs))
        boluses.append((mt - timedelta(minutes=5), round(carbs / 10.0, 1), carbs))

    return readings, meals, boluses


def build_patient(pid, days, rng):
    root = Element("patient", {
        "id": str(pid),
        "weight": str(rng.randint(65, 105)),
        "insulin_type": "Novalog",
    })

    all_readings, all_meals, all_boluses = [], [], []
    for d in range(days):
        r, m, b = simulate_day(rng, START + timedelta(days=d))
        all_readings += r
        all_meals += m
        all_boluses += b

    g = SubElement(root, "glucose_level")
    for t, v in all_readings:
        SubElement(g, "event", {"ts": fmt(t), "value": str(v)})

    fs = SubElement(root, "finger_stick")
    for t, v in all_readings[::144]:             # roughly twice a day
        SubElement(fs, "event", {"ts": fmt(t), "value": str(v)})

    ba = SubElement(root, "basal")
    for d in range(days):
        for hour in (0, 6, 12, 18):
            t = START + timedelta(days=d, hours=hour)
            SubElement(ba, "event", {"ts": fmt(t),
                                     "value": str(round(rng.uniform(0.45, 0.95), 2))})

    SubElement(root, "temp_basal")

    bo = SubElement(root, "bolus")
    for t, dose, carbs in all_boluses:
        SubElement(bo, "event", {"ts_begin": fmt(t), "ts_end": fmt(t),
                                 "type": "normal", "dose": str(dose),
                                 "bwz_carb_input": str(carbs)})

    me = SubElement(root, "meal")
    for t, name, carbs in all_meals:
        SubElement(me, "event", {"ts": fmt(t), "type": name, "carbs": str(carbs)})

    sl = SubElement(root, "sleep")
    for d in range(days):
        b_ = START + timedelta(days=d, hours=23, minutes=rng.randint(0, 50))
        e_ = START + timedelta(days=d + 1, hours=6, minutes=rng.randint(0, 50))
        SubElement(sl, "event", {"ts_begin": fmt(b_), "ts_end": fmt(e_),
                                 "quality": str(rng.randint(2, 4))})

    wk = SubElement(root, "work")
    for d in range(days):
        b_ = START + timedelta(days=d, hours=8)
        e_ = START + timedelta(days=d, hours=17)
        SubElement(wk, "event", {"ts_begin": fmt(b_), "ts_end": fmt(e_),
                                 "intensity": str(rng.randint(2, 5))})

    for tag in ("stressors", "hypo_event", "illness", "exercise"):
        SubElement(root, tag)

    hr = SubElement(root, "basis_heart_rate")
    gs = SubElement(root, "basis_gsr")
    sk = SubElement(root, "basis_skin_temperature")
    ai = SubElement(root, "basis_air_temperature")
    st = SubElement(root, "basis_steps")
    for t, _ in all_readings:
        ts = fmt(t)
        awake = 7 <= t.hour <= 22
        SubElement(hr, "event", {"ts": ts, "value": str(rng.randint(58, 95))})
        SubElement(st, "event", {"ts": ts,
                                 "value": str(rng.randint(0, 120) if awake else 0)})
        SubElement(sk, "event", {"ts": ts, "value": str(round(rng.uniform(80, 92), 2))})
        SubElement(ai, "event", {"ts": ts, "value": str(round(rng.uniform(70, 88), 2))})
        SubElement(gs, "event", {"ts": ts, "value": f"{rng.uniform(5e-5, 2e-4):.1E}"})

    SubElement(root, "basis_sleep")
    return root


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="sample_data", help="output directory")
    ap.add_argument("--days", type=int, default=5, help="days per participant")
    ap.add_argument("--ids", type=int, nargs="+", default=IDS,
                    help="participant identifiers to generate "
                         "(default: all twelve OhioT1DM identifiers)")
    ap.add_argument("--seed", type=int, default=SEED,
                    help="base seed; a per-participant seed is derived from it "
                         f"(default: {SEED}, mirrored in globals.DEMO_SEED)")
    args = ap.parse_args()

    # The per-participant seed is derived from the identifier, so a given
    # identifier always yields the same file whether it is generated on its
    # own or as part of the full set.
    unknown = [i for i in args.ids if i not in IDS]
    if unknown:
        ap.error(f"not OhioT1DM identifiers: {unknown}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    for pid in args.ids:
        rng = random.Random(args.seed + pid)     # deterministic per participant
        root = build_patient(pid, args.days, rng)
        xml = minidom.parseString(tostring(root)).toprettyxml(indent="  ")
        path = out / f"{pid}-ws-training.xml"
        path.write_text(xml, encoding="utf-8")
        print(f"wrote {path}")

    (out / "README.txt").write_text(
        "SYNTHETIC DATA - NOT PATIENT DATA\n"
        "=================================\n\n"
        "These files were produced by generate_sample_data.py. They follow the\n"
        "OhioT1DM XML schema so that the pipeline can be executed end to end,\n"
        "but every value is simulated.\n\n"
        "They must not be used to reproduce or interpret any reported result.\n"
        "The real dataset requires a Data Use Agreement; see the project README\n"
        "for how to request it and where to place it.\n\n"
        f"Generated: {len(args.ids)} participant(s), {args.days} day(s) each, "
        f"base seed {args.seed}.\n"
        "A short run is enough to verify that every pipeline step executes, but\n"
        "the resulting figures are sparse and the last day of each participant\n"
        "is incomplete, because the midnight-overflow trimming needs the\n"
        "following day to close. This is expected, not a fault.\n",
        encoding="utf-8",
    )
    print(f"wrote {out / 'README.txt'}")


if __name__ == "__main__":
    main()
