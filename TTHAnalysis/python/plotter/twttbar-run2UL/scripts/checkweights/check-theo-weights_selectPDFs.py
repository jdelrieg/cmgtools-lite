""" Small piece of code to compute trigger efficiencies on data and MC"""
# -- Python libraries
import ROOT as r
import os, sys
from copy import deepcopy
import argparse
import array

import json


# Analysis libraries
sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/twttbar-run2UL"))#wz-run3
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

    main_path_2016   = f"/lustrefs/analysis/nanoAODv9/bb4l/productions/2025-12-23/2016/mergedFiles/" #Let's start for a single year and then keep alltogether
    main_path_2016apv   = f"/lustrefs/analysis/nanoAODv9/bb4l/productions/2025-12-23/2016apv/mergedFiles/"
    main_path_2017   = f"/lustrefs/analysis/nanoAODv9/bb4l/productions/2025-12-23/2017/mergedFiles/"
    main_path_2018   = f"/lustrefs/analysis/nanoAODv9/bb4l/productions/2025-12-23/2018/mergedFiles/"    
    

    main_ntuple = ntuple_reader( 
        samplename = [ 
            os.path.join( main_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),#We are satrting with a single file, later on we should add all the files
            os.path.join( main_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            os.path.join( main_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            os.path.join( main_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),
            os.path.join( main_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_4.root/Events"),
            
            os.path.join( main_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),#We are satrting with a single file, later on we should add all the files
            os.path.join( main_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            os.path.join( main_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            os.path.join( main_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),
            
            os.path.join( main_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),#We are satrting with a single file, later on we should add all the files
            os.path.join( main_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            os.path.join( main_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            os.path.join( main_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),
            os.path.join( main_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_4.root/Events"),
            os.path.join( main_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_5.root/Events"),
            os.path.join( main_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_6.root/Events"),
            os.path.join( main_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_7.root/Events"),
            os.path.join( main_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_8.root/Events"),      

            os.path.join( main_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),#We are satrting with a single file, later on we should add all the files
            os.path.join( main_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            os.path.join( main_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            os.path.join( main_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),
            os.path.join( main_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_4.root/Events"),
            os.path.join( main_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_5.root/Events"),
            os.path.join( main_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_6.root/Events"),
            os.path.join( main_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_7.root/Events"),
            os.path.join( main_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_8.root/Events"),   
            os.path.join( main_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_9.root/Events"),
            os.path.join( main_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_10.root/Events"),
            os.path.join( main_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_11.root/Events"),
            os.path.join( main_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_12.root/Events"),
            
        ],
        friends = [ 
            os.path.join( main_path_2016, "0_jecs/BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0_Friend.root"),
            os.path.join( main_path_2016, "1_lepsuncsAndParticle/BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0_Friend.root"),
            os.path.join( main_path_2016, "2_cleaning/BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0_Friend.root"),
            os.path.join( main_path_2016, "3_varstrigger/BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0_Friend.root"),           #esto creo que aqui no se usa para nada
            os.path.join( main_path_2016, "4_scalefactors/BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0_Friend.root"),
            #os.path.join( main_path, "5_isHF/BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0_Friend.root"),
        ],
        ftreename = "Friends"
    )
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
        "nDressBSelJet == 2"
    ]


    variable = "LepGood_pt_corrAll[0]"
    binning = "25,25,400" #(bins detector)
    binning = [25., 35., 45., 55., 65., 75., 85., 95., 150.] #solo para correr plots rapido [25., 35., 45., 55., 65., 75., 85., 95., 150.],
    #binning = "16,25,400" #(bins particula)

    recocut = " && ".join( [f"({cut})" for cut in reco] )
    fiducialcut = " && ".join( [f"({cut})" for cut in fiducial] )
    outfolder = "plots-fiducial"


    
    shapes_reco = [
        # SCALE WEIGHTS
        ("Nominal",         f"({recocut})*({fiducialcut})*((genWeight))", "(genEventSumw)", "nom", "4"), 
#        ("mur=1.0,muf=2.0", f"({recocut})*({fiducialcut})*(LHEScaleWeight[5]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "muR_1p0_muF=2p0", "5"),
#        ("mur=1.0,muf=0.5", f"({recocut})*({fiducialcut})*(LHEScaleWeight[3]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "muR_1p0_muF=0p5", "3"),
#        ("mur=2.0,muf=1.0", f"({recocut})*({fiducialcut})*(LHEScaleWeight[7]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "muR_2p0_muF=1p0", "7"),
#        ("mur=0.5,muf=1.0", f"({recocut})*({fiducialcut})*(LHEScaleWeight[1]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "muR_0p5_muF=1p0", "1"),
#        ("mur=2.0,muf=2.0", f"({recocut})*({fiducialcut})*(LHEScaleWeight[8]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "muR_2p0_muF=2p0", "8"),
#        ("mur=0.5,muf=0.5", f"({recocut})*({fiducialcut})*(LHEScaleWeight[0]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "muR_0p5_muF=0p5", "0"),
    ]

    for ipdf in range(1, 34):
        shapes_reco.append( (f"pdf{ipdf}", f"({recocut})*({fiducialcut})*(LHEPdfWeight[{ipdf}]/LHEPdfWeight[0])*((genWeight))", f"(genEventSumw)", f"pdf_{ipdf}", f"{ipdf}"))

    shapes_total = [
        # SCALE WEIGHTS
        ("total_Nominal",         f"({fiducialcut})*((genWeight))", "genEventSumw", "nom"),
#        ("total_mur=1.0,muf=2.0", f"({fiducialcut})*(LHEScaleWeight[5]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "scaleweight_5"),
#        ("total_mur=1.0,muf=0.5", f"({fiducialcut})*(LHEScaleWeight[3]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "scaleweight_3"),
#        ("total_mur=2.0,muf=1.0", f"({fiducialcut})*(LHEScaleWeight[7]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "scaleweight_7"),
#        ("total_mur=0.5,muf=1.0", f"({fiducialcut})*(LHEScaleWeight[1]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "scaleweight_1"),
#        ("total_mur=2.0,muf=2.0", f"({fiducialcut})*(LHEScaleWeight[8]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "scaleweight_8"),
#        ("total_mur=0.5,muf=0.5", f"({fiducialcut})*(LHEScaleWeight[0]/LHEScaleWeight[4])*((genWeight))", "(genEventSumw)", "scaleweight_0"),
    ]

    
    for ipdf in range(1, 34):
        shapes_total.append( (f"pdf{ipdf}", f"({fiducialcut})*(LHEPdfWeight[{ipdf}]/LHEPdfWeight[0])*((genWeight))", f"(genEventSumw)", f"pdf_{ipdf}"))

    # Make the histograms
    histos_reco  = []
    histos_total = []
    ratios_reco  = []
    ratios_total = []
    ratios_ratio = []


    for isr, (sr_name, sr, sr_varNormToGenSum, _, asdas) in enumerate( shapes_reco ):
        srtotal_name, srtotal, srtotal_varNormToGenSum, _ = shapes_total[ isr ]
        #print('sr_name',sr_name)
        #print('sr',sr,'sr_varNormToGenSum',sr_varNormToGenSum, '_', _, 'asdas', asdas)
        hreco  = main_ntuple.draw( variable, binning, sr, sr_name, normToGenSum = True, varNormToGenSum =  sr_varNormToGenSum)
        htotal = main_ntuple.draw( variable, binning, srtotal, srtotal_name, normToGenSum = True, varNormToGenSum =  srtotal_varNormToGenSum)       
        print('hreco', hreco.Integral())
        print('hreco bins', [hreco.GetBinContent(ibin) for ibin in range(1, 1+hreco.GetNbinsX())])
        print('htotal', htotal.Integral())
        print('htotal bins', [htotal.GetBinContent(ibin) for ibin in range(1, 1+htotal.GetNbinsX())])

        histos_reco.append( hreco )
        histos_total.append( htotal )

        if isr != 0:
            hreco.SetLineColor( 2 )
            hreco.SetLineWidth( 2 )
            hreco.SetFillColor(0)

            htotal.SetLineColor( 2 )
            htotal.SetLineWidth( 2 )
            htotal.SetFillColor(0)

            ratio_hreco = deepcopy( hreco )
            ratio_hreco.Divide( histos_reco[0] )
            ratio_hreco.SetLineColor( 2 )
            ratio_hreco.SetLineWidth( 2 )
            ratio_hreco.SetFillColor( 0 )
            ratios_reco.append( ratio_hreco )

            ratio_htotal = deepcopy( htotal )
            ratio_htotal.Divide( histos_total[0] )
            ratio_htotal.SetLineColor( 2 )
            ratio_htotal.SetLineWidth( 2 )
            ratio_htotal.SetFillColor( 0 )
            ratios_total.append( ratio_htotal )

            ratio_hratio = deepcopy( ratio_hreco )
            ratio_hratio.Divide( ratio_htotal )
            ratio_hratio.SetLineColor( 2 )
            ratio_hratio.SetLineWidth( 2 )
            ratio_hratio.SetFillColor( 0 )
            ratios_ratio.append( ratio_hratio )

            print('ratios reco',ratios_reco[-1].Integral(),'ratios_total', ratios_total[-1].Integral(),'ratios_ratio', ratios_ratio[-1].Integral())
            print('ratios reco per bin',[ratios_reco[-1].GetBinContent(ibin) for ibin in range(1, 1+ratios_reco[-1].GetNbinsX())])
            print('ratios total per bin (QUE SON LOS QUE TENGO QUE PONER en el ejercicios de separar)',[ratios_ratio[-1].GetBinContent(ibin) for ibin in range(1, 1+ratios_ratio[-1].GetNbinsX())])
            
        else:
            hreco.SetLineColor( 1 )
            hreco.SetLineWidth( 2 )
            hreco.SetFillColor(0)

            htotal.SetLineColor( 1 )
            htotal.SetLineWidth( 2 )
            htotal.SetFillColor(0)
            
            ratio_hreco = deepcopy( hreco )
            ratio_hreco.Divide( hreco )
            ratio_hreco.SetLineColor( 1 )
            ratio_hreco.SetLineWidth( 2 )
            ratio_hreco.SetFillColor( 0 )
            ratios_reco.append( ratio_hreco )

            ratio_htotal = deepcopy( htotal )
            ratio_htotal.Divide( htotal )
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
        
        print(f" >>> ISR: {isr}")
        for ibin in range(1, 1+hreco.GetNbinsX()):
            print(f"    - {ibin}: reco={ratio_hreco.GetBinContent(ibin):3.3f}, total={ratio_htotal.GetBinContent(ibin):3.3f}, ratio={ratio_hratio.GetBinContent(ibin):3.3f}")
    # Write out the results 


    ## Plot
    for ih, h in enumerate(histos_reco[1:]):
        name_plot = f"{shapes_reco[ih+1][-2]}"
        name = f"{shapes_reco[ih][-2]}"
        height = 0.05 * 1.15 * 7

        if variable == "LepGood_pt_corrAll[0]":
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
        
        
        
        
        c = r.TCanvas(f"canvas_{name_plot}", "",  800, 800)
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
        doSpam("138 fb^{-1} (13 TeV)", 0.75, .933, .975, .96,textSize = 22*0.98)
        doSpam('#splitline{#scale[1.2]{#bf{CMS}}}{#scale[1.0]{#it{Preliminary}}}',.2, .745, .35, .795, textSize = 22)

        if not os.path.exists( outfolder ):
            os.system( f"mkdir -p {outfolder}" )
        c.SaveAs( f"{outfolder}/{name_plot}.png" )

    
        # Now write a txt
        weight_index = shapes_reco[ih][-1]
        f = open( f"{outfolder}/fr-{name}.txt", "w" )

        if "pdf" in name:
            f.write(f"# This number has been computed by properly normalizing to the fiducial cross section of the bb4l sample\n")
            f.write(f"weight : LHEPdfWeight[{weight_index}]\n")
            f.write(f"weight   : {ratios_reco[ih].Integral() / ratios_total[ih].Integral()}\n")
                    #alt-normm
            f.write(f"# Individual bins {[ratios_ratio[ih].GetBinContent(ibin) for ibin in range(1, 1+ratios_ratio[ih].GetNbinsX())]}\n")
            
        else:
            f.write(f"# This number has been computed by properly normalizing to the fiducial cross section of the bb4l sample\n")
            f.write(f"weight : LHEScaleWeight[{weight_index}]\n")
            f.write(f"weight   : {ratios_reco[ih].Integral() / ratios_total[ih].Integral()}\n")
                   #alt-norm
            f.write(f"# Individual bins {[ratios_ratio[ih].GetBinContent(ibin) for ibin in range(1, 1+ratios_ratio[ih].GetNbinsX())]}\n")
            
        f.close()

