import ROOT as r 
import re
import collections
import math 
import os,sys
import numpy as np
import json
from copy import deepcopy
from collections import OrderedDict

lumi = 16.8+19.5+41.48+59.83#use the lumi used to normalized the gen histos (fb-1)

varname = {
    "lep1_pt"  : ("p_{T} (lep1)"),
    #"lep2_pt"  : ("p_{T} (lep2)"),
    #"lep1_eta" : ("#eta (lep1)"),
    #"lep2_eta" : ("#eta (lep2)"),
    #"njets": ("N Jet"),
    #"njets_7bins" : ("N Jet"),
    #"nbjets" : ("N b-tag Loose"), 
    #"jet1_pt":("p_{T} (jet)"),
    #"jet1_eta":("|#eta| (jet1)"),
    #"deta_llss":("#Delta #eta (ll)"),
    #"HT":("HT"),
    #"dR_ll":("#Delta R (ll)"),
    #"max_eta":("max(#eta) (ll)"), 
    #"pt3l": ("p_{T} 3l"), 
    #"m3l":("m_{3l}"),
    #"dR_lbmedium":(" #Delta R (l bmedium)"),
    #"mindr_lep1_jet25":("min #Delta R (lj)"),
    #"dR_lbloose":(" #Delta R (l bloose)"),
    #"jet2_pt":(" p_{T} (jet 2)"),
    #"jet2_eta":(" |#eta| (jet 2)"),
    #"bLooseLeadingJet_eta":(" |#eta| (bLoose 1)"),
    #"bLooseLeadingJet_pt":(" p_{T}  (bLoose 1)"),
    #"bMediumLeadingJet_eta":(" |#eta| (bMedium 1)"),
    #"bMediumLeadingJet_pt":(" p_{T}  (bMedium 1)"),
    #"sum_2lss_pt":(" p_{T}^{lep1}+p_{T}^{lep2}  "),
    #"nbjets_medium":(" N b-tag medium ") ,
    #"mll":(" m_ll ")  
}
def check_exist(what):
    
    if not os.path.isfile( what ):
        raise RuntimeError("FATAL: file {0} does not exist.".format( what ))

def combine_files(files,name):
    """ Get a common histogram accross a given number of files and sum """

    check_exist( files[0] )
    rfile = r.TFile( files[0] )
    refhisto = rfile.Get( name )
    reference = deepcopy( refhisto.Clone( refhisto.GetName() + "_clone" ) )
    rfile.Close()
    for file in files[1:]:
        check_exist( file )

        rfile = r.TFile( file )
        refhisto = rfile.Get( name )
        reference_i = deepcopy( refhisto.Clone( refhisto.GetName() + "_clone" ) )
        rfile.Close()

        reference.Add( reference_i )
    
    return reference

results = OrderedDict()


