#!/usr/bin/env python3
"""
Add a symmetric 'nonfiducial_modelling' template to the bb4l_bkg process of a
combine shapes file.

The bb4l_bkg histograms are in DETECTOR binning, while the variation is given
per PARTICLE bin. Every detector bin inside a particle bin gets that particle
bin's variation:

    Up   = nominal * (1 + p_i/100)
    Down = nominal * (1 - p_i/100)

where i is the particle bin containing the detector bin. Underflow/overflow
bins are left unchanged (no variation).

The binnings depend on the observable, selected with -x/--variable. Available
variables are defined in the VARIABLES dictionary below; add new cases there.

New histograms:  <nominal>_nonfiducial_modellingUp / ...Down
(e.g.  x_bb4l_bkg  ->  x_bb4l_bkg_nonfiducial_modellingUp / Down)
Everything else in the file is copied unchanged.

Examples
--------
  # 5% in every particle bin
  ./add_nonfiducial.py -i card.root -o card_nf.root -x default -v 5

  # one value per particle bin
  ./add_nonfiducial.py -i card.root -o card_nf.root -x default \\
        -v 10 10 5 5 5 3 3 5 10 20

  # only some bins (others 0%): index=percent
  ./add_nonfiducial.py -i card.root -o card_nf.root -x default --set 0=10 9=20

  # list variables and their binnings
  ./add_nonfiducial.py --list-variables

  # no arguments -> interactive prompts
  ./add_nonfiducial.py
"""

import argparse
import os
import sys

# ------------------------------------------------------------
# Binning per variable.
#   'particle' : bins in which the variation is given
#   'detector' : bins of the histograms in the file (must match exactly;
#                every detector bin must lie inside one particle bin)
# Add new variables by adding entries to this dictionary.
# ------------------------------------------------------------
VARIABLES = {
    'minimax_2j2b': {
        'particle': [0., 40., 60., 80., 100., 120., 180., 220., 270., 340., 500.],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [0., 40., 50., 60., 70., 80., 85., 90., 95., 100., 105., 110.,
                     120., 130., 140., 150., 160., 170., 180., 190., 200., 210.,
                     220., 230., 240., 255., 270., 310., 340., 500.],
    },

    'minimax_geq2j2b': {
        'particle': [0., 40., 60., 80., 100., 120., 180., 220., 270., 340.,490.,640., 790.],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [0., 40., 50., 60., 70., 80., 85., 90., 95., 100., 105., 110., 120., 130.,
                       140., 150., 160., 170., 180., 190., 200., 210., 220., 230., 240., 255.,
                       270., 310., 340.,415.,490.,565.,640.,715., 790.],
    },

    'minimax_geq2j2b_short': {
        'particle': [0., 40., 60., 80., 100., 120., 180., 220., 270., 340.,490.,790.],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [0., 40., 50., 60., 70., 80., 85., 90., 95., 100., 105., 110., 120., 130.,
                       140., 150., 160., 170., 180., 190., 200., 210., 220., 230., 240., 255.,
                       270., 310., 340.,415.,490.,640., 790.],
    },

    'Lep1_Pt': {
        'particle': [25., 35., 45., 55., 65., 75., 85., 95., 150.,200.,250.,300.],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [25., 35., 50., 55., 60., 65., 70., 75., 80., 85., 90., 95., 100., 105., 115., 125., 150.,175.,200.,225.,250.,275.,300.],
    },
    
    'Jet1_Pt': {
        'particle': [30., 50., 70., 85., 110., 150.,200.,250.,350.,500.],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [30., 40., 45., 50., 55., 60., 65., 70., 85., 110., 150.,175.,200.,225.,250.,300.,350.,425.,500.],
    },
    
    'Lep1Lep2_DPhi': {
        'particle': [0., .17, .33, .5, .67, .83, 1.0],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [0., 0.083, .17, 0.25, 0.33, 0.417, .5, 0.583, 0.67, 0.75, 0.83, 0.917, 1.0],
    },
    
    'BJet1BJet2_Pt': {
        'particle': [0., 30., 55., 80., 110., 145., 190., 260., 360.,700.],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [0., 30., 55., 60., 70., 85., 95., 100., 105., 115., 120., 130.,
                       140., 150., 160., 170., 180., 190., 200., 210., 220., 230., 240., 250.,
                       270., 320., 360., 500., 600., 700.],
    },
    
    'NJets': {
        'particle': [-0.5,0.5,1.5,2.5,3.5,4.5,5.5],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [-0.5,0.5,1.5,2.5,3.5,4.5,5.5],
    },
    
    'NBJets': {
        'particle': [-0.5,0.5,1.5,2.5,3.5],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [-0.5,0.5,1.5,2.5,3.5],
    },

    'NJetsNBJets': {
        'particle': [-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5],
    },
    
    'Lep1Lep2BJet1BJet2_Pt_ATLAS': {
        'particle': [0., 30., 55., 85., 115., 150., 200., 250., 320., 400., 500., 800.],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [0., 30., 55., 60., 70., 85., 95., 100., 105., 115., 120., 130.,
                       140., 150., 160., 170., 180., 190., 200., 210., 220., 230., 240., 250.,
                       270., 320., 340., 400., 450., 500., 600., 700., 800.],
    },
    
    'Lep1Lep2BJet1BJet2_M': {
        'particle': [0., 180., 200., 230., 270., 300., 390., 420., 500., 580., 730., 820., 1000., 1300., 2000.],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [0., 180., 200., 215., 230., 250., 270., 285., 300., 345., 390., 400.,
                       420., 450., 470., 500., 540., 580., 650., 730., 820., 890., 950., 1000.,
                       1100., 1200., 1300., 1400., 1500., 1750., 2000.],
    },
    
    'Lep1Lep2BJet1BJet2MET_Pt_atlasbin': {
        'particle': [0., 50., 105., 155., 210., 265., 325., 395., 470., 800.],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [0., 25.,50.,77.5, 105.,130., 155.,182.5, 210.,237.5, 265.,295., 325.,360., 395.,432.5, 470.,635., 800.],
    },                                    

    'Lep1Lep2BJet1BJet2MET_Mt_atlasbin': {
        'particle': [120., 225., 275., 325., 380., 450., 520., 600., 700., 820.,960.,1150.,1400.,2000.],
        # DO NOT CHANGE THESE BECAUSE THEY ARE ATLAS' ONES
        'detector': [120., 172.5, 225., 250., 275.,300., 325., 352.5, 380.,415.,
                       450., 485., 520., 560., 600., 650., 700., 760.,
                       820., 890., 960., 1055.,1150.,1275.,1400.,1700.,  2000.],
    },

}

