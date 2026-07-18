#!/usr/bin/env python3
"""Build eao/webapp/dist/index.html: inject site config + seed catalogue."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

def main(sheet_id="", sheet_gid="0"):
    with open(os.path.join(ROOT, "data", "eao_seed.json")) as f:
        seed = json.load(f)
    site = seed["site"]
    config = {"title": "Emirates Astronomical Observatory (EAO)",
              "sheet_id": sheet_id, "sheet_gid": sheet_gid,
              "site": {"lat": site["lat"], "lon": site["lon"],
                       "min_peak_alt": site["min_peak_alt"], "horizon": site["horizon"]}}
    with open(os.path.join(HERE, "template.html")) as f:
        tpl = f.read()
    out = (tpl.replace("__CONFIG_JSON__", json.dumps(config))
              .replace("__SEED_JSON__", json.dumps(seed)))
    os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)
    outp = os.path.join(HERE, "dist", "index.html")
    with open(outp, "w") as f:
        f.write(out)
    print(f"wrote {outp} ({len(out)//1024} KB, {len(seed['targets'])} seed targets, "
          f"sheet={'set' if sheet_id else 'unset'})")

if __name__ == "__main__":
    sid = sys.argv[1] if len(sys.argv) > 1 else ""
    gid = sys.argv[2] if len(sys.argv) > 2 else "0"
    main(sid, gid)
