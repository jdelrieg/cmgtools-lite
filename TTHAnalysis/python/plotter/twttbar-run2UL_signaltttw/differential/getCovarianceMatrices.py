from copy import deepcopy
import ROOT as r
import warnings as wr
import os, sys, math, argparse, shutil
from   array import array
from multiprocessing import Pool

sys.path.append('{cmsswpath}/src/CMGTools/TTHAnalysis/python/plotter/tw-run2/differential/'.format(cmsswpath = os.environ['CMSSW_BASE']))
from . import beautifulUnfoldingPlots as bp
from . import errorPropagator as ep
#import getLaTeXtable as tex
from . import varList as vl
from . import CMS_lumi, tdrstyle

r.gROOT.SetBatch(True)
vl.SetUpWarnings()


CMS_lumi.writeExtraText = 1

def printCovarianceMatrix(tsk):
    inpath, iY, var, ty, nofidufile = tsk
    #print inpath, iY, var, ty
    fidornot = "fid" in ty
    binornot = "bin" in ty
    ty = ty.replace("fid", "").replace("bin", "")

    pathtothings = inpath + "/" + iY + "/" + var

    if ty == 'particle' and not fidornot: tfile = r.TFile(pathtothings + "/particleOutput.root",       "read")
    elif not binornot   and     fidornot: tfile = r.TFile(pathtothings + "/particlefidOutput.root",    "read")
    elif     binornot   and     fidornot: tfile = r.TFile(pathtothings + "/particlefidbinOutput.root", "read")
    elif     binornot   and not fidornot: tfile = r.TFile(pathtothings + "/particlebinOutput.root",    "read")
    else:                                 tfile = r.TFile(pathtothings + "/detectorsignal_bs.root",    "read")
    
    if ty == "detector": nominal = deepcopy(tfile.Get("data_").Clone("nominal"))
    else:                nominal = deepcopy(tfile.Get(var).Clone("nominal"))

    thelumi = vl.TotalLumi if iY == "run2" else vl.LumiDict[iY]
    scaleval = 1/thelumi/1000
    if vl.doxsec and ty == 'detector': nominal.Scale(scaleval)
    
    varMat  = {}; doneenvs = []
    for key in tfile.GetListOfKeys():
        if key.GetName() == "data_" or "asimov" in key.GetName() or key.GetName() == var or key.GetName() == "nom0" or key.GetName() == "nom1":
            continue
        elif key.GetName() == "CovMat" and ty == "particle":
            varMat["unfCovMat"] = deepcopy(key.ReadObj())
        else:
            if "Down" in key.GetName() or "Up" not in key.GetName(): continue
            #elif "Up" not in key.GetName():
                #print key.GetName()
                #varMat[key.GetName().replace("data_", "").replace(var + "_", "")] = deepcopy(ep.getCovarianceFromVar(nominal, key.ReadObj(), var, ty))
            else:
                tmphistoup = deepcopy(key.ReadObj().Clone("tmphistoup"))
                tmphistodw = None
                isEnv      = None

                for iU in vl.UncertaintiesToEnvelope:
                    if iU in key.GetName():
                        isEnv = iU

                if isEnv:
                    if isEnv in doneenvs: continue
                    doneenvs.append(isEnv)
                    tmphistodw = deepcopy(nominal.Clone("tmphistodw"))
                    nbins = tmphistoup.GetNbinsX()
                    for iB in range(1, nbins + 1):
                        if tmphistoup.GetBinContent(iB) - nominal.GetBinContent(binin) >= 0:
                            tmphistoup.SetBinContent(iB, tmphistoup.GetBinContent(iB))
                        else:
                            tmphistoup.SetBinContent(iB, nominal.GetBinContent(iB))
                            tmphistodw.SetBinContent(iB, tmphistoup.GetBinContent(iB))
                    doneentries = [key.GetName()]
                    for key2 in tfile.GetListOfKeys():
                        if isEnv in key2.GetName() and key2.GetName() not in doneentries:
                            for iB in range(1, nbins + 1):
                                if key.ReadObj().GetBinContent(iB) > tmphistoup.GetBinContent(binin):
                                    tmphistoup.SetBinContent(iB, key.ReadObj().GetBinContent(iB))
                                elif key.ReadObj().GetBinContent(iB) < tmphistodw.GetBinContent(binin):
                                    tmphistodw.SetBinContent(iB, key.ReadObj().GetBinContent(iB))

                else:
                    for key2 in tfile.GetListOfKeys():
                        if key2.GetName() == key.GetName().replace("Up", "Down"):
                            tmphistodw = deepcopy(key2.ReadObj().Clone("tmphistodw"))

                    if not tmphistodw:
                        #print "Variation", key.GetName(), "is asymmetrical."
                        tmphistodw = deepcopy(tmphistoup.Clone("tmphistodw"))

                varsup  = [abs(tmphistoup.GetBinContent(binin) - nominal.GetBinContent(binin)) for binin in range(1, nominal.GetNbinsX() + 1)]
                varsdw  = [abs(tmphistodw.GetBinContent(binin) - nominal.GetBinContent(binin)) for binin in range(1, nominal.GetNbinsX() + 1)]
                varsfin = [(varsup[binin] + varsdw[binin])/2 for binin in range(nominal.GetNbinsX())]
                for binin in range(1, nominal.GetNbinsX() + 1):
                    tmphistoup.SetBinContent(binin, nominal.GetBinContent(binin) + varsfin[binin - 1])
                del varsup, varsdw, varsfin, tmphistodw

                varMat[key.GetName().replace("data_", "").replace(var + "_", "") if not isEnv else var + "_" + isEnv] = deepcopy(ep.getCovarianceFromVar(nominal, tmphistoup, var, iY, ty))
                del tmphistoup
    #sys.exit()
    #colup = deepcopy(nominal.Clone("ColorRUp"))
    #coldn = deepcopy(nominal.Clone("ColorRDown"))
    
    #for bin in range(1, nominal.GetNbinsX() + 1): # Colour envelope is applied in any case
        #tmpuncUp   = nominal.GetBinContent(bin)
        #tmpuncDown = nominal.GetBinContent(bin)
        #tmpunc     = 0.
        #for key in tfile.GetListOfKeys():
            #if key.GetName().replace("data_", "").replace(var+"_", "") in vl.varList['Names']['colorSysts']:
                #tmpunc  = key.ReadObj().GetBinContent(bin)
                #if tmpunc > tmpuncUp:
                    #tmpuncUp    = tmpunc
                #elif tmpunc < tmpuncDown:
                    #tmpuncDown  = tmpunc
        #colup.SetBinContent(bin, tmpuncUp)
        #coldn.SetBinContent(bin, tmpuncDown)
    
    #varsup  = [abs(colup.GetBinContent(binin) - nominal.GetBinContent(binin)) for binin in range(1, nominal.GetNbinsX() + 1)]
    #varsdw  = [abs(coldn.GetBinContent(binin) - nominal.GetBinContent(binin)) for binin in range(1, nominal.GetNbinsX() + 1)]
    #varsfin = [(varsup[binin] + varsdw[binin])/2 for binin in range(nominal.GetNbinsX())]
    #for binin in range(1, nominal.GetNbinsX() + 1):
        #colup.SetBinContent(binin, nominal.GetBinContent(binin) + varsfin[binin - 1])
    #del varsup, varsdw, varsfin
    
    #varMat["ColorRUp"]   = ep.getCovarianceFromVar(nominal, colup, var, ty)
    #varMat["ColorRDown"] = ep.getCovarianceFromVar(nominal, coldn, var, ty)
    
    binning  = array('f', vl.varList[var]['bins_detector'] if ty == "detector" else vl.varList[var]['bins_particle'])
    
    if fidornot and not nofidufile: # We must calculate the (complete) covariance matrix for the statistical uncertainties for this case, as it is not directly providen by doFiducial.py nor TUnfold.
        ffid = r.TFile.Open(inpath + "/" + iY + "/Fiducial/particleOutput.root", "read")
        fvar = r.TFile.Open(pathtothings + "/particleOutput.root",               "read")

        newmat = r.TH2F('newmat', '', nominal.GetNbinsX(), binning, nominal.GetNbinsX(), binning)
        
        dxs = deepcopy(fvar.Get(var).Clone("dxs"))
        covm = deepcopy(fvar.Get("CovMat").Clone("covm"))

        for key in ffid.GetListOfKeys():
            if key.GetName() != "Fiducial": continue
            dfid = r.TH1D(fvar.Get(var))
            for bin in range(1, dfid.GetNbinsX() + 1):
                dfid.SetBinContent(bin, key.ReadObj().GetBinContent(1))
                dfid.SetBinError(bin,   key.ReadObj().GetBinError(1))
        #print "\nFiducial"
        for bin1 in range(1, nominal.GetNbinsX() + 1):
            for bin2 in range(1, nominal.GetNbinsX() + 1):
                goodunc = (covm.GetBinContent(bin1, bin2) / dfid.GetBinContent(bin1)**2 +
                           dxs.GetBinContent(bin1) * dxs.GetBinContent(bin2) * dfid.GetBinError(bin1)**2 / dfid.GetBinContent(bin1)**4 -
                           dxs.GetBinContent(bin2) / dfid.GetBinContent(bin1)**3 * sum([covm.GetBinContent(bin1, j) for j in range(1, dxs.GetNbinsX() + 1)]) -
                           dxs.GetBinContent(bin1) / dfid.GetBinContent(bin1)**3 * sum([covm.GetBinContent(bin2, j) for j in range(1, dxs.GetNbinsX() + 1)]) )
                #if bin1 == bin2: print "bin", bin1, goodunc
                newmat.SetBinContent(bin1, bin2, goodunc)
        
        if binornot:
            newmat.Scale(1, "width"); # THIS IS A COVARIANCE!! Constants that apply to the random variable apply SQUARED to the covariance (and variance)! NOTE: when you have a 2D histo, the scale is already done "two times".
            #print "\nFiducialnorm"
        varMat["statistical"] = deepcopy(newmat.Clone("statistical"))
        #for bin in range(1, nominal.GetNbinsX() + 1):
            #print "bin", bin, newmat.GetBinContent(bin, bin)
        ffid.Close(); fvar.Close(); del ffid, fvar, dfid, dxs, newmat;

    elif fidornot: # We must calculate the (complete) covariance matrix for the statistical uncertainties for this case, as it is not directly providen by doFiducial.py nor TUnfold.
        fvar = r.TFile.Open(pathtothings + "/particleOutput.root",               "read")

        newmat = r.TH2F('newmat', '', nominal.GetNbinsX(), binning, nominal.GetNbinsX(), binning)

        dxs = deepcopy(fvar.Get(var).Clone("dxs"))
        covm = deepcopy(fvar.Get("CovMat").Clone("covm"))

        for key in fvar.GetListOfKeys():
            if key.GetName() != var: continue
            dfid = r.TH1D(fvar.Get(var))

            for bin in range(1, dfid.GetNbinsX() + 1):
                dfid.SetBinContent(bin, sum([fvar.Get(var).GetBinContent(i) for i in range(1, fvar.Get(var).GetNbinsX() + 1)]))
                dfid.SetBinError(bin,   r.TMath.Sqrt(sum([fvar.Get("CovMat").GetBinContent(i, j) for i in range(1, fvar.Get("CovMat").GetNbinsX() + 1) for j in range(1, fvar.Get("CovMat").GetNbinsX() + 1) ])))
        #print "\nFiducial"
        for bin1 in range(1, nominal.GetNbinsX() + 1):
            for bin2 in range(1, nominal.GetNbinsX() + 1):
                goodunc = (covm.GetBinContent(bin1, bin2) / dfid.GetBinContent(bin1)**2 +
                           dxs.GetBinContent(bin1) * dxs.GetBinContent(bin2) * dfid.GetBinError(bin1)**2 / dfid.GetBinContent(bin1)**4 -
                           dxs.GetBinContent(bin2) / dfid.GetBinContent(bin1)**3 * sum([covm.GetBinContent(bin1, j) for j in range(1, dxs.GetNbinsX() + 1)]) -
                           dxs.GetBinContent(bin1) / dfid.GetBinContent(bin1)**3 * sum([covm.GetBinContent(bin2, j) for j in range(1, dxs.GetNbinsX() + 1)]) )
                #if bin1 == bin2: print "bin", bin1, goodunc
                newmat.SetBinContent(bin1, bin2, goodunc)

        if binornot:
            newmat.Scale(1, "width"); # THIS IS A COVARIANCE!! Constants that apply to the random variable apply SQUARED to the covariance (and variance)! NOTE: when you have a 2D histo, the scale is already done "two times".
            #print "\nFiducialnorm"
        varMat["statistical"] = deepcopy(newmat.Clone("statistical"))
        #for bin in range(1, nominal.GetNbinsX() + 1):
            #print "bin", bin, newmat.GetBinContent(bin, bin)
        fvar.Close(); del fvar, dfid, dxs, newmat;
    
    if ty == "detector":
        newmat = r.TH2F('newmat', '', nominal.GetNbinsX(), binning, nominal.GetNbinsX(), binning)
        for bin in range(1, nominal.GetNbinsX() + 1):
            newmat.SetBinContent(bin, bin, nominal.GetBinError(bin)**2)
        varMat["statistical"] = deepcopy(newmat.Clone("statistical"))
        del newmat;
    idnx = 0
    finalmat = r.TH2F('finalmat', '', nominal.GetNbinsX(), binning, nominal.GetNbinsX(), binning)
    for key in varMat:
        idnx += 1
        #print idnx, key
        #print "finalmat.GetNbinsX()", finalmat.GetNbinsX()
        #print "varMat[key].GetNbinsX()", varMat[key].GetNbinsX()
        finalmat.Add(varMat[key])
    
    #for bin in range(1, nominal.GetNbinsX() + 1): print "matfinal bin", bin, ":", finalmat.GetBinContent(bin, bin)
    
    if binornot and not fidornot: finalmat.Scale(1, "width")

    if fidornot and ("unfCovMat" in varMat or "statistical" not in varMat):
        raise RuntimeError("You are calculating the covariance matrix of some fiducial results but you do not have the statistical uncertainties covariance matrix!!!!")
    
    tdrstyle.setTDRStyle()
    finalmat.SetStats(False)
    finalmat.SetXTitle(vl.varList[var]['xaxis'])
    finalmat.SetYTitle(vl.varList[var]['xaxis'])
    finalmat.SetMarkerColor(r.kRed)
    finalmat.SetMarkerColor(r.kRed)

    if   'txtsize_covparticle' in vl.varList[var] and ty == "particle" and not fidornot:
        finalmat.SetMarkerSize(vl.varList[var]['txtsize_covparticle'])
    elif 'txtsize_covdetector' in vl.varList[var] and ty == "detector":
        finalmat.SetMarkerSize(vl.varList[var]['txtsize_covdetector'])
    elif ('txtsize_covparticlefid' in vl.varList[var] and fidornot and not binornot):
        finalmat.SetMarkerSize(vl.varList[var]['txtsize_covparticlefid'])
    elif 'txtsize_covparticlefidbin' in vl.varList[var] and fidornot and binornot:
        finalmat.SetMarkerSize(vl.varList[var]['txtsize_covparticlefidbin'])
    
    fcovmat = r.TFile(pathtothings + "/CovMat_{t}{lodefid}{lodenorm}.root".format(t = ty, lodefid = "fid" * (fidornot), lodenorm = "bin" * (binornot)), "recreate")
    finalmat.Write()
    fcovmat.Close()
    
    r.gStyle.SetPaintTextFormat("4.5f" if not binornot else "4.8f")
    r.gStyle.SetPadRightMargin(0.17)
    r.gStyle.SetPadTopMargin(0.05)
    r.gStyle.SetPadBottomMargin(0.1)
    r.gStyle.SetPadLeftMargin(0.12)
    finalmat.GetYaxis().SetTitleOffset(1.5)
    finalmat.GetXaxis().SetTitleOffset(1.1)
    finalmat.GetXaxis().SetTitleFont(43)
    finalmat.GetXaxis().SetTitleSize(22)
    finalmat.GetXaxis().SetLabelFont(43)
    finalmat.GetXaxis().SetLabelSize(22)
    finalmat.GetYaxis().SetTitleFont(43)
    finalmat.GetYaxis().SetTitleSize(22)
    finalmat.GetYaxis().SetLabelFont(43)
    finalmat.GetYaxis().SetLabelSize(22)
    r.gStyle.SetLabelFont(43, "XYZ")
    r.gStyle.SetLabelSize(22, "XYZ")

    c = r.TCanvas('c', "", 200, 10, 600, 600)

    txtanglestring = ""
    if   ('txtangle_covdetector' in vl.varList[var] and ty == "detector"):
        txtanglestring = vl.varList[var]['txtangle_covdetector']
    elif ('txtangle_covparticle' in vl.varList[var] and ty == "particle" and not fidornot and not binornot):
        txtanglestring = vl.varList[var]['txtangle_covparticle']
    elif ('txtangle_covparticlefid' in vl.varList[var] and fidornot and not binornot):
        txtanglestring = vl.varList[var]['txtangle_covparticlefid']
    elif ('txtangle_covparticlefidbin' in vl.varList[var] and binornot):
        txtanglestring = vl.varList[var]['txtangle_covparticlefidbin']

    finalmat.Draw("colz text{s}".format(s = txtanglestring))
    r.gPad.Update()

    CMS_lumi.lumi_13TeV = ""
    CMS_lumi.extraText  = 'Preliminary' * vl.doPre
    CMS_lumi.lumi_sqrtS = ''
    #CMS_lumi.cmsTextSize += 0.1
    CMS_lumi.CMS_lumi(r.gPad, 0, 0, 0.05)

    plotsoutputpath = pathtothings + "/CovMatplots"
    if not os.path.isdir(plotsoutputpath):
        os.system('mkdir -p ' + plotsoutputpath)

    c.SaveAs(plotsoutputpath + "/Cov_{vr}_{t}{lodefid}{lodenorm}.png" .format(vr = var, t = ty, lodefid = "fid" * (fidornot), lodenorm = "bin" * (binornot)))
    c.SaveAs(plotsoutputpath + "/Cov_{vr}_{t}{lodefid}{lodenorm}.pdf" .format(vr = var, t = ty, lodefid = "fid" * (fidornot), lodenorm = "bin" * (binornot)))
    c.SaveAs(plotsoutputpath + "/Cov_{vr}_{t}{lodefid}{lodenorm}.eps" .format(vr = var, t = ty, lodefid = "fid" * (fidornot), lodenorm = "bin" * (binornot)))
    c.SaveAs(plotsoutputpath + "/Cov_{vr}_{t}{lodefid}{lodenorm}.root".format(vr = var, t = ty, lodefid = "fid" * (fidornot), lodenorm = "bin" * (binornot)))
    c.Close(); tfile.Close()
    del c, nominal, tfile, varMat, finalmat, binning
    return