TOL = 1e-6


# ============================================================
# Pure-python logic (no ROOT needed)
# ============================================================

def get_binning(variable):
    if variable not in VARIABLES:
        raise ValueError("unknown variable '%s'. Available: %s"
                         % (variable, ", ".join(VARIABLES)))
    v = VARIABLES[variable]
    return v['particle'], v['detector']


def detector_to_particle_map(det_edges, variable):
    """
    For each detector bin, return the index of the particle bin that contains
    it, using the binnings of `variable`. Raises ValueError if det_edges
    doesn't match the expected detector binning, or if a detector bin is not
    fully inside one particle bin.
    """
    part_edges, expected_det = get_binning(variable)

    if (len(det_edges) != len(expected_det) or
            any(abs(a - b) > TOL for a, b in zip(det_edges, expected_det))):
        raise ValueError(
            "histogram binning is not the expected detector binning for "
            "variable '%s'.\n  found   : %s\n  expected: %s"
            % (variable, list(det_edges), expected_det))

    mapping = []
    for lo, hi in zip(det_edges[:-1], det_edges[1:]):
        found = None
        for ip in range(len(part_edges) - 1):
            if lo >= part_edges[ip] - TOL and hi <= part_edges[ip + 1] + TOL:
                found = ip
                break
        if found is None:
            raise ValueError("detector bin [%g, %g] straddles particle bins "
                             "(variable '%s')" % (lo, hi, variable))
        mapping.append(found)
    return mapping


