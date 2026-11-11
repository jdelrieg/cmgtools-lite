#!/usr/bin/env python3
"""Plot post-fit results from a Combine FitDiagnostics output.

This script is intentionally focused on the plotting step. It assumes that
step 1 (text2workspace.py) and step 2 (combine -M FitDiagnostics) have already
been run, and that the relevant ROOT files are available.

Typical usage:

  python plotFromFitDiagnostics.py \
      --fitdiagnostics fitDiagnosticsrun2_Jet1_Pt.root \
      --higgscombine higgsCombineRun2_Jet1_Pt.FitDiagnostics.mH125.root \
      --particle-root particle.root \
      --year run2 \
      --variable Jet1_Pt \
      --outdir ./temp/differential
"""

import argparse
import glob
import os
import sys
from array import array
from copy import deepcopy

import ROOT as r

# Allow running from the repository directory or from elsewhere.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

import varList as vl
import beautifulUnfoldingPlots as bp
import tdrstyle
import CMS_lumi


def ensure_dir(path):
    if path and not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def find_file(patterns, default_hint=None):
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    if default_hint:
        raise FileNotFoundError("Could not find a matching file. Tried: {0}".format(default_hint))
    raise FileNotFoundError("Could not find a matching file for patterns: {0}".format(patterns))


def draw_covariance_matrix(mat, outdir, year, var):
    tdrstyle.setTDRStyle()
    mat.SetStats(False)
    mat.SetXTitle(vl.varList[var]['xaxis'])
    mat.SetYTitle(vl.varList[var]['xaxis'])
    mat.SetMarkerColor(r.kRed)

    if 'txtsize_covpostfit' in vl.varList[var]:
        mat.SetMarkerSize(vl.varList[var]['txtsize_covpostfit'])

    r.gStyle.SetPaintTextFormat('4.5f')
    r.gStyle.SetPadRightMargin(0.17)
    r.gStyle.SetPadTopMargin(0.05)
    r.gStyle.SetPadBottomMargin(0.1)
    r.gStyle.SetPadLeftMargin(0.12)
    mat.GetYaxis().SetTitleOffset(1.5)
    mat.GetXaxis().SetTitleOffset(1.1)
    mat.GetXaxis().SetTitleFont(43)
    mat.GetXaxis().SetTitleSize(22)
    mat.GetXaxis().SetLabelFont(43)
    mat.GetXaxis().SetLabelSize(22)
    mat.GetYaxis().SetTitleFont(43)
    mat.GetYaxis().SetTitleSize(22)
    mat.GetYaxis().SetLabelFont(43)
    mat.GetYaxis().SetLabelSize(22)
    r.gStyle.SetLabelFont(43, 'XYZ')
    r.gStyle.SetLabelSize(22, 'XYZ')

    c = r.TCanvas('c', '', 600, 600)
    txtanglestring = vl.varList[var].get('txtangle_covpostfit', '')
    mat.Draw('colz text{0}'.format(txtanglestring))
    r.gPad.Update()

    CMS_lumi.lumi_13TeV = ''
    CMS_lumi.extraText = 'Preliminary'
    CMS_lumi.lumi_sqrtS = ''
    CMS_lumi.CMS_lumi(r.gPad, 0, 0, 0.05)

    plot_dir = os.path.join(outdir, year, var, 'sigextr_fit_combine', 'CovMatplots')
    ensure_dir(plot_dir)

    c.SaveAs(os.path.join(plot_dir, 'Cov_{0}_postfit.png'.format(var)))
    c.SaveAs(os.path.join(plot_dir, 'Cov_{0}_postfit.pdf'.format(var)))
    c.SaveAs(os.path.join(plot_dir, 'Cov_{0}_postfit.root'.format(var)))
    c.Close()


def draw_correlation_matrix(mat, outdir, year, var):
    tdrstyle.setTDRStyle()
    c = r.TCanvas('c', '{0} correlation matrix'.format(var), 1200, 1200)
    c.SetTopMargin(0.06)
    c.SetRightMargin(0.06)
    mat.GetXaxis().SetTitle('Free parameters of the fit')
    mat.GetXaxis().SetLabelSize(0.0275)
    mat.GetXaxis().SetTitleSize(0.01)
    mat.GetXaxis().SetTitleOffset(3)
    mat.GetYaxis().SetTitle('Free parameters of the fit')
    mat.GetYaxis().SetLabelSize(0.0275)
    mat.GetYaxis().SetTitleSize(0.01)
    mat.GetYaxis().SetTitleOffset(3)
    mat.SetTitle('{0} correlation matrix'.format(var))
    mat.SetStats(False)
    mat.Draw('colz')

    plot_dir = os.path.join(outdir, year, var, 'sigextr_fit_combine', 'CorrMatplots')
    ensure_dir(plot_dir)

    c.SaveAs(os.path.join(plot_dir, 'Corr_{0}.pdf'.format(var)))
    c.SaveAs(os.path.join(plot_dir, 'Corr_{0}.png'.format(var)))
    c.SaveAs(os.path.join(plot_dir, 'Corr_{0}.root'.format(var)))
    c.Close()