f = open("xsecs.txt", "w")
for var in varname.keys():
#for var in ["jet1_pt"]:

    if var != "dR_ll":
        folder = sys.argv[1] + "/{0}/".format(var)
        region = "2lss"
    else:
        folder = sys.argv[1] + "/{0}_withVVV/".format(var)
        region = "2lss"

    if var not in varname.keys():
        print("Variable not included, please add")

    if "2lss" in region:
        region = "2lss"
        regioncard = "2lss_0tau"
    
    elif "3l" in region:
        region = "3l"
        regioncard  = "3l_0tau"
    

    """ Read the GEN input """
    GenInfo  = "{0}/ttW_{1}_Gen_{2}".format(folder, regioncard, var)
    RecoInfo = "{0}/ttW_{1}_Gen_{2}".format(folder, regioncard, var) 

    genfiles = []
    for year in ["2016", "2016APV", "2017", "2018"]:
        genfiles.append( "{0}_{1}.root".format( GenInfo, year) )
    reference = combine_files(genfiles,"x_TTW_inclusive") #Get MC Histogram


    #Get info needed from the fit
    Fit = "{0}/fitDiagnosticsNoasimov_nominal_{1}_{2}_withPlots.root".format( folder, var, region )
    fit_st = "{0}/fitDiagnosticsNoasimov_freezing_{1}_{2}_withPlots.root".format( folder, var, region )
    ws = folder+"/ws_"+var+"_"+region+".root"
    # Get the nominal fit result
    tf_fit = r.TFile.Open(str(Fit))
    fitResult = tf_fit.Get('fit_s')

    # Get the statistical fit result
    tf_fit_st = r.TFile.Open(str(fit_st))
    fitResult_stat = tf_fit_st.Get('fit_s')


    results[var] = OrderedDict()
    results[var] = {}
    
    count = 0

    """ Save the POIs """
    pois = {}

    # 1. Nominal fit
    for v in fitResult.floatParsFinal():
        if "r_TTW" in v.GetName():

            # Create the entry
            pois[ v.GetName() ] = [ 
                v.getVal(), 
                v.getErrorHi(), 
                v.getErrorLo(), 
            ]
            count += 1
        if count == reference.GetNbinsX(): break # Otherwise it breaks lol

    # Freezing systematics
    count2 = 0
    for vstat in fitResult_stat.floatParsFinal():
        if "r_TTW" in vstat.GetName():
            # Extend the entry
            pois[ vstat.GetName() ].extend([ 
                vstat.getErrorHi(), 
                vstat.getErrorLo(), 
            ])
            count2 += 1
        if count2 == reference.GetNbinsX(): break # Otherwise it breaks lol
    
    results[var]["pois"] = pois

    """ Do the covariance matrix stuff """
    # Open the workspace
    tws = r.TFile.Open(ws)
    w = tws.Get("w")

    # Create a POI list 
    poiList = r.RooArgList('poiList')
    for poi in pois:
       variation = w.var(poi)
       poiList.add(variation)

    
    # Get the covariance matrix for the main fit
    covariance_matrix = fitResult.reducedCovarianceMatrix(poiList)
    npois = len( results[var]["pois"] )
    result = {}
    for i  in range(1, 1 + npois):
        poi_i = poiList.at( i - 1 )
        #print( " >> Filling {0}".format( poi_i.GetName() ))

        result[ poi_i.GetName()] = {}
        for j in range(1, 1 + npois):
            poi_j = poiList.at( j - 1 )
            #print( "   + Filling {0}".format( poi_j.GetName() ))
            element = covariance_matrix[i - 1][j - 1]
            result[poi_i.GetName()][ poi_j.GetName()] = element        

    # Get the covariance matrix for the freeze fit
    covariance_matrix_stat = fitResult_stat.reducedCovarianceMatrix(poiList)
    result_st = {}
    for i  in range(1, 1 + npois):
        poi_i = poiList.at( i - 1 )
        #print( " >> Filling {0}".format( poi_i.GetName() ))

        result_st[ poi_i.GetName()] = {}
        for j in range(1, 1 + npois):
            poi_j = poiList.at( j - 1 )
            #print( "   + Filling {0}".format( poi_j.GetName() ))
            element = covariance_matrix_stat[i - 1][j - 1]
            result_st[poi_i.GetName()][ poi_j.GetName()] = element     


    # Now make the systematic matrix
    result_syst = {}
    for i  in range(1, 1 + npois):
        poi_i = poiList.at( i - 1 )
        #print( " >> Filling {0}".format( poi_i.GetName() ))

        result_syst[ poi_i.GetName()] = {}
        for j in range(1, 1 + npois):
            poi_j = poiList.at( j - 1 )
            #print( "   + Filling {0}".format( poi_j.GetName() ))
            element = covariance_matrix[i - 1][j - 1] - covariance_matrix_stat[i - 1][j - 1]
            result_syst[poi_i.GetName()][ poi_j.GetName()] = element

    # Get the covariance on the cross section
    xsec_covariance_matrix = deepcopy( covariance_matrix )
    for ibin in range(1, 1 + reference.GetNbinsX() ):
        for jbin in range(1, 1 + reference.GetNbinsX() ):

            xsec_covariance_matrix[ ibin - 1][jbin - 1] = reference.GetBinContent( ibin ) * reference.GetBinContent( jbin ) * covariance_matrix[i-1][j-1] / (lumi**2)

    # Get the covariance on the cross section (stat)
    xsec_covariance_matrix_stat = deepcopy( covariance_matrix )
    for ibin in range(1, 1 + reference.GetNbinsX() ):
        for jbin in range(1, 1 + reference.GetNbinsX() ):
            xsec_covariance_matrix_stat[ ibin - 1][jbin - 1] = reference.GetBinContent( ibin ) * reference.GetBinContent( jbin ) * covariance_matrix_stat[i-1][j-1] / (lumi**2)


    # Scale the differential distribution to the signal strenght
    data_histo = deepcopy( reference.Clone("data_histo") )
    for ibin in range(1, 1+data_histo.GetNbinsX()):
        signal_strength = pois[ "r_TTW_{0}_bin{1}".format( var, ibin - 1 ) ][0]    
        data_histo.SetBinContent( ibin, data_histo.GetBinContent(ibin) / lumi * signal_strength )
    
    xsec = data_histo.Integral() 

    # The total uncertainty is the sum over all the entries of the covariance matrix
    tot_unc = r.TMath.Sqrt( sum([ xsec_covariance_matrix[i-1][j-1] for i in range(1, npois+1) for j in range(1, npois+1) ]  ) )
    stat_unc = r.TMath.Sqrt( sum([ xsec_covariance_matrix_stat[i-1][j-1] for i in range(1, npois+1) for j in range(1, npois+1) ]  ) )
    syst_unc = r.TMath.Sqrt( sum([ xsec_covariance_matrix[i-1][j-1] - xsec_covariance_matrix_stat[i-1][j-1] for i in range(1, npois+1) for j in range(1, npois+1) ]  ) )
    print([reference.GetBinContent(ibin) for ibin in range(1, reference.GetNbinsX() + 1)])
    f.write("xsec({0}): {1:3.2f} +/- {2:3.2f} (total) = {1:3.2f} +/- {3:3.2f} (syst) +/- {4:3.2f} (stat) fb\n".format(var, xsec, tot_unc, syst_unc, stat_unc ) )
    f.write("fid_xsec({0}): {1:3.2f} fb\n".format(var, reference.Integral()/lumi ) )
    f.write(" -----\n ")

    
    

