from copy import deepcopy
import os, sys, argparse

sys.path.append('{cmsswpath}/src/CMGTools/TTHAnalysis/python/plotter/twttbar-run2/differential/'.format(cmsswpath = os.environ['CMSSW_BASE']))
import beautifulUnfoldingPlots as bp
import errorPropagator as ep
import varList as vl
from multiprocessing import Pool

#basecommand = 'combineTool.py -M MultiDimFit {algosettings} --setParameters {setpars} --rMin 0 --rMax 2 --floatOtherPOIs=1 -m 125 --split-points 1 --saveInactivePOI 1 {parallel} {queue} {extra} --robustFit 1 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=5000000'
#basecommand = 'combineTool.py -M MultiDimFit {algosettings} --setParameters {setpars}  --split-points 1 --saveInactivePOI 1 {parallel} {queue} {extra} --robustFit 1 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=5000000'
#basecommand = 'combineTool.py -M MultiDimFit {algosettings} --setParameters {setpars} --split-points 1 --floatOtherPOIs=1 --saveInactivePOI 1 {parallel} {queue} {extra} --robustFit 1 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=5000000 --setParameterRanges {minmaxlist} --squareDistPoiStep --autoRange 2 -m 125'

# basecommand = 'combine -M FitDiagnostics -m 125 --setParameters {setpars} --saveWorkspace --saveShapes --saveWithUncertainties --robustFit 1 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=5000000 --setParameterRanges {minmaxlist} {extra}'
#basecommand = 'combine -M FitDiagnostics -m 125 --setParameters {setpars} --saveWorkspace --saveShapes --saveWithUncertainties --robustFit 1 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=5000000 {extra}'
basecommand = 'combine -M FitDiagnostics  -m 125 --setParameters {setpars} --saveWorkspace --saveShapes --saveWithUncertainties --robustFit 1 --cminDefaultMinimizerStrategy 0 --X-rtd MINIMIZER_analytic --X-rtd MINIMIZER_MaxCalls=5000000 --robustHesse 1 {extra}'

userstorage = "/pool/phedex/userstorage/asoto/Proyectos/twttbar_run2/misc/"
userstorage = "/pool/phedex/userstorage/jriego/nanoAODv9/bb4l/productions/2025-12-23/misc/"




individual_scaff_closesttoATLAS = {
    #### Statistical
    'mc_stat' : [],

    #### Systematic
    # Experimental
    'leptons_met' : [
        "unclenergy_2016",
        "unclenergy_2017",
        "unclenergy_2018",   
        "muonen_2016",
        "muonen_2017",
        "muonen_2018",         
        "elecidsf",
        "elecrecosf",
        "elecsigma",
        "elecscale",
        #"muonidsf_stat_2016apv",
        "muonidsf_stat_2016",
        "muonidsf_stat_2017",
        "muonidsf_stat_2018",
        "muonidsf_syst",
        "muonisosf_stat_2016apv",
        "muonisosf_stat_2016",
        "muonisosf_stat_2017",
        "muonisosf_stat_2018",
        "muonisosf_syst",
    
    ],

    'lumi_trigger' : [
        "triggereff_2016apv",
        "triggereff_2016",
        "triggereff_2017",
        "triggereff_2018",  
        "lumi_13TeV_1516_l",
        "lumi_13TeV_151617_l",
        "lumi_13TeV_15161718_l",        
    
    ],

    'flavour_tagging' : [
        "btagging_2016apv",
        "btagging_2016",
        "btagging_2017",
        "btagging_2018",
        "btagging_corr",
        "mistagging_2016apv",
        "mistagging_2016",
        "mistagging_2017",
        "mistagging_2018",
        "mistagging_corr",       
    
    ],

    'jets': [
#        "jes",
        "jes_HF",
        #"jes_HF_2016apv",
        "jes_HF_2016",
        "jes_HF_2017",
        "jes_HF_2018",
        "jes_BBEC1",
        #"jes_BBEC1_2016apv",
        "jes_BBEC1_2016",
        "jes_BBEC1_2017",
        "jes_BBEC1_2018",
        "jes_FlavorQCD",
        #"jes_RelativeSample_2016apv",
        "jes_RelativeSample_2016",
        "jes_RelativeSample_2017",
        "jes_RelativeSample_2018",
        "jes_EC2",
        #"jes_EC2_2016apv",
        "jes_EC2_2016",
        "jes_EC2_2017",
        "jes_EC2_2018",
        "jes_RelativeBal",
        "jes_Absolute",
        #"jes_Absolute_2016apv",
        "jes_Absolute_2016",
        "jes_Absolute_2017",
        "jes_Absolute_2018",

        #"jer_2016apv",
        "jer_2016",
        "jer_2017",
        "jer_2018",
        "jetpuid_2016apv",
        "jetpuid_2016",
        "jetpuid_2017",
        "jetpuid_2018",


        "pileup",



        "prefiring_2016",
        "prefiring_2017",
        #"unclenergy",
    ],

    'normalisation' : [
        "nonworz_norm",
        "dy_norm",
        "vvttv_norm",
        "nonfiducial_norm",
    ],

    # Modelling
    'generator_params' : [
        "bb4l_pdf1","bb4l_pdf2","bb4l_pdf3","bb4l_pdf4","bb4l_pdf5","bb4l_pdf6","bb4l_pdf7","bb4l_pdf8","bb4l_pdf9","bb4l_pdf10","bb4l_pdf11","bb4l_pdf12","bb4l_pdf13","bb4l_pdf14","bb4l_pdf15","bb4l_pdf16","bb4l_pdf17","bb4l_pdf18","bb4l_pdf19","bb4l_pdf20","bb4l_pdf21","bb4l_pdf22","bb4l_pdf23","bb4l_pdf24","bb4l_pdf25","bb4l_pdf26","bb4l_pdf27","bb4l_pdf28","bb4l_pdf29","bb4l_pdf30","bb4l_pdf31","bb4l_pdf32","bb4l_pdf33","bb4l_pdf34","bb4l_pdf35","bb4l_pdf36","bb4l_pdf37","bb4l_pdf38","bb4l_pdf39","bb4l_pdf40","bb4l_pdf41","bb4l_pdf42","bb4l_pdf43","bb4l_pdf44","bb4l_pdf45","bb4l_pdf46","bb4l_pdf47","bb4l_pdf48","bb4l_pdf49","bb4l_pdf50","bb4l_pdf51","bb4l_pdf52","bb4l_pdf53","bb4l_pdf54","bb4l_pdf55","bb4l_pdf56","bb4l_pdf57","bb4l_pdf58","bb4l_pdf59","bb4l_pdf60","bb4l_pdf61","bb4l_pdf62","bb4l_pdf63","bb4l_pdf64","bb4l_pdf65","bb4l_pdf66","bb4l_pdf67","bb4l_pdf68","bb4l_pdf69","bb4l_pdf70","bb4l_pdf71","bb4l_pdf72","bb4l_pdf73","bb4l_pdf74","bb4l_pdf75","bb4l_pdf76","bb4l_pdf77","bb4l_pdf78","bb4l_pdf79","bb4l_pdf80","bb4l_pdf81","bb4l_pdf82","bb4l_pdf83","bb4l_pdf84","bb4l_pdf85","bb4l_pdf86","bb4l_pdf87","bb4l_pdf88","bb4l_pdf89","bb4l_pdf90","bb4l_pdf91","bb4l_pdf92","bb4l_pdf93","bb4l_pdf94","bb4l_pdf95","bb4l_pdf96","bb4l_pdf97","bb4l_pdf98","bb4l_pdf99","bb4l_pdf100","bb4l_pdf101","bb4l_pdf102",
    #    "ttbar_matching",
        "scales_muR",
        "scales_muF",
        "isr",
        "fsr",

        "underlying_event",
        "colour_rec_cr1",
        "colour_rec_cr2",
        "colour_rec_erdon",
        "colour_rec_single",
        "bb4l_topmass",
        "hdamp",
    ],

    'generators' : [
        "non_closure",
        "nonfiducial_modelling",
    ],


}