def draw_particle_result(hist, unc_info, particle_file, outdir, year, var):
    tdrstyle.setTDRStyle()

    thelumi = vl.TotalLumi if year == 'run2' else vl.LumiDict[year]
    scaleval = 1 / thelumi / 1000 if vl.doxsec else 1.0

    nominal_withErrors = [deepcopy(hist.Clone(var + 'uncUp')), deepcopy(hist.Clone(var + 'uncDown'))]
    statOnlyList = [deepcopy(nominal_withErrors[0].Clone('statUp')), deepcopy(nominal_withErrors[1].Clone('statDown'))]
    for iB in range(1, hist.GetNbinsX() + 1):
        nominal_withErrors[0].SetBinError(iB, unc_info.GetBinError(iB))
        nominal_withErrors[1].SetBinError(iB, unc_info.GetBinContent(iB))
        statOnlyList[0].SetBinError(iB, unc_info.GetBinError(iB))
        statOnlyList[1].SetBinError(iB, unc_info.GetBinContent(iB))

    for h in nominal_withErrors:
        h.SetFillColorAlpha(r.kOrange, 1.0)
        h.SetLineColor(0)
        h.SetFillStyle(1001)
    for h in statOnlyList:
        h.SetFillColorAlpha(r.kGray + 1, 1.0)
        h.SetLineColor(0)
        h.SetFillStyle(1001)

    tru = vl.giveMeOneComparison(particle_file, 'bb4l', scaleval, var, part = True)
    twttbardr = vl.giveMeOneComparison(particle_file, 'twttbardr', scaleval, var, part = True)
    twttbards = vl.giveMeOneComparison(particle_file, 'twttbards', scaleval, var, part = True)

    plot_dirs = [
        os.path.join(outdir, year, 'particleplots'),
        os.path.join(outdir, year, var, 'sigextr_fit_combine', 'particleplots'),
    ]
    for plot_dir in plot_dirs:
        ensure_dir(plot_dir)

    for plot_dir in plot_dirs:
        plot = bp.beautifulUnfPlot(var, var)
        plot.doRatio = True
        plot.doFit = True
        plot.doPreliminary = vl.doPre
        plot.doSupplementary = False
        plot.plotspath = plot_dir
        plot.displayedLumi = thelumi
        if 'yaxisuplimitunf' in vl.varList[var]:
            plot.yaxisuplimit = vl.varList[var]['yaxisuplimitunf']

        plot.addHisto(nominal_withErrors, 'A2', 'Total unc.', 'F', 'total')
        plot.addHisto(statOnlyList, '2,same', 'Stat unc.', 'F', 'stat')
        plot.addHisto(tru, 'P,same', 'b#bar{b}l^{+}#nu l^{-}#nu PH + P8', 'P', 'mc')
        plot.addHisto(twttbardr, 'P,same', 'tW DR + t#bar{t} PH + P8', 'P', 'mc')
        plot.addHisto(twttbards, 'P,same', 'tW DS + t#bar{t} PH + P8', 'P', 'mc')
        plot.addHisto(hist, 'P,same{0}'.format(',X0' if 'equalbinsunf' in vl.varList[var] else ''),
                      'Asimov dataset' if vl.asimov else vl.labellegend,
                      'P,same', 'data', redrawaxis = True)

        legloc = vl.varList[var].get('legpos_particle', 'TR')
        plot.saveCanvasv2(legloc)
        del plot


