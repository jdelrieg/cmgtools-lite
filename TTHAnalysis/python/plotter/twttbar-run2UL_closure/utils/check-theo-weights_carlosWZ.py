""" Small piece of code to compute trigger efficiencies on data and MC"""
# -- Python libraries
import ROOT as r
import os, sys
from copy import deepcopy
import argparse
import array

import json


# Analysis libraries
sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/twttbar-run2UL"))
from functions import color_msg
from scripts.ntuple_reader import ntuple_reader
from scripts.make_latex_table import dict_to_latex_table

# Turn off root gui mode
r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(1)
r.gStyle.SetPadTickX(1)
r.gStyle.SetPadTickY(1)

def add_parsing_options():
    ''' Function with base parsing arguments used by any script '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', '-m', dest = "mode", default = "total", help = "Choose total or fiducial")
    return parser.parse_args()

def doSpam(text,x1,y1,x2,y2,align=12,fill=False,textSize=0.033,_noDelete={}):
  cmsprel = r.TPaveText(x1,y1,x2,y2,"NDC")
  cmsprel.SetTextSize(textSize)
  cmsprel.SetFillColor(0)
  cmsprel.SetFillStyle(1001 if fill else 0)
  cmsprel.SetLineStyle(2)
  cmsprel.SetLineColor(0)
  cmsprel.SetLineWidth(0)
  cmsprel.SetTextAlign(align)
  cmsprel.SetTextFont(43)
  cmsprel.AddText(text)
  cmsprel.Draw("same")
  _noDelete[text] = cmsprel; ## so it doesn't get deleted by PyROOT                                                                                                                    
  return cmsprel

if __name__ == "__main__":
    opts = add_parsing_options()
    mode = opts.mode

    #run3_path   = f"/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v3/mc/2022"
    run3_path   = f"/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v3/mc/2022"
    

    run3_ntuple = ntuple_reader( 
        samplename = [ 
            os.path.join( run3_path, "WZto3LNu.root/Events") 
        ],
        friends = [ 
            os.path.join( run3_path, "leptonJetRecleaning/WZto3LNu_Friend.root"),
            os.path.join( run3_path, "leptonBuilder/WZto3LNu_Friend.root"),
            os.path.join( run3_path, "scalefactors_chargeID/WZto3LNu_Friend.root"),
            os.path.join( run3_path, "lepGEN_withTau/WZto3LNu_Friend.root"),
        ],
        ftreename = "Friends"
    )
    reco = [
        "(1)",
        "Trigger_3l || HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
        "nLepSel >= 3",
        "LepSel_isTight[0] && LepSel_isTight[1] && LepSel_isTight[2]",
        "LepZ1_pt >= 25 && LepZ2_pt >= 15 && LepW_pt >= 25",
        "abs(LepSel_pdgId[0]) < 15 && abs(LepSel_pdgId[1]) < 15 && abs(LepSel_pdgId[2]) < 15 && nOSSF_3l >= 1",
        "m3L >= 100",
        "nLepGood < 4",
        "MET_pt_central > 35",
        "nBJetTight25_Mini == 0",
        "abs(mll_3l - 91.16) < 15",
        "minMllSFOS_Mini > 4 || minMllSFOS_Mini == -1",
        "LepGood_tightCharge[0]==2 && LepGood_tightCharge[1]==2 && LepGood_tightCharge[2]==2",
    ]

    total = [
        "(1)",
        "mll_3l_gen > 60  && mll_3l_gen < 120",
        "nLepGen_gen >= 3",
        "minmllSFOS_gen >= 4",
    ]

    fiducial = [ 
        "abs(genLepZ1_pdgId) < 14 && abs(genLepZ2_pdgId) < 14 && abs(genLepW_pdgId) < 14",
        "nOSSF_3l_gen > 0",
        "genLepZ1_pt > 25 && genLepZ2_pt > 15 && genLepW_pt > 25",
        "abs(genLepZ1_eta) < 2.5  && abs(genLepZ2_eta) < 2.5  && abs(genLepW_eta) < 2.5",
        "m3L_gen >= 100"
    ]


    variable = "(abs(LepZ1_pdgId)+abs(LepZ2_pdgId)+abs(LepW_pdgId)-33)/2"
    binning = "4,-0.5,3.5"
    recocut = " && ".join( [f"({cut})" for cut in reco] )
    fiducialcut = " && ".join( [f"({cut})" for cut in total+fiducial] )

    if mode == "total":
        outfolder = "plots-total"
        totalcut = " && ".join( [f"({cut})" for cut in total] )
    else:
        outfolder = "plots-fiducial"
        totalcut = " && ".join( [f"({cut})" for cut in total+fiducial] )
    
    shapes_reco = [
        # SCALE WEIGHTS
        #("Nominal",         f"(puWeight_fix*bTagWeight*electronSF*muonSF)*({recocut})*({fiducialcut})*((genWeight))", "(genWeight)", "nom", "0"), #"genEventSumw"),
        #("mur=1.0,muf=2.0", f"(puWeight_fix*bTagWeight*electronSF*muonSF)*({recocut})*({fiducialcut})*(LHEScaleWeight[5]/LHEScaleWeight[4])*((genWeight))", "(genWeight*LHEScaleWeight[5]/LHEScaleWeight[4])", "muR_1p0_muF=2p0", "5"),#"LHEScaleSumw[5]*genEventSumw"),
        #("mur=1.0,muf=0.5", f"(puWeight_fix*bTagWeight*electronSF*muonSF)*({recocut})*({fiducialcut})*(LHEScaleWeight[3]/LHEScaleWeight[4])*((genWeight))", "(genWeight*LHEScaleWeight[3]/LHEScaleWeight[4])", "muR_1p0_muF=0p5", "3"),#"LHEScaleSumw[3]*genEventSumw"),
        #("mur=2.0,muf=1.0", f"(puWeight_fix*bTagWeight*electronSF*muonSF)*({recocut})*({fiducialcut})*(LHEScaleWeight[7]/LHEScaleWeight[4])*((genWeight))", "(genWeight*LHEScaleWeight[7]/LHEScaleWeight[4])", "muR_2p0_muF=1p0", "7"),#"LHEScaleSumw[7]*genEventSumw"),
        #("mur=0.5,muf=1.0", f"(puWeight_fix*bTagWeight*electronSF*muonSF)*({recocut})*({fiducialcut})*(LHEScaleWeight[1]/LHEScaleWeight[4])*((genWeight))", "(genWeight*LHEScaleWeight[1]/LHEScaleWeight[4])", "muR_0p5_muF=1p0", "1"),#"LHEScaleSumw[1]*genEventSumw"),
        #("mur=2.0,muf=2.0", f"(puWeight_fix*bTagWeight*electronSF*muonSF)*({recocut})*({fiducialcut})*(LHEScaleWeight[8]/LHEScaleWeight[4])*((genWeight))", "(genWeight*LHEScaleWeight[8]/LHEScaleWeight[4])", "muR_2p0_muF=2p0", "8"),#"LHEScaleSumw[7]*genEventSumw"),
        #("mur=0.5,muf=0.5", f"(puWeight_fix*bTagWeight*electronSF*muonSF)*({recocut})*({fiducialcut})*(LHEScaleWeight[0]/LHEScaleWeight[4])*((genWeight))", "(genWeight*LHEScaleWeight[0]/LHEScaleWeight[4])", "muR_0p5_muF=0p5", "0"),#"LHEScaleSumw[1]*genEventSumw"),
        #("Nominal",         f"({recocut})*({fiducialcut})*((genWeight))", "(genEventSumw)", "nom", "0"), 
        #("mur=1.0,muf=2.0", f"({recocut})*({fiducialcut})*(LHEScaleWeight[5]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleSumw[5]*genEventSumw)", "muR_1p0_muF=2p0", "5"),
        #("mur=1.0,muf=0.5", f"({recocut})*({fiducialcut})*(LHEScaleWeight[3]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleSumw[3]*genEventSumw)", "muR_1p0_muF=0p5", "3"),
        #("mur=2.0,muf=1.0", f"({recocut})*({fiducialcut})*(LHEScaleWeight[7]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleSumw[7]*genEventSumw)", "muR_2p0_muF=1p0", "7"),
        #("mur=0.5,muf=1.0", f"({recocut})*({fiducialcut})*(LHEScaleWeight[1]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleSumw[1]*genEventSumw)", "muR_0p5_muF=1p0", "1"),
        #("mur=2.0,muf=2.0", f"({recocut})*({fiducialcut})*(LHEScaleWeight[8]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleSumw[7]*genEventSumw)", "muR_2p0_muF=2p0", "8"),
        #("mur=0.5,muf=0.5", f"({recocut})*({fiducialcut})*(LHEScaleWeight[0]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleSumw[1]*genEventSumw)", "muR_0p5_muF=0p5", "0"),
        ("Nominal",         f"({recocut})*({fiducialcut})*((genWeight))", "(genEventSumw)", "nom", "0"), 
        ("mur=1.0,muf=2.0", f"({recocut})*({fiducialcut})*(LHEScaleWeight[5]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "muR_1p0_muF=2p0", "5"),
        ("mur=1.0,muf=0.5", f"({recocut})*({fiducialcut})*(LHEScaleWeight[3]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "muR_1p0_muF=0p5", "3"),
        ("mur=2.0,muf=1.0", f"({recocut})*({fiducialcut})*(LHEScaleWeight[7]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "muR_2p0_muF=1p0", "7"),
        ("mur=0.5,muf=1.0", f"({recocut})*({fiducialcut})*(LHEScaleWeight[1]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "muR_0p5_muF=1p0", "1"),
        ("mur=2.0,muf=2.0", f"({recocut})*({fiducialcut})*(LHEScaleWeight[8]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "muR_2p0_muF=2p0", "8"),
        ("mur=0.5,muf=0.5", f"({recocut})*({fiducialcut})*(LHEScaleWeight[0]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "muR_0p5_muF=0p5", "0"),
    ]

    for ipdf in range(1, 103):
        shapes_reco.append( (f"pdf{ipdf}", f"({recocut})*({fiducialcut})*(LHEPdfWeight[{ipdf}]/LHEPdfWeight[0])*((genWeight))", f"(genEventSumw)", f"pdf_{ipdf}", f"{ipdf}"))

    shapes_total = [
        # SCALE WEIGHTS
        #("total_Nominal",         f"({totalcut})*((genWeight))", "genWeight", "nom"),#"genEventSumw"),
        #("total_mur=1.0,muf=2.0", f"({totalcut})*(LHEScaleWeight[5]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleWeight[5]/LHEScaleWeight[4]*genWeight)", "scaleweight_5"),#"LHEScaleSumw[5]*genEventSumw"),
        #("total_mur=1.0,muf=0.5", f"({totalcut})*(LHEScaleWeight[3]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleWeight[3]/LHEScaleWeight[4]*genWeight)", "scaleweight_3"),#"LHEScaleSumw[3]*genEventSumw"),
        #("total_mur=2.0,muf=1.0", f"({totalcut})*(LHEScaleWeight[7]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleWeight[7]/LHEScaleWeight[4]*genWeight)", "scaleweight_7"),#"LHEScaleSumw[7]*genEventSumw"),
        #("total_mur=0.5,muf=1.0", f"({totalcut})*(LHEScaleWeight[1]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleWeight[1]/LHEScaleWeight[4]*genWeight)", "scaleweight_1"),#"LHEScaleSumw[1]*genEventSumw"),
        #("total_mur=2.0,muf=2.0", f"({totalcut})*(LHEScaleWeight[8]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleWeight[8]/LHEScaleWeight[4]*genWeight)", "scaleweight_8"),#"LHEScaleSumw[7]*genEventSumw"),
        #("total_mur=0.5,muf=0.5", f"({totalcut})*(LHEScaleWeight[0]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleWeight[0]/LHEScaleWeight[4]*genWeight)", "scaleweight_0"),#"LHEScaleSumw[1]*genEventSumw"),
        
        #("total_Nominal",         f"({totalcut})*((genWeight))", "genEventSumw", "nom"),
        #("total_mur=1.0,muf=2.0", f"({totalcut})*(LHEScaleWeight[5]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleSumw[5]*genEventSumw)", "scaleweight_5"),
        #("total_mur=1.0,muf=0.5", f"({totalcut})*(LHEScaleWeight[3]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleSumw[3]*genEventSumw)", "scaleweight_3"),
        #("total_mur=2.0,muf=1.0", f"({totalcut})*(LHEScaleWeight[7]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleSumw[7]*genEventSumw)", "scaleweight_7"),
        #("total_mur=0.5,muf=1.0", f"({totalcut})*(LHEScaleWeight[1]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleSumw[1]*genEventSumw)", "scaleweight_1"),
        #("total_mur=2.0,muf=2.0", f"({totalcut})*(LHEScaleWeight[8]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleSumw[7]*genEventSumw)", "scaleweight_8"),
        #("total_mur=0.5,muf=0.5", f"({totalcut})*(LHEScaleWeight[0]/LHEScaleWeight[4])*((genWeight))", "(LHEScaleSumw[1]*genEventSumw)", "scaleweight_0"),
        ("total_Nominal",         f"({totalcut})*((genWeight))", "genEventSumw", "nom"),
        ("total_mur=1.0,muf=2.0", f"({totalcut})*(LHEScaleWeight[5]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "scaleweight_5"),
        ("total_mur=1.0,muf=0.5", f"({totalcut})*(LHEScaleWeight[3]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "scaleweight_3"),
        ("total_mur=2.0,muf=1.0", f"({totalcut})*(LHEScaleWeight[7]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "scaleweight_7"),
        ("total_mur=0.5,muf=1.0", f"({totalcut})*(LHEScaleWeight[1]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "scaleweight_1"),
        ("total_mur=2.0,muf=2.0", f"({totalcut})*(LHEScaleWeight[8]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "scaleweight_8"),
        ("total_mur=0.5,muf=0.5", f"({totalcut})*(LHEScaleWeight[0]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "scaleweight_0"),
    ]

    for ipdf in range(1, 103):
        shapes_total.append( (f"pdf{ipdf}", f"({totalcut})*(LHEPdfWeight[{ipdf}]/LHEPdfWeight[0])*((genWeight))", f"(genEventSumw)", f"pdf_{ipdf}"))

    # Make the histograms
    histos_reco  = []
    histos_total = []
    ratios_reco  = []
    ratios_total = []
    ratios_ratio = []


    for isr, (sr_name, sr, sr_varNormToGenSum, _, asdas) in enumerate( shapes_reco ):
        srtotal_name, srtotal, srtotal_varNormToGenSum, _ = shapes_total[ isr ]
        hreco  = run3_ntuple.draw( variable, binning, sr, sr_name, normToGenSum = True, varNormToGenSum =  sr_varNormToGenSum)
        htotal = run3_ntuple.draw( variable, binning, srtotal, srtotal_name, normToGenSum = True, varNormToGenSum =  srtotal_varNormToGenSum)       
        

        histos_reco.append( hreco )
        histos_total.append( htotal )

        if isr != 0:
            hreco.SetLineColor( 1 )
            hreco.SetLineWidth( 2 )
            hreco.SetFillColor(0)

            htotal.SetLineColor( 1 )
            htotal.SetLineWidth( 2 )
            htotal.SetFillColor(0)

            ratio_hreco = deepcopy( hreco )
            ratio_hreco.Divide( histos_reco[0] )
            ratio_hreco.SetLineColor( 1 )
            ratio_hreco.SetLineWidth( 2 )
            ratio_hreco.SetFillColor( 0 )
            ratios_reco.append( ratio_hreco )

            ratio_htotal = deepcopy( htotal )
            ratio_htotal.Divide( histos_total[0] )
            ratio_htotal.SetLineColor( 1 )
            ratio_htotal.SetLineWidth( 2 )
            ratio_htotal.SetFillColor( 0 )
            ratios_total.append( ratio_htotal )

            ratio_hratio = deepcopy( ratio_hreco )
            ratio_hratio.Divide( ratio_htotal )
            ratio_hratio.SetLineColor( 1 )
            ratio_hratio.SetLineWidth( 2 )
            ratio_hratio.SetFillColor( 0 )
            ratios_ratio.append( ratio_hratio )
            
        else:
            hreco.SetLineColor( 5 )
            hreco.SetLineWidth( 2 )
            hreco.SetFillColor(0)

            htotal.SetLineColor( 5 )
            htotal.SetLineWidth( 2 )
            htotal.SetFillColor(0)
            
            ratio_hreco = deepcopy( hreco )
            ratio_hreco.Divide( hreco )
            ratio_hreco.SetLineColor( 5 )
            ratio_hreco.SetLineWidth( 2 )
            ratio_hreco.SetFillColor( 0 )
            ratios_reco.append( ratio_hreco )

            ratio_htotal = deepcopy( htotal )
            ratio_htotal.Divide( htotal )
            ratio_htotal.SetLineColor( 5 )
            ratio_htotal.SetLineWidth( 2 )
            ratio_htotal.SetFillColor( 0 )
            ratios_total.append( ratio_htotal )

            ratio_hratio = deepcopy( ratio_hreco )
            ratio_hratio.Divide( ratio_htotal )
            ratio_hratio.SetLineColor( 5 )
            ratio_hratio.SetLineWidth( 2 )
            ratio_hratio.SetFillColor( 0 )
            ratios_ratio.append( ratio_hratio )
        
        print(f" >>> ISR: {isr}")
        for ibin in range(1, 1+hreco.GetNbinsX()):
            print(f"    - {ibin}: reco={ratio_hreco.GetBinContent(ibin):3.3f}, total={ratio_htotal.GetBinContent(ibin):3.3f}, ratio={ratio_hratio.GetBinContent(ibin):3.3f}")
    # Write out the results 


    ## Plot
    for ih, h in enumerate(histos_reco[1:]):
        name = f"{shapes_reco[ih][-2]}"
        height = 0.05 * 1.15 * 7

        if variable == "(abs(LepZ1_pdgId)+abs(LepZ2_pdgId)+abs(LepW_pdgId)-33)/2":
            legend = r.TLegend(0.62, .59-height, 0.22 + 0.8, .59) #0.85 for the first number in the CMGTools plotter
        elif variable == "min(max(mll_3l_gen, 1), 149)":
            legend = r.TLegend(0.22, .59-height, 0.22 + 0.4, .59) #0.85 for the first number in the CMGTools plotter
        elif variable == "(abs(genLepZ1_pdgId)+abs(genLepZ2_pdgId)+abs(genLepW_pdgId)-33)/2":
            legend = r.TLegend(0.22, .59-height, 0.22 + 0.4, .59) #0.85 for the first number in the CMGTools plotter
        legend.SetBorderSize(0)
        legend.SetFillColor(0)
        legend.SetShadowColor(0)
        legend.SetFillStyle(0)
        legend.SetTextFont(42)
        legend.SetTextSize( 0.05 )
        legend.SetNColumns(1)
        
        
        
        
        c = r.TCanvas(f"canvas_{name}", "",  800, 800)
        topSpamSize     = 1.1
        c.SetTopMargin(c.GetTopMargin() * topSpamSize)
        c.Divide(1,4)

        # --- First pad
        p1 = c.GetPad(1)
        p1.SetPad(0, 0.65, 1, 1)
        p1.SetBottomMargin(0.12)
        p1.SetLeftMargin(0.16)
        p1.SetRightMargin(0.03)

        # --- Second pad
        p2 = c.GetPad(2)
        p2.SetPad(0, 0.45, 1, 0.65)
        p2.SetTopMargin(0.0)
        p2.SetBottomMargin(0.12)
        p2.SetLeftMargin(0.16)
        p2.SetRightMargin(0.03)
        
        # --- Third pad
        p3 = c.GetPad(3)
        p3.SetPad(0, 0.25, 1, 0.45)
        p3.SetTopMargin(0.0)
        p3.SetBottomMargin(0.12)
        p3.SetLeftMargin(0.16)
        p3.SetRightMargin(0.03)

        # --- Fouratios_total[0]h pad
        p4 = c.GetPad(4)
        p4.SetPad(0, 0, 1, 0.25)
        p4.SetTopMargin(0.0)
        p4.SetBottomMargin(0.42)
        p4.SetLeftMargin(0.16)
        p4.SetRightMargin(0.03)


        p1.cd()
        histos_reco[0].Draw("hist")
        histos_reco[ih+1].Draw("hist same")

        histos_reco[0].GetYaxis().SetRangeUser( 0, histos_reco[0].GetMaximum() * 1.2 )
        histos_reco[0].GetXaxis().SetLabelSize(0)
        histos_reco[0].SetTitle("")
        histos_reco[0].GetYaxis().SetTitleOffset( histos_reco[0].GetYaxis().GetTitleOffset()*2.8 )
        histos_reco[0].GetYaxis().SetTitle("Normalized Events")
        histos_reco[0].GetYaxis().SetLabelSize( 15 )
        histos_reco[0].GetYaxis().SetLabelFont(43)
        histos_reco[0].GetYaxis().SetTitleSize(15)
        histos_reco[0].GetYaxis().SetTitleFont(43)
        histos_reco[0].GetYaxis().SetMaxDigits(4)
        legend.AddEntry( histos_reco[0], histos_reco[0].GetName(), "l")
        legend.AddEntry( histos_reco[ih+1], histos_reco[ih+1].GetName(), "l")
                
        p2.cd()
        ratios_reco[0].Draw("hist")
        ratios_reco[ih+1].Draw("hist same")
        ratios_reco[0].GetYaxis().SetRangeUser( 0.9, 1.1 )

        ratios_reco[0].GetXaxis().SetLabelSize( 0 )
        ratios_reco[0].GetYaxis().SetLabelSize( 15 )   
        ratios_reco[0].GetYaxis().SetLabelFont(43)
        ratios_reco[0].SetTitle("")
        ratios_reco[0].GetYaxis().SetTitle("Varied / Nom. (RECO)")
        ratios_reco[0].GetYaxis().SetTitleOffset( ratios_reco[0].GetYaxis().GetTitleOffset() * 0.1 )
        ratios_reco[0].GetXaxis().SetTitle("")
        ratios_reco[0].GetYaxis().SetTitleSize( ratios_reco[0].GetYaxis().GetTitleSize()*2.5 )
        ratios_reco[0].GetXaxis().SetTitleOffset(4.0)
        ratios_reco[0].GetXaxis().SetTitleSize(15)
        ratios_reco[0].GetXaxis().SetTitleFont(43)
        ratios_reco[0].GetYaxis().SetNdivisions(503)
        ratios_reco[0].GetXaxis().SetNdivisions(410)
        ratios_reco[0].GetYaxis().CenterTitle(True)
            

        p3.cd()
        ratios_total[0].Draw("hist")
        ratios_total[ih+1].Draw("hist same")
        ratios_total[0].GetYaxis().SetRangeUser( 0.9, 1.1 )
        ratios_total[0].GetXaxis().SetLabelSize( 0 )
        ratios_total[0].GetYaxis().SetLabelSize( 15 )   
        ratios_total[0].GetYaxis().SetLabelFont(43)
        ratios_total[0].SetTitle("")
        ratios_total[0].GetYaxis().SetTitle("Varied / Nom. (TOTAL)")
        ratios_total[0].GetYaxis().SetTitleOffset( ratios_total[0].GetYaxis().GetTitleOffset() * 0.1 )
        ratios_total[0].GetXaxis().SetTitle("")
        ratios_total[0].GetYaxis().SetTitleSize( ratios_total[0].GetYaxis().GetTitleSize()*2.5 )
        ratios_total[0].GetXaxis().SetTitleOffset(4.0)
        ratios_total[0].GetXaxis().SetTitleSize(0)
        ratios_total[0].GetXaxis().SetTitleFont(43)
        ratios_total[0].GetYaxis().SetNdivisions(503)
        ratios_total[0].GetXaxis().SetNdivisions(410)
        ratios_total[0].GetYaxis().CenterTitle(True)

        p4.cd()
            
        ratios_ratio[0].Draw("hist")
        ratios_ratio[ih+1].Draw("hist same")

        ratios_ratio[0].GetYaxis().SetRangeUser( 0.9, 1.1 )
        ratios_ratio[0].GetXaxis().SetLabelSize( 0.12 )
        ratios_ratio[0].GetYaxis().SetLabelSize( 15 )   
        ratios_ratio[0].GetYaxis().SetLabelFont(43)
        ratios_ratio[0].SetTitle("")
        ratios_ratio[0].GetYaxis().SetTitleOffset( ratios_ratio[0].GetYaxis().GetTitleOffset() * 0.1 )
        ratios_ratio[0].GetYaxis().SetTitleSize( ratios_ratio[0].GetYaxis().GetTitleSize()*2.5 )
        ratios_ratio[0].GetYaxis().SetTitle("Ratio")
        ratios_ratio[0].GetXaxis().SetTitle("Flavor 3l (gen)")
        ratios_ratio[0].GetXaxis().SetTitleOffset(4.0)
        ratios_ratio[0].GetXaxis().SetTitleSize(26)
        ratios_ratio[0].GetXaxis().SetTitleFont(43)
        ratios_ratio[0].GetYaxis().SetNdivisions(503)
        ratios_ratio[0].GetXaxis().SetNdivisions(410)
        ratios_ratio[0].GetYaxis().CenterTitle(True)
        ratios_ratio[0].Draw("hist same")
        
        
        p1.cd()
        legend.Draw("same")
        doSpam("34.6 fb^{-1} (13.6 TeV)", 0.75, .933, .975, .96,textSize = 22*0.98)
        doSpam('#splitline{#scale[1.2]{#bf{CMS}}}{#scale[1.0]{#it{Preliminary}}}',.2, .745, .35, .795, textSize = 22)

        if not os.path.exists( outfolder ):
            os.system( f"mkdir -p {outfolder}" )
        c.SaveAs( f"{outfolder}/{name}.png" )

    
        # Now write a txt
        weight_index = shapes_reco[ih][-1]
        f = open( f"{outfolder}/fr-{name}.txt", "w" )

        if "pdf" in name:
            f.write(f"# This number has been computed by properly normalizing to the fiducial cross section of the WZ sample\n")
            f.write(f"weight   : {ratios_reco[ih].Integral() / ratios_total[ih].Integral()}\n")
            #f.write(f"alt-norm : LHEPdfSumw[{weight_index}]")
        else:
            f.write(f"# This number has been computed by properly normalizing to the fiducial cross section of the WZ sample\n")
            f.write(f"weight   : {ratios_reco[ih].Integral() / ratios_total[ih].Integral()}\n")
            #f.write(f"alt-norm : LHEScaleSumw[{weight_index}]")
        f.close()



    """
    ## Plot
    height = 0.05 * 1.15 * 7

    if variable == "(abs(LepZ1_pdgId)+abs(LepZ2_pdgId)+abs(LepW_pdgId)-33)/2":
        legend = r.TLegend(0.62, .59-height, 0.22 + 0.8, .59) #0.85 for the first number in the CMGTools plotter
    elif variable == "min(max(mll_3l_gen, 1), 149)":
        legend = r.TLegend(0.22, .59-height, 0.22 + 0.4, .59) #0.85 for the first number in the CMGTools plotter
    elif variable == "(abs(genLepZ1_pdgId)+abs(genLepZ2_pdgId)+abs(genLepW_pdgId)-33)/2":
        legend = r.TLegend(0.22, .59-height, 0.22 + 0.4, .59) #0.85 for the first number in the CMGTools plotter
    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    legend.SetShadowColor(0)
    legend.SetFillStyle(0)
    legend.SetTextFont(42)
    legend.SetTextSize( 0.05 )
    legend.SetNColumns(1)
    
    
    
    
    c = r.TCanvas("canvas", "",  800, 800)
    topSpamSize     = 1.1
    c.SetTopMargin(c.GetTopMargin() * topSpamSize)
    c.Divide(1,4)

    # --- First pad
    p1 = c.GetPad(1)
    p1.SetPad(0, 0.65, 1, 1)
    p1.SetBottomMargin(0.12)
    p1.SetLeftMargin(0.16)
    p1.SetRightMargin(0.03)

    # --- Second pad
    p2 = c.GetPad(2)
    p2.SetPad(0, 0.45, 1, 0.65)
    p2.SetTopMargin(0.0)
    p2.SetBottomMargin(0.12)
    p2.SetLeftMargin(0.16)
    p2.SetRightMargin(0.03)
    
    # --- Third pad
    p3 = c.GetPad(3)
    p3.SetPad(0, 0.25, 1, 0.45)
    p3.SetTopMargin(0.0)
    p3.SetBottomMargin(0.12)
    p3.SetLeftMargin(0.16)
    p3.SetRightMargin(0.03)

    # --- Fouratios_total[0]h pad
    p4 = c.GetPad(4)
    p4.SetPad(0, 0, 1, 0.25)
    p4.SetTopMargin(0.0)
    p4.SetBottomMargin(0.42)
    p4.SetLeftMargin(0.16)
    p4.SetRightMargin(0.03)


    p1.cd()
    for ih, h in enumerate(histos_reco):
        if ih == 0:
            h.Draw("hist")
        else:
            h.Draw("hist same")
        h.GetYaxis().SetRangeUser( 0, h.GetMaximum() * 1.2 )
        #h.GetXaxis().SetRangeUser( 0, 3.5 )
        h.GetXaxis().SetLabelSize(0)
        h.SetTitle("")
        h.GetYaxis().SetTitleOffset( h.GetYaxis().GetTitleOffset()*2.8 )
        h.GetYaxis().SetTitle("Normalized Events")
        h.GetYaxis().SetLabelSize( 15 )
        h.GetYaxis().SetLabelFont(43)
        h.GetYaxis().SetTitleSize(15)
        h.GetYaxis().SetTitleFont(43)
        h.GetYaxis().SetMaxDigits(4)
        legend.AddEntry( h, h.GetName(), "l")
            
    p2.cd()
    for iratios_reco[0], ratios_reco[0] in enumerate(ratios_reco):
        if iratios_reco[0] == 0:
            ratios_reco[0].Draw("hist")
        else:
            ratios_reco[0].Draw("hist same")
        ratios_reco[0].GetYaxis().SetRangeUser( 0.9, 1.1 )

        ratios_reco[0].GetXaxis().SetLabelSize( 0 )
        ratios_reco[0].GetYaxis().SetLabelSize( 15 )   
        ratios_reco[0].GetYaxis().SetLabelFont(43)
        ratios_reco[0].SetTitle("")
        ratios_reco[0].GetYaxis().SetTitle("Varied / Nom. (RECO)")
        ratios_reco[0].GetYaxis().SetTitleOffset( ratios_reco[0].GetYaxis().GetTitleOffset() * 0.1 )
        ratios_reco[0].GetXaxis().SetTitle("")
        ratios_reco[0].GetYaxis().SetTitleSize( ratios_reco[0].GetYaxis().GetTitleSize()*2.5 )
        ratios_reco[0].GetXaxis().SetTitleOffset(4.0)
        ratios_reco[0].GetXaxis().SetTitleSize(15)
        ratios_reco[0].GetXaxis().SetTitleFont(43)
        ratios_reco[0].GetYaxis().SetNdivisions(503)
        ratios_reco[0].GetXaxis().SetNdivisions(410)
        ratios_reco[0].GetYaxis().Centeratios_total[0]itle(True)
        

    p3.cd()
    for iratios_total[0], ratios_total[0] in enumerate(ratios_total):
        if iratios_total[0] == 0:
            ratios_total[0].Draw("hist")
        else:
            ratios_total[0].Draw("hist same")
        ratios_total[0].GetYaxis().SetRangeUser( 0.9, 1.1 )
        ratios_total[0].GetXaxis().SetLabelSize( 0 )
        ratios_total[0].GetYaxis().SetLabelSize( 15 )   
        ratios_total[0].GetYaxis().SetLabelFont(43)
        ratios_total[0].SetTitle("")
        ratios_total[0].GetYaxis().SetTitle("Varied / Nom. (TOTAL)")
        ratios_total[0].GetYaxis().SetTitleOffset( ratios_total[0].GetYaxis().GetTitleOffset() * 0.1 )
        ratios_total[0].GetXaxis().SetTitle("")
        ratios_total[0].GetYaxis().SetTitleSize( ratios_total[0].GetYaxis().GetTitleSize()*2.5 )
        ratios_total[0].GetXaxis().SetTitleOffset(4.0)
        ratios_total[0].GetXaxis().SetTitleSize(0)
        ratios_total[0].GetXaxis().SetTitleFont(43)
        ratios_total[0].GetYaxis().SetNdivisions(503)
        ratios_total[0].GetXaxis().SetNdivisions(410)
        ratios_total[0].GetYaxis().Centeratios_total[0]itle(True)

    p4.cd()
    for irr, rr in enumerate(ratios_ratio):
        
        if irr == 0:
            print("Drawing")
            for ibin in range(1, 1+rr.GetNbinsX()+1):
                print( ibin, rr.GetBinContent(ibin) )
            rr.Draw("hist")
        else:
            print("Drawing with same")
            for ibin in range(1, 1+rr.GetNbinsX()+1):
                print( ibin, rr.GetBinContent(ibin) )
            rr.Draw("hist same")

        rr.GetYaxis().SetRangeUser( 0.9, 1.1 )
        rr.GetXaxis().SetLabelSize( 0.12 )
        rr.GetYaxis().SetLabelSize( 15 )   
        rr.GetYaxis().SetLabelFont(43)
        rr.SetTitle("")
        rr.GetYaxis().SetTitleOffset( rr.GetYaxis().GetTitleOffset() * 0.1 )
        rr.GetYaxis().SetTitleSize( rr.GetYaxis().GetTitleSize()*2.5 )
        rr.GetYaxis().SetTitle("Ratio")
        rr.GetXaxis().SetTitle("Flavor 3l (gen)")
        rr.GetXaxis().SetTitleOffset(4.0)
        rr.GetXaxis().SetTitleSize(26)
        rr.GetXaxis().SetTitleFont(43)
        rr.GetYaxis().SetNdivisions(503)
        rr.GetXaxis().SetNdivisions(410)
        rr.GetYaxis().Centeratios_total[0]itle(True)
        rr.Draw("hist same")
    
    
    p1.cd()
    legend.Draw("same")
    doSpam("34.6 fb^{-1} (13.6 TeV)", 0.75, .933, .975, .96,textSize = 22*0.98)
    doSpam('#splitline{#scale[1.2]{#bf{CMS}}}{#scale[1.0]{#it{Preliminary}}}',.2, .745, .35, .795, textSize = 22)
    c.SaveAs( "checkweights-flavor3lgen-withFid.png" )
    """