individual_scaff = {
    #### Statistical
    'mc_stat' : [],

    #### Systematic
    # Experimental




    'flavour_tagging' : [
        "btagging_2016apv",
        "btagging_2016",
        "btagging_2017",
        "btagging_2018",
        "btagging_corr",
        "mistagging_2016apv",
        "mistagging_2016",
        "mistagging_2017",
        "mistagging_2018",
        "mistagging_corr",       
    
    ],

    'other_experimental': [ #jets, lumi trigger leptons met
#        "jes",
        "jes_HF",
        #"jes_HF_2016apv",
        "jes_HF_2016",
        "jes_HF_2017",
        "jes_HF_2018",
        "jes_BBEC1",
        #"jes_BBEC1_2016apv",
        "jes_BBEC1_2016",
        "jes_BBEC1_2017",
        "jes_BBEC1_2018",
        "jes_FlavorQCD",
        #"jes_RelativeSample_2016apv",
        "jes_RelativeSample_2016",
        "jes_RelativeSample_2017",
        "jes_RelativeSample_2018",
        "jes_EC2",
        #"jes_EC2_2016apv",
        "jes_EC2_2016",
        "jes_EC2_2017",
        "jes_EC2_2018",
        "jes_RelativeBal",
        "jes_Absolute",
        #"jes_Absolute_2016apv",
        "jes_Absolute_2016",
        "jes_Absolute_2017",
        "jes_Absolute_2018",

        #"jer_2016apv",
        "jer_2016",
        "jer_2017",
        "jer_2018",
        "jetpuid_2016apv",
        "jetpuid_2016",
        "jetpuid_2017",
        "jetpuid_2018",


        "pileup",



        "prefiring_2016",
        "prefiring_2017",
        #"unclenergy",
        "triggereff_2016apv",
        "triggereff_2016",
        "triggereff_2017",
        "triggereff_2018",  
        "lumi_13TeV_1516_l",
        "lumi_13TeV_151617_l",
        "lumi_13TeV_15161718_l",    
        "unclenergy_2016",
        "unclenergy_2017",
        "unclenergy_2018",   
        "muonen_2016",
        "muonen_2017",
        "muonen_2018",         
        "elecidsf",
        "elecrecosf",
        "elecsigma",
        "elecscale",
        #"muonidsf_stat_2016apv",
        "muonidsf_stat_2016",
        "muonidsf_stat_2017",
        "muonidsf_stat_2018",
        "muonidsf_syst",
        "muonisosf_stat_2016apv",
        "muonisosf_stat_2016",
        "muonisosf_stat_2017",
        "muonisosf_stat_2018",
        "muonisosf_syst",     
        "nonworz_norm", "dy_norm","vvttv_norm","nonfiducial_norm",          
    ],

    #'normalisation' : ["nonworz_norm", "dy_norm","vvttv_norm","nonfiducial_norm"],

    # Modelling
    'generator_params' : [
        "bb4l_pdf1","bb4l_pdf2","bb4l_pdf3","bb4l_pdf4","bb4l_pdf5","bb4l_pdf6","bb4l_pdf7","bb4l_pdf8","bb4l_pdf9","bb4l_pdf10","bb4l_pdf11","bb4l_pdf12","bb4l_pdf13","bb4l_pdf14","bb4l_pdf15","bb4l_pdf16","bb4l_pdf17","bb4l_pdf18","bb4l_pdf19","bb4l_pdf20","bb4l_pdf21","bb4l_pdf22","bb4l_pdf23","bb4l_pdf24","bb4l_pdf25","bb4l_pdf26","bb4l_pdf27","bb4l_pdf28","bb4l_pdf29","bb4l_pdf30","bb4l_pdf31","bb4l_pdf32","bb4l_pdf33","bb4l_pdf34","bb4l_pdf35","bb4l_pdf36","bb4l_pdf37","bb4l_pdf38","bb4l_pdf39","bb4l_pdf40","bb4l_pdf41","bb4l_pdf42","bb4l_pdf43","bb4l_pdf44","bb4l_pdf45","bb4l_pdf46","bb4l_pdf47","bb4l_pdf48","bb4l_pdf49","bb4l_pdf50","bb4l_pdf51","bb4l_pdf52","bb4l_pdf53","bb4l_pdf54","bb4l_pdf55","bb4l_pdf56","bb4l_pdf57","bb4l_pdf58","bb4l_pdf59","bb4l_pdf60","bb4l_pdf61","bb4l_pdf62","bb4l_pdf63","bb4l_pdf64","bb4l_pdf65","bb4l_pdf66","bb4l_pdf67","bb4l_pdf68","bb4l_pdf69","bb4l_pdf70","bb4l_pdf71","bb4l_pdf72","bb4l_pdf73","bb4l_pdf74","bb4l_pdf75","bb4l_pdf76","bb4l_pdf77","bb4l_pdf78","bb4l_pdf79","bb4l_pdf80","bb4l_pdf81","bb4l_pdf82","bb4l_pdf83","bb4l_pdf84","bb4l_pdf85","bb4l_pdf86","bb4l_pdf87","bb4l_pdf88","bb4l_pdf89","bb4l_pdf90","bb4l_pdf91","bb4l_pdf92","bb4l_pdf93","bb4l_pdf94","bb4l_pdf95","bb4l_pdf96","bb4l_pdf97","bb4l_pdf98","bb4l_pdf99","bb4l_pdf100","bb4l_pdf101","bb4l_pdf102",
    #    "ttbar_matching",
        "scales_muR",
        "scales_muF",
        "isr",
        "fsr",

        "underlying_event",
        "colour_rec_cr1",
        "colour_rec_cr2",
        "colour_rec_erdon",
        "colour_rec_single",
        "bb4l_topmass",
        "hdamp",
    ],

    'generators' : [
        "non_closure",
        "nonfiducial_modelling",
    ],


}