def main():
    parser = argparse.ArgumentParser(description='Make plots from Combine FitDiagnostics outputs.')
    parser.add_argument('--fitdiagnostics', help='Path to the fitDiagnostics ROOT file')
    parser.add_argument('--higgscombine', help='Path to the higgsCombine*.FitDiagnostics*.root file')
    parser.add_argument('--particle-root', help='Path to the particle.root file')
    parser.add_argument('--year', required=True, help='Year label, e.g. run2, 2018, ...')
    parser.add_argument('--variable', required=True, help='Variable name, e.g. Jet1_Pt')
    parser.add_argument('--outdir', default='./temp/differential', help='Base output directory')
    parser.add_argument('--verbose', action='store_true', help='Print extra information')
    args = parser.parse_args()

    r.gROOT.SetBatch(True)

    if not args.fitdiagnostics:
        args.fitdiagnostics = find_file([
            os.path.join(os.getcwd(), 'fitDiagnostics*.root'),
            os.path.join(args.outdir, args.year, args.variable, 'sigextr_fit_combine', 'fitdiagnostics', 'fitDiagnostics*.root'),
            os.path.join(args.outdir, args.year, args.variable, 'sigextr_fit_combine', 'fitDiagnostics*.root'),
        ], 'fitDiagnostics*.root')

    if not args.higgscombine:
        args.higgscombine = find_file([
            os.path.join(os.getcwd(), 'higgsCombine*.root'),
            os.path.join(args.outdir, args.year, args.variable, 'sigextr_fit_combine', 'higgsCombine*.root'),
        ], 'higgsCombine*.root')

    if not args.particle_root:
        args.particle_root = find_file([
            os.path.join(args.outdir, args.year, args.variable, 'particle.root'),
            os.path.join(os.getcwd(), 'particle.root'),
        ], 'particle.root')

    if args.verbose:
        print('Using fitDiagnostics file: {0}'.format(args.fitdiagnostics))
        print('Using higgsCombine file: {0}'.format(args.higgscombine))
        print('Using particle file: {0}'.format(args.particle_root))

    fit_file = r.TFile.Open(args.fitdiagnostics, 'READ')
    if not fit_file or fit_file.IsZombie():
        raise RuntimeError('Could not open fitDiagnostics file: {0}'.format(args.fitdiagnostics))

    hc_file = r.TFile.Open(args.higgscombine, 'READ')
    if not hc_file or hc_file.IsZombie():
        raise RuntimeError('Could not open higgsCombine file: {0}'.format(args.higgscombine))

    particle_file = r.TFile.Open(args.particle_root, 'READ')
    if not particle_file or particle_file.IsZombie():
        raise RuntimeError('Could not open particle file: {0}'.format(args.particle_root))

    fit_result = fit_file.Get('fit_s')
    if not fit_result:
        raise RuntimeError('Could not find fit_s in {0}'.format(args.fitdiagnostics))

    corrmat = deepcopy(fit_result.correlationHist('corrmat'))
    if args.verbose:
        print('Read correlation matrix with shape {0}x{1}'.format(corrmat.GetNbinsX(), corrmat.GetNbinsY()))

    workspace = hc_file.Get('w')
    if not workspace:
        raise RuntimeError('Could not find workspace in {0}'.format(args.higgscombine))

    bins_particle = vl.varList[args.variable]['bins_particle']
    nparticlebins = len(bins_particle) - 1

    poi_list = r.RooArgList('poiList')
    for i in range(nparticlebins):
        poi = workspace.var('r_bb4l_{0}'.format(i))
        if poi is None:
            raise RuntimeError('Could not find POI r_bb4l_{0} in workspace'.format(i))
        poi_list.add(poi)

    cov = fit_result.reducedCovarianceMatrix(poi_list)

    results = {}
    for par in fit_result.floatParsFinal():
        results[par.GetName()] = [par.getVal(), par.getErrorLo(), par.getErrorHi(), par.getError()]

    signal_hist = particle_file.Get('x_bb4l')
    if not signal_hist:
        raise RuntimeError('Could not find x_bb4l in particle file: {0}'.format(args.particle_root))

    thelumi = vl.TotalLumi if args.year == 'run2' else vl.LumiDict[args.year]
    scaleval = 1 / thelumi / 1000 if vl.doxsec else 1.0

    out_hist = r.TH1D('hFitResult_{0}'.format(args.variable), '', nparticlebins, array('d', bins_particle))
    unc_info = deepcopy(out_hist.Clone('hFitResult_forPlotting_{0}'.format(args.variable)))

    for i in range(1, nparticlebins + 1):
        idx = i - 1
        parname = 'r_bb4l_{0}'.format(idx)
        if parname not in results:
            raise RuntimeError('Missing fit parameter {0}'.format(parname))

        scale = signal_hist.GetBinContent(i) * scaleval
        results[parname][0] *= scale
        results[parname][1] *= scale
        results[parname][2] *= scale
        results[parname][3] *= scale

        out_hist.SetBinContent(i, results[parname][0])
        out_hist.SetBinError(i, results[parname][3])
        unc_info.SetBinContent(i, results[parname][3])
        unc_info.SetBinError(i, results[parname][3])

    h_cov = r.TH2D('hCovar_{0}'.format(args.variable), '', nparticlebins, -0.5, nparticlebins - 0.5,
                   nparticlebins, -0.5, nparticlebins - 0.5)
    for i in range(1, nparticlebins + 1):
        tmpintx = signal_hist.GetBinContent(i)
        for j in range(1, nparticlebins + 1):
            tmpinty = signal_hist.GetBinContent(j)
            normx = tmpintx * scaleval
            normy = tmpinty * scaleval
            h_cov.SetBinContent(h_cov.GetBin(i, j), cov[i - 1][j - 1] * normx * normy)

    outdir = os.path.join(args.outdir, args.year, args.variable, 'sigextr_fit_combine')
    ensure_dir(outdir)

    out_root = r.TFile.Open(os.path.join(outdir, 'particleOutput.root'), 'RECREATE')
    out_hist.Write()
    unc_info.Write()
    h_cov.Write()
    corrmat.Write('CorrMat')
    out_root.Close()

    draw_correlation_matrix(corrmat, args.outdir, args.year, args.variable)
    draw_covariance_matrix(h_cov, args.outdir, args.year, args.variable)
    draw_particle_result(out_hist, unc_info, particle_file, args.outdir, args.year, args.variable)

    if args.verbose:
        print('Saved plots and root output in {0}'.format(outdir))


if __name__ == '__main__':
    main()
