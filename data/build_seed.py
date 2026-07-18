"""
Build the EAO seed catalogue (eao_seed.json): curated NB emission + broadband
targets (galaxies, clusters, reflection/dark nebulae, bright PNe/SNRs), with
OBSERVABILITY PRECOMPUTED for the fixed EAO site (Abu Dhabi). The dashboard then
only does the rig-dependent math (framing/score) live, so it stays fast even
when the cloud Action expands this to thousands of objects.

Reuses the narrowband-scout observability engine (same site).
imaging_type: NB (narrowband emission) | BB (broadband) | both
"""
import json, os, sys
sys.path.insert(0, "/home/claude/narrowband-scout")
from scout.observability import compute
from scout.config import SITE, RIG

# ---- broadband + "both" targets (name, common, type, imaging, ra, dec, maj', min', mag, sb, note) ----
BB = [
    # galaxies
    ("M31","Andromeda Galaxy","Galaxy","BB",10.685,41.269,190,60,3.4,"bright","Huge; fits short-FL frames, core detail at longer FL. Add Ha for its HII knots."),
    ("M33","Triangulum Galaxy","Galaxy","BB",23.462,30.660,70,42,5.7,"medium","Big face-on spiral; superb Ha regions - LRGB+Ha."),
    ("M51","Whirlpool Galaxy","Galaxy","BB",202.470,47.195,11,7,8.4,"medium","Classic interacting spiral; wants >=1000mm to fill frame."),
    ("M81","Bode's Galaxy","Galaxy","BB",148.888,69.065,27,14,6.9,"medium","Bright grand-design spiral; pairs with M82 at short FL."),
    ("M82","Cigar Galaxy","Galaxy","BB",148.968,69.680,11,4,8.4,"medium","Starburst edge-on; strong Ha outflow - LRGB+Ha."),
    ("M101","Pinwheel Galaxy","Galaxy","BB",210.802,54.349,29,27,7.9,"faint","Large low-SB face-on; needs dark sky + long integration."),
    ("M104","Sombrero Galaxy","Galaxy","BB",189.998,-11.623,9,4,8.0,"medium","Bright dust-lane edge-on; long FL."),
    ("M106","","Galaxy","BB",184.740,47.304,19,7,8.4,"medium","Bright spiral with anomalous arms; add Ha."),
    ("M63","Sunflower Galaxy","Galaxy","BB",198.955,42.029,13,7,8.6,"medium","Flocculent spiral; medium-long FL."),
    ("M64","Black Eye Galaxy","Galaxy","BB",194.182,21.683,10,5,8.5,"medium","Dark dust cap; long FL."),
    ("M94","","Galaxy","BB",192.721,41.120,11,9,8.2,"medium","Bright compact spiral with outer ring."),
    ("M74","Phantom Galaxy","Galaxy","BB",24.174,15.783,10,9,9.4,"faint","Grand-design face-on, low SB; add Ha."),
    ("M77","","Galaxy","BB",40.670,-0.013,7,6,8.9,"medium","Bright Seyfert; long FL."),
    ("NGC 891","","Galaxy","BB",35.639,42.349,14,2.5,9.9,"faint","Knife-edge dust-lane galaxy; long FL."),
    ("NGC 253","Sculptor Galaxy","Galaxy","BB",11.888,-25.288,27,7,7.1,"medium","Bright dusty starburst; sits at your southern edge - shoot at transit."),
    ("NGC 4565","Needle Galaxy","Galaxy","BB",189.087,25.988,16,2.5,9.6,"faint","Iconic edge-on; medium-long FL."),
    ("NGC 7331","","Galaxy","BB",339.267,34.416,10,4,9.5,"faint","Spiral with 'Deer Lick' companions; long FL."),
    ("NGC 2903","","Galaxy","BB",143.042,21.501,12,6,9.0,"medium","Bright barred spiral in Leo."),
    ("NGC 4631","Whale Galaxy","Galaxy","BB",190.533,32.541,15,3,9.2,"faint","Edge-on with the Crowbar; add Ha."),
    ("Leo Triplet","M65/M66/NGC 3628","Galaxy group","BB",170.06,13.20,50,30,9.0,"faint","Three galaxies in one field ~700-1000mm; a framing gem."),
    ("Markarian's Chain","","Galaxy group","BB",186.75,13.20,90,30,9.5,"faint","Virgo galaxy string; wide-ish FL, many galaxies per frame."),
    ("NGC 7814","Little Sombrero","Galaxy","BB",0.812,16.145,6,3,10.5,"faint","Compact edge-on; long FL."),
    ("Stephan's Quintet","","Galaxy group","BB",339.009,33.959,4,3,13.0,"vfaint","Tight compact group; 2000mm+ target."),
    # globular clusters
    ("M13","Hercules Cluster","Globular cluster","BB",250.421,36.460,20,20,5.8,"bright","Showpiece globular; medium-long FL, easy."),
    ("M3","","Globular cluster","BB",205.548,28.377,18,18,6.2,"bright","Rich bright globular."),
    ("M5","","Globular cluster","BB",229.638,2.081,23,23,5.6,"bright","One of the finest globulars."),
    ("M15","","Globular cluster","BB",322.493,12.167,18,18,6.2,"bright","Dense core globular."),
    ("M92","","Globular cluster","BB",259.281,43.136,14,14,6.4,"bright","Underrated bright globular."),
    ("M2","","Globular cluster","BB",323.363,-0.823,16,16,6.5,"bright","Bright globular in Aquarius."),
    ("M10","","Globular cluster","BB",254.288,-4.100,20,20,6.6,"medium","Bright Ophiuchus globular."),
    ("M22","","Globular cluster","BB",279.100,-23.905,32,32,5.1,"bright","Huge bright globular; low south - shoot at transit."),
    # open clusters
    ("M45","Pleiades","Open cluster + reflection","both",56.75,24.117,110,110,1.6,"bright","Bright stars + blue reflection nebulosity; short FL, LRGB (long L for dust)."),
    ("M44","Beehive Cluster","Open cluster","BB",130.10,19.667,95,95,3.7,"bright","Big bright cluster; short FL."),
    ("M11","Wild Duck Cluster","Open cluster","BB",282.766,-6.267,14,14,6.3,"bright","Dense rich open cluster."),
    ("M35","","Open cluster","BB",92.27,24.35,28,28,5.3,"bright","Large open cluster with NGC 2158 nearby."),
    ("Double Cluster","NGC 869 & 884","Open cluster","BB",34.75,57.14,60,30,4.3,"bright","Twin clusters in one field; short-medium FL, gorgeous."),
    ("M36","","Open cluster","BB",84.0,34.13,12,12,6.3,"bright","Auriga cluster; frame with M37/M38."),
    ("M37","","Open cluster","BB",88.07,32.55,24,24,6.2,"bright","Richest Auriga open cluster."),
    ("M38","","Open cluster","BB",82.17,35.85,21,21,7.4,"medium","Auriga cluster; near Sh2-229."),
    ("M34","","Open cluster","BB",40.50,42.72,35,35,5.5,"bright","Loose bright cluster in Perseus."),
    ("M52","","Open cluster","BB",351.20,61.59,13,13,7.3,"medium","Cassiopeia cluster; near the Bubble Nebula."),
    ("NGC 457","Owl / ET Cluster","Open cluster","BB",19.90,58.29,13,13,6.4,"bright","Charming 'ET' cluster in Cassiopeia."),
    # reflection / dark nebulae
    ("NGC 7023","Iris Nebula","Reflection nebula","BB",315.40,68.16,18,18,6.8,"medium","Blue reflection nebula in dark dust; LRGB, long L."),
    ("IC 2118","Witch Head Nebula","Reflection nebula","BB",76.90,-7.23,180,60,None,"vfaint","Huge faint blue reflection; short FL, very dark sky."),
    ("M78","","Reflection nebula","BB",86.69,0.05,8,6,8.3,"medium","Brightest reflection nebula; LRGB."),
    ("NGC 1333","","Reflection nebula","BB",52.29,31.32,6,6,None,"faint","Reflection + dust in Perseus molecular cloud."),
    ("Barnard 150","Seahorse Nebula","Dark nebula","BB",324.50,50.50,60,20,None,"faint","Dark molecular filament; LRGB, long L, dark sky."),
    ("LDN 1235","Dark Shark Nebula","Dark nebula","BB",331.90,73.00,60,25,None,"faint","Dark nebula 'shark'; wide-ish FL, very dark sky."),
    # bright emission also great in broadband ("both")
    ("M42","Orion Nebula","Emission nebula","both",83.822,-5.391,85,60,4.0,"bright","The showpiece; huge dynamic range. SHO or LRGB+Ha. Low south - transit."),
    ("M43","De Mairan's Nebula","Emission nebula","both",83.880,-5.270,20,15,9.0,"medium","Part of the Orion complex."),
    ("M8","Lagoon Nebula","Emission nebula","both",270.92,-24.38,90,40,6.0,"bright","Bright HII; low south - shoot at transit. SHO/HOO or LRGB+Ha."),
    ("M20","Trifid Nebula","Emission + reflection","both",270.60,-23.03,28,28,6.3,"medium","Emission + blue reflection; low south."),
    ("M16","Eagle Nebula","Emission nebula","both",274.70,-13.81,35,28,6.0,"medium","Pillars of Creation; SHO shines."),
    ("M17","Omega / Swan Nebula","Emission nebula","both",275.20,-16.17,46,37,6.0,"bright","Very bright HII; SHO/HOO."),
    ("M27","Dumbbell Nebula","Planetary nebula","both",299.90,22.72,8,6,7.4,"bright","Bright big PN; HOO/SHO or LRGB+Ha; medium-long FL."),
    ("M57","Ring Nebula","Planetary nebula","both",283.40,33.03,1.4,1.0,8.8,"bright","Small bright ring; 1500mm+; HOO."),
    ("M76","Little Dumbbell","Planetary nebula","both",25.58,51.58,3.1,2.0,10.1,"medium","Bipolar PN; long FL; HOO."),
    ("M97","Owl Nebula","Planetary nebula","both",168.70,55.02,3.4,3.3,9.9,"medium","Round PN; long FL; HOO. Pairs with M108."),
    ("M1","Crab Nebula","Supernova remnant","both",83.633,22.015,6,4,8.4,"medium","Bright SNR; SHO or LRGB+Ha; medium-long FL."),
    ("NGC 7000","North America Nebula","Emission nebula","both",314.75,44.53,120,100,4.0,"bright","Huge; short FL. SHO/HOO or Ha+RGB."),
    ("IC 5070","Pelican Nebula","Emission nebula","both",313.10,44.36,60,50,8.0,"medium","Beside the North America; SHO."),
    ("IC 1805","Heart Nebula","Emission nebula","both",38.20,61.45,150,150,6.5,"medium","Big classic; short FL; SHO."),
    ("IC 1848","Soul Nebula","Emission nebula","both",43.30,60.43,100,60,6.5,"medium","Pairs with the Heart; short FL; SHO."),
    ("NGC 2237","Rosette Nebula","Emission nebula","both",97.95,4.95,80,80,9.0,"medium","Big flower; short-medium FL; SHO."),
    ("NGC 7635","Bubble Nebula","Emission nebula","both",350.20,61.20,15,8,10.0,"medium","Wind-blown bubble; medium-long FL; SHO."),
    ("NGC 281","Pacman Nebula","Emission nebula","both",13.23,56.62,35,30,7.0,"medium","Pac-Man shape; medium FL; SHO."),
    ("NGC 1499","California Nebula","Emission nebula","both",60.00,36.60,160,40,6.0,"medium","Very long; short FL; Ha/SHO."),
    ("IC 434","Horsehead Nebula","Emission nebula","both",85.24,-2.46,30,30,6.8,"medium","Horsehead + Flame; medium FL; Ha/SHO."),
    ("NGC 2264","Cone & Christmas Tree","Emission nebula","both",100.24,9.90,40,30,3.9,"medium","Cone + cluster + Fox Fur; medium FL; SHO."),
]

FIELDS_BB = ["name","common_name","type","imaging_type","ra_deg","dec_deg",
             "size_major_arcmin","size_minor_arcmin","magnitude","surface_brightness","note"]


def load_nb():
    with open("/home/claude/narrowband-scout/data/seed_catalog.json") as f:
        nb = json.load(f)["targets"]
    for t in nb:
        t["imaging_type"] = "NB"
        t["magnitude"] = None
    return nb


def main():
    rows = load_nb()
    for r in BB:
        d = dict(zip(FIELDS_BB, r))
        d["id"] = d["name"].lower().replace(" ", "-")
        d["emission"] = d.get("emission", "")  # BB have none
        d["novelty"] = "classic"
        d["low_precision"] = False
        d["ref_url"] = ""
        rows.append(d)

    out = []
    for t in rows:
        obs = compute(SITE, RIG, t["ra_deg"], t["dec_deg"])
        if not obs.observable:
            continue
        t.update({
            "peak_alt_deg": obs.peak_alt_deg,
            "best_months": obs.best_months_label,
            "peak_dark_hours": obs.peak_dark_hours,
            "monthly_dark_hours": obs.monthly_dark_hours,
            "monthly_night_max_alt": obs.monthly_night_max_alt,
        })
        out.append(t)

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "eao_seed.json"), "w") as f:
        json.dump({"version": "1.0", "site": {"lat": SITE.lat_deg, "lon": SITE.lon_deg,
                   "min_peak_alt": SITE.min_peak_alt_deg, "horizon": SITE.scope_horizon_deg},
                   "targets": out}, f)
    nb = sum(1 for t in out if t["imaging_type"] == "NB")
    bb = sum(1 for t in out if t["imaging_type"] == "BB")
    both = sum(1 for t in out if t["imaging_type"] == "both")
    print(f"wrote {len(out)} targets (NB {nb}, BB {bb}, both {both})")


if __name__ == "__main__":
    main()
