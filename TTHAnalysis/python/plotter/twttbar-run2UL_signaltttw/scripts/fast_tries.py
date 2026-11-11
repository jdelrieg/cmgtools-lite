""" Small piece of code to compute trigger efficiencies on data and MC"""
# -- Python libraries
import ROOT as r
import os, sys
from copy import deepcopy
from optparse import OptionParser
import array
from optparse import OptionParser
import json

# Analysis libraries
sys.path.append( os.path.join(os.environ["CMSSW_BASE"], "src/CMGTools/TTHAnalysis/python/plotter/twttbar-run2UL"))
from functions import color_msg
import canvas as cv 
from scripts.ntuple_reader import ntuple_reader
from scripts.make_latex_table import dict_to_latex_table

# Turn off root gui mode
r.gROOT.SetBatch(1)
r.gStyle.SetOptStat(0)

def add_parsing_opts():
    ''' Function with base parsing arguments used by any script '''
    parser = OptionParser(usage = "python wz-run.py [options]", 
                                    description = "Main options for running WZ analysis")
    return parser.parse_args()

if __name__ == "__main__":

    opts, args = add_parsing_opts()

    legacy_path_2016apv = f"/pool/phedex/userstorage/jriego/nanoAODv9/bb4l/productions/2025-12-23/2016apv/mergedFiles/"
    legacy_path_2016 = f"/pool/phedex/userstorage/jriego/nanoAODv9/bb4l/productions/2025-12-23/2016/mergedFiles/"
    legacy_path_2017 = f"/pool/phedex/userstorage/jriego/nanoAODv9/bb4l/productions/2025-12-23/2017/mergedFiles/"
    legacy_path_2018 = f"/pool/phedex/userstorage/jriego/nanoAODv9/bb4l/productions/2025-12-23/2018/mergedFiles/"
    
    legacy_path_2016apv_old = f"/pool/phedex/userstorage/jriego/nanoAODv9/bb4l/productions/2025-12-23/2016apv/old_bb4l/"
    legacy_path_2017_old = f"/pool/phedex/userstorage/jriego/nanoAODv9/bb4l/productions/2025-12-23/2017/old_bb4l/"
    legacy_path_2018_old = f"/pool/phedex/userstorage/jriego/nanoAODv9/bb4l/productions/2025-12-23/2018/old_bb4l/"

    legacy_ntuple = ntuple_reader( 
        samplename = [ 
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_4.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_5.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_6.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_7.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_8.root/Events"),
            
            #os.path.join( legacy_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),
            #os.path.join( legacy_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            #os.path.join( legacy_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            #os.path.join( legacy_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),

            #os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),
            #os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            #os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            #os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),
            #os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_4.root/Events"),
            #os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_5.root/Events"),
            #os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_6.root/Events"),
            #os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_7.root/Events"),
            #os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_8.root/Events"),                        

            #os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),
            #os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            #os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            #os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),
            #os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_4.root/Events"),
            #os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_5.root/Events"),
            #os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_6.root/Events"),
            #os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_7.root/Events"),
            #os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_8.root/Events"), 
            #os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_9.root/Events"),
            #os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_10.root/Events"),
            #os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_11.root/Events"),
            #os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_12.root/Events")
            '''
            os.path.join( legacy_path_2016, "SingleElectron_0.root/Events"),
            os.path.join( legacy_path_2016, "SingleMuon_0.root/Events"),
            os.path.join( legacy_path_2016, "SingleMuon_1.root/Events"),
            os.path.join( legacy_path_2016, "MuonEG_0.root/Events"),
            os.path.join( legacy_path_2016, "DoubleEG_0.root/Events"),
            os.path.join( legacy_path_2016, "DoubleMuon_0.root/Events"),
            os.path.join( legacy_path_2016, "DoubleMuon_1.root/Events"), 

            os.path.join( legacy_path_2016apv, "SingleElectron_0.root/Events"),
            os.path.join( legacy_path_2016apv, "SingleElectron_1.root/Events"),
            os.path.join( legacy_path_2016apv, "SingleMuon_0.root/Events"),
            os.path.join( legacy_path_2016apv, "SingleMuon_1.root/Events"),
            os.path.join( legacy_path_2016apv, "MuonEG_0.root/Events"),
            os.path.join( legacy_path_2016apv, "DoubleEG_0.root/Events"),
            os.path.join( legacy_path_2016apv, "DoubleMuon_0.root/Events"),
            os.path.join( legacy_path_2016apv, "DoubleMuon_1.root/Events"),
            
            os.path.join( legacy_path_2017, "SingleElectron_0.root/Events"),
            os.path.join( legacy_path_2017, "SingleElectron_1.root/Events"),
            os.path.join( legacy_path_2017, "SingleElectron_2.root/Events"),            
            os.path.join( legacy_path_2017, "SingleMuon_0.root/Events"),
            os.path.join( legacy_path_2017, "SingleMuon_1.root/Events"),
            os.path.join( legacy_path_2017, "SingleMuon_2.root/Events"),
            os.path.join( legacy_path_2017, "SingleMuon_3.root/Events"),
            os.path.join( legacy_path_2017, "SingleMuon_4.root/Events"),            
            os.path.join( legacy_path_2017, "MuonEG_0.root/Events"),
            os.path.join( legacy_path_2017, "DoubleEG_0.root/Events"),
            os.path.join( legacy_path_2017, "DoubleEG_1.root/Events"),
            os.path.join( legacy_path_2017, "DoubleEG_2.root/Events"),            
            os.path.join( legacy_path_2017, "DoubleMuon_0.root/Events"),
            os.path.join( legacy_path_2017, "DoubleMuon_1.root/Events"),             
            os.path.join( legacy_path_2017, "DoubleMuon_2.root/Events"),
            os.path.join( legacy_path_2017, "DoubleMuon_3.root/Events"),
           
            os.path.join( legacy_path_2018, "SingleMuon_0.root/Events"),
            os.path.join( legacy_path_2018, "SingleMuon_1.root/Events"),
            os.path.join( legacy_path_2018, "SingleMuon_2.root/Events"),
            os.path.join( legacy_path_2018, "SingleMuon_3.root/Events"),
            os.path.join( legacy_path_2018, "SingleMuon_4.root/Events"),            
            os.path.join( legacy_path_2018, "SingleMuon_5.root/Events"),
            os.path.join( legacy_path_2018, "SingleMuon_6.root/Events"),
            os.path.join( legacy_path_2018, "MuonEG_0.root/Events"),
            os.path.join( legacy_path_2018, "EGamma_0.root/Events"),
            os.path.join( legacy_path_2018, "EGamma_1.root/Events"),
            os.path.join( legacy_path_2018, "EGamma_2.root/Events"),            
            os.path.join( legacy_path_2018, "EGamma_3.root/Events"),
            os.path.join( legacy_path_2018, "DoubleMuon_0.root/Events"),
            os.path.join( legacy_path_2018, "DoubleMuon_1.root/Events"),             
            os.path.join( legacy_path_2018, "DoubleMuon_2.root/Events"),
            os.path.join( legacy_path_2018, "DoubleMuon_3.root/Events"),
            os.path.join( legacy_path_2018, "DoubleMuon_4.root/Events"),
            os.path.join( legacy_path_2018, "DoubleMuon_5.root/Events")
            '''
        ],
        friends = [ 
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_TTTo2L2Nu_part0.root")
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_WZTo3LNu_pow.root")
        ],
        ftreename = "sf/t"
    )

    legacy_ntuple_2016 = ntuple_reader( 
        samplename = [ 
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_4.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_5.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_6.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_7.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_8.root/Events"),
            
            #os.path.join( legacy_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),
            #os.path.join( legacy_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            #os.path.join( legacy_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            #os.path.join( legacy_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events")

            
            os.path.join( legacy_path_2016, "SingleElectron_0.root/Events"),
            os.path.join( legacy_path_2016, "SingleMuon_0.root/Events"),
            os.path.join( legacy_path_2016, "SingleMuon_1.root/Events"),
            os.path.join( legacy_path_2016, "MuonEG_0.root/Events"),
            os.path.join( legacy_path_2016, "DoubleEG_0.root/Events"),
            os.path.join( legacy_path_2016, "DoubleMuon_0.root/Events"),
            os.path.join( legacy_path_2016, "DoubleMuon_1.root/Events"), 

            os.path.join( legacy_path_2016apv, "SingleElectron_0.root/Events"),
            os.path.join( legacy_path_2016apv, "SingleElectron_1.root/Events"),
            os.path.join( legacy_path_2016apv, "SingleMuon_0.root/Events"),
            os.path.join( legacy_path_2016apv, "SingleMuon_1.root/Events"),
            os.path.join( legacy_path_2016apv, "MuonEG_0.root/Events"),
            os.path.join( legacy_path_2016apv, "DoubleEG_0.root/Events"),
            os.path.join( legacy_path_2016apv, "DoubleMuon_0.root/Events"),
            os.path.join( legacy_path_2016apv, "DoubleMuon_1.root/Events") 
        ],
        friends = [ 
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_TTTo2L2Nu_part0.root")
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_WZTo3LNu_pow.root")
        ],
        ftreename = "sf/t"
    )

    legacy_ntuple_2016_mc = ntuple_reader( 
        samplename = [ 
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_4.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_5.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_6.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_7.root/Events"),
            #os.path.join( legacy_path_2016, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_8.root/Events"),
            
            os.path.join( legacy_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),
            os.path.join( legacy_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            os.path.join( legacy_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            os.path.join( legacy_path_2016apv, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events")
        ],
        friends = [ 
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_TTTo2L2Nu_part0.root")
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_WZTo3LNu_pow.root")
        ],
        ftreename = "sf/t"
    )

    legacy_ntuple_2017_old = ntuple_reader( 
        samplename = [ 
            
            os.path.join( legacy_path_2017_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),
            os.path.join( legacy_path_2017_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            os.path.join( legacy_path_2017_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            os.path.join( legacy_path_2017_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),
            os.path.join( legacy_path_2017_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_4.root/Events"),
            os.path.join( legacy_path_2017_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_5.root/Events"),
            os.path.join( legacy_path_2017_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_6.root/Events"),
            os.path.join( legacy_path_2017_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_7.root/Events"),
            os.path.join( legacy_path_2017_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_8.root/Events")
        ],
        friends = [ 
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_TTTo2L2Nu_part0.root")
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_WZTo3LNu_pow.root")
        ],
        ftreename = "sf/t"
    )

    legacy_ntuple_2017 = ntuple_reader( 
        samplename = [ 
          

            os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),
            os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),
            os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_4.root/Events"),
            os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_5.root/Events"),
            os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_6.root/Events"),
            os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_7.root/Events"),
            os.path.join( legacy_path_2017, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_8.root/Events")
            #os.path.join( legacy_path_2017, "SingleElectron_0.root/Events"),
            #os.path.join( legacy_path_2017, "SingleElectron_1.root/Events"),
            #os.path.join( legacy_path_2017, "SingleElectron_2.root/Events"),            
            #os.path.join( legacy_path_2017, "SingleMuon_0.root/Events"),
            #os.path.join( legacy_path_2017, "SingleMuon_1.root/Events"),
            #os.path.join( legacy_path_2017, "SingleMuon_2.root/Events"),
            #os.path.join( legacy_path_2017, "SingleMuon_3.root/Events"),
            #os.path.join( legacy_path_2017, "SingleMuon_4.root/Events"),            
            #os.path.join( legacy_path_2017, "MuonEG_0.root/Events"),
            #os.path.join( legacy_path_2017, "DoubleEG_0.root/Events"),
            #os.path.join( legacy_path_2017, "DoubleEG_1.root/Events"),
            #os.path.join( legacy_path_2017, "DoubleEG_2.root/Events"),            
            #os.path.join( legacy_path_2017, "DoubleMuon_0.root/Events"),
            #os.path.join( legacy_path_2017, "DoubleMuon_1.root/Events"),             
            #os.path.join( legacy_path_2017, "DoubleMuon_2.root/Events"),
            #os.path.join( legacy_path_2017, "DoubleMuon_3.root/Events")            
 
        ],
        friends = [ 
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_TTTo2L2Nu_part0.root")
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_WZTo3LNu_pow.root")
        ],
        ftreename = "sf/t"
    )

    legacy_ntuple_2018 = ntuple_reader( 
        samplename = [ 
                      

            os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),
            os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),
            os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_4.root/Events"),
            os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_5.root/Events"),
            os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_6.root/Events"),
            os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_7.root/Events"),
            os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_8.root/Events"), 
            os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_9.root/Events"),
            os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_10.root/Events"),
            os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_11.root/Events"),
            os.path.join( legacy_path_2018, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_12.root/Events")
            #os.path.join( legacy_path_2018, "SingleMuon_0.root/Events"),
            #os.path.join( legacy_path_2018, "SingleMuon_1.root/Events"),
            #os.path.join( legacy_path_2018, "SingleMuon_2.root/Events"),
            #os.path.join( legacy_path_2018, "SingleMuon_3.root/Events"),
            #os.path.join( legacy_path_2018, "SingleMuon_4.root/Events"),            
            #os.path.join( legacy_path_2018, "SingleMuon_5.root/Events"),
            #os.path.join( legacy_path_2018, "SingleMuon_6.root/Events"),
            #os.path.join( legacy_path_2018, "MuonEG_0.root/Events"),
            #os.path.join( legacy_path_2018, "EGamma_0.root/Events"),
            #os.path.join( legacy_path_2018, "EGamma_1.root/Events"),
            #os.path.join( legacy_path_2018, "EGamma_2.root/Events"),            
            #os.path.join( legacy_path_2018, "EGamma_3.root/Events"),
            #os.path.join( legacy_path_2018, "DoubleMuon_0.root/Events"),
            #os.path.join( legacy_path_2018, "DoubleMuon_1.root/Events"),             
            #os.path.join( legacy_path_2018, "DoubleMuon_2.root/Events"),
            #os.path.join( legacy_path_2018, "DoubleMuon_3.root/Events"),
            #os.path.join( legacy_path_2018, "DoubleMuon_4.root/Events"),
            #os.path.join( legacy_path_2018, "DoubleMuon_5.root/Events")            
 
        ],
        friends = [ 
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_TTTo2L2Nu_part0.root")
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_WZTo3LNu_pow.root")
        ],
        ftreename = "sf/t"
    )


    legacy_ntuple_2018_old = ntuple_reader( 
        samplename = [ 
            os.path.join( legacy_path_2018_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_0.root/Events"),
            os.path.join( legacy_path_2018_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_1.root/Events"),
            os.path.join( legacy_path_2018_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_2.root/Events"),
            os.path.join( legacy_path_2018_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_3.root/Events"),
            os.path.join( legacy_path_2018_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_4.root/Events"),
            os.path.join( legacy_path_2018_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_5.root/Events"),
            os.path.join( legacy_path_2018_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_6.root/Events"),
            os.path.join( legacy_path_2018_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_7.root/Events"),
            os.path.join( legacy_path_2018_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_8.root/Events"), 
            os.path.join( legacy_path_2018_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_9.root/Events"),
            os.path.join( legacy_path_2018_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_10.root/Events"),
            os.path.join( legacy_path_2018_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_11.root/Events"),
            os.path.join( legacy_path_2018_old, "BBLLNuNu_TuneCP5_13TeV_powheg_pythia8_12.root/Events")     
 
        ],
        friends = [ 
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_TTTo2L2Nu_part0.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_TTTo2L2Nu_part0.root")
            #os.path.join( legacy_path, "leptonJetReCleanerWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "leptonBuilderWZSM/evVarFriend_WZTo3LNu_pow.root"),
            #os.path.join( legacy_path, "bTagEventWeights_NEWID/evVarFriend_WZTo3LNu_pow.root")
        ],
        ftreename = "sf/t"
    )

    sr_2018 = [ #2j2t
      "HLT_Ele32_WPTight_Gsf && HLT_IsoMu24 && (HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL || HLT_DoubleEle25_CaloIdL_MW ) && HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8 && (HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL || HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ)",      #trigger up
      "((year == 2016) && (Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter && Flag_BadPFMuonDzFilter && Flag_eeBadScFilter)) || ((year != 2016) && (Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter && Flag_BadPFMuonDzFilter && Flag_eeBadScFilter && Flag_ecalBadCalibFilter))",
      #metfilters
      
      "(nLepGood == 2)",
      "(abs(LepGood_pdgId[0]) == 11 && abs(LepGood_pdgId[1]) == 13) || (abs(LepGood_pdgId[0]) == 11 && abs(LepGood_pdgId[1]) == 13)",
      "LepGood_pdgId[0]*LepGood_pdgId[1]<0", #emu opposite sign
      
      "(LepGood_pt[0]>25)&&(LepGood_pt[1]>20)", #pt requirement in leptons
      
      
      "(Jet_pt>30)&&(abs(Jet_eta)<2.4)",
      "Jet_jetId==6",
      "((Jet_pt<50)&&(Jet_puId)>0) || (Jet_pt>=50)", #basic preselection of jets. Assuming jetId==6 means the 4th bullet of AN
      
      "(nJet==2)",
      "((((Jet_btagDeepFlavB[0]>0.2543) + (Jet_btagDeepFlavB[1]>0.2543) +(Jet_btagDeepFlavB[2]>0.2543) + (Jet_btagDeepFlavB[3]>0.2543)+(Jet_btagDeepFlavB[4]>0.2543) + (Jet_btagDeepFlavB[5]>0.2543) +(Jet_btagDeepFlavB[6]>0.2543) + (Jet_btagDeepFlavB[7]>0.2543)+(Jet_btagDeepFlavB[8]>0.2543) + (Jet_btagDeepFlavB[9]>0.2543))==2)&&(year==2016)) || ((((Jet_btagDeepFlavB[0]>0.3040) + (Jet_btagDeepFlavB[1]>0.3040) +(Jet_btagDeepFlavB[2]>0.3040) + (Jet_btagDeepFlavB[3]>0.3040)+(Jet_btagDeepFlavB[4]>0.3040) + (Jet_btagDeepFlavB[5]>0.3040) +(Jet_btagDeepFlavB[6]>0.3040) + (Jet_btagDeepFlavB[7]>0.3040)+(Jet_btagDeepFlavB[8]>0.3040) + (Jet_btagDeepFlavB[9]>0.3040))==2)&&(year==2017)) || ((((Jet_btagDeepFlavB[0]>0.2783) + (Jet_btagDeepFlavB[1]>0.2783) +(Jet_btagDeepFlavB[2]>0.2783) + (Jet_btagDeepFlavB[3]>0.2783)+(Jet_btagDeepFlavB[4]>0.2783) + (Jet_btagDeepFlavB[5]>0.2783) +(Jet_btagDeepFlavB[6]>0.2783) + (Jet_btagDeepFlavB[7]>0.2783)+(Jet_btagDeepFlavB[8]>0.2783) + (Jet_btagDeepFlavB[9]>0.2783))==2)&&(year==2018))",
      #2jets-2bjets (pequeña trampilla pa unir 2016, 2016apv)
      "abs(sqrt(2*LepGood_pt[0]*LepGood_pt[1]*(cosh(LepGood_eta[0]-LepGood_eta[1])-cos(LepGood_phi[0]-LepGood_phi[1])))-91)>15"
    ]
    
    sr_sel_2018 = " && ".join(sr_2018)
    
    sr_2017 = [ #2j2t
      "( (HLT_Ele35_WPTight_Gsf && HLT_IsoMu27 && (HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL ||HLT_DoubleEle33_CaloIdL_MW) && (HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ || HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8 || HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8) && (HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL || HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ) )&&(year==2017))",
      #trigger up
      "((year == 2016) && (Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter && Flag_BadPFMuonDzFilter && Flag_eeBadScFilter)) || ((year != 2016) && (Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter && Flag_BadPFMuonDzFilter && Flag_eeBadScFilter && Flag_ecalBadCalibFilter))",
      #metfilters
      
      "(nLepGood == 2)",
      "(abs(LepGood_pdgId[0]) == 11 && abs(LepGood_pdgId[1]) == 13) || (abs(LepGood_pdgId[0]) == 11 && abs(LepGood_pdgId[1]) == 13)",
      "LepGood_pdgId[0]*LepGood_pdgId[1]<0", #emu opposite sign
      
      "(LepGood_pt[0]>25)&&(LepGood_pt[1]>20)", #pt requirement in leptons
      
      
      "(Jet_pt>30)&&(abs(Jet_eta)<2.4)",
      "Jet_jetId==6",
      "((Jet_pt<50)&&(Jet_puId)>0) || (Jet_pt>=50)", #basic preselection of jets. Assuming jetId==6 means the 4th bullet of AN
      
      "(nJet==2)",
      "((((Jet_btagDeepFlavB[0]>0.2543) + (Jet_btagDeepFlavB[1]>0.2543) +(Jet_btagDeepFlavB[2]>0.2543) + (Jet_btagDeepFlavB[3]>0.2543)+(Jet_btagDeepFlavB[4]>0.2543) + (Jet_btagDeepFlavB[5]>0.2543) +(Jet_btagDeepFlavB[6]>0.2543) + (Jet_btagDeepFlavB[7]>0.2543)+(Jet_btagDeepFlavB[8]>0.2543) + (Jet_btagDeepFlavB[9]>0.2543))==2)&&(year==2016)) || ((((Jet_btagDeepFlavB[0]>0.3040) + (Jet_btagDeepFlavB[1]>0.3040) +(Jet_btagDeepFlavB[2]>0.3040) + (Jet_btagDeepFlavB[3]>0.3040)+(Jet_btagDeepFlavB[4]>0.3040) + (Jet_btagDeepFlavB[5]>0.3040) +(Jet_btagDeepFlavB[6]>0.3040) + (Jet_btagDeepFlavB[7]>0.3040)+(Jet_btagDeepFlavB[8]>0.3040) + (Jet_btagDeepFlavB[9]>0.3040))==2)&&(year==2017)) || ((((Jet_btagDeepFlavB[0]>0.2783) + (Jet_btagDeepFlavB[1]>0.2783) +(Jet_btagDeepFlavB[2]>0.2783) + (Jet_btagDeepFlavB[3]>0.2783)+(Jet_btagDeepFlavB[4]>0.2783) + (Jet_btagDeepFlavB[5]>0.2783) +(Jet_btagDeepFlavB[6]>0.2783) + (Jet_btagDeepFlavB[7]>0.2783)+(Jet_btagDeepFlavB[8]>0.2783) + (Jet_btagDeepFlavB[9]>0.2783))==2)&&(year==2018))",
      #2jets-2bjets (pequeña trampilla pa unir 2016, 2016apv)
      "abs(sqrt(2*LepGood_pt[0]*LepGood_pt[1]*(cosh(LepGood_eta[0]-LepGood_eta[1])-cos(LepGood_phi[0]-LepGood_phi[1])))-91)>15"
    ]
    
    sr_sel_2017 = " && ".join(sr_2017)    
    
    sr_2016 = [ #2j2t
      " ((HLT_Ele27_WPTight_Gsf && (HLT_IsoMu24 || HLT_IsoTkMu24) && (HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ || HLT_DoubleEle33_CaloIdL_MW || HLT_DoubleEle33_CaloIdL_GsfTrkIdVL) && (HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL || HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL) && (HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL || HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL) )&&(year==2016))",
      #trigger up
      "((year == 2016) && (Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter && Flag_BadPFMuonDzFilter && Flag_eeBadScFilter)) || ((year != 2016) && (Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter && Flag_BadPFMuonDzFilter && Flag_eeBadScFilter && Flag_ecalBadCalibFilter))",
      #metfilters
      
      "(nLepGood == 2)",
      "(abs(LepGood_pdgId[0]) == 11 && abs(LepGood_pdgId[1]) == 13) || (abs(LepGood_pdgId[0]) == 11 && abs(LepGood_pdgId[1]) == 13)",
      "LepGood_pdgId[0]*LepGood_pdgId[1]<0", #emu opposite sign
      
      "(LepGood_pt[0]>25)&&(LepGood_pt[1]>20)", #pt requirement in leptons
      
      
      "(Jet_pt>30)&&(abs(Jet_eta)<2.4)",
      "Jet_jetId==6",
      "((Jet_pt<50)&&(Jet_puId)>0) || (Jet_pt>=50)", #basic preselection of jets. Assuming jetId==6 means the 4th bullet of AN
      
      "(nJet==2)",
      "((((Jet_btagDeepFlavB[0]>0.2543) + (Jet_btagDeepFlavB[1]>0.2543) +(Jet_btagDeepFlavB[2]>0.2543) + (Jet_btagDeepFlavB[3]>0.2543)+(Jet_btagDeepFlavB[4]>0.2543) + (Jet_btagDeepFlavB[5]>0.2543) +(Jet_btagDeepFlavB[6]>0.2543) + (Jet_btagDeepFlavB[7]>0.2543)+(Jet_btagDeepFlavB[8]>0.2543) + (Jet_btagDeepFlavB[9]>0.2543))==2)&&(year==2016)) || ((((Jet_btagDeepFlavB[0]>0.3040) + (Jet_btagDeepFlavB[1]>0.3040) +(Jet_btagDeepFlavB[2]>0.3040) + (Jet_btagDeepFlavB[3]>0.3040)+(Jet_btagDeepFlavB[4]>0.3040) + (Jet_btagDeepFlavB[5]>0.3040) +(Jet_btagDeepFlavB[6]>0.3040) + (Jet_btagDeepFlavB[7]>0.3040)+(Jet_btagDeepFlavB[8]>0.3040) + (Jet_btagDeepFlavB[9]>0.3040))==2)&&(year==2017)) || ((((Jet_btagDeepFlavB[0]>0.2783) + (Jet_btagDeepFlavB[1]>0.2783) +(Jet_btagDeepFlavB[2]>0.2783) + (Jet_btagDeepFlavB[3]>0.2783)+(Jet_btagDeepFlavB[4]>0.2783) + (Jet_btagDeepFlavB[5]>0.2783) +(Jet_btagDeepFlavB[6]>0.2783) + (Jet_btagDeepFlavB[7]>0.2783)+(Jet_btagDeepFlavB[8]>0.2783) + (Jet_btagDeepFlavB[9]>0.2783))==2)&&(year==2018))",
      #2jets-2bjets (pequeña trampilla pa unir 2016, 2016apv)
      "abs(sqrt(2*LepGood_pt[0]*LepGood_pt[1]*(cosh(LepGood_eta[0]-LepGood_eta[1])-cos(LepGood_phi[0]-LepGood_phi[1])))-91)>15"
    ]
    
    sr_sel_2016 = " && ".join(sr_2016)    


    # Plot the distributions of btag score for different taggers in Run 2 legacy and Run 3
   # hlegacy_deepcsv = legacy_ntuple.draw("LepGood_pt[0]", "13,20,150", f"{sr_sel}", "legacy_leading_deepcsv", normToGenSum = False)
    #hlegacy_2016 = legacy_ntuple_2016_mc_old.draw("LepGood_pt[0]", "13,20,150", f"{sr_sel_2016}", "legacy_leading_deepcsv", normToGenSum = False)
    #hlegacy_2016_mc = legacy_ntuple_2016_mc.draw("LepGood_pt[0]", "13,20,150", f"{sr_sel_2016}", "legacy_leading_deepcsv_mc", normToGenSum = False)
    #hlegacy_2017 = legacy_ntuple_2017.draw("LepGood_pt[0]", "13,20,150", f"{sr_sel_2017}", "legacy_leading_deepcsv", normToGenSum = False)
    #hlegacy_2017_old = legacy_ntuple_2017_old.draw("LepGood_pt[0]", "13,20,150", f"{sr_sel_2017}", "legacy_leading_deepcsv_old", normToGenSum = False)
    hlegacy_2018 = legacy_ntuple_2018.draw("LepGood_pt[0]", "13,20,150", f"{sr_sel_2018}", "legacy_leading_deepcsv", normToGenSum = False)
    hlegacy_2018_old = legacy_ntuple_2018_old.draw("LepGood_pt[0]", "13,20,150", f"{sr_sel_2018}", "legacy_leading_deepcsv_old", normToGenSum = False)
    #hlegacy_deepcsv_dn = legacy_ntuple.draw("bTagWeightDeepCSVT_nom - bTagWeightDeepCSVT_HF_Dn", "200,-0.02,0.02", f"{sr_sel} && (bTagWeightDeepCSVT_nom - bTagWeightDeepCSVT_HF_Dn) != 0", "legacy_leading_deepcsv_dn", normToGenSum = False)
    
    htotal= hlegacy_2018.Clone("hist_total")
    #htotal.Add(hlegacy_2017)
    #htotal.Add(hlegacy_2018)



    c = r.TCanvas("c", "", 600, 600)
    # deepcsv up
    #hlegacy_deepcsv.SetFillColor(0)
    #hlegacy_deepcsv.SetLineColor(2)
    #hlegacy_deepcsv.SetLineWidth(2)
    #hlegacy_deepcsv.Rebin(10)
    #hlegacy_deepcsv.GetYaxis().SetRangeUser(0, 1.0)
    #hlegacy_deepcsv.Scale( 1 / hlegacy_deepcsv.Integral() )
    #hlegacy_deepcsv.SetTitle("eta leading lepton")

    htotal.SetFillColor(0)
    htotal.SetLineColor(2)
    htotal.SetLineWidth(2)
    #hlegacy_deepcsv.Rebin(10)
    #hlegacy_deepcsv.GetYaxis().SetRangeUser(0, 1.0)
    #hlegacy_deepcsv.Scale( 1 / hlegacy_deepcsv.Integral() )
    htotal.SetTitle("eta leading lepton")
    # deepcsv dn
    hlegacy_2018_old.SetFillColor(0)
    hlegacy_2018_old.SetLineColor(3)
    hlegacy_2018_old.SetLineWidth(1)
   # hlegacy_deepcsv_dn.Rebin(10)
   # hlegacy_deepcsv_dn.SetLineStyle(9)
   # hlegacy_deepcsv_dn.Scale( 1 / hlegacy_deepcsv_dn.Integral() )

    #legend_legacy = r.TLegend(0.2, 0.6, 0.8, 0.75)
    #legend_legacy.SetBorderSize(0)
    #legend_legacy.AddEntry( hlegacy_deepcsv, "Nominal", "l" )
    #legend_legacy.AddEntry( hlegacy_deepcsv_dn, "Variation down", "l" )

    #hlegacy_deepcsv.Draw("hist")
    print("Data integral:", htotal.Integral())
    print("MC integral:", hlegacy_2018_old.Integral())

    htotal.Draw("hist")
    hlegacy_2018_old.Draw("hist same")
    #legend_legacy.Draw("same")
    c.SaveAs("btag_weight_legacy.png")
    
'''    
    sr = [ #2j2t
      "(HLT_Ele32_WPTight_Gsf && HLT_IsoMu24 && (HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL || HLT_DoubleEle25_CaloIdL_MW ) && HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8 && (HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL || HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ) && (year==2018)) || ( (HLT_Ele35_WPTight_Gsf && HLT_IsoMu27 && (HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL ||HLT_DoubleEle33_CaloIdL_MW) && (HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ || HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8 || HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8) && (HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL || HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ) )&&(year==2017)) || ((HLT_Ele27_WPTight_Gsf && (HLT_IsoMu24 || HLT_IsoTkMu24) && (HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ || HLT_DoubleEle33_CaloIdL_MW || HLT_DoubleEle33_CaloIdL_GsfTrkIdVL) && (HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL || HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL) && (HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL || HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL) )&&(year==2016))",
      #trigger up
      "((year == 2016) && (Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter && Flag_BadPFMuonDzFilter && Flag_eeBadScFilter)) || ((year != 2016) && (Flag_goodVertices && Flag_globalSuperTightHalo2016Filter && Flag_HBHENoiseFilter && Flag_HBHENoiseIsoFilter && Flag_EcalDeadCellTriggerPrimitiveFilter && Flag_BadPFMuonFilter && Flag_BadPFMuonDzFilter && Flag_eeBadScFilter && Flag_ecalBadCalibFilter))",
      #metfilters
      
      "(nLepGood == 2)",
      "(abs(LepGood_pdgId[0]) == 11 && abs(LepGood_pdgId[1]) == 13) || (abs(LepGood_pdgId[0]) == 11 && abs(LepGood_pdgId[1]) == 13)",
      "LepGood_pdgId[0]*LepGood_pdgId[1]<0", #emu opposite sign
      
      "(LepGood_pt[0]>25)&&(LepGood_pt[1]>20)", #pt requirement in leptons
      
      
      "(Jet_pt>30)&&(abs(Jet_eta)<2.4)",
      "Jet_jetId==6",
      "((Jet_pt<50)&&(Jet_puId)>0) || (Jet_pt>=50)", #basic preselection of jets. Assuming jetId==6 means the 4th bullet of AN
      
      "(nJet==2)",
      "((((Jet_btagDeepFlavB[0]>0.2543) + (Jet_btagDeepFlavB[1]>0.2543) +(Jet_btagDeepFlavB[2]>0.2543) + (Jet_btagDeepFlavB[3]>0.2543)+(Jet_btagDeepFlavB[4]>0.2543) + (Jet_btagDeepFlavB[5]>0.2543) +(Jet_btagDeepFlavB[6]>0.2543) + (Jet_btagDeepFlavB[7]>0.2543)+(Jet_btagDeepFlavB[8]>0.2543) + (Jet_btagDeepFlavB[9]>0.2543))==2)&&(year==2016)) || ((((Jet_btagDeepFlavB[0]>0.3040) + (Jet_btagDeepFlavB[1]>0.3040) +(Jet_btagDeepFlavB[2]>0.3040) + (Jet_btagDeepFlavB[3]>0.3040)+(Jet_btagDeepFlavB[4]>0.3040) + (Jet_btagDeepFlavB[5]>0.3040) +(Jet_btagDeepFlavB[6]>0.3040) + (Jet_btagDeepFlavB[7]>0.3040)+(Jet_btagDeepFlavB[8]>0.3040) + (Jet_btagDeepFlavB[9]>0.3040))==2)&&(year==2017)) || ((((Jet_btagDeepFlavB[0]>0.2783) + (Jet_btagDeepFlavB[1]>0.2783) +(Jet_btagDeepFlavB[2]>0.2783) + (Jet_btagDeepFlavB[3]>0.2783)+(Jet_btagDeepFlavB[4]>0.2783) + (Jet_btagDeepFlavB[5]>0.2783) +(Jet_btagDeepFlavB[6]>0.2783) + (Jet_btagDeepFlavB[7]>0.2783)+(Jet_btagDeepFlavB[8]>0.2783) + (Jet_btagDeepFlavB[9]>0.2783))==2)&&(year==2018))",
      #2jets-2bjets (pequeña trampilla pa unir 2016, 2016apv)
      "abs(sqrt(2*LepGood_pt[0]*LepGood_pt[1]*(cosh(LepGood_eta[0]-LepGood_eta[1])-cos(LepGood_phi[0]-LepGood_phi[1])))-91)>15"
    ]
    
    sr_sel = " && ".join(sr)
'''    
