#!/usr/bin/env python
from CMGTools.TTHAnalysis.plotter.mcAnalysis import *
from CMGTools.TTHAnalysis.plotter.histoWithNuisances import _cloneNoDir
import re, sys, os, os.path
systs = {}

from optparse import OptionParser
parser = OptionParser(usage="%prog [options] mc.txt cuts.txt var bins")
addMCAnalysisOptions(parser)
parser.add_option("--od", "--outdir",       dest="outdir", type="string", default=None, help="output directory name")
parser.add_option("--asimov",               dest="asimov", type="string", default=None, help="Use an Asimov dataset of the specified kind: including signal ('signal','s','sig','s+b') or background-only ('background','bkg','b','b-only')")
parser.add_option("--pseudoData",           dest="pseudoData", type="string", default=None, help="Use an pseudoData dataset of the specified kind: including signal ('signal','s','sig','s+b') or background-only ('background','bkg','b','b-only')")
parser.add_option("--bbb",                  dest="bbb", type="string", default=None, help="Options for bin-by-bin statistical uncertainties with the specified nuisance name")
parser.add_option("--amc", "--autoMCStats", dest="autoMCStats", action="store_true", default=False, help="use autoMCStats")
parser.add_option("--autoMCStatsThreshold", dest="autoMCStatsValue", type="int", default=10, help="threshold to put on autoMCStats")
parser.add_option("--infile",               dest="infile", action="store_true", default=False, help="Read histograms to file")
parser.add_option("--savefile",             dest="savefile", action="store_true", default=False, help="Save histos to file")
parser.add_option("--categorize",           dest="categ", type="string", nargs=3, default=None, help="Split in categories. Requires 3 arguments: expression, binning, bin labels")
parser.add_option("--categorize-by-ranges", dest="categ_ranges", type="string", nargs=2, default=None, help="Split in categories according to the signal extraction variables. Requires 2 arguments: binning (in bin numbers), bin labels")
parser.add_option("--regularize",           dest="regularize", action="store_true", default=False, help="Regularize templates")
parser.add_option("--threshold",            dest="threshold", type=float, default=0.0, help="Minimum event yield to consider processes")
parser.add_option("--control_lnN",          dest="control_lnN", action="store_true", default=False, help="Decide whether to keep lnN systematics even if the variation is very low")
parser.add_option("--filter",               dest="filter", type="string", default=None, help="File with list of processes to be removed from the datacards")
parser.add_option("--storeAll",             dest = "storeall",       action = "store_true", default = False, help = "Store all histograms in the final rootfile, including those of normalisation uncertainties.")
parser.add_option("--notMinimumFill",       dest = "notminimumfill", action = "store_true", default = False, help = "Don't crop bins whenever they show low number of entries, or negative ones.")
parser.add_option("--notVarsChanges",       dest = "notvarschanges", action = "store_true", default = False, help = "Don't modify variations in extreme situations.")
parser.add_option("--notCropNegUncs",       dest = "cropnegativeuncs", action = "store_true", default = False, help = "Don't crop uncertainties of histograms that might go below zero.")
parser.add_option("--forceShape",           dest = "forceshape",     type = "string",       default = "",    help = "Force this list of nuisances to be of shape origin.")
parser.add_option("--minBinContent",        dest = "minbincont",     type = float,       default = 1e-5,    help = "Minimum content of any bin.")
(options, args) = parser.parse_args()
options.weight = True
options.final  = True

if "/functions_cc.so" not in ROOT.gSystem.GetLibraries(): 
    ROOT.gROOT.ProcessLine(".L %s/src/CMGTools/TTHAnalysis/python/plotter/functions.cc+" % os.environ['CMSSW_BASE']);

mca  = MCAnalysis(args[0], options)
cuts = CutsFile(args[1],   options)

binname = os.path.basename(args[1]).replace(".txt","") if options.binname == 'default' else options.binname
if binname[0] in "1234567890": raise RuntimeError("Bins should start with a letter.")
outdir  = options.outdir+"/" if options.outdir else ""
if not os.path.exists(outdir): os.mkdir(outdir)

forcedshape = options.forceshape.split(",")

report = {}
if options.infile:
    infile = ROOT.TFile(outdir+binname+".bare.root","read")
    for p in mca.listSignals(True)+mca.listBackgrounds(True)+['data']:
        variations = mca.getProcessNuisances(p) if p != "data" else []
        h = readHistoWithNuisances(infile, "x_"+p, variations, mayBeMissing=True)
        if h: report[p] = h
else:
    if options.categ:
       cexpr, cbins, _ = options.categ
       report = mca.getPlotsRaw("x", cexpr+":"+args[2], makeBinningProductString(args[3],cbins), cuts.allCuts(), nodata=options.asimov, closeTreeAfter=True)
    else:
       report = mca.getPlotsRaw("x", args[2], args[3], cuts.allCuts(), nodata=options.asimov, closeTreeAfter=True)

    if not options.notminimumfill:
        for p,h in report.items(): h.cropNegativeBins(threshold = options.minbincont)

if options.savefile:
    savefile = ROOT.TFile(outdir + binname + ".bare.root", "recreate")
    for k,h in report.items(): 
        h.writeToFile(savefile, takeOwnership = False)
    savefile.Close()

if options.asimov:
    if options.asimov in ("s","sig","signal","s+b"):
        asimovprocesses = mca.listSignals() + mca.listBackgrounds()
    elif options.asimov in ("b","bkg","background", "b-only"):
        asimovprocesses = mca.listBackgrounds()
    else: raise RuntimeError("the --asimov option requires to specify signal/sig/s/s+b or background/bkg/b/b-only")
    tomerge = None
    for p in asimovprocesses:
        if p in report: 
            if tomerge is None: 
                tomerge = report[p].raw().Clone("x_data_obs"); tomerge.SetDirectory(0)
            else: tomerge.Add(report[p].raw())
    report['data_obs'] = HistoWithNuisances(tomerge)
elif options.pseudoData:
    if options.pseudoData in ("s","sig","signal","s+b"):
        asimovprocesses = mca.listSignals() + mca.listBackgrounds()
    elif options.pseudoData in ("b","bkg","background", "b-only"):
        asimovprocesses = mca.listBackgrounds()
    else: raise RuntimeError("the --pseudoData option requires to specify signal/sig/s/s+b or background/bkg/b/b-only")
    tomerge = None
    for p in asimovprocesses:
        if p in report: 
            if tomerge is None: 
                tomerge = report[p].raw().Clone("x_data_obs"); tomerge.SetDirectory(0)
            else: tomerge.Add(report[p].raw())
    # We have to generate a Poisson fluctuation of the total background
    for b in range(1, tomerge.GetNbinsX()+1):
        tomerge.SetBinContent(b, ROOT.gRandom.Poisson(tomerge.GetBinContent(b)))
    report['data_obs'] = HistoWithNuisances(tomerge)
else:
    report['data_obs'] = report['data'].Clone("x_data_obs") 


#### Categories
if options.categ:
    allreports = dict()
    catlabels = options.categ[2].split(",")
    if len(catlabels) != report["data_obs"].GetNbinsY(): raise RuntimeError("Mismatch between category labels and bins")
    for ic,lab in enumerate(catlabels):
        allreports["%s_%s"%(binname,lab)] = dict( (k, h.projectionX("x_"+k,ic+1,ic+1)) for (k,h) in report.items() )
elif options.categ_ranges: 
    allreports = dict()
    catlabels = options.categ_ranges[1].split(',')
    catbinning = eval( options.categ_ranges[0] ) 
    
    for ic,lab in enumerate(catlabels):
        kk = {} 
        for (k,h) in report.items(): 
            kk[k] = h.getHistoInRange( "x_"+k, catbinning[ic],catbinning[ic+1])
        allreports["%s_%s"%(binname,lab)] = kk
else:
    allreports = {binname:report}


if options.filter:
    toremove=[]
    with open(options.filter, 'r') as f:
        for l in f.readlines(): 
            binname,proc = l.split(':')
            procpattern = re.compile( proc.rstrip() ) 
            if binname in allreports:
                for p in allreports[binname]:
                    if procpattern.match(p):
                        if (binname,p) not in toremove:
                           toremove.append( (binname, p))
    for binname,p in toremove:
        allreports[binname].pop(p)


#### Processing
for binname, report in allreports.items():
    if options.bbb:
        if options.autoMCStats: raise RuntimeError("Can't use --bbb together with --amc/--autoMCStats")
        for p,h in report.items():
            if p not in ("data", "data_obs"):
                h.addBinByBin(namePattern = "%s_%s_%s_bin{bin}" % (options.bbb, binname, p), conservativePruning = True)
    if not options.cropnegativeuncs:
        for p,h in report.items():
            for b in range(1, h.GetNbinsX() + 1):
                h.SetBinError(b, min(h.GetBinContent(b), h.GetBinError(b))) # crop all uncertainties to 100% to avoid negative variations
    nuisances = sorted(listAllNuisances(report))

    allyields = dict([(p,h.Integral()) for p,h in report.items()])
    procs = []; iproc = {}
    for i,s in enumerate(mca.listSignals()):
        if s not in allyields: continue
        if allyields[s] <= options.threshold:
            print("Dropping", s, "for low yields")
            continue
        procs.append(s); iproc[s] = i-len(mca.listSignals()) + 1
    for i,b in enumerate(mca.listBackgrounds()):
        if b not in allyields: continue
        if allyields[b] <= options.threshold:
            print("Dropping", s, "for low yields")
            continue
        procs.append(b); iproc[b] = i+1
    #for p in procs: print "%-10s %10.4f" % (p, allyields[p])

    systs = {}
    for name in nuisances:
        effshape = {}
        isShape = False
        print(nuisances)
        if name in forcedshape:
            isShape = True

        for p in procs:
            h  = report[p]
            n0 = h.Integral()
            if h.hasVariation(name):
                if isShape or h.isShapeVariation(name):
                    if name.endswith("_lnU"):
                        raise RuntimeError("Nuisance %s should be lnU but has shape effect on %s." % (name,p))
                    #print "Nuisance %s has a shape effect on process %s" % (name, p)
                    #if "templstat" not in name and not isShape:
                    #    h.isShapeVariation(name,debug=True)
                    isShape = True
                variants = list(h.getVariation(name))

                if not options.notvarschanges:
                    for bin in range(1, h.GetXaxis().GetNbins() + 1):
                        if variants[0].GetBinContent( bin ) <= options.minbincont:
                            variants[0].SetBinContent( bin, options.minbincont)
                        if variants[1].GetBinContent( bin ) <= options.minbincont:
                            variants[1].SetBinContent( bin, options.minbincont)
                        if h.raw().GetBinContent( bin ) <= options.minbincont:
                            variants[0].SetBinContent( bin, options.minbincont)
                            variants[1].SetBinContent( bin, options.minbincont)


                effshape[p] = variants

        if isShape:
            if options.regularize:
                for p in procs:
                    report[p].regularizeVariation(name,binname=binname)
            systs[name] = ("shape", dict((p, "1" if p in effshape else "-") for p in procs), effshape)
        else:
            effyield = dict((p, "-") for p in procs)
            isNorm = False
            for p,(hup,hdn) in effshape.items():
                i0 = allyields[p]
                kup, kdn = hup.Integral()/i0, hdn.Integral()/i0
                if options.control_lnN == True:
                    if abs(kup*kdn-1)<1e-5 or abs(kdn-1)<5e-4:
                        if abs(kup-1)>5e-4:
                            effyield[p] = "%.5f" % kup
                            isNorm = True
                else:
                    effyield[p] = "%.5f/%.5f" % (kdn,kup)
                    isNorm = True
            if isNorm or options.storeall:
                thedict = {}
                if options.storeall:
                    thedict = effshape
                if name.endswith("_lnU"):
                    systs[name] = ("lnU", effyield, thedict)
                else:
                    systs[name] = ("lnN", effyield, thedict)

    # make a new list with only the ones that have an effect
    nuisances = sorted(systs.keys())

    datacard = open(outdir + binname + ".txt", "w");
    datacard.write("## Datacard for cut file %s\n"%args[1])
    datacard.write("shapes *        * %s.root x_$PROCESS x_$PROCESS_$SYSTEMATIC\n" % binname)
    datacard.write('##----------------------------------\n')
    datacard.write('bin         %s\n' % binname)
    datacard.write('observation %s\n' % allyields['data_obs'])
    datacard.write('##----------------------------------\n')
    klen = max([7, len(binname)]+[len(p) for p in procs])
    kpatt = " %%%ds "  % klen
    fpatt = " %%%d.%df " % (klen,3)
    npatt = "%%-%ds " % max([len('process')]+list(map(len,nuisances)))
    datacard.write('##----------------------------------\n')
    datacard.write((npatt % 'bin    ')+(" "*6)+(" ".join([kpatt % binname  for p in procs]))+"\n")
    datacard.write((npatt % 'process')+(" "*6)+(" ".join([kpatt % p        for p in procs]))+"\n")
    datacard.write((npatt % 'process')+(" "*6)+(" ".join([kpatt % iproc[p] for p in procs]))+"\n")
    datacard.write((npatt % 'rate   ')+(" "*6)+(" ".join([fpatt % allyields[p] for p in procs]))+"\n")
    datacard.write('##----------------------------------\n')
    towrite = [ report[p].raw() for p in procs ] + [ report["data_obs"].raw() ]
    for name in nuisances:
        (kind,effmap,effshape) = systs[name]
        datacard.write(('%s %5s' % (npatt % name,kind)) + " ".join([kpatt % effmap[p]  for p in procs]) +"\n")
        for p,(hup,hdn) in effshape.items():
            towrite.append(hup.Clone("x_%s_%sUp"   % (p,name)))
            towrite.append(hdn.Clone("x_%s_%sDown" % (p,name)))
    if options.autoMCStats:
        datacard.write('* autoMCStats %d\n' % options.autoMCStatsValue)


    workspace = ROOT.TFile.Open(outdir+binname+".root", "RECREATE")
    for h in towrite:
        workspace.WriteTObject(h,h.GetName())
    workspace.Close()

    print("Wrote to {0}.txt and {0}.root .".format(outdir+binname))