def build_variations(variation, set_items, n_part):
    """Return list of n_part fractional variations (percent / 100)."""
    pct = [0.0] * n_part
    if variation:
        if len(variation) == 1:
            pct = [variation[0]] * n_part
        elif len(variation) == n_part:
            pct = list(variation)
        else:
            raise ValueError("-v needs 1 value (all bins) or %d values "
                             "(one per particle bin), got %d"
                             % (n_part, len(variation)))
    for item in set_items or []:
        try:
            idx, val = item.split("=")
            idx, val = int(idx), float(val)
        except ValueError:
            raise ValueError("bad --set entry '%s', use index=percent" % item)
        if not 0 <= idx < n_part:
            raise ValueError("--set index %d out of range 0..%d"
                             % (idx, n_part - 1))
        pct[idx] = val
    for i, p in enumerate(pct):
        if p < 0 or p > 100:
            raise ValueError("variation for particle bin %d is %g%%; "
                             "must be between 0 and 100" % (i, p))
    return [p / 100.0 for p in pct]


def print_particle_bins(variable):
    part_edges, _ = get_binning(variable)
    print("Particle bins for '%s':" % variable)
    for i in range(len(part_edges) - 1):
        print("   %d: %g-%g" % (i, part_edges[i], part_edges[i + 1]))


# ============================================================
# Arguments / interactive input
# ============================================================