global_scaff = {
   'systematics': [
        "jes_HF",
        "jes_HF_2016",
        "jes_HF_2017",
        "jes_HF_2018",
        "jes_BBEC1",
        "jes_BBEC1_2016",
        "jes_BBEC1_2017",
        "jes_BBEC1_2018",
        "jes_FlavorQCD",
        "jes_RelativeSample_2016",
        "jes_RelativeSample_2017",
        "jes_RelativeSample_2018",
        "jes_EC2",
        "jes_EC2_2016",
        "jes_EC2_2017",
        "jes_EC2_2018",
        "jes_RelativeBal",
        "jes_Absolute",
        "jes_Absolute_2016",
        "jes_Absolute_2017",
        "jes_Absolute_2018",
        "jer_2016",
        "jer_2017",
        "jer_2018",
        "jetpuid_2016apv",
        "jetpuid_2016",
        "jetpuid_2017",
        "jetpuid_2018",
        #"unclenergy",
        "muonen_2016",
        "muonen_2017",
        "muonen_2018",
        "triggereff_2016apv",
        "triggereff_2016",
        "triggereff_2017",
        "triggereff_2018",
        "pileup",
        "elecidsf",
        "elecrecosf",
        #"muonidsf_stat_2016apv",
        "muonidsf_stat_2016",
        "muonidsf_stat_2017",
        "muonidsf_stat_2018",
        "muonidsf_syst",
        "muonisosf_stat_2016apv",
        "muonisosf_stat_2016",
        "muonisosf_stat_2017",
        "muonisosf_stat_2018",
        "muonisosf_syst",
        "btagging_2016apv",
        "btagging_2016",
        "btagging_2017",
        "btagging_2018",
        "btagging_corr",
        "mistagging_2016apv",
        "mistagging_2016",
        "mistagging_2017",
        "mistagging_2018",
        "mistagging_corr",
        "prefiring_2016",
        "prefiring_2017",
        "elecsigma",
        "elecscale",
        "nonworz_norm",
        "dy_norm",
        "vvttv_norm",
        "bb4l_pdf1","bb4l_pdf2","bb4l_pdf3","bb4l_pdf4","bb4l_pdf5","bb4l_pdf6","bb4l_pdf7","bb4l_pdf8","bb4l_pdf9","bb4l_pdf10","bb4l_pdf11","bb4l_pdf12","bb4l_pdf13","bb4l_pdf14","bb4l_pdf15","bb4l_pdf16","bb4l_pdf17","bb4l_pdf18","bb4l_pdf19","bb4l_pdf20","bb4l_pdf21","bb4l_pdf22","bb4l_pdf23","bb4l_pdf24","bb4l_pdf25","bb4l_pdf26","bb4l_pdf27","bb4l_pdf28","bb4l_pdf29","bb4l_pdf30","bb4l_pdf31","bb4l_pdf32","bb4l_pdf33","bb4l_pdf34","bb4l_pdf35","bb4l_pdf36","bb4l_pdf37","bb4l_pdf38","bb4l_pdf39","bb4l_pdf40","bb4l_pdf41","bb4l_pdf42","bb4l_pdf43","bb4l_pdf44","bb4l_pdf45","bb4l_pdf46","bb4l_pdf47","bb4l_pdf48","bb4l_pdf49","bb4l_pdf50","bb4l_pdf51","bb4l_pdf52","bb4l_pdf53","bb4l_pdf54","bb4l_pdf55","bb4l_pdf56","bb4l_pdf57","bb4l_pdf58","bb4l_pdf59","bb4l_pdf60","bb4l_pdf61","bb4l_pdf62","bb4l_pdf63","bb4l_pdf64","bb4l_pdf65","bb4l_pdf66","bb4l_pdf67","bb4l_pdf68","bb4l_pdf69","bb4l_pdf70","bb4l_pdf71","bb4l_pdf72","bb4l_pdf73","bb4l_pdf74","bb4l_pdf75","bb4l_pdf76","bb4l_pdf77","bb4l_pdf78","bb4l_pdf79","bb4l_pdf80","bb4l_pdf81","bb4l_pdf82","bb4l_pdf83","bb4l_pdf84","bb4l_pdf85","bb4l_pdf86","bb4l_pdf87","bb4l_pdf88","bb4l_pdf89","bb4l_pdf90","bb4l_pdf91","bb4l_pdf92","bb4l_pdf93","bb4l_pdf94","bb4l_pdf95","bb4l_pdf96","bb4l_pdf97","bb4l_pdf98","bb4l_pdf99","bb4l_pdf100","bb4l_pdf101","bb4l_pdf102",
        #"ttbar_matching",
        "scales_muR",
        "scales_muF",
        "isr",
        "fsr",
        "non_closure",
        "nonfiducial_modelling",
        "nonfiducial_norm",
        "underlying_event",
        "colour_rec_cr1",
        "colour_rec_cr2",
        "colour_rec_erdon",
        "colour_rec_single",
        "bb4l_topmass",
        "hdamp",        
        #"colour_rec_erdon",
        #"colour_rec_cr1",
        #"colour_rec_cr2",
        #"ue",
        #"topptrew",
        #"mtop",
        #"ds",
        "lumi_13TeV_1516_l",
        "lumi_13TeV_151617_l",
        "lumi_13TeV_15161718_l",
   ],
}