if __name__=="__main__":
    parser = argparse.ArgumentParser(usage = "python nanoAOD_checker.py [options]", description = "Checker tool for the outputs of nanoAOD production (NOT postprocessing)", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--inpath',    '-i', metavar = 'inpath',     dest = "inpath",   required = False, default = "./temp/differential")
    parser.add_argument('--year',      '-y', metavar = 'year',       dest = "year",     required = False, default = "all")
    parser.add_argument('--variable',  '-v', metavar = 'variable',   dest = "variable", required = False, default = "all")
    parser.add_argument('--extraArgs', '-e', metavar = 'extra',      dest = "extra",    required = False, default = "")
    parser.add_argument('--nthreads',  '-j', metavar = 'nthreads',   dest = "nthreads", required = False, default = 0, type = int)
    parser.add_argument('--pretend',   '-p', action  = "store_true", dest = "pretend",  required = False, default = False)
    parser.add_argument('--notFiduFile', '-nf', action  = "store_true", dest = "notfidufile", required = False, default = False)

    args     = parser.parse_args()
    year     = args.year
    extra    = args.extra
    nthreads = args.nthreads
    pretend  = args.pretend
    inpath   = args.inpath
    variable = args.variable
    notFiduFile = args.notfidufile

    #### First, find the tasks
    tasks = []
    if year == "all":
        if variable == "all":
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

            for iY in theyears:
                thevars = next(os.walk(inpath + "/" + iY))[1]
                for iV in thevars:
                    if "plots" in iV or "Fiducial" in iV or "table" in iV or "response" in iV: continue
                    #if iY != "run2": continue

                    #for t in ["detector", "particle", "particlefid", "particlebin", "particlefidbin"]:
                    for t in ["particle", "particlefidbin"]:
                    #for t in ["particlefidbin"]:
                        tasks.append( (inpath, iY, iV, t, notFiduFile) )

    vl.SetUpWarnings()
    if nthreads > 1:
        pool = Pool(nthreads)
        pool.map(printCovarianceMatrix, tasks)
        pool.close()
        pool.join()
        del pool
    else:
        for tsk in tasks:
            printCovarianceMatrix(tsk)
