#!/usr/bin/env python3
"""
LOWESS-smooth any systematic template(s) stored as <prefix><process>_<syst>Up / Down.

Scheme (per process and systematic, over the real bins, x = bin centres):
  ratio_diff   = (up/nom - down/nom) / 2          (nom := 1 where nom <= --nom-min)
  diff_smooth  = lowess(ratio_diff, x)
  up_scale     = chi2 fit of nom*(1+s*diff_smooth) to the original up    (same for down)
  new_up       = nom*(1 + up_scale  *diff_smooth)
  new_down     = nom*(1 + down_scale*diff_smooth)

One-sided systematics (Down missing, or identical to nominal) are mirrored:
Down := 2*nom - Up, as in the usual "onlyone" treatment (override with --onesided / --twosided).

Examples:
  # smooth one systematic, all processes that have it -> new file with only the smoothed hists
  python lowess_smooth_templates.py in.root -s colour_rec_single

  # several systematics, only some processes, keep the original names in a full copy of the file
  python lowess_smooth_templates.py in.root -s colour_rec_cr1 colour_rec_cr2 -p 'bb4l_partbin[0-3]' --copy-all -o out.root

  # keep the unsmoothed ones too: write smoothed ones as <syst>_lowess
  python lowess_smooth_templates.py in.root -s colour_rec_cr1 --suffix _lowess --copy-all

Output names: <prefix><process>_<syst><suffix>Up/Down (suffix is empty by default, i.e. same names).
Requires: uproot, numpy, boost_histogram, statsmodels
"""
import argparse
import re
import numpy as np
import uproot
import boost_histogram as bh
import statsmodels.api as sm

FLOOR = 1e-5


def read(f, name):
    h = f[name]
    vals = h.values(flow=True)
    var = h.variances(flow=True)
    if var is None:
        var = vals.copy()
    return vals, var, h.axis().edges()


def to_hist(edges, vals, var):
    h = bh.Histogram(bh.axis.Variable(edges), storage=bh.storage.Weight())
    v = h.view(flow=True)
    v.value = vals
    v.variance = var
    return h


def get_smoothed_scale_factor(diff_smooth, nominal, var_vals, var_nom, var_var):
    """chi2 fit of s in  nominal*(1+s*diff_smooth) ~ var_vals ; var_* scalars or per-bin arrays."""
    tot = np.asarray(var_nom, float) + np.asarray(var_var, float)
    with np.errstate(divide="ignore"):
        w = np.where(tot > 0, 1.0 / np.where(tot > 0, tot, 1.0), 0.0)
    w = np.broadcast_to(w, nominal.shape)
    a = nominal * diff_smooth
    den = np.sum(w * a * a)
    if den <= 0:
        return 1.0
    return float(np.sum(w * a * (var_vals - nominal)) / den)


def lowess_template(nom, up, down, centers, frac, nom_min, var_nom=None, var_up=None, var_down=None):
    nom_ratio = nom.copy()
    nom_ratio[nom_ratio <= nom_min] = 1.0
    ratio_diff = (up / nom_ratio - down / nom_ratio) / 2.0
    diff_smooth = sm.nonparametric.lowess(ratio_diff, centers, frac=frac, return_sorted=False)
    if var_nom is None:
        var_nom, var_up, var_down = np.var(nom), np.var(up), np.var(down)
    up_scale = get_smoothed_scale_factor(diff_smooth, nom, up, var_nom, var_up)
    down_scale = get_smoothed_scale_factor(diff_smooth, nom, down, var_nom, var_down)
    new_up = nom * np.nan_to_num(1 + up_scale * diff_smooth, nan=1.0)
    new_down = nom * np.nan_to_num(1 + down_scale * diff_smooth, nan=1.0)
    return new_up, new_down, up_scale, down_scale


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("-s", "--syst", nargs="+", required=True,
                    help="systematic name(s) without Up/Down, e.g. colour_rec_single")
    ap.add_argument("-p", "--process", default=None,
                    help="regex (full match) selecting processes; default: all that have the systematic")
    ap.add_argument("-o", "--output", default=None)
    ap.add_argument("--prefix", default="x_", help="histogram name prefix (default 'x_')")
    ap.add_argument("--suffix", default="", help="appended to the systematic name of the smoothed hists")
    ap.add_argument("--frac", type=float, default=2.0 / 3.0, help="LOWESS frac (default 2/3)")
    ap.add_argument("--nom-min", type=float, default=1e-4,
                    help="bins with nominal <= this use 1 as ratio denominator (default 1e-4)")
    ap.add_argument("--bin-errors", action="store_true",
                    help="use per-bin sumw2 (not np.var of contents) in the chi2 scale factor")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--onesided", action="store_true", help="force mirroring Down := 2*nom - Up")
    g.add_argument("--twosided", action="store_true", help="never mirror; Down must exist")
    ap.add_argument("--no-floor", action="store_true", help="do not clip negative contents to 1e-5")
    ap.add_argument("--copy-all", action="store_true",
                    help="output = full copy of the input file, with the smoothed hists added "
                         "(replacing same-named ones when --suffix is empty)")
    a = ap.parse_args()

    out = a.output or a.input.replace(".root", "") + "_lowess.root"
    fin = uproot.open(a.input)
    names = {k.split(";")[0] for k in fin.keys()}
    preg = re.compile(a.process) if a.process else None

    new = {}
    print(f"{'systematic':<22}{'process':<18}{'mode':<10}{'up_scale':>10}{'down_scale':>12}")
    for syst in a.syst:
        tail = f"_{syst}Up"
        procs = sorted(n[len(a.prefix):-len(tail)] for n in names
                       if n.startswith(a.prefix) and n.endswith(tail))
        procs = [p for p in procs if (preg is None or preg.fullmatch(p)) and f"{a.prefix}{p}" in names]
        if not procs:
            print(f"!! no histograms found for systematic '{syst}' (prefix '{a.prefix}')")
            continue
        for p in procs:
            nom, nvar, edges = read(fin, f"{a.prefix}{p}")
            up, uvar, _ = read(fin, f"{a.prefix}{p}_{syst}Up")
            dname = f"{a.prefix}{p}_{syst}Down"
            have_down = dname in names
            if have_down:
                down, dvar, _ = read(fin, dname)
            if a.twosided and not have_down:
                raise SystemExit(f"{dname} missing but --twosided given")
            mirror = a.onesided or (not a.twosided and (not have_down or np.allclose(down, nom, rtol=1e-6, atol=a.nom_min)))
            if mirror:
                down, dvar = 2 * nom - up, uvar
            sl = slice(1, -1)                                  # real bins only
            centers = 0.5 * (edges[:-1] + edges[1:])
            kw = dict(var_nom=nvar[sl], var_up=uvar[sl], var_down=dvar[sl]) if a.bin_errors else {}
            lu, ld, su, sd = lowess_template(nom[sl], up[sl], down[sl], centers, a.frac, a.nom_min, **kw)
            nu, nd = up.copy(), down.copy()                    # flow bins unchanged
            nu[sl], nd[sl] = lu, ld
            if not a.no_floor:
                nu = np.where(nu < 0, FLOOR, nu)
                nd = np.where(nd < 0, FLOOR, nd)
            new[f"{a.prefix}{p}_{syst}{a.suffix}Up"] = to_hist(edges, nu, uvar)
            new[f"{a.prefix}{p}_{syst}{a.suffix}Down"] = to_hist(edges, nd, dvar)
            print(f"{syst:<22}{p:<18}{'mirrored' if mirror else 'two-sided':<10}{su:>10.3f}{sd:>12.3f}")

    if not new:
        raise SystemExit("nothing to write")

    if a.copy_all:
        with uproot.recreate(out) as fo:
            for k in fin.keys():
                base = k.split(";")[0]
                if base in new or fin.classname_of(k).startswith("TTree"):
                    continue
                fo[base] = fin[k]
            for k, h in new.items():
                fo[k] = h
    else:
        with uproot.recreate(out) as fo:
            for k, h in new.items():
                fo[k] = h
    print(f"\nWrote {len(new)} smoothed histograms to {out}" + (" (+ copy of input)" if a.copy_all else ""))


if __name__ == "__main__":
    main()