def getBestFitParsValue(thefile):
    outdict = {}
    with open(thefile, "r") as f:
        for line in f:
            splits = line.strip().replace(" ", "").split(":")
            outdict[splits[0]] = splits[1:]
    return outdict


def doMeThisFitPlease(task):
    outpath, thecard, tmpfreeze, thegoodvalsdict, pois, gr, redo, pretend = task
    #print tmpfreeze
    if not os.path.isfile(outpath + "/higgsCombine{g}.FitDiagnostics.mH125.root".format(g = gr)) or redo:
        thecomm = basecommand.format(setpars     = ",".join([el + "=1" for el in pois] + [el + "=" + str(thegoodvalsdict[el][0]) for el in tmpfreeze if el in thegoodvalsdict]),
                                    extra        = '-n {g} {card} --freezeParameters {c} --out {o}'.format(card = thecard,
                                                                                                            g    = gr,
                                                                                                            c    = ",".join(tmpfreeze),
                                                                                                            o    = outpath),
                                    minmaxlist   = ":".join([el + "=0,3" for el in pois]),
                                    )
        print("\nCommand:", thecomm)
        if not pretend:
            os.system(thecomm)
            os.system("mv higgsCombine{u}.FitDiagnostics.mH125.root ".format(u = gr) + outpath + "/")

    return


