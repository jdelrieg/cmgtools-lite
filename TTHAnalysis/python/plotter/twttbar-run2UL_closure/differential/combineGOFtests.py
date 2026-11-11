import os, sys, enum, argparse
from multiprocessing import Pool
import warnings as wr
import ROOT as r
r.PyConfig.IgnoreCommandLineOptions = True
r.gROOT.SetBatch(True)
sys.path.append('{cmsswpath}/src/CMGTools/TTHAnalysis/python/plotter/tw-run2/differential/'.format(cmsswpath = os.environ['CMSSW_BASE']))
from . import varList as vl

gofcomm = "combineTool.py -M GoodnessOfFit --expectSignal 1 {combcard} -n {y}_{r} --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=5000000 --algo=saturated {preorpost} {tois} {nthreads} {queue}"

slurmscaff = 'sbatch {extraS} -p {queue} -J {jobname} -e {logpath}/log.%j.%x.err -o {logpath}/log.%j.%x.out --wrap "{command}"'

haddcomm      = "hadd {out} {inputs}"


nToysPerChunk = 200
nToysPerJob   = 20
nThreshold    = 1000


def doSomeToysForMePlease(tsk):
    thei, gofoutpath, combcard_, extra, year, region, toistodo, doPost, verbose, pretend = tsk

    comm = "cd " + gofoutpath + "; " +  gofcomm.format(combcard  = combcard_,
        extra     = extra,
        y         = year,
        r         = region + "_toy{i}".format(i = thei) if "," not in region else region.replace(",", "") + "_toy{i}".format(i = thei),
        tois      = "-t " + str(toistodo) + " -s -1",
        nthreads  = "",
        queue     = "",
        preorpost = "--fixedSignalStrength=1" if not doPost else "--toysFreq") + "; " + "cd -"

    if verbose:
        print("Toys GOF command:", comm, "\n")

    if not pretend:
        outstat = os.system(comm)
        if outstat:
            raise RuntimeError("FATAL: Combine failed to execute for year {y} and region(s) {r} during the nominal GOF test fit execution.".format(y = year, r = region))

    return


def makeGOF(task):
    year, thevar, inpath, verbose, pretend, extra, doPost, nth, nToys, theQ, Eslurm = task
    fitoutpath = inpath + "/" + year + "/" + thevar + "/sigextr_fit_combine/"
    gofoutpath = fitoutpath + "/GOF{p}_{y}_{r}".format(y = year, r = thevar, p = "" if not doPost else "post")
    if not os.path.isdir(gofoutpath):
        os.system("mkdir -p " + gofoutpath)

    combcard_ = "../bincards/card_{r}.txt".format(r = thevar)


    if not theQ:
        comm = "cd " + gofoutpath + "; " +  gofcomm.format(combcard  = combcard_,
                              extra     = extra,
                              y         = year,
                              r         = thevar,
                              tois      = "",
                              nthreads  = "",
                              queue     = "",
                              preorpost = "--fixedSignalStrength=1" if not doPost else "") + "; " + "cd -"
        if verbose:
            print("Nominal GOF command:", comm, "\n")

        if not pretend:
            outstat = os.system(comm)
            if outstat:
                raise RuntimeError("FATAL: Combine failed to execute for year {y} and region(s) {r} during the nominal GOF test fit execution.".format(y = year, r = region))

        nToyChunks = nToys // nToysPerJob
        tmptasks = []
        for i in range(nToyChunks):
            tmptasks.append( (i, gofoutpath, combcard_, extra, year, thevar, nToysPerJob if i != nToyChunks - 1 else nToys - nToysPerJob * (nToyChunks - 1), doPost, verbose, pretend) )

        if nth > 1:
            pool = Pool(nth)
            pool.map(doSomeToysForMePlease, tmptasks)
            pool.close()
            pool.join()
            del pool
        else:
            for el in tmptasks:
                doSomeToysForMePlease(el)

        #comm = "cd " + gofoutpath + "; " +  gofcomm.format(combcard  = combcard_,
                              #extra     = extra,
                              #y         = year,
                              #r         = thevar,
                              #tois      = "",
                              #nthreads  = "--parallel " + str(nth) if nth else "",
                              #queue     = "--job-mode slurm --task-name CMGTGOFnom_{y}_{r}".format(y = year, r = thevar) if theQ else "",
                              #preorpost = "--fixedSignalStrength=1" if not doPost else "") + "; " + "cd -"
        #if verbose:
            #print "Nominal GOF command:", comm, "\n"

        #if not pretend:
            #outstat = os.system(comm)
            #if outstat:
                #raise RuntimeError("FATAL: Combine failed to execute for year {y} and variable {r} during the nominal GOF test fit execution.".format(y = year, r = thevar))


        #comm = "cd " + gofoutpath + "; " +  gofcomm.format(combcard  = combcard_,
                              #extra     = extra,
                              #y         = year,
                              #r         = thevar + "_toy",
                              #tois      = "-t " + str(nToys),
                              #nthreads  = "--parallel " + str(nth) if nth else "",
                              #queue     = "--job-mode slurm --task-name CMGTGOFtoys_{y}_{r}".format(y = year, r = thevar) if theQ else "",
                              #preorpost = "--fixedSignalStrength=1" if not doPost else "--toysFreq") + "; " + "cd -"

        #if verbose:
            #print "Toys GOF command:", comm, "\n"

        #if not pretend:
            #outstat = os.system(comm)
            #if outstat:
                #raise RuntimeError("FATAL: Combine failed to execute for year {y} and variable {r} during the nominal GOF test fit execution.".format(y = year, r = thevar))
    else:
        logpath = gofoutpath + "/slurmlogs"
        if not os.path.isdir(logpath):
            os.system("mkdir -p " + logpath)

        if not nth:
            comm = gofcomm.format(combcard  = combcard_,
                                extra       = extra,
                                y           = year,
                                r           = thevar,
                                tois        = "",
                                nthreads    = "",
                                queue       = "",
                                preorpost   = "--fixedSignalStrength=1" if not doPost else "")

            slcomm = "cd " + gofoutpath + "; " + slurmscaff.format(extraS  = Eslurm,
                                                                   queue   = queue,
                                                                   jobname = "CMGTGOFnom_{y}_{r}".format(y = year, r = thevar),
                                                                   logpath = "./slurmlogs",
                                                                   command = comm) + "; " + "cd -"

            if verbose:
                print("Nominal GOF command:", slcomm, "\n")

            if not pretend:
                outstat = os.system(slcomm)
                if outstat:
                    raise RuntimeError("FATAL: Combine failed to execute for year {y} and variable {r} during the nominal GOF test fit execution.".format(y = year, r = thevar))

            comm = gofcomm.format(combcard  = combcard_,
                                  extra     = extra,
                                  y         = year,
                                  r         = thevar + "_toy{i}",
                                  tois      = "-t {ntois} -s -1",
                                  nthreads  = "",
                                  queue     = "",
                                  preorpost = "--fixedSignalStrength=1" if not doPost else "--toysFreq")


            if nToys < nThreshold:
                for i in range(nToys):                     #### TODO: paralelizar
                    slcomm = "cd " + gofoutpath + "; " +  slurmscaff.format(extraS  = Eslurm,
                                                                            queue   = queue,
                                                                            jobname = "CMGTGOFtoys_{y}_{r}_{i}".format(y = year, r = thevar, i = i),
                                                                            logpath = "./slurmlogs",
                                                                            command = comm.format(i = i, ntois = 1)) + "; " + "cd -"
                    if verbose:
                        print("Toys GOF command:", slcomm, "\n")

                    if not pretend:
                        outstat = os.system(slcomm)
                        if outstat:
                            raise RuntimeError("FATAL: Combine failed to execute for year {y} and variable {r} during the nominal GOF test fit execution.".format(y = year, r = thevar))
            else:
                nToyChunks = nToys // nToysPerChunk
                for i in range(nToyChunks):                     #### TODO: paralelizar
                    slcomm = "cd " + gofoutpath + "; " +  slurmscaff.format(extraS  = Eslurm,
                                                                            queue   = queue,
                                                                            jobname = "CMGTGOFtoys_{y}_{r}_{i}".format(y = year, r = thevar, i = i),
                                                                            logpath = "./slurmlogs",
                                                                            command = comm.format(i = i, ntois = nToysPerChunk if i != nToyChunks - 1 else nToys - nToysPerChunk * (nToyChunks - 1))) + "; " + "cd -"
                    if verbose:
                        print("Toys GOF command:", slcomm, "\n")

                    if not pretend:
                        outstat = os.system(slcomm)
                        if outstat:
                            raise RuntimeError("FATAL: Combine failed to execute for year {y} and variable {r} during the nominal GOF test fit execution.".format(y = year, r = thevar))


        else:
            comm = gofcomm.format(combcard  = combcard_,
                                extra       = extra,
                                y           = year,
                                r           = thevar,
                                tois        = "",
                                nthreads    = "",
                                queue       = "",
                                preorpost   = "--fixedSignalStrength=1" if not doPost else "")

            slcomm = "cd " + gofoutpath + "; " + slurmscaff.format(extraS  = Eslurm,
                                                                   queue   = queue,
                                                                   jobname = "CMGTGOFnom_{y}_{r}".format(y = year, r = thevar),
                                                                   logpath = "./slurmlogs",
                                                                   command = comm) + "; " + "cd -"

            if verbose:
                print("Nominal GOF command:", slcomm, "\n")

            if not pretend:
                outstat = os.system(slcomm)
                if outstat:
                    raise RuntimeError("FATAL: Combine failed to execute for year {y} and variable {r} during the nominal GOF test fit execution.".format(y = year, r = thevar))

            comm = gofcomm.format(combcard  = combcard_,
                                  extra     = extra,
                                  y         = year,
                                  r         = thevar,
                                  tois      = "-t " + str(nToys),
                                  nthreads  = "--parallel " + str(nth),
                                  queue     = "",
                                  preorpost = "--fixedSignalStrength=1" if not doPost else "--toysFreq")


            slcomm = "cd " + gofoutpath + "; " + slurmscaff.format(extraS  = Eslurm,
                                    queue   = queue,
                                    jobname = "CMGTGOFtoys_{y}_{r}".format(y = year, r = thevar),
                                    logpath = "./slurmlogs",
                                    command = comm) + "; " + "cd -"
            if verbose:
                print("Toys GOF command:", slcomm, "\n")

            if not pretend:
                outstat = os.system(slcomm)
                if outstat:
                    raise RuntimeError("FATAL: Combine failed to execute for year {y} and variable {r} during the nominal GOF test fit execution.".format(y = year, r = thevar))
    return


def makeGOFplot(task):
    year, thevar, inpath, verbose, pretend, extra, doPost = task
    fitoutpath = inpath + "/" + year + "/" + thevar + "/sigextr_fit_combine/"
    gofoutpath = fitoutpath + "/GOF{p}_{y}_{r}".format(y = year, r = thevar, p = "" if not doPost else "post")
    if not os.path.isdir(gofoutpath):
        raise RuntimeError("FATAL: no present GOF folder for given parameters.")

    thefiles = os.listdir(gofoutpath)
    if "higgsCombine{y}_{r}.GoodnessOfFit.mH120.root".format(y = year, r = thevar) not in thefiles:
        raise RuntimeError("FATAL: no nominal fit found. Plot cannot be made!")

    if "higgsCombine{y}_{r}_toy.GoodnessOfFit.mH120.root".format(y = year, r = thevar) not in thefiles:
        comm = "cd " + gofoutpath + "; " + haddcomm.format(inputs = "higgsCombine{y}_{r}_toy*.GoodnessOfFit.mH120.*.root".format(y = year, r = thevar),
                                                           out    = "higgsCombine{y}_{r}_toy.GoodnessOfFit.mH120.root".format(y = year, r = thevar)) + "; " + "cd -"

        if verbose:
            print("Merging command:", comm, "\n")

        if not pretend:
            outstat = os.system(comm)
            if outstat:
                raise RuntimeError("FATAL: merge of toys' files for year {y} and variable {r} failed.".format(y = year, r = thevar))


    r.gStyle.SetOptStat(0)

    inpData = r.TFile(gofoutpath + "/higgsCombine{y}_{r}.GoodnessOfFit.mH120.root".format(y = year, r = thevar),     "READ")
    inptoys = r.TFile(gofoutpath + "/higgsCombine{y}_{r}_toy.GoodnessOfFit.mH120.root".format(y = year, r = thevar), "READ")

    tData = inpData.Get("limit")
    tToys = inptoys.Get("limit")

    c = r.TCanvas("c" ,"c" , 800, 600)

    valToys = []
    valData = 0.

    for ev in tData:
        valData = ev.limit

    up   = 0.
    down = 0.

    for ev in tToys:
        valToys.append(ev.limit)
        if ev.limit >= valData:
            up += 1
        else:
            down +=1

    minX = min(0., min(valToys))
    maxX = min(max(valToys), sorted(valToys)[len(valToys)/2] * 4) # To avoid skewing for exta high values

    if valData > maxX * 0.9: maxX = valData * 1.1

    hToys = r.TH1F("hToys", "hToys", 100, minX, maxX)

    for v in valToys: hToys.Fill(v)

    hToys.SetLineColor(r.kBlue)
    hToys.GetXaxis().SetTitle("Saturated test statistic (adim.)")
    hToys.GetYaxis().SetTitle("# toys (adim.)")
    hToys.SetTitle(("Pre-fit GOF test" if not doPost else "Post-fit GOF test") + " - {y} - {r}".format(y = year, r = thevar))
    hToys.Draw("hist")

    lineData = r.TLine(valData, 0, valData, hToys.GetMaximum() * 1.05)
    lineData.Draw("same")

    tl = r.TLegend(0.65, 0.6, 0.85, 0.85)
    tl.SetHeader("p-value = %1.4f"%(up / ((up + down)*1.)))
    tl.AddEntry(hToys,    "Toys (# = {n})".format(n = tToys.GetEntries()), "f")
    tl.AddEntry(lineData, "Data", "l")
    tl.Draw("same")

    if not os.path.isdir(gofoutpath + "/plots"):
        os.system("mkdir -p " + gofoutpath + "/plots")

    c.SaveAs(gofoutpath + "/plots/GOF{p}_{y}_{r}.png".format(y = year, r = thevar, p = "" if not doPost else "post"))
    c.SaveAs(gofoutpath + "/plots/GOF{p}_{y}_{r}.pdf".format(y = year, r = thevar, p = "" if not doPost else "post"))
    c.Close(); del c
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage = "python nanoAOD_checker.py [options]", description = "Checker tool for the outputs of nanoAOD production (NOT postprocessing)", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--year',           '-y',  metavar = 'year',        dest = "year",         required = False, default = "2016")
    parser.add_argument('--extraArgs',      '-e',  metavar = 'extra',       dest = "extra",        required = False, default = "")
    parser.add_argument('--nthreads',       '-j',  metavar = 'nthreads',    dest = "nthreads",     required = False, default = 0, type = int)
    parser.add_argument('--pretend',        '-p',  action  = "store_true",  dest = "pretend",      required = False, default = False)
    parser.add_argument('--inpath',         '-i',  metavar = 'inpath ',     dest = "inpath",       required = False, default = "./temp/cards")
    parser.add_argument('--queue',          '-q',  metavar = 'queue',       dest = "queue",        required = False, default = None)
    parser.add_argument('--verbose',        '-V',  action  = "store_true",  dest = "verbose",      required = False, default = False)
    parser.add_argument('--nToys',          '-nT', metavar = 'ntoys',       dest = "ntoys",        required = False, default = 100, type = int)
    parser.add_argument('--gofpostfit',     '-gF', action  = "store_true",  dest = "gofpostfit",   required = False, default = False) #Option to make gof test
    parser.add_argument('--gofplot',        '-gH', action  = "store_true",  dest = "gofhisto",     required = False, default = False) #Option to make gof test
    parser.add_argument('--extraSlurmArgs', '-eS', metavar = 'extraslurm',  dest = "extraslurm",   required = False, default = "")
    parser.add_argument('--variable',       '-v',  metavar = 'variable',    dest = "variable",     required = False, default = "all")

    args     = parser.parse_args()
    year     = args.year
    extra    = args.extra
    extraslurm=args.extraslurm
    nthreads = args.nthreads
    pretend  = args.pretend
    inpath   = args.inpath
    queue    = args.queue
    verbose  = args.verbose
    nts      = args.ntoys
    gofpost  = args.gofpostfit
    gofhisto = args.gofhisto


    theyears = ["2016", "2017", "2018", "run2"]
    tasks    = []


    if year.lower() != "all":
        if "," in year:
            theyears = year.split(",")
        else:
            theyears = [ year ]

    if not gofhisto:
        for iY in theyears:
            thevars = next(os.walk(inpath + "/" + iY))[1]
            for iV in thevars:
                if any([el in iV for el in vl.vetolist]): continue
                if not os.path.isdir(inpath + "/" + iY + "/" + iV + "/sigextr_fit_combine"): continue
                tasks.append( (iY, iV, inpath, verbose, pretend, extra, gofpost, nthreads, nts, queue, extraslurm) )

        for task in tasks:
            if verbose: print("\nProcessing " + str(task) + "\n")
            makeGOF(task)
    else:
        for iY in theyears:
            thevars = next(os.walk(inpath + "/" + iY))[1]
            for iV in thevars:
                if any([el in iV for el in vl.vetolist]): continue
                tasks.append( (iY, iV, inpath, verbose, pretend, extra, gofpost) )

        for task in tasks:
            if verbose: print("\nProcessing " + str(task) + "\n")
            makeGOFplot(task)