def parse_args():
    p = argparse.ArgumentParser(
        description="Add a symmetric nonfiducial_modelling template to bb4l_bkg.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("-i", "--input", help="input ROOT file")
    p.add_argument("-o", "--output", help="output ROOT file")
    p.add_argument("-x", "--variable",
                   help="variable name, selects the binning mapping "
                        "(available: %s)" % ", ".join(VARIABLES))
    p.add_argument("--list-variables", action="store_true",
                   help="print the available variables and their binnings, "
                        "then exit")
    p.add_argument("-v", "--variation", type=float, nargs="+",
                   help="percent variation: 1 value (all particle bins) or "
                        "one value per particle bin")
    p.add_argument("--set", nargs="+", metavar="IDX=PCT",
                   help="set individual particle bins, e.g. --set 0=10 9=20 "
                        "(unspecified bins are 0%% unless -v is given)")
    p.add_argument("--process", default="bb4l_bkg",
                   help="process whose templates get the variation "
                        "(default: bb4l_bkg)")
    p.add_argument("--name", default="nonfiducial_modelling",
                   help="uncertainty name (default: nonfiducial_modelling)")
    p.add_argument("--up-suffix", default="Up")
    p.add_argument("--down-suffix", default="Down")
    p.add_argument("--sep", default="_",
                   help="separator before the uncertainty name (default: '_')")

    args = p.parse_args()

    if args.list_variables:
        for name, v in VARIABLES.items():
            print("%s:" % name)
            print("   particle:", v['particle'])
            print("   detector:", v['detector'])
        sys.exit(0)

    if not args.input:
        args.input = input("Input ROOT file: ").strip()
    if not args.output:
        args.output = input("Output ROOT file: ").strip()
    if not args.variable:
        if len(VARIABLES) == 1:
            args.variable = next(iter(VARIABLES))
            print("Using the only available variable:", args.variable)
        else:
            args.variable = input("Variable [%s]: "
                                  % ", ".join(VARIABLES)).strip()
    if args.variable not in VARIABLES:
        p.error("unknown variable '%s'. Available: %s"
                % (args.variable, ", ".join(VARIABLES)))

    n_part = len(VARIABLES[args.variable]['particle']) - 1

    if not args.variation and not args.set:
        print_particle_bins(args.variable)
        raw = input("Percent variation [1 value for all bins, or %d values, "
                    "space separated]: " % n_part)
        try:
            args.variation = [float(x) for x in raw.replace(",", " ").split()]
        except ValueError:
            p.error("could not parse variation values")

    try:
        args.fractions = build_variations(args.variation, args.set, n_part)
    except ValueError as e:
        p.error(str(e))

    if os.path.abspath(args.input) == os.path.abspath(args.output):
        p.error("input and output must be different files")
    return args


# ============================================================
# ROOT part
# ============================================================

def is_target(name, process):
    return name == process or name.endswith("_" + process)


def make_variation(h_nom, mapping, fractions, sign):
    """Clone nominal and scale bin i by (1 + sign*frac[particle bin of i])."""
    h = h_nom.Clone()
    h.SetDirectory(0)
    for ib in range(1, h.GetNbinsX() + 1):
        f = 1.0 + sign * fractions[mapping[ib - 1]]
        h.SetBinContent(ib, h_nom.GetBinContent(ib) * f)
        h.SetBinError(ib, h_nom.GetBinError(ib) * f)
    return h


def process_directory(in_dir, out_dir, cfg, counts):
    # First pass: which histograms get new variations?
    keys = [k.GetName() for k in in_dir.GetListOfKeys()]
    new_names = set()
    for name in keys:
        if is_target(name, cfg["process"]):
            base = name + cfg["sep"] + cfg["name"]
            new_names.add(base + cfg["up"])
            new_names.add(base + cfg["down"])

    seen = set()
    for key in in_dir.GetListOfKeys():
        name = key.GetName()
        if name in seen:          # skip older cycles of the same object
            continue
        seen.add(name)
        obj = key.ReadObj()

        if obj.InheritsFrom("TDirectory"):
            process_directory(obj, out_dir.mkdir(name), cfg, counts)
            continue

        # Drop pre-existing copies of the templates we are about to create
        if name in new_names:
            print("WARNING: replacing existing histogram:", name)
            continue

        out_dir.cd()
        if obj.InheritsFrom("TH1"):
            h = obj.Clone(name)
            h.SetDirectory(0)
            h.Write()
        else:
            obj.Write()

        if is_target(name, cfg["process"]) and obj.InheritsFrom("TH1"):
            edges = [obj.GetXaxis().GetBinLowEdge(i)
                     for i in range(1, obj.GetNbinsX() + 2)]
            try:
                mapping = detector_to_particle_map(edges, cfg["variable"])
            except ValueError as e:
                print("ERROR in %s: %s" % (name, e))
                sys.exit(1)

            base = name + cfg["sep"] + cfg["name"]
            for suffix, sign in ((cfg["up"], +1), (cfg["down"], -1)):
                hv = make_variation(obj, mapping, cfg["fractions"], sign)
                hv.SetName(base + suffix)
                hv.SetTitle(base + suffix)
                out_dir.cd()
                hv.Write()
            print("Added: %s%s / %s%s" % (base, cfg["up"], base, cfg["down"]))
            counts[0] += 1


def main():
    args = parse_args()

    import ROOT
    ROOT.gROOT.SetBatch(True)

    if not os.path.isfile(args.input):
        print("ERROR: input file does not exist:", args.input)
        sys.exit(1)
    fin = ROOT.TFile.Open(args.input, "READ")
    if not fin or fin.IsZombie():
        print("ERROR: could not open input file:", args.input)
        sys.exit(1)
    fout = ROOT.TFile.Open(args.output, "RECREATE")
    if not fout or fout.IsZombie():
        print("ERROR: could not create output file:", args.output)
        sys.exit(1)

    cfg = {"process": args.process, "name": args.name, "sep": args.sep,
           "up": args.up_suffix, "down": args.down_suffix,
           "fractions": args.fractions, "variable": args.variable}
    counts = [0]

    part_edges, _ = get_binning(args.variable)
    print("Variable: %s" % args.variable)
    print("Variation (+/-) per particle bin:")
    for i, f in enumerate(args.fractions):
        print("   %d  %5g-%-5g  %g%%" % (i, part_edges[i],
                                          part_edges[i + 1], 100 * f))
    print()

    process_directory(fin, fout, cfg, counts)
    fout.Close()
    fin.Close()

    print()
    print("Done.  Input: %s   Output: %s" % (args.input, args.output))
    if counts[0] == 0:
        print("WARNING: no histogram for process '%s' found; nothing added."
              % args.process)
    else:
        print("Nominal templates varied: %d" % counts[0])
        print("Remember to add to the datacard:  %s shape  ... (1 for %s)"
              % (args.name, args.process))


if __name__ == "__main__":
    main()