def calculateRelativeUncertainties(task):
    inpath, iY, iV, pretend,nps, nth, redo = task
    
    bins_detector = vl.varList[iV]['bins_detector']
    ndetectorbins = len(bins_detector) - 1
    bins_particle = vl.varList[iV]['bins_particle']
    nparticlebins = len(bins_particle) - 1
    
    reluncpath = inpath + "/"+ iY + "/" + iV + "/sigextr_fit_combine/relativeuncs_fd"
    for iP in ["", "/individual", "/global"]:
        if not os.path.isdir(reluncpath + iP):
            os.system("mkdir -p " + reluncpath + iP)

    doBatch = False
    userstdirrw = userstorage.replace("phedex", "phedexrw").replace("ciencias", "cienciasrw") + "/" + inpath + iY + "/" + iV + "/relativeuncs_fd"
    userstdir   = userstdirrw.replace("phedexrw", "phedex").replace("cienciasrw", "ciencias")

    #print userstdirrw

    if not os.path.isdir(userstdirrw):
        os.system("mkdir -p " + userstdirrw)
        os.system("cp " + inpath + "/"+ iY + "/" + iV + "/sigextr_fit_combine/fit_output.root " + userstdirrw + "/")
        thecard = userstdirrw + "/fit_output.root"
    elif os.path.isfile(userstdir + "/fit_output.root"):
        thecard = userstdir + "/fit_output.root"
    else:
        thecard = userstdirrw + "/fit_output.root"

    thecard = inpath + "/"+ iY + "/" + iV + "/sigextr_fit_combine/fit_output.root"
    
    #print thecard
    #sys.exit()

    #thecard = "../../fit_output.root"
    POIs    = ["r_bb4l_{iB}".format(iB = i) for i in range(nparticlebins)]
    indGroup = deepcopy(individual_scaff)
    #if variable == "Fiducial": indGroup = deepcopy(global_scaff); vl.individual_list=["systematics"]
    gloGroup = deepcopy(global_scaff)

    for iB in range(ndetectorbins):
        indGroup["mc_stat"].append(    "prop_bincard_" + iV + "_bin" + str(iB))
        #if variable != "Fiducial": indGroup["mc_stat"].append(    "prop_bincard_" + iV + "_bin" + str(iB))
        gloGroup["systematics"].append("prop_bincard_" + iV + "_bin" + str(iB))


    thegoodvalsdict = getBestFitParsValue(inpath + "/"+ iY + "/" + iV + "/sigextr_fit_combine/fitdiagnostics/fitpars.txt")


    subtasks = []
    indfreeze = []
    
    for gr in vl.individual_list:
        print('GROUP',gr)
        indfreeze += indGroup[gr]
        subtasks.append( (reluncpath + "/individual/", thecard, deepcopy(indfreeze), thegoodvalsdict, POIs, gr, redo, pretend) )



    # And finally, the globals
    glofreeze = []
    for gr in vl.global_list:
        glofreeze += gloGroup[gr]
        subtasks.append( (reluncpath + "/global/", thecard, deepcopy(glofreeze), thegoodvalsdict, POIs, gr, redo, pretend) )

    #print subtasks

    if nth > 1:
        pool = Pool(nth)
        pool.map(doMeThisFitPlease, subtasks)
        pool.close()
        pool.join()
    else:
        for tsk in subtasks:
            doMeThisFitPlease(tsk)


    ### First, we obtain the individual-separated files.
    #cumulative = []
    #for gr in vl.individual_list:
        #cumulative += indGroup[gr]
        #if not os.path.isfile(reluncpath + "/individual/higgsCombine{g}.FitDiagnostics.mH125.root".format(g = gr, p = poi)) or redo:
            #thecomm = basecommand.format(setpars     = ",".join([el + "=1" for el in POIs] + [el + "=" + str(thegoodvalsdict[el][0]) for el in cumulative if el in thegoodvalsdict]),
                                        #extra        = '-n {g} {card} --freezeParameters {c} --out {o}'.format(card = thecard,
                                                                                                               #g    = gr,
                                                                                                               #c    = ",".join(cumulative),
                                                                                                               #o    = reluncpath + "/individual/"),
                                        #minmaxlist   = ":".join([el + "=0,3" for el in POIs]),
            #print "\nCommand:", thecomm
            #if not pretend:
                #os.system(thecomm)
                #os.system("mv higgsCombine{u}.FitDiagnostics.mH125.root ".format(u = gr) + reluncpath + "/individual/")



    ## And finally, the globals
    #cumulative = []
    #for gr in vl.global_list:
        #cumulative += gloGroup[gr]
        #thecomm = basecommand.format(setpars      = ",".join([el + "=1" for el in POIs] + [el + "=" + str(thegoodvalsdict[el][0]) for el in cumulative if el in thegoodvalsdict]),
                                     #extra        = '-n {g} {card} --freezeParameters {c} --out {o}'.format(card = thecard,
                                                                                                            #g    = gr,
                                                                                                            #c    = ",".join(cumulative),
                                                                                                            #o    = reluncpath + "/global/"),
                                     ##extra        = '-n {g} {card} --freezeParameters {c} --snapshotName FitDiagnostics'.format(card = inpath + "/"+ iY + "/" + iV + "/sigextr_fit_combine/fitdiagnostics/higgsCombine" + iY + "_" + iV + ".FitDiagnostics.mH120.root", g = gr, c = ",".join(cumulative)),
                                     #minmaxlist   = ":".join([el + "=0,3" for el in POIs]),
        #)

        #print "\nCommand:", thecomm
        #if not pretend:
            #os.system(thecomm)
            #os.system("mv higgsCombine{u}.FitDiagnostics.mH125.root ".format(u = gr) + reluncpath + "/global/")
    return




