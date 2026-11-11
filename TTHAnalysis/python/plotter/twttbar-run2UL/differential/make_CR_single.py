#!/usr/bin/env python3
"""
Build a single "colour_rec_single" systematic from colour_rec_cr1 / cr2 / erdon.

For every process (bb4l_partbin0 ... bb4l_partbin9, bb4l_bkg) and every bin:
  - delta_k = Up_k - nominal for k in {cr1, cr2, erdon}
  - pick the delta with the largest |delta| (sign is kept)
  - colour_rec_singleUp   = nominal + delta_max
  - colour_rec_singleDown = nominal - delta_max   (symmetric about nominal)

The existing *Down histograms of the three inputs are identical to the
nominal (one-sided systematics), so only the Up histograms are used.

Statistical errors (sumw2) of each bin are taken from the input variation
that was selected in that bin; the Down template gets the same errors.

Optional --lowess: the colour_rec_singleUp/Down templates are LOWESS-smoothed
(see lowess_template()) and written under the same names; the unsmoothed ones are not kept.

Usage:
  python make_colour_rec_single.py in.root --lowess
  python make_colour_rec_single.py in.root                 # -> in_colour_rec_single.root (new hists only)
  python make_colour_rec_single.py in.root -o out.root --copy-all   # full copy of input + new hists
Requires: uproot, numpy, boost_histogram, statsmodels (only for --lowess)
"""
import argparse
import re
import shutil
import numpy as np
import uproot
import boost_histogram as bh

PREFIX = "x_"                       # histogram name prefix in the datacard file
SYSTS = ["colour_rec_cr1", "colour_rec_cr2", "colour_rec_erdon"]
NEW = "colour_rec_single"
FLOOR = 1e-5                        # the file uses 1e-5 as an empty-bin floor
PROC_RE = re.compile(r"^bb4l_(partbin\d+|bkg|bckg)$")


def get(f, name):
    """Return (values, variances, edges) including under/overflow bins."""
    h = f[name]
    vals = h.values(flow=True)
    var = h.variances(flow=True)
    if var is None:                 # no sumw2 stored
        var = vals.copy()
    return vals, var, h.axis().edges()


def to_hist(edges, vals, var):
    h = bh.Histogram(bh.axis.Variable(edges), storage=bh.storage.Weight())
    arr = h.view(flow=True)
    arr.value = vals
    arr.variance = var
    return h


def get_smoothed_scale_factor(diff_smooth, nominal, var_vals, var_nom, var_var):
    """
    Best-fit scale s (chi2 minimisation) such that nominal*(1 + s*diff_smooth) matches
    the original template `var_vals`:
        chi2(s) = sum_i (nom_i*(1+s*d_i) - y_i)^2 / (var_nom_i + var_y_i)
        ->  s = sum_i w_i * nom_i*d_i*(y_i-nom_i) / sum_i w_i * (nom_i*d_i)^2 ,  w=1/(var_nom+var_y)
    var_nom / var_var can be scalars (e.g. np.var(...), then w is constant and cancels)
    or per-bin arrays (--bin-errors).
    """
    tot = np.asarray(var_nom, float) + np.asarray(var_var, float)
    with np.errstate(divide="ignore"):
        w = np.where(tot > 0, 1.0 / np.where(tot > 0, tot, 1.0), 0.0)   # bins without error info are ignored
    w = np.broadcast_to(w, nominal.shape)
    a = nominal * diff_smooth
    den = np.sum(w * a * a)
    if den <= 0:
        return 1.0
    return float(np.sum(w * a * (var_vals - nominal)) / den)


def lowess_template(nom, up, down, centers, frac=2.0 / 3.0, nom_min=1e-4,
                    var_nom=None, var_up=None, var_down=None):
    """LOWESS smoothing of the template, following the scheme requested.
    All inputs are 1D arrays over the real bins (no under/overflow)."""
    import statsmodels.api as sm

    # bins with (almost) empty nominal: ratio is meaningless -> use 1 as denominator
    nom_ratio = nom.copy()
    nom_ratio[nom_ratio <= nom_min] = 1.0
    ratio_diff = (up / nom_ratio - down / nom_ratio) / 2.0
    diff_smooth = sm.nonparametric.lowess(ratio_diff, centers, frac=frac, return_sorted=False)

    if var_nom is None:                       # scheme default: global variances
        var_nom, var_up, var_down = np.var(nom), np.var(up), np.var(down)
    up_scale = get_smoothed_scale_factor(diff_smooth, nom, up, var_nom, var_up)
    down_scale = get_smoothed_scale_factor(diff_smooth, nom, down, var_nom, var_down)

    new_up = nom * np.nan_to_num(1 + up_scale * diff_smooth, nan=1.0)
    new_down = nom * np.nan_to_num(1 + down_scale * diff_smooth, nan=1.0)
    return new_up, new_down, up_scale, down_scale


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--output")
    ap.add_argument("--copy-all", action="store_true",
                    help="write a copy of the input file with the new histograms added")
    ap.add_argument("--no-floor", action="store_true",
                    help="do not clip negative bin contents to the 1e-5 floor")
    ap.add_argument("--lowess", action="store_true",
                    help=f"LOWESS-smooth the templates; only the smoothed {NEW}{{Up,Down}} are written")
    ap.add_argument("--frac", type=float, default=2.0 / 3.0,
                    help="LOWESS fraction of points used per local fit (default 2/3 = statsmodels default)")
    ap.add_argument("--bin-errors", action="store_true",
                    help="use per-bin sumw2 instead of np.var() of the contents in the chi2 scale factor")
    a = ap.parse_args()

    out = a.output or a.input.replace(".root", "") + ("_with_colour_rec_single.root"
                                                      if a.copy_all else "_colour_rec_single.root")

    fin = uproot.open(a.input)
    names = {k.split(";")[0] for k in fin.keys()}
    procs = sorted(
        {n[len(PREFIX):] for n in names
         if n.startswith(PREFIX) and PROC_RE.match(n[len(PREFIX):])},
        key=lambda s: (s == "bb4l_bkg", s))

    new_hists = {}
    print(f"{'process':<16}{'bins varied':>12}{'  picked cr1/cr2/erdon':>24}{'  Down<0 clipped':>17}")
    for p in procs:
        nom, nvar, edges = get(fin, f"{PREFIX}{p}")
        deltas, variances = [], []
        for s in SYSTS:
            v, var, _ = get(fin, f"{PREFIX}{p}_{s}Up")
            deltas.append(v - nom)
            variances.append(var)
        deltas = np.array(deltas)           # (3, nbins+2)
        variances = np.array(variances)
        idx = np.argmax(np.abs(deltas), axis=0)
        cols = np.arange(deltas.shape[1])
        dmax = deltas[idx, cols]
        svar = variances[idx, cols]

        up = nom + dmax
        down = nom - dmax
        nclip = int(np.sum(down < 0) + np.sum(up < 0))
        if not a.no_floor:
            up = np.where(up < 0, FLOOR, up)
            down = np.where(down < 0, FLOOR, down)

        new_hists[f"{PREFIX}{p}_{NEW}Up"] = to_hist(edges, up, svar)
        new_hists[f"{PREFIX}{p}_{NEW}Down"] = to_hist(edges, down, svar)

        if a.lowess:
            sl = slice(1, -1)                     # real bins only
            centers = 0.5 * (edges[:-1] + edges[1:])
            up_raw, down_raw = nom + dmax, nom - dmax   # unclipped, exactly symmetric
            vn = vu = vd = None
            if a.bin_errors:
                vn, vu, vd = nvar[sl], svar[sl], svar[sl]
            lu, ld, su, sd = lowess_template(nom[sl], up_raw[sl], down_raw[sl], centers,
                                             frac=a.frac, var_nom=vn, var_up=vu, var_down=vd)
            lup, ldown = up.copy(), down.copy()   # flow bins: keep unsmoothed values
            lup[sl], ldown[sl] = lu, ld
            if not a.no_floor:
                lup = np.where(lup < 0, FLOOR, lup)
                ldown = np.where(ldown < 0, FLOOR, ldown)
            # with --lowess the smoothed templates REPLACE the unsmoothed ones (same names)
            new_hists[f"{PREFIX}{p}_{NEW}Up"] = to_hist(edges, lup, svar)
            new_hists[f"{PREFIX}{p}_{NEW}Down"] = to_hist(edges, ldown, svar)
            lowess_msg = f"{'':<16}  lowess scale factors: up={su:.3f} down={sd:.3f}"

        varied = dmax != 0
        picks = [int(np.sum((idx == k) & varied)) for k in range(3)]
        print(f"{p:<16}{int(varied.sum()):>12}{str(picks):>24}{nclip:>17}")
        if a.lowess:
            print(lowess_msg)

    if a.copy_all:
        shutil.copy(a.input, out)
        with uproot.update(out) as fo:
            for k, h in new_hists.items():
                fo[k] = h
    else:
        with uproot.recreate(out) as fo:
            for k, h in new_hists.items():
                fo[k] = h
    print(f"\nWrote {len(new_hists)} histograms to {out}")


if __name__ == "__main__":
    main()