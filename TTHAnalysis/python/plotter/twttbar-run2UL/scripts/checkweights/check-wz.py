""" Small piece of code to compute trigger efficiencies on data and MC"""
# -- Python libraries
import ROOT as r
import os, sys
from copy import deepcopy
import argparse
import array

import json


# Analysis libraries
sys.path.append( os.path.join("../../../wz-run3"))
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

    run3_path   = f"/lustrefs/hdd_pool_dir/nanoAODv12/wz-run3/trees_v3/data/2022"

    files = [_file for _file in os.listdir( run3_path ) if ".root" in _file ]
    
    # Create ntuple readers for each file
    ntuples = [
        ntuple_reader( 
            samplename = [ 
                os.path.join( run3_path, f"EGamma_Run2022C.root/Events") 
            ],
            friends = [ 
                os.path.join( run3_path, f"leptonJetRecleaning/EGamma_Run2022C_Friend.root"),
                os.path.join( run3_path, f"lepmva/EGamma_Run2022C_Friend.root"),
                os.path.join( run3_path, f"leptonBuilder/EGamma_Run2022C_Friend.root"),
            ],
            ftreename = "Friends"
        ),
        ntuple_reader( 
            samplename = [ 
                os.path.join( run3_path, f"EGamma_Run2022D.root/Events") 
            ],
            friends = [ 
                os.path.join( run3_path, f"leptonJetRecleaning/EGamma_Run2022D_Friend.root"),
                os.path.join( run3_path, f"lepmva/EGamma_Run2022D_Friend.root"),
                os.path.join( run3_path, f"leptonBuilder/EGamma_Run2022D_Friend.root"),
            ],
            ftreename = "Friends"
        ),
        ntuple_reader( 
            samplename = [ 
                os.path.join( run3_path, f"Muon_Run2022C.root/Events") 
            ],
            friends = [ 
                os.path.join( run3_path, f"leptonJetRecleaning/Muon_Run2022C_Friend.root"),
                os.path.join( run3_path, f"lepmva/Muon_Run2022C_Friend.root"),
                os.path.join( run3_path, f"leptonBuilder/Muon_Run2022C_Friend.root"),
            ],
            ftreename = "Friends"
        ),
        ntuple_reader( 
            samplename = [ 
                os.path.join( run3_path, f"Muon_Run2022D.root/Events") 
            ],
            friends = [ 
                os.path.join( run3_path, f"leptonJetRecleaning/Muon_Run2022D_Friend.root"),
                os.path.join( run3_path, f"lepmva/Muon_Run2022D_Friend.root"),
                os.path.join( run3_path, f"leptonBuilder/Muon_Run2022D_Friend.root"),
            ],
            ftreename = "Friends"
        ),       
        ntuple_reader( 
            samplename = [ 
                os.path.join( run3_path, f"MuonEG_Run2022C.root/Events") 
            ],
            friends = [ 
                os.path.join( run3_path, f"leptonJetRecleaning/MuonEG_Run2022C_Friend.root"),
                os.path.join( run3_path, f"lepmva/MuonEG_Run2022C_Friend.root"),
                os.path.join( run3_path, f"leptonBuilder/MuonEG_Run2022C_Friend.root"),
            ],
            ftreename = "Friends"
        ),
        ntuple_reader( 
            samplename = [ 
                os.path.join( run3_path, f"MuonEG_Run2022D.root/Events") 
            ],
            friends = [ 
                os.path.join( run3_path, f"leptonJetRecleaning/MuonEG_Run2022D_Friend.root"),
                os.path.join( run3_path, f"lepmva/MuonEG_Run2022D_Friend.root"),
                os.path.join( run3_path, f"leptonBuilder/MuonEG_Run2022D_Friend.root"),
            ],
            ftreename = "Friends"
        )
    ]
    variable = "1"
    binning = "1,0.5,1.5"

    reco = [
        "Flag_goodVertices && Flag_eeBadScFilter && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter",
        "Trigger_3l || HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL",
        "nLepSel >= 3",
        #"nLepGood < 4",
        #"(event == 121735242 && run == 356946 && luminosityBlock == 73)"
        #"LepSel_isTight[0] && LepSel_isTight[1] && LepSel_isTight[2]",
        #"LepZ1_pt >= 25 && LepZ2_pt >= 15 && LepW_pt >= 25",
        #"abs(LepSel_pdgId[0]) < 15 && abs(LepSel_pdgId[1]) < 15 && abs(LepSel_pdgId[2]) < 15 && nOSSF_3l >= 1",
        #"m3L >= 100",
        #"MET_pt_central > 35",
        #"nBJetTight25_Mini == 0",
        #"abs(mll_3l - 91.16) < 15",
        #"minMllSFOS_Mini > 4 || minMllSFOS_Mini == -1",
        #"LepGood_tightCharge[0]==2 && LepGood_tightCharge[1]==2 && LepGood_tightCharge[2]==2"
    ]
    string = "event:run:luminosityBlock:LepGood_isFO_Mini[0]:LepGood_isFO_Mini[1]:LepGood_isFO_Mini[2]"
    recocut = " && ".join( [f"({cut})" for cut in reco] )
    total_events = 0
    for ntuple in ntuples[:1]: 
        hreco  = ntuple.draw( variable, binning, recocut, f"tot_weight_{ntuple.samplename[0].split('/')[-2]}", normToGenSum = False )
        total_events += hreco.Integral() 
        #hreco  = ntuple.scan( string, recocut )

    print(f"Total events: {total_events}")
