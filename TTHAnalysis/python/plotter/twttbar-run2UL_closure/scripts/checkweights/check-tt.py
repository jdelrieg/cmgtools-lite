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
    


    for part in (1, 2, 3, 4, 5, 6): 
        run3_ntuple = ntuple_reader( 
            samplename = [ 
                os.path.join( run3_path, f"TTto2L2Nu_part{part}.root/Events") 
            ],
            friends = [ 
                os.path.join( run3_path, f"leptonJetRecleaning/TTto2L2Nu_part{part}_Friend.root"),
                os.path.join( run3_path, f"leptonBuilder/TTto2L2Nu_part{part}_Friend.root"),
                os.path.join( run3_path, f"scalefactors_chargeID/TTto2L2Nu_part{part}_Friend.root"),
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
    
    
        variable = "1"
        binning = "1,0.5,1.5"
        recocut = " && ".join( [f"({cut})" for cut in reco] )
    
        
    
        hreco  = run3_ntuple.draw( variable, binning, f"({recocut})*((genWeight*puWeight_fix*bTagWeight*electronSF*muonSF*8.0*97.4488*1000))", f"name_{part}", normToGenSum = True, varNormToGenSum =  "genEventSumw")
            
        print(part, hreco.Integral(), hreco.GetBinContent(1) ) 
