#!/usr/bin/env python3
"""
Symmetrise systematic variations in a ROOT datacard / shapes file.

For each requested uncertainty <syst>, histograms named
    <...>_<syst>Down   and   <...>_<syst>Up
are paired with the nominal histogram <...>, and one variation is rebuilt as

    rebuilt = 2 * nominal - kept

By default the Up variation is kept and Down is rebuilt (--keep up).
Use --keep down to keep Down and rebuild Up instead.

Examples
--------
  ./symmetrise.py -i card.root -o card_sym.root -u bb4l_topmass
  ./symmetrise.py -i card.root -o card_sym.root -u bb4l_topmass ttbar_scale --keep down
  ./symmetrise.py        # no arguments -> interactive prompts
"""

import argparse
import os
import sys

import ROOT

ROOT.gROOT.SetBatch(True)


# ============================================================
# Arguments / interactive input
# ============================================================

def parse_args():
    p = argparse.ArgumentParser(
        description="Symmetrise Up/Down systematic histograms in a ROOT file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("-i", "--input", help="input ROOT file")
    p.add_argument("-o", "--output", help="output ROOT file")
    p.add_argument(
        "-u", "--uncertainties", nargs="+",
        help="uncertainty names to symmetrise (e.g. bb4l_topmass), "
             "without the Up/Down suffix",
    )
    p.add_argument("--keep", choices=["up", "down"], default="up",
                   help="variation to keep; the other is rebuilt (default: up)")
    p.add_argument("--up-suffix", default="Up", help="suffix of Up histograms")
    p.add_argument("--down-suffix", default="Down", help="suffix of Down histograms")
    p.add_argument("--sep", default="_",
                   help="separator between nominal name and uncertainty name "
                        "(default: '_')")
    p.add_argument("--clip-negative", action="store_true",
                   help="set negative rebuilt bin contents to 0")

    args = p.parse_args()

    # Interactive fallback for anything not given on the command line
    if not args.input:
        args.input = input("Input ROOT file: ").strip()
    if not args.output:
        args.output = input("Output ROOT file: ").strip()
    if not args.uncertainties:
        raw = input("Uncertainties to symmetrise (space/comma separated): ")
        args.uncertainties = [u for u in raw.replace(",", " ").split() if u]

    if not args.uncertainties:
        p.error("no uncertainties specified")
    if os.path.abspath(args.input) == os.path.abspath(args.output):
        p.error("input and output must be different files")

    return args


# ============================================================
# Core logic
# ============================================================

def find_match(name, systs, kept_suffix, rebuilt_suffix, sep):
    """
    If `name` is a histogram of the variation to rebuild for one of the
    requested uncertainties, return (syst, kept_name, nominal_name).
    Otherwise return None.
    """
    for syst in systs:
        tag = sep + syst + rebuilt_suffix
        if name.endswith(tag):
            nominal = name[: -len(tag)]
            kept = nominal + sep + syst + kept_suffix
            return syst, kept, nominal
    return None


def process_directory(in_dir, out_dir, cfg, counts):
    for key in in_dir.GetListOfKeys():
        obj = key.ReadObj()
        name = obj.GetName()

        # Subdirectory: recurse
        if obj.InheritsFrom("TDirectory"):
            new_dir = out_dir.mkdir(name)
            process_directory(obj, new_dir, cfg, counts)
            continue

        # Non-histogram objects: copy unchanged
        if not obj.InheritsFrom("TH1"):
            out_dir.cd()
            obj.Write()
            continue

        hist = obj.Clone(name)
        hist.SetDirectory(0)

        match = find_match(name, cfg["systs"], cfg["kept_suffix"],
                           cfg["rebuilt_suffix"], cfg["sep"])

        if match:
            syst, kept_name, nominal_name = match
            h_kept = in_dir.Get(kept_name)
            h_nom = in_dir.Get(nominal_name)

            if not h_kept:
                print("WARNING: kept histogram not found, copying unchanged:")
                print("   ", kept_name)
            elif not h_nom:
                print("WARNING: nominal histogram not found, copying unchanged:")
                print("   ", nominal_name)
            else:
                print("Symmetrising [%s]:" % syst)
                print("   Rebuilding:", name)
                print("   Nominal   :", nominal_name)
                print("   Kept      :", kept_name)

                # rebuilt = 2 * nominal - kept  (including under/overflow)
                for ibin in range(0, hist.GetNbinsX() + 2):
                    val = 2.0 * h_nom.GetBinContent(ibin) - h_kept.GetBinContent(ibin)
                    if cfg["clip_negative"] and val < 0:
                        val = 0.0
                    hist.SetBinContent(ibin, val)
                # Original statistical uncertainties of the rebuilt histogram
                # are kept as they were.
                counts[syst] = counts.get(syst, 0) + 1

        out_dir.cd()
        hist.Write()


# ============================================================
# Main
# ============================================================

def main():
    args = parse_args()

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

    if args.keep == "up":
        kept_suffix, rebuilt_suffix = args.up_suffix, args.down_suffix
    else:
        kept_suffix, rebuilt_suffix = args.down_suffix, args.up_suffix

    cfg = {
        "systs": args.uncertainties,
        "kept_suffix": kept_suffix,
        "rebuilt_suffix": rebuilt_suffix,
        "sep": args.sep,
        "clip_negative": args.clip_negative,
    }
    counts = {}

    process_directory(fin, fout, cfg, counts)

    fout.Close()
    fin.Close()

    print()
    print("Done.")
    print("Input :", args.input)
    print("Output:", args.output)
    print("Histograms symmetrised per uncertainty:")
    for syst in args.uncertainties:
        n = counts.get(syst, 0)
        flag = "" if n else "   <-- none found, check the name"
        print("   %-30s %d%s" % (syst, n, flag))


if __name__ == "__main__":
    main()