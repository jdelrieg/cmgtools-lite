import ROOT  as r
import os, sys, argparse
import warnings as wr
from array import array
from copy  import deepcopy
from multiprocessing import Pool
from numpy import random

sys.path.append('{cmsswpath}/src/CMGTools/TTHAnalysis/python/plotter/tw-run2/differential/'.format(cmsswpath = os.environ['CMSSW_BASE']))
from . import varList as vl
from . import beautifulUnfoldingPlots as bp
from . import tdrstyle, CMS_lumi
from . import errorPropagator as ep


combinecommscaff = 'combine -M FitDiagnostics --out {outdir} {infile} {asimov} --saveWorkspace -n {y}_{var} --saveShapes --saveWithUncertainties --robustFit 1 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=5000000 --robustHesse 1'

rs = random.RandomState(34)


def createPoissonToy(task):
    inpath, year, varName, pretend, itoy, nbs = task
    if not os.path.isdir(inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/bincards/toy{i}".format(i = itoy)):
        os.system("mkdir -p " + inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/bincards/toy{i}".format(i = itoy))
    
    f  = r.TFile(inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/bincards/card_{v}.root".format(v = varName), "READ")
    f2 = r.TFile(inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/bincards/toy{i}/card_{v}.root".format(v = varName, i = itoy), "RECREATE")
    theint = 0
    for iK in f.GetListOfKeys():
        if "data" not in iK.GetName():
            f2.WriteTObject(f.Get(iK.GetName()))
        else:
            tmph  = deepcopy(f.Get(iK.GetName()).Clone("x_data_obs"))
            tmpprocs = []
            tmpprocs.append(deepcopy(f.Get("x_dy").Clone("tmp_dy")))
            tmpprocs.append(deepcopy(f.Get("x_nonworz").Clone("tmp_nonworz")))
            tmpprocs.append(deepcopy(f.Get("x_ttbar").Clone("tmp_ttbar")))
            tmpprocs.append(deepcopy(f.Get("x_vvttv").Clone("tmp_vvttv")))
            tmpprocs.append(deepcopy(f.Get("x_tw_bkg").Clone("tmp_twbkg")))
            for iB in range(nbs):
                tmpprocs.append(deepcopy(f.Get("x_tw_partbin{i}".format(i = iB)).Clone("tmp_twpartbin{i}".format(i = iB))))
            
            for iB in range(1, tmph.GetNbinsX() + 1):
                tmph.SetBinContent(iB, random.poisson(round(sum( [ h.GetBinContent(iB) for h in tmpprocs ] ))))
                tmph.SetBinError(iB, r.TMath.Sqrt(tmph.GetBinContent(iB)))
#                print round(tmptw.GetBinContent(iB)), tmph.GetBinContent(iB)
            theint = tmph.Integral()
            f2.WriteTObject(tmph)
    
    f2.Close(); del f2
    f.Close();  del f
    
    outmain = ""
    with open(inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/bincards/card_{v}.txt".format(v = varName), "r") as scaff:
        for line in scaff:
            if "observation" in line:
                outmain += "observation " + str(theint) + "\n"
            else:
                outmain += line
    
    foutmain = open(inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/bincards/toy{i}/card_{v}.txt".format(v = varName, i = itoy), "w")
    foutmain.write(outmain)
    foutmain.close(); del foutmain
    return


def readResults(f1, f2, nbs):
    if not os.path.isfile(f1):
        raise RuntimeError("FATAL: no valid fitDiagnostics file found as {v}.\n".format(v = f1))

    if not os.path.isfile(f2):
        raise RuntimeError("FATAL: no valid higgsCombine file found as {v}.\n".format(v = f2))
    
    tfile     = r.TFile.Open(f1)
    tfile2    = r.TFile.Open(f2)

    fitsb     = tfile.Get('tree_fit_sb')
    fitsb.GetEntry(0)
    fitstatus = fitsb.fit_status

    if   fitstatus == -1:
        raise RuntimeError('Fit has not converged (fit status value: {fitv}) of file {v}'.format(v = f1, fitv = fitstatus))
    elif fitstatus != 0:
        wr.warn('Fit of file {v} has a nonzero fit status value: {fitv}'.format(v = f2, fitv = fitstatus), UserWarning, stacklevel = 2)
    elif verbose:
        print("    - Fit status:", fitstatus)

    fitResult = tfile.Get('fit_s')
    if verbose: fitResult.Print()

    # Tambien necesitamos el workspace
    w       = tfile2.Get('w')
    poiList = r.RooArgList('poiList')
    for i in range(nbs):
        var = w.var('r_tW_%d'%i)
        poiList.add(var)

    cov = fitResult.reducedCovarianceMatrix(poiList)

    results = {}
    count   = 0
    for var in fitResult.floatParsFinal():
        count += 1
        results[var.GetName()] = [ var.getVal(), var.getErrorLo(), var.getErrorHi(), var.getError() ]
        if count == fitResult.floatParsFinal().getSize(): break

    tfile2.Close(); tfile.Close()
    return results, cov


def makeClosure(task):
    inpath, year, varName, pretend, ntoys, redoFits = task

    bins_detector = vl.varList[varName]['bins_detector']
    ndetectorbins   = len(bins_detector) - 1
    bins_particle = vl.varList[varName]['bins_particle']
    nparticlebins   = len(bins_particle) - 1
    
    physicsModel = 'text2workspace.py -m 125 -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel '
    for idx in range(nparticlebins):
        physicsModel += "--PO 'map=.*/tw_partbin{iBp}:r_tW_{iBp}[1,0,20]' ".format(iBp  = idx)

    physicsModel += '{infile} -o {outfile}'.format(infile  = inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/bincards/card_{v}.txt".format(v = varName),
                                                   outfile = inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/ws_asimov.root",
                                                   var     = varName,)

    if verbose:
        print("Text2Workspace command:", physicsModel, "\n")
    
    outstat = None
    if not pretend:
        if os.path.isfile(inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/ws_asimov.root"):
            if redoFits:
                if verbose:
                    print("    - Erasing old closure tests results...")
                os.system("rm " + inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/closuretests/ws_asimov.root")
                outstat = os.system(physicsModel)
        else:
            outstat = os.system(physicsModel)
        if outstat:
            raise RuntimeError("FATAL: text2workspace.py failed to execute for variable {v} of year {y}.".format(v = varName, y = year))

    fitoutpath = inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/closuretests"

    asimov_ =  "-t -1 --setParameters "
    for idx in range(nparticlebins - 1):
        asimov_ += "r_tW_{iBp}=1,".format(iBp = idx)
    asimov_ += "r_tW_{iBp}=1".format(iBp = nparticlebins - 1)
    
    combinecomm = combinecommscaff.format(
        y      = year,
        outdir = fitoutpath,
        infile = inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/ws_asimov.root",
        var    = varName + "asimov",
        asimov = asimov_,
    )

    if verbose:
        print("Combine command:", combinecomm, "\n")

    #sys.exit()
    outstat = None
    if not pretend:
        if (not (os.path.isfile(fitoutpath + "/higgsCombine{y}_{var}.FitDiagnostics.mH120.root".format(y = year, var = varName + "asimov")) and os.path.isfile(fitoutpath + '/fitDiagnostics{y}_{var}.root'.format(y = year, var = varName + "asimov")))) or redoFits:
            outstat = os.system(combinecomm)
            if outstat:
                raise RuntimeError("FATAL: combine failed to execute for variable {v} of year {y}.".format(v = varName, y = year))
        
            if not pretend:
                if not os.path.isfile('higgsCombine{y}_{var}.FitDiagnostics.mH120.root'.format(y = year, var = varName + "asimov")):
                    raise RuntimeError("FATAL: no valid higgsCombine file found for variable {v} of year {y}.".format(v = varName, y = year))
                else:
                    os.system("mv ./higgsCombine{y}_{var}.FitDiagnostics.mH120.root {fdir}".format(y = year, var = varName + "asimov", fdir = fitoutpath + "/"))

    
    print("> Creating toys...")
    for i in range(ntoys):
        createPoissonToy( (inpath, year, varName, pretend, i, nparticlebins) )
#        sys.exit()

        physicsModel = 'text2workspace.py -m 125 -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel '

        for idx in range(nparticlebins):
            physicsModel += "--PO 'map=.*/tw_partbin{iBp}:r_tW_{iBp}[1,0,20]' ".format(iBp  = idx)

        physicsModel += '{infile} -o {outfile}'.format(infile  = inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/bincards/toy{i}/card_{v}.txt".format(v = varName, i = i),
                                                       outfile = inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/closuretests/ws_toy{i}.root".format(i = i),
                                                       var     = varName,)

        if verbose:
            print("Text2Workspace command:", physicsModel, "\n")

        outstat = None
        if not pretend:
            if os.path.isfile(inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/closuretests/ws_toy{i}.root".format(i = i)):
                if redoFits:
                    if verbose:
                        print("    - Erasing old closure tests results...")
                    os.system("rm " + inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/closuretests/ws_toy{i}.root".format(i = i))
                    outstat = os.system(physicsModel)
            else:
                outstat = os.system(physicsModel)
            if outstat:
                raise RuntimeError("FATAL: text2workspace.py failed to execute for variable {v} of year {y}.".format(v = varName, y = year))

        asimov_ =  "--setParameters "
        for idx in range(nparticlebins - 1):
            asimov_ += "r_tW_{iBp}=1,".format(iBp = idx)
        asimov_ += "r_tW_{iBp}=1".format(iBp = nparticlebins - 1)
        
        combinecomm = combinecommscaff.format(
            y      = year,
            outdir = fitoutpath,
            infile = inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/closuretests/ws_toy{i}.root".format(i = i),
            var    = varName + "toy" + str(i),
            asimov = asimov_,
#            asimov = "",
        )

        if verbose:
            print("Combine command:", combinecomm, "\n")

        #sys.exit()
        if not pretend:
            if (not (os.path.isfile(fitoutpath + "/higgsCombine{y}_{var}.FitDiagnostics.mH120.root".format(y = year, var = varName + "toy" + str(i))) and os.path.isfile(fitoutpath + '/fitDiagnostics{y}_{var}.root'.format(y = year, var = varName + "toy" + str(i))))) or redoFits:
                outstat = os.system(combinecomm)
                if outstat:
                    raise RuntimeError("FATAL: combine failed to execute for variable {v} of year {y}.".format(v = varName, y = year))

                if not pretend:
                    #sys.exit()
                    if not os.path.isfile('higgsCombine{y}_{var}.FitDiagnostics.mH120.root'.format(y = year, var = varName + "toy" + str(i))):
                        raise RuntimeError("FATAL: no valid higgsCombine file found for variable {v} of year {y}.".format(v = varName, y = year))
                    else:
                        os.system("mv ./higgsCombine{y}_{var}.FitDiagnostics.mH120.root {fdir}".format(y = year, var = varName + "toy" + str(i), fdir = fitoutpath + "/"))
    
    
#    sys.exit()
    #### plotiar
    if not pretend:
        # Ahora recogemos la virutilla
        # PRIMERO, ASIMOV
        res_as,cov_as = readResults(fitoutpath + '/fitDiagnostics{y}_{var}.root'.format(y = year, var = varName + "asimov"),
                                    fitoutpath + "/higgsCombine{y}_{var}.FitDiagnostics.mH120.root".format(y = year, var = varName + "asimov"),
                                    nparticlebins)
        res_toys = {}
        for i in range(ntoys):
            res_toys[i] = {}
            res_toys[i]["res"], res_toys[i]["cov"] = readResults(fitoutpath + '/fitDiagnostics{y}_{var}.root'.format(y = year, var = varName + "toy" + str(i)),
                                                                 fitoutpath + "/higgsCombine{y}_{var}.FitDiagnostics.mH120.root".format(y = year, var = varName + "toy" + str(i)),
                                                                 nparticlebins)
        
        
        #### SAVING
        # Put results into histos
        hAsimov = r.TH1D('hFitResult_{var}'.format(var = varName),
                         '', nparticlebins, array('d', vl.varList[varName]['bins_particle']))
        htoys = []
        for iT in range(ntoys):
            htoys.append(r.TH1D('hFitResultToy_{i}'.format(i = iT),
                         '', nparticlebins, array('d', vl.varList[varName]['bins_particle'])))
        
        scaleval = 1.
        thelumi = vl.TotalLumi if year == "run2" else vl.LumiDict[int(iY)]
        if vl.doxsec: scaleval = 1/thelumi/1000.

        signalname = "x_tw"
        card = r.TFile.Open(inpath + "/" + year + "/" + varName + "/particle.root", "READ")
        for i in range(1, nparticlebins + 1):
            tmpint = card.Get(signalname).GetBinContent(i)
            thestatunc = r.TMath.Sqrt(res_as['r_tW_%d'%(i-1)][0] * tmpint) * scaleval
            
            res_as['r_tW_%d'%(i-1)][0] *= tmpint * scaleval
            res_as['r_tW_%d'%(i-1)][1] *= tmpint * scaleval
            res_as['r_tW_%d'%(i-1)][2] *= tmpint * scaleval
            res_as['r_tW_%d'%(i-1)][3] *= tmpint * scaleval
            
            # The uncertainties here are symmetric...
            hAsimov.SetBinContent(i, res_as['r_tW_%d'%(i-1)][0])
#            hAsimov.SetBinError  (i, res_as['r_tW_%d'%(i-1)][3])
            hAsimov.SetBinError  (i, thestatunc)
            
            for iT in range(ntoys):
                res_toys[iT]["res"]['r_tW_%d'%(i-1)][0] *= tmpint * scaleval
                res_toys[iT]["res"]['r_tW_%d'%(i-1)][1] *= tmpint * scaleval
                res_toys[iT]["res"]['r_tW_%d'%(i-1)][2] *= tmpint * scaleval
                res_toys[iT]["res"]['r_tW_%d'%(i-1)][3] *= tmpint * scaleval
                
                htoys[iT].SetBinContent(i, res_toys[iT]["res"]['r_tW_%d'%(i-1)][0])
#                htoys[iT].SetBinError  (i, res_toys[iT]["res"]['r_tW_%d'%(i-1)][3])
                htoys[iT].SetBinError  (i, 0.)
            
        card.Close()

    
    ################################### dibujinos
    plot               = bp.beautifulUnfPlot(varName + "_closuretest", varName)
    plot.doRatio       = True
    plot.doFit         = True
    
    if not os.path.isdir(inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/closuretests/plots"):
        os.system("mkdir -p " + inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/closuretests/plots")
    
    plot.plotspath     = inpath + "/" + year + "/" + varName + "/sigextr_fit_combine/closuretests/plots"
    plot.displayedLumi = vl.TotalLumi if year == "run2" else vl.LumiDict[int(iY)]
    plot.doPreliminary = vl.doPre

    hAsimov.SetMarkerStyle(r.kFullCircle)
    hAsimov.SetLineColor(r.kBlack)
    
    for iT in range(ntoys):
        htoys[iT].SetMarkerStyle(r.kFullCircle)
#        htoys[iT].SetMarkerSize(0.5)
        htoys[iT].SetMarkerColor(vl.coloursForToys[iT if iT <= 10 else iT - 10])
        htoys[iT].SetLineColor(vl.coloursForToys[iT if iT <= 10 else iT - 10])
    
    #nominal_withErrors[0].SetFillColorAlpha(r.kBlue, 0.35)
    #nominal_withErrors[0].SetLineColor(0)
    #nominal_withErrors[0].SetFillStyle(1001)
    
    legloc = "TR"
    thelumi = vl.TotalLumi if year == "run2" else vl.LumiDict[int(year)]
    scaleval = 1/thelumi/1000.

    if not os.path.isfile(inpath + "/" + year + "/" + varName + '/particle.root'):
        raise RuntimeError('The rootfile with the generated information does not exist.')
    tmptfile = r.TFile.Open(inpath + "/" + year + "/" + varName + '/particle.root')
    tru = deepcopy(tmptfile.Get('x_tw').Clone('tru'))
    tru.SetLineWidth(2)
    tru.SetLineColor(bp.colorMap[0])
    tru.Scale(scaleval)
    tru.SetMarkerSize(0)
    
    htmp = deepcopy(tru.Clone("htmp"))
    fiduval = None; fiduunc = None

    for el in [tru, hAsimov]:
        tmpval = vl.getAConservativeMaximum(el)
        if hAsimov.GetMaximum() <= tmpval: hAsimov.SetMaximum(tmpval)

    plot.addHisto(hAsimov,  'P,E,same{s}'.format(s = ",X0" if "equalbinsunf" in vl.varList[varName] else ""), "Asimov dataset", 'PEL', 'data')
    #plot.addHisto(nominal_withErrors, 'hist',    'Uncertainty',              'F', 'unc')
    plot.addHisto(tru,      'L,same', 'tW PH DR + P8', 'L', 'mc')
    
    for iT in range(ntoys):
        plot.addHisto(htoys[iT], 'P,same{s}'.format(s = ",X0" if "equalbinsunf" in vl.varList[varName] else ""), "Toy " + str(iT), 'L', 'mc')
    
    plot.saveCanvas(legloc)

    #plot.addHisto(nominal_withErrors, 'E2',     'Uncertainty',   'F')
    #plot.addHisto(hAsimov, 'P,same',vl.labellegend,'PE', 'data')
    #plot.saveCanvas(legloc)
    del plot
    return



if __name__ == '__main__':
    vl.SetUpWarnings()
    r.gROOT.SetBatch(True)
    parser = argparse.ArgumentParser(usage = "python doClosureTests.py [options]", description = "", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--inpath',     '-i', metavar = 'inpath',     dest = "inpath",   required = False, default = "./temp/differential/")
    parser.add_argument('--year',       '-y', metavar = 'year',       dest = "year",     required = False, default = "all")
    parser.add_argument('--variable',   '-v', metavar = 'variable',   dest = "variable", required = False, default = "all")
    parser.add_argument('--nthreads',   '-j', metavar = 'nthreads',   dest = "nthreads", required = False, default = 0, type = int)
    parser.add_argument('--pretend',    '-p', action  = "store_true", dest = "pretend",  required = False, default = False)
    parser.add_argument('--verbose',    '-V', action  = "store_true", dest = "verbose",  required = False, default = False)
    parser.add_argument('--redoFits',   '-r', action  = "store_true", dest = "redofits", required = False, default = False)
    parser.add_argument('--ntoys',      '-t', metavar = 'ntoys',      dest = "ntoys",    required = False, default = 10, type = int)


    args     = parser.parse_args()
    year     = args.year
    nthreads = args.nthreads
    pretend  = args.pretend
    inpath   = args.inpath
    variable = args.variable
    verbose  = args.verbose
    redofits = args.redofits
    ntoys    = args.ntoys


    tasks = []
    theyears = []
    presentyears = next(os.walk(inpath))[1]

    if "2016" in presentyears:
        theyears.append("2016")
    if "2017" in presentyears:
        theyears.append("2017")
    if "2018" in presentyears:
        theyears.append("2018")
    if "run2" in presentyears:
        theyears.append("run2")

    if year.lower() != "all" and year in presentyears:
        theyears = [ year ]
    elif year.lower() != "all":
        raise RuntimeError("FATAL: the year requested is not in the provided input folder.")

    for iY in theyears:
        thevars = next(os.walk(inpath + "/" + iY))[1]

        if variable.lower() != "all" and variable in thevars:
            thevars = [ variable ]
        elif variable.lower() != "all":
            raise RuntimeError("FATAL: the variable requested is not in the provided input folder.")

        if not os.path.isdir(inpath + "/" + iY + "/particleplots"):
            os.system("mkdir -p " + inpath + "/" + iY + "/particleplots")
        for iV in thevars:
            if "plots" in iV or "Fiducial" in iV or "table" in iV or "response" in iV: continue
            if not os.path.isdir(inpath + "/" + iY + "/" + iV + "/sigextr_fit_combine"): continue
            if not os.path.isdir(inpath + "/" + iY + "/" + iV + "/sigextr_fit_combine/closuretests"):
                os.system("mkdir -p " + inpath + "/" + iY + "/" + iV + "/sigextr_fit_combine/closuretests")
            tasks.append( (inpath, iY, iV, pretend, ntoys, redofits) )


    if verbose:
        print('Tasks:', tasks)

    #for el in tasks: print el
    #sys.exit()

    if nthreads > 1:
        pool = Pool(nthreads)
        pool.map(makeClosure, tasks)
        pool.close()
        pool.join()
    else:
        for tsk in tasks:
            makeClosure(tsk)
            #sys.exit()
    
