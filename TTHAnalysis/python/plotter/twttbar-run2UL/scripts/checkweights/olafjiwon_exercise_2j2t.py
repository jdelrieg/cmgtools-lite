""" Small piece of code to compute nominal reco / fiducial / fiducial_big yields """
# -- Python libraries
import ROOT as r
import os, sys
from copy import deepcopy
import argparse

# Analysis libraries
sys.path.append(os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/twttbar-run2UL"))
from functions import color_msg
from scripts.ntuple_reader_corrected import ntuple_reader

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(1)


if __name__ == "__main__":

    #main_path_2016    = "/lustrefs/analysis/nanoAODv9/bb4l/productions/2025-12-23/2016/mergedFiles/"
    main_path_2016apv = "/lustrefs/analysis/nanoAODv9/bb4l/productions/2025-12-23/2016apv/mergedFiles/"
    #main_path_2017    = "/lustrefs/analysis/nanoAODv9/bb4l/productions/2025-12-23/2017/mergedFiles/"
    #main_path_2018    = "/lustrefs/analysis/nanoAODv9/bb4l/productions/2025-12-23/2018/mergedFiles/"

    # ---- build the main file list, tracking (era_path, index) per file so the
    #      friend files can be generated in the exact same order ----
    era_indices = {
        #main_path_2016:    range(5),   # _0 .. _4
        main_path_2016apv: range(4),   # _0 .. _3
        #main_path_2017:    range(9),   # _0 .. _8
        #main_path_2018:    range(13),  # _0 .. _12
    }

    main_files = []       # bare file paths (no "/Events"), in chain order
    for era_path, indices in era_indices.items():
        for i in indices:
            main_files.append(os.path.join(era_path, f"BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_{i}.root"))

    samplename = [f + "/Events" for f in main_files]

    # ---- build one friend file list per correction stage, matching
    #      main_files 1-to-1 in the same order ----
    friend_stages = [
        "0_jecs",
        "1_lepsuncsAndParticle",
        "2_cleaning",
        "3_varstrigger",
        "4_scalefactors",
    ]

    friends = []
    for stage in friend_stages:
        stage_files = []
        for f in main_files:
            era_path = os.path.dirname(f)
            base = os.path.basename(f).replace(".root", "_Friend.root")
            stage_files.append(os.path.join(era_path, stage, base))
        friends.append(stage_files)

    main_ntuple = ntuple_reader(
        samplename=samplename,
        friends=friends,
        ftreename="Friends"
    )

    # ---- selections ----
    reco = [
        "(1)",
        "pass_trigger",
        "channel == 1",
        "nLepGood == 2 && LepGood_pt_corrAll[0] > 25 && LepGood_pt_corrAll[1] > 20 && isSS == 0 && minMllAFAS > 20",
        "channel == 1 || abs(Mll - 91) > 15",
        "nJetSel30_Recl == 2",
        "nBJetSelMedium30_Recl == 2",
    ]

    fiducial = [
        "(1)",
        "Dresschannel == 1",
        "nDressSelLep == 2 && DressLep1_Pt > 25 && DressLep2_Pt > 20 && DressisSS == 0 && DressminMllAFAS > 20",
        "nDressSelJet == 2",
        "nDressBSelJet == 2",
    ]

    # replace this with your actual, looser/bigger fiducial definition
    fiducial_great3 = [
        "(1)",
        "Dresschannel == 1",
        "nDressSelLep == 2 && DressLep1_Pt > 25 && DressLep2_Pt > 20 && DressisSS == 0 && DressminMllAFAS > 20",
        "nDressSelJet >= 3",
        "nDressBSelJet >= 3",
    ]

    fiducial_less2b = [
        "(1)",
        "Dresschannel == 1",
        "nDressSelLep == 2 && DressLep1_Pt > 25 && DressLep2_Pt > 20 && DressisSS == 0 && DressminMllAFAS > 20",
        "nDressSelJet == 2",
        "nDressBSelJet < 2",
    ]

    fiducial_less2j = [
        "(1)",
        "Dresschannel == 1",
        "nDressSelLep == 2 && DressLep1_Pt > 25 && DressLep2_Pt > 20 && DressisSS == 0 && DressminMllAFAS > 20",
        "nDressSelJet < 2",
        "nDressBSelJet < 2",
    ]
    
    recocut            = " && ".join([f"({cut})" for cut in reco])
    fiducialcut         = " && ".join([f"({cut})" for cut in fiducial])
    fiducial_great3cut  = " && ".join([f"({cut})" for cut in fiducial_great3])

    fiducial_less2bcut  = " && ".join([f"({cut})" for cut in fiducial_less2b])
    fiducial_less2jcut  = " && ".join([f"({cut})" for cut in fiducial_less2j])    
    # reco AND fiducial together -> this is what the datacard's bb4l_partbinX
    # rows actually represent: reco-selected events, binned by which fiducial
    # (particle-level) bin they fall into. Comparing THIS to the card,
    # bin by bin, is the apples-to-apples check -- plain "fiducial" alone
    # has no reco requirement and will not match partbinX.
    reco_and_fiducialcut = f"({recocut}) && ({fiducialcut})"
    reco_and_fiducialg3cut = f"({recocut}) && ({fiducial_great3cut})"
    reco_and_fiducialless2bcut = f"({recocut}) && ({fiducial_less2bcut})"
    reco_and_fiducialless2jcut = f"({recocut}) && ({fiducial_less2jcut})"
    reco_and_nonfiducialcut = f"({recocut}) && !({fiducialcut})"

    # ---- physical normalization ----
    # sample cross section and integrated luminosity used by the datacard
    xsec_pb = 95.57     # pb
    lumi_fb = 138.0     # fb^-1 (full Run 2)
    norm_factor = xsec_pb * lumi_fb * 1000.0   # -> xsec[pb] * lumi[pb^-1], gives events

    # ---- scale-factor corrections ----
    # Confirmed weight expression from the analysis framework's plotter
    # (the same one used to build the datacard), applied on top of genWeight.
    sf_branches = [
        "MuonIDSF",
        "MuonISOSF",
        "ElecIDSF",
        "ElecRECOSF",
        "TrigSF",
        "puWeight",
        "bTagWeight",
        "L1PreFiringWeight_Nom",
        "jetPUidWeight",
    ]
    sf_weight = " * ".join(sf_branches)

    #variable = "LepGood_pt_corrAll[0]"   # any variable works, we just integrate it
    variable = "minimax"
    binning  = [0., 40., 60., 80., 100., 120., 180., 220., 270., 340., 500.]  # full range -> Integral() = total yield

    # Reco-level selections get the SF-corrected weight (to match the card,
    # which is built at reco level). Pure fiducial (truth-level) selections
    # only ever had genWeight applied in the card too, so they stay as-is.
    selections = {
        "reco":              (f"({recocut})*(genWeight*{sf_weight})",              "(genEventSumw)"),
        "fiducial":          (f"({fiducialcut})*(genWeight)",                      "(genEventSumw)"),
        "fiducial_great3":   (f"({fiducial_great3cut})*(genWeight)",               "(genEventSumw)"),
        "reco_and_fiducial": (f"({reco_and_fiducialcut})*(genWeight*{sf_weight})", "(genEventSumw)"),
        "reco_and_fiducialg3": (f"({reco_and_fiducialg3cut})*(genWeight*{sf_weight})", "(genEventSumw)"),
        "reco_and_fiducialless2b": (f"({reco_and_fiducialless2bcut})*(genWeight*{sf_weight})", "(genEventSumw)"),
        "reco_and_fiducialless2j": (f"({reco_and_fiducialless2jcut})*(genWeight*{sf_weight})", "(genEventSumw)"),
        "nonfiducial" : (f"({reco_and_nonfiducialcut})*(genWeight*{sf_weight})", "(genEventSumw)"),
    }

    results = {}
    for name, (cut, varNormToGenSum) in selections.items():

        # Raw (weighted) event yield -- NOT normalized to genEventSumw.
        # This is just MC statistics (sum of genWeight*SF passing the cut),
        # NOT a physical event count -- do not compare this to the card.
        h_raw = main_ntuple.draw(variable, binning, cut, name + "_raw",
                                  normToGenSum=False)

        # Same selection, but scaled by 1/genEventSumw -> fraction of the
        # total weighted generated sample that passes this selection.
        # This IS the physically meaningful quantity.
        h_frac = main_ntuple.draw(variable, binning, cut, name + "_frac",
                                   normToGenSum=True, varNormToGenSum=varNormToGenSum)

        # Pull out real numbers now, while we still have live histograms.
        nevt_total = h_raw.Integral()
        frac_total = h_frac.Integral()
        nphys_total = frac_total * norm_factor
        results[name] = (nevt_total, frac_total, nphys_total)

        print(f"\n--- {name} ---")
        for ibin in range(1, h_raw.GetNbinsX() + 1):
            low  = h_raw.GetXaxis().GetBinLowEdge(ibin)
            high = h_raw.GetXaxis().GetBinUpEdge(ibin)

            nevt  = h_raw.GetBinContent(ibin)   # raw MC stat sum, NOT physical
            frac  = h_frac.GetBinContent(ibin)  # fraction of genEventSumw in this bin
            nphys = frac * norm_factor          # physical (xsec*lumi-scaled) yield

            print(f"bin {ibin:2d} [{low:7.1f}, {high:7.1f}] : "
                  f"raw_mc_stat = {nevt:12.3f}   "
                  f"fraction = {frac:.6f}   "
                  f"N_physical = {nphys:12.3f}")

    print("\n--- Summary ---")
    print(f"(normalization: xsec = {xsec_pb} pb, lumi = {lumi_fb} fb^-1 "
          f"-> xsec*lumi = {norm_factor:.3f} events for fraction = 1)\n")
    for name, (nevt, frac, nphys) in results.items():
        print(f"{name:20s}: N_physical = {nphys:12.3f} events   "
              f"(fraction = {100*frac:.4f}% of weighted sample, "
              f"raw MC stat sum = {nevt:.3f})")
