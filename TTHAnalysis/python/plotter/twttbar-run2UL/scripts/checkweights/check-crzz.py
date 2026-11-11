""" Small piece of code to compute trigger efficiencies on data and MC"""
# -- Python libraries
import ROOT as r
import os, sys
from copy import deepcopy
import argparse
import array

import json


# Analysis libraries
sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/wz-run3"))
from functions import color_msg
from scripts.ntuple_reader import ntuple_reader
from scripts.make_latex_table import dict_to_latex_table

# Turn off root gui mode
r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(1)
r.gStyle.SetPadTickX(1)
r.gStyle.SetPadTickY(1)


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


    #run3_path   = f"/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v3/mc/2022"
    run3_path   = f"/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v3/mc/2022/"
    

    run3_ntuple = ntuple_reader( 
        samplename = [ 
            os.path.join( run3_path, "ZZto4L_part1.root/Events") 
        ],
        friends = [ 
            os.path.join( run3_path, "leptonJetRecleaning/ZZto4L_part1_Friend.root"),
            os.path.join( run3_path, "leptonBuilder/ZZto4L_part1_Friend.root"),
            os.path.join( run3_path, "scalefactors_chargeID/ZZto4L_part1_Friend.root"),
            #os.path.join( run3_path, "lepGEN_withTau/ZZto4L_part1_Friend.root"),
        ],
        ftreename = "Friends"
    )
    reco = [
        "1",
        #"$DATA{Flag_eeBadScFilter && Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter} $MC{Flag_eeBadScFilter && Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter}",
        "Trigger_3l || HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
        "nLepSel == 4",
        "LepSel_isTight[0] == 1 && LepSel_isTight[1] == 1 && LepSel_isTight[2] == 1 && LepSel_isTight[3] == 1",
        "LepZ1_pt >= 25 && LepZ2_pt >= 15 && LepW_pt >= 25 && LepZ3_pt > 15",
        "abs(LepSel_pdgId[0]) < 15 && abs(LepSel_pdgId[1]) < 15 && abs(LepSel_pdgId[2]) < 15 && nOSSF_3l >= 1",
        "m3L >= 100",
        "nBJetTight25_Mini == 0",
        "abs(mll_3l - 91.16) < 15",
        "minMllSFOS_Mini > 4 || minMllSFOS_Mini == -1",
        #"((abs(LepSel_pdgId[0]) + abs(LepSel_pdgId[1]) + abs(LepSel_pdgId[2]) + abs(LepSel_pdgId[3]) - 44)/2)%2 == 0",
        "LepGood_tightCharge[0]==2 && LepGood_tightCharge[1]==2 && LepGood_tightCharge[2]==2 && LepGood_tightCharge[3]==2",
    ]

    total_charge_zero = "abs( abs(LepSel_pdgId[0])/LepSel_pdgId[0] + abs(LepSel_pdgId[1])/LepSel_pdgId[1] + abs(LepSel_pdgId[2])/LepSel_pdgId[2] + abs(LepSel_pdgId[3])/LepSel_pdgId[3] ) == 0"

    variable = "1"

    cr = " && ".join( f"({cut})" for cut in reco )
    cr_charge = " && ".join( f"({cut})" for cut in reco + [total_charge_zero])

    print(cr)

    hreco  = run3_ntuple.draw( variable, "2,1,2", cr, "nocharge", normToGenSum = False)
    htotal = run3_ntuple.draw( variable, "2,1,2", cr_charge, "charge", normToGenSum = False)       
    
    print( hreco.Integral(), htotal.Integral(), hreco.Integral()/htotal.Integral() )