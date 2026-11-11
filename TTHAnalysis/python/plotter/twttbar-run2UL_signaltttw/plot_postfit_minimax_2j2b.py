import ROOT as r
import os
import argparse
import numpy as np
from copy import deepcopy
from array import array
#import tdrstyle, CMS_lumi
r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(False)
r.gStyle.SetPadTickX(1)
r.gStyle.SetPadTickY(1)
r.gStyle.SetEndErrorSize(0)

postFitWithRatioPrefit = False



ColourMapForProcesses = {
    "bb4l_partbin0"       : r.TColor.GetColor(122,33,221),
    "bb4l_partbin1"       : r.TColor.GetColor(122,33,221),
    "bb4l_partbin2"       : r.TColor.GetColor(122,33,221),
    "bb4l_partbin3"       : r.TColor.GetColor(122,33,221),
    "bb4l_partbin4"       : r.TColor.GetColor(122,33,221),
    "bb4l_partbin5"       : r.TColor.GetColor(122,33,221),
    "bb4l_partbin6"       : r.TColor.GetColor(122,33,221),
    "bb4l_partbin7"       : r.TColor.GetColor(122,33,221),
    "bb4l_partbin8"       : r.TColor.GetColor(122,33,221),
    "bb4l_partbin9"       : r.TColor.GetColor(122,33,221),
    "bb4l_bkg"       : r.TColor.GetColor(122,33,221),
    "nonworz"  : r.TColor.GetColor(156,156,161),
    "vvttv"    : r.TColor.GetColor(248,156,32),
    "dy"       : r.TColor.GetColor(87,144,252),
}

orderedProcesses = ["nonworz", "vvttv", "dy", "bb4l_partbin0","bb4l_partbin1","bb4l_partbin2","bb4l_partbin3","bb4l_partbin4","bb4l_partbin5","bb4l_partbin6","bb4l_partbin7","bb4l_partbin8","bb4l_partbin9","bb4l_bkg"]

orderedLegendFor1Col = ["data", "bb4l_partbin0", "dy", "vvttv", "nonworz", "postunc"]

#orderedProcesses = ["nonworz", "vvttv", "dy", "ttbartw"]

#### Size of all text in the plots (except legend)
extraSizeForChannelSpam = 2
spamsSize = 22
titleSize = 26
axisLabelsSize = 24
tick_length = 0.24  


dictNames = {
    "bb4l_partbin0"   : "bb4l",
    "nonworz"  : "Non-W/Z",
    "vvttv"    : "VV+t#bar{t}V",
    "dy"       : "DY",
    "data"     : "Data",
    "total"    : "Uncertainty",
}

dictRegions = {
    "card_minimax_2j2b"      : "e^{#pm}#mu^{#mp} 2j2b-exclusive",
}

dictRegionsXaxisLabels = {
    "card_minimax_2j2b"      : "minimax",
}

dictRegionsYaxisLabels = {
    "card_minimax_2j2b"      : "Events / Bin",
}

dictBinEdgesRegions = {
  "card_minimax_2j2b"      : [0., 50., 70., 90., 110., 130., 150., 170., 190., 210., 230., 255., 270., 310., 340., 500.],
}

dictBinsCenterRegions = {
    "card_minimax_2j2b"      : [20., 45., 55., 65., 75., 82.5, 87.5, 92.5, 97.5, 102.5,107.5, 115., 125., 135., 145., 155., 165., 175., 185., 195.,205., 215., 225., 235., 247.5, 262.5, 290., 325., 420.],
}

# Optional custom labels for each bin. Leave empty to use the default numeric axis.
dictBinLabelsRegions = {
}

dictMaximumYaxis = {
  "card_minimax_2j2b" : 1.7,
}

legendHeigh = {
    "prefit" : {
    "card_minimax_2j2b" : 4,
    },
    "fit_s" : {
    "card_minimax_2j2b" : 4,
    },
}

lumidict     = {"2022"       : 8.0,
                "2022PostEE" : 26.67,
                #"2022PostEE" : 20.67,
                "run2" : 138}



def doSpam(text,x1,y1,x2,y2,align=12,fill=False,textSize=0.033,_noDelete={}):
  cmsprel = r.TPaveText(x1,y1,x2,y2,"NDC");
  cmsprel.SetTextSize(textSize);
  cmsprel.SetFillColor(0);
  cmsprel.SetFillStyle(1001 if fill else 0);
  cmsprel.SetLineStyle(2);
  cmsprel.SetLineColor(0);
  cmsprel.SetLineWidth(0);
  cmsprel.SetTextAlign(align);
  cmsprel.SetTextFont(43);
  cmsprel.AddText(text);
  cmsprel.Draw("same");
  _noDelete[text] = cmsprel; ## so it doesn't get deleted by PyROOT                                                                                                                    
  return cmsprel

def producePlots(year, region, path, fit_file='fitDiagnosticsTest.root'):
  
  def addLegendEntries(orderList): 
    for entry in orderList:
      if entry in orderedProcesses:
        h = subdirNew[entry]
        legend.AddEntry(h,dictNames[h.GetName().replace("V2","")],"f") 
#        if entry == "tw":
#          legend.AddEntry(h,dictNames[h.GetName()] + " (#mu = %1.2f)" %round(r_tW, 2),"f")
#        else:
#          legend.AddEntry(h,dictNames[h.GetName()],"f")
      elif entry == "data":
        legend.AddEntry(gr_forLegend,dictNames[gr.GetName()],"PE")
      elif entry == "postunc":
        legend.AddEntry(htotal,"Uncertainty" if key=="fit_s" else dictNames[htotal.GetName().replace("V2","")],"f")
      elif entry == "preunc":
        legend.AddEntry(preFitHistsUnc[dire],"Prefit unc.","f")
      elif entry == "ratio":
        legend.AddEntry(preFitHists[dire],"Prefit Data / Pred.","l")
    

  
  preFitHists = {}
  preFitHistsUnc = {}
  for key in ["prefit", "fit_s"]:
    #filename = path + "/fitDiagnostics{y}_{r}.root".format(y = year, r = region)
    #outpath = path + "/plots_result_{y}_{r}/".format(y = year, r = region)
    filename = os.path.join(path, fit_file)
    outpath = os.path.join(path, "plots_result")
    #Directories with the pre or postfit results
    maindir = "shapes_%s" %(key)
    f = r.TFile.Open(filename)
    # Extract the fit result
    rooFit = f.Get("fit_s")
    rooFitList = rooFit.floatParsFinal()
    for param in rooFitList:
      if param.GetName() == "r":
        r_tW = param.getVal()
        break
              
    # Change to the directory containing the prefit/postfit plots
    shapes = f.Get(maindir)
    shapes.cd()
    				
	  # This directory contains a list with the different channels
    dirs = shapes.GetListOfKeys()
    dirnames = []
    for dire in dirs:
      dirnames.append(dire.GetName())
				
    for dire in dirnames:
      c = r.TCanvas("canvas", "",  600, 600)
      topSpamSize     = 1.1
      c.SetTopMargin(c.GetTopMargin() * topSpamSize)
      c.Divide(1,2)    		        
      
      p1 = c.GetPad(1)    		        
      p1.SetPad(0, 0.25, 1, 1)
      p1.SetTopMargin(0.055)
      p1.SetBottomMargin(0.025)
      p1.SetLeftMargin(0.16)
      p1.SetRightMargin(0.03)
	        		        
      p2 = c.GetPad(2)
      p2.SetPad(0, 0, 1, 0.25)
      p2.SetTopMargin(0.06)
      p2.SetBottomMargin(0.42)
      p2.SetLeftMargin(0.16)
      p2.SetRightMargin(0.03)
	        		        
	
      subdir = shapes.Get(dire)
      subdir.cd()
      binEdges = array("d", dictBinEdgesRegions[dire])
      nBins = len(binEdges) - 1

      sourceBinGroups = []
      for lowerEdge, upperEdge in zip(binEdges[:-1], binEdges[1:]):
        sourceBinGroups.append([
          index for index, center in enumerate(dictBinsCenterRegions[dire])
          if lowerEdge <= center < upperEdge
        ])

      def rebinHistogram(source, name):
        rebinned = r.TH1F(name, "", nBins, binEdges)
        for targetBin, sourceBins in enumerate(sourceBinGroups, 1):
          content = 0.
          error2 = 0.
          for sourceBin in sourceBins:
            content += source.GetBinContent(sourceBin + 1)
            error2 += source.GetBinError(sourceBin + 1) ** 2
          rebinned.SetBinContent(targetBin, content)
          rebinned.SetBinError(targetBin, error2 ** 0.5)
        return rebinned

      hstack = r.THStack()
      #We define the legend
      textSize = 0.05616
      height = textSize*1.15*legendHeigh[key][dire]
      if dire != "ch3":
        legend = r.TLegend(.46, .9-height, .96, .91) #0.85 for the first number in the CMGTools plotter
      else:
        legend = r.TLegend(.68, .9-height, .93, .91) #0.85 for the first number in the CMGTools plotter
      legend.SetBorderSize(0)
      legend.SetFillColor(0)
      legend.SetShadowColor(0)
      legend.SetFillStyle(0)
      legend.SetTextFont(42)
      legend.SetTextSize(textSize)
      legend.SetNColumns(1)
      
      #TotalHisto MC
      htotal = rebinHistogram(subdir.Get("total"), "totalV2")

      # Get and merge the data points using the same source-bin groups as MC.
      sourceData = subdir.Get("data")
      sourceDataY = sourceData.GetY()
      sourceDataHigh = sourceData.GetEYhigh()
      sourceDataLow = sourceData.GetEYlow()
      datapointsX = []
      datapointsY = []
      uncpointsHigh = []
      uncpointsLow = []
      for sourceBins, lowerEdge, upperEdge in zip(sourceBinGroups, binEdges[:-1], binEdges[1:]):
        datapointsX.append((lowerEdge + upperEdge) / 2.)
        datapointsY.append(sum(sourceDataY[index] for index in sourceBins))
        uncpointsHigh.append(sum(sourceDataHigh[index] ** 2 for index in sourceBins) ** 0.5)
        uncpointsLow.append(sum(sourceDataLow[index] ** 2 for index in sourceBins) ** 0.5)
      gr = r.TGraphAsymmErrors(
        nBins,
        np.array(datapointsX, dtype="float64"),
        np.array(datapointsY, dtype="float64"),
        np.zeros(nBins, dtype="float64"),
        np.zeros(nBins, dtype="float64"),
        np.array(uncpointsLow, dtype="float64"),
        np.array(uncpointsHigh, dtype="float64"),
      )
      gr.SetName("data")
      dataNpoints = nBins
      gr.SetMarkerStyle(8)
      # Get the data/MC
      ratio_hist = deepcopy(gr.Clone("ratiohist"))
      gr_forLegend = r.TH1F("dataPoints", "", 1,0.5,1.5)
      gr_forLegend.SetMarkerStyle(8)
      # Error bar with color black
      gr_forLegend.SetMarkerColor(1)
      gr_forLegend.SetLineColor(1)
      

      #Remove horizontal error bars
      for i in range(dataNpoints):
        gr.SetPointEXlow(i,0)
        gr.SetPointEXhigh(i,0)
        try:
          gr.SetPoint(i,datapointsX[i],datapointsY[i])
        except:
          # Remove the last point if it is not in the range
          gr.RemovePoint(i)
        if htotal.GetBinContent(i+1) != 0:
          ratio_hist.SetPoint(i,datapointsX[i],datapointsY[i]/htotal.GetBinContent(i+1))
          ratio_hist.SetPointEYhigh(i,uncpointsHigh[i]/htotal.GetBinContent(i+1))
          ratio_hist.SetPointEYlow(i,uncpointsLow[i]/htotal.GetBinContent(i+1))
          ratio_hist.SetPointEXhigh(i,0)
          ratio_hist.SetPointEXlow(i,0)
      if key == "prefit":        
        ratioPreFit = r.TH1F("ratioPreFit_%s" %dire, "ratioPreFit_%s" %dire, nBins, binEdges)
        for bin in range(1, nBins + 1):
          ratioPreFit.SetBinContent(bin, datapointsY[bin - 1]/htotal.GetBinContent(bin))
        
        preFitHists[dire] = deepcopy(ratioPreFit)
      
      #legend.AddEntry(gr_forLegend,dictNames[gr.GetName()],"PE")
      subdirNew = {}
      for histoName in orderedProcesses:
        h = subdir.Get(histoName)
        htoFill = rebinHistogram(h, histoName+"V2")
        h = htoFill 
        h.GetXaxis().SetLabelSize(0)
        h.SetLineColor(1)
        h.SetLineWidth(0)
        h.SetFillColor(ColourMapForProcesses[histoName])
        subdirNew[histoName] = h
        hstack.Add(h)
	    
#      for histoName in reversed(orderedProcesses):
#        h = subdir.Get(histoName) 
#        if histoName == "tw":
#          legend.AddEntry(h,dictNames[h.GetName()] + " (#mu = %1.2f)" %round(r_tW, 2),"f")
#        else:
#          legend.AddEntry(h,dictNames[h.GetName()],"f")
      p1.cd()

      p1.SetLogy()
      hstack.Draw("hist")
      hstack.GetXaxis().SetLabelSize(0)
      hstack.GetYaxis().SetTitleOffset(1.8)
      hstack.SetMaximum(1e6)
      hstack.SetMinimum(1e1)
      hstack.GetYaxis().SetTitle(dictRegionsYaxisLabels[dire])
      ##if dire == "ch3":
      ##  # Log scale
      ##  p1.SetLogy()
      hstack.GetYaxis().SetLabelSize(axisLabelsSize)
      hstack.GetYaxis().SetLabelFont(43)
      hstack.GetYaxis().SetTitleSize(titleSize)
      hstack.GetYaxis().SetTitleFont(43)
      hstack.GetYaxis().SetMaxDigits(4)
      
      hstack.GetXaxis().SetRange(1,nBins)
      if dire in dictBinLabelsRegions and len(dictBinLabelsRegions[dire]) == len(dictBinsCenterRegions[dire]):
          for i, label in enumerate(dictBinLabelsRegions[dire]):
              hstack.GetXaxis().SetBinLabel(i + 1, label)


      # now draw error bands
      htotal.SetFillStyle(3444)
      htotal.SetFillColor(r.kGray+2)
      htotal.SetMarkerStyle(0)
      htotal.SetMarkerColor(920)
      htotal.SetLineWidth(0)
      #if postFitWithRatioPrefit:
      #  legend.AddEntry(htotal,"Postfit unc." if key=="fit_s" else dictNames[htotal.GetName()],"f")
      htotal.Draw("E2 same")

      # now draw data
      gr.GetXaxis().SetLabelSize(0)
      gr.Draw("p E same")


      legend.Draw("same")      
      # Ratio plot
      p2.cd()
      lin = r.TLine(binEdges[0], 1, binEdges[-1], 1)
      lin.SetLineWidth(1)
      lin.SetLineColor(1)
      lin.SetLineStyle(2)

      #if postFitWithRatioPrefit:
      #  ratio_hist = r.TGraphAsymmErrors(dataNpoints,datapointsX,np.array(datapointsYRatio,dtype='float64'),gr.GetEXlow(),gr.GetEXhigh(),np.array(uncpointsLowRatio,dtype='float64'),np.array(uncpointsHighRatio,dtype='float64'))	
      #  ratio_hist = ratio_hist.Divide(htotal,ratio_hist,'pois')
								
      #ratio_hist.SetLineWidth()
      ratio_hist.SetMarkerStyle(20)
      ratio_hist.SetMarkerSize(1)
	
      htotalNoErr = deepcopy(htotal.Clone("ratiounc"))
      htotalErr = deepcopy(htotal.Clone("ratiouncErr"))
      for i in range(1, htotalNoErr.GetNbinsX()+1):
        htotalNoErr.SetBinError(i, 0)
      
      htotalErr.Divide(htotalNoErr)
      htotalErr.SetTitle("")
      #htotalErr.SetFillColorAlpha(r.kCyan)
      htotalErr.SetBins(nBins, binEdges)

      if key == "prefit": 
        preFitHistsUnc[dire] = deepcopy(htotalErr)

      #for i in range(1,htotalErr.GetNbinsX()+1):
      #  htotalErr.SetBins(i,dictBinsCenterRegions[dire][i-1]-0.5,dictBinsCenterRegions[dire][i-1]+0.5)
      #htotalErr.GetXaxis().SetRange(dictRangeRegions[dire][0],dictRangeRegions[dire][1])
      
      hAuxForAxis = r.TH1F("axis","", nBins, binEdges)
      hAuxForAxis.SetMarkerSize(0)
      hAuxForAxis.GetXaxis().SetLabelSize(axisLabelsSize)
      hAuxForAxis.GetYaxis().SetLabelSize(axisLabelsSize)
      hAuxForAxis.GetXaxis().SetLabelFont(43)
      hAuxForAxis.GetYaxis().SetLabelFont(43)
      hAuxForAxis.GetYaxis().SetTitle("Data / Pred.     ")
      hAuxForAxis.GetYaxis().SetTitleOffset(1.8)
      hAuxForAxis.GetXaxis().SetTitle(dictRegionsXaxisLabels[dire])
      if dire in dictBinLabelsRegions and len(dictBinLabelsRegions[dire]) == len(dictBinsCenterRegions[dire]):
          for i, label in enumerate(dictBinLabelsRegions[dire]):
              hAuxForAxis.GetXaxis().SetBinLabel(i + 1, label)
      hAuxForAxis.GetYaxis().SetTitleSize(titleSize)
      hAuxForAxis.GetYaxis().SetTitleFont(43)
      hAuxForAxis.GetXaxis().SetTitleOffset(4.0)
      hAuxForAxis.GetXaxis().SetTitleSize(titleSize)
      hAuxForAxis.GetXaxis().SetTitleFont(43)
      if key == "prefit": 
        hAuxForAxis.GetYaxis().SetRangeUser(0.7 , 1.3)
      elif postFitWithRatioPrefit:
        hAuxForAxis.GetYaxis().SetRangeUser(0.8 , 1.2)
      else:
        hAuxForAxis.GetYaxis().SetRangeUser(0.8 if dire=="ch3" else 0.9 , 1.2 if dire=="ch3" else 1.1)
      hAuxForAxis.GetYaxis().SetNdivisions(503)
      if dire != "ch3":
        hAuxForAxis.GetXaxis().SetNdivisions(210)
      else:
        hAuxForAxis.GetXaxis().SetNdivisions(410)
      hAuxForAxis.GetYaxis().CenterTitle(True)
      # Set the tick lenght
      hAuxForAxis.GetXaxis().SetTickLength(tick_length * (p2.GetWh() * p2.GetAbsHNDC()) / (p1.GetWh() * p1.GetAbsHNDC()))
      #print("The tick lenght: ", tick_length * (p2.GetWh() * p2.GetAbsHNDC()) / (p1.GetWh() * p1.GetAbsHNDC()))
      hAuxForAxis.Draw("axis")
      p2.cd()
      doSpam(dictRegionsXaxisLabels[dire], 0.2, 0.03, 0.9, 0.15, align=22, textSize=spamsSize*1.2)
      if key == "fit_s":
        preFitHistsUnc[dire].SetFillStyle(1001)
        preFitHistsUnc[dire].SetFillColorAlpha(r.kAzure, 0.35)
        preFitHistsUnc[dire].SetLineColor(r.kBlack)
        preFitHistsUnc[dire].SetLineWidth(0)
        if postFitWithRatioPrefit:
          legend.AddEntry(preFitHistsUnc[dire],"Prefit unc.","f")
          preFitHistsUnc[dire].Draw("E2 same")	
        preFitHists[dire].SetLineColor(2)
        preFitHists[dire].SetLineWidth(2)
        if postFitWithRatioPrefit:
          legend.AddEntry(preFitHists[dire],"Prefit Data/Pred.","l")
          preFitHists[dire].Draw("same")
      
      
      addLegendEntries(orderedLegendFor1Col)
        
      htotalErr.Draw("e2 same")	
      lin.Draw("same L")
      ratio_hist.Draw("p E same")	

      p1.cd()
      #doSpam('#splitline{#scale[1.2]{#bf{CMS}}}{#scale[1.0]{#it{Preliminary}}}',.2, .835, .35, .875,textSize = 22)
      #doSpam('#scale[1.1]{#bf{CMS}}',.2, .845, .35, .885,textSize = spamsSize)
      keyname = key
      if keyname == "fit_s": keyname = "postfit"
      doSpam(str(round(lumidict[year], 1)) + " fb^{-1} (13 TeV)",0.65, .963, .975, .99,textSize = spamsSize*0.98)
      if keyname == "postfit":
        doSpam('#splitline{#scale[1.2]{#bf{CMS}}}{#scale[1.0]{#it{Preliminary}}}',.2, .835, .35, .875,textSize = 22)  
      else:
        doSpam('#splitline{#scale[1.2]{#bf{CMS}}}{#scale[1.0]{#it{Preliminary}}}',.2, .835, .35, .875,textSize = 22)     
        
      if keyname == "postfit":
        doSpam( dictRegions[dire], .2, .690, .35, .710, textSize = spamsSize + extraSizeForChannelSpam)
        doSpam("Postfit", .2, .748, .35, .788, textSize = spamsSize + extraSizeForChannelSpam)
      else:
          # If I don't use the prefit label put the commented line
        doSpam( dictRegions[dire], .2, .690, .35, .710, textSize = spamsSize + extraSizeForChannelSpam)
        doSpam("Prefit", .2, .748, .35, .788, textSize = spamsSize + extraSizeForChannelSpam)

      if not os.path.exists(outpath): os.system("mkdir -p %s"%outpath)
      print('saving plots in %s/%s_%s.png and %s/%s_%s.pdf'%(outpath,keyname,dire,outpath,keyname,dire))
      c.SaveAs("%s/%s_%s.png"%(outpath,keyname,dire))
      c.SaveAs("%s/%s_%s.pdf"%(outpath,keyname,dire))
      c.Close()
  return


def main():
    parser = argparse.ArgumentParser(description='Produce postfit plots from a fitDiagnostics root file')
    parser.add_argument('--year', default='run2', help='Year/lumi label to use (default: run2)')
    parser.add_argument('--path', default=os.getcwd(), help='Directory containing the fitDiagnostics root file (default: current directory)')
    parser.add_argument('--fit-file', default='fitDiagnosticsTest.root', help='Name of the fitDiagnostics root file (default: fitDiagnosticsTest.root)')
    parser.add_argument('--region', default=None, help='Optional region filter; if omitted, plots are made for all regions in the file')
    args = parser.parse_args()

    if os.path.isfile(args.path):
        fit_file = os.path.basename(args.path)
        input_path = os.path.dirname(args.path) or '.'
    else:
        fit_file = args.fit_file
        input_path = args.path

    fit_path = os.path.join(input_path, fit_file)
    if not os.path.exists(fit_path):
        raise RuntimeError('Could not find fit file: %s' % fit_path)

    print('Using fit file: %s' % fit_path)
    producePlots(args.year, args.region, input_path, fit_file=fit_file)


if __name__ == '__main__':
    main()