if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage = "python nanoAOD_checker.py [options]", description = "Checker tool for the outputs of nanoAOD production (NOT postprocessing)", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--inpath',      '-i',  metavar = 'inpath',     dest = "inpath",      required = False, default = "./temp/differential")
    parser.add_argument('--pretend',     '-p',  action  = "store_true", dest = "pretend",     required = False, default = False)
    parser.add_argument('--nPoints',     '-P',  metavar = 'npoints',    dest = "npoints",     required = False, default = 128, type = int)
    parser.add_argument('--queue',       '-q',  action  = "store_true", dest = "queue",       required = False, default = False)
    parser.add_argument('--ncores',      '-j',  metavar = 'ncores',     dest = "ncores",      required = False, default = -1, type = int)
    parser.add_argument('--redoAll',     '-r',  action  = "store_true", dest = "redo",        required = False, default = False)
    parser.add_argument('--year',        '-y',  metavar = 'year',       dest = "year",        required = False, default = "all")
    parser.add_argument('--variable',    '-v',  metavar = 'variable',   dest = "variable",    required = False, default = "all")

    args     = parser.parse_args()
    pretend  = args.pretend
    inpath   = args.inpath
    npoints  = args.npoints
    doBatch  = args.queue
    nthreads = args.ncores
    variable = args.variable
    year     = args.year
    redo     = args.redo

    tasks = []
    theyears = []
    presentyears = next(os.walk(inpath))[1]

    if "2016apv" in presentyears:
        theyears.append("2016apv")
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

        theyears = []
        presentyears = next(os.walk(inpath))[1]
        if "2016apv" in presentyears:
            theyears.append("2016apv")
        if "2016" in presentyears:
            theyears.append("2016")
        if "2017" in presentyears:
            theyears.append("2017")
        if "2018" in presentyears:
            theyears.append("2018")
        if "run2" in presentyears:
            theyears.append("run2")

        for iV in thevars:
            if any( [el in iV for el in vl.vetolist] ): continue
            tasks.append( (inpath, iY, iV, pretend,npoints, nthreads, redo) )


    """
    if nthreads > 1:
        pool = Pool(nthreads)
        pool.map(calculateRelativeUncertainties, tasks)
        pool.close()
        pool.join()
    else:
        for tsk in tasks:
            calculateRelativeUncertainties(tsk)
    """
    print(tasks)

    for tsk in tasks:
        calculateRelativeUncertainties(tsk)
