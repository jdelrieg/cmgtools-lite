import ROOT  as r
import tdrstyle, CMS_lumi
import copy
import varList as vl
import ctypes
###############################################################################

CMS_lumi.writeExtraText = 1

colorMap = [
    r.TColor.GetColor("#e41a1c"),
    r.TColor.GetColor("#377eb8"),
    r.TColor.GetColor("#4daf4a"),
    r.TColor.GetColor("#984ea3"),
    r.TColor.GetColor("#ff7f00"),
    r.TColor.GetColor("#ffff33"),
    r.TColor.GetColor("#a65628"),
    r.TColor.GetColor("#f781bf"),
    ]



class beautifulUnfPlot:
    def __init__(self, name, variable):
        #r.gROOT.SetBatch(True)
        self.name           = name
        self.isUncPlot      = False
        if "uncs" in self.name:
            self.isUncPlot = True
        self.var            = variable
        self.inited         = False
        self.objectsInLeg   = []
        self.plotspath      = ""
        self.doWide         = False
        self.doRatio        = False
        self.isLCurve       = False
        self.doFit          = True
        self.doPreliminary  = True
        self.doSupplementary= False
        self.extraLabel      = ''
        self.displayedLumi  = vl.TotalLumi
        self.yaxisuplimit   = 0
        self.yaxislowlimit   = 0
        # self.yaxis_unclabel = 'Relative uncertainty (adim.)'
        self.yaxis_unclabel = 'Relative uncertainty'
        self.yaxistitleoffset = 1.8#1.5
        print('polaaa')
        self.yaxistitleoffset_wide = 0.5
        self.yaxistitleoffset_noratio = 1.8
        self.maxdigits = 3
        self.doLogY = False
        self.legNColumns = 2 if self.isUncPlot else 1   # legend columns (uncertainty plots only)
        # Multi-column legend geometry (only used when legNColumns > 1 on uncertainty plots).
        # All values are NDC fractions of the pad, except the text size which is a fraction of pad height.
        self.legUncTextSize  = 0.03          # smaller text so the columns do not collide
        self.legUncColWidth  = 0.26          # width of ONE column (must fit the longest label)
        self.legUncRowHeight = 0.045         # height of ONE row
        self.legUncAnchor    = (0.97, 0.92)  # (x2, y2): top-right corner of the legend box
        self.legUncMargin    = 0.18          # fraction of a column used by the line/marker sample


    def _plotKind(self):
        if self.isUncPlot:                                return 'unc'
        if "detector" in self.name:                        return 'detector'
        if "fid" in self.name and "bin" in self.name:       return 'particlefidbin'
        if "fid" in self.name:                              return 'particlefid'
        if "bin" in self.name:                              return 'bin'
        return 'particle'

    def _isUncLike(self):
        """True for any uncertainty-breakdown plot (same criteria used elsewhere in this class)."""
        return self.isUncPlot or ("unc" in self.name.lower()) or ("unc" in str(self.var).lower())

    def _uncDrawStyle(self, histo, options, name, legOptions):
        """Uncertainty plots only. The draw option is REBUILT from scratch (not edited):
          - total                      -> original options, untouched
          - name starts with 'stat'    -> circle markers  (e.g. 'Statistical'; NOT 'MC stat')
          - name starts with 'syst'    -> square markers  (e.g. 'Systematic')
          - everything else            -> plain line through bin centers (no steps, no error bars)
        """
        lname = name.lower().strip()
        same  = ',same' if 'same' in options.lower() else ''

        if 'total' in lname or lname.startswith('tot'):
            kind, newopt, newleg = 'total', options, legOptions
        elif lname.startswith('stat'):
            histo.SetMarkerStyle(5)
            histo.SetMarkerSize(1.5)
            histo.SetMarkerColor(histo.GetLineColor())
            kind, newopt, newleg = 'stat', 'P' + same, 'p'
        elif lname.startswith('syst'):
            histo.SetMarkerStyle(3)
            histo.SetMarkerSize(1.5)
            histo.SetMarkerColor(histo.GetLineColor())
            kind, newopt, newleg = 'syst', 'P' + same, 'p'
        else:
            # 'L' joins bin centers with a straight line: no vertical segments
            kind, newopt, newleg = 'line', '', 'l'
            
        print("> [uncStyle] '%s' -> %s | options: '%s' -> '%s' | legend: '%s' -> '%s'"
              % (name, kind, options, newopt, legOptions, newleg))
        return newopt, newleg

    def initCanvasAndAll(self):
        if self.inited: return
        self.inited     = True
        tdrstyle.setTDRStyle()

        topSpamSize     = 1.2
        doOfficialCMS   = True

        #plotformat  = (1200, 600) if self.doWide else (600,600)
        plotformat  = (600, 600)
        #height      = plotformat[1]+150 if self.doRatio else plotformat[1]
        height      = plotformat[1]

        self.canvas = r.TCanvas(self.name + "_canvas", self.name, plotformat[0], height)
        
        self.canvas.SetTopMargin(self.canvas.GetTopMargin() * topSpamSize)
        topsize = 0.12*600./height if self.doRatio else 0.06*600./height
        if doOfficialCMS: self.canvas.SetTopMargin(topsize*1.2 if self.doWide else topsize)
        #self.canvas.SetWindowSize(plotformat[0] + (plotformat[0] - self.canvas.GetWw()), (plotformat[1]+150 + (plotformat[1]+150 - self.canvas.GetWh())))
        self.canvas.SetRightMargin(0.03)

        if self.doRatio:
            self.canvas.Divide(1, 2)
            self.canvas.GetPad(1).SetPad(*vl.plotlimits)
            self.canvas.GetPad(2).SetPad(*vl.ratiolimits)
            self.canvas.GetPad(1).SetTopMargin(0.08)
            self.canvas.GetPad(1).SetRightMargin(0.03)
            self.canvas.GetPad(1).SetLeftMargin(0.16)
            self.canvas.GetPad(1).SetBottomMargin(0.025)
            #self.canvas.GetPad(2).SetBottomMargin(0.3)
            self.canvas.GetPad(2).SetBottomMargin(0.35)
            self.canvas.GetPad(2).SetBottomMargin(0.375)
            self.canvas.GetPad(2).SetRightMargin(0.03)
            self.canvas.GetPad(2).SetLeftMargin(0.16)

            if self.doLogY: self.canvas.GetPad(1).SetLogy()

        else:
            self.canvas.SetBottomMargin(0.1)

            if self.doLogY: self.canvas.SetLogy()
        return
    
    def _paintCustomAxisLabels(self, axis, pad, cfg):
        """Paint custom labels via TLatex at bin centers, in the given pad,
        using the given axis's current range/margins for coordinate mapping."""
        edges = vl.varList[self.var]['bins_particle']
        overrides = cfg.get('overrides', {})
        pad.cd()
        pad.Update()
        xmin, xmax = axis.GetXmin(), axis.GetXmax()
        leftm, rightm = pad.GetLeftMargin(), pad.GetRightMargin()
        ypos = 0.3  # NDC y-position under the ratio pad axis; tune if needed

        if not hasattr(self, '_customlabels'):self._customlabels = []

        for b in range(len(edges) - 1):
            center = 0.5 * (edges[b] + edges[b + 1])
            for value, text in overrides.items():
                if abs(center - value) < 1e-6 and text != '':
                    ndc_x = leftm + (center - xmin) / (xmax - xmin) * (1 - leftm - rightm)
                    lat = r.TLatex(ndc_x, ypos, text)
                    lat.SetNDC()
                    lat.SetTextAlign(22)
                    lat.SetTextFont(43)
                    lat.SetTextSize(23)
                    lat.Draw()
                    self._customlabels.append(lat)
                    break

        pad.Modified()
        pad.Update()
    
    def addHisto(self, histos, options, name, legOptions, idname = '', padnum = 1, redrawaxis = False):
        if not self.inited: self.initCanvasAndAll()
        if self.doRatio: self.canvas.cd(1)
        else:            self.canvas.cd()
        r.gPad.SetTickx()
        r.gPad.SetTicky()
        r.gPad.RedrawAxis()
        if isinstance(histos, list):
            histo = histos[0]
            asymhisto = r.TGraphAsymmErrors(histo)
            for bin in range(asymhisto.GetN()):
                asymhisto.SetPointEYhigh(bin, histo.GetBinError(bin + 1))
                asymhisto.SetPointEYlow(bin,  histos[1].GetBinError(bin + 1))
                asymhisto.SetPointEXhigh(bin, abs(histo.GetXaxis().GetBinUpEdge(bin + 1) - histo.GetXaxis().GetBinLowEdge(bin + 1))/2)
                asymhisto.SetPointEXlow(bin,  abs(histo.GetXaxis().GetBinUpEdge(bin + 1) - histo.GetXaxis().GetBinLowEdge(bin + 1))/2)
            
            if self.var in vl.varList:
                asymhisto.GetXaxis().SetTitle( vl.varList[self.var]['xaxis'] )
                if self.isUncPlot:
                    asymhisto.GetYaxis().SetTitle( self.yaxis_unclabel )
                elif "detector" in self.name:
                    asymhisto.GetYaxis().SetTitle( 'Events' )
                elif "fid" in self.name and not "bin" in self.name:
                    asymhisto.GetYaxis().SetTitle( vl.varList[self.var]['yaxisfid'] )
                elif "fid" in self.name and "bin" in self.name:
                    asymhisto.GetYaxis().SetTitle( vl.varList[self.var]['yaxisfidbin'] )
                elif "bin" in self.name:
                    asymhisto.GetYaxis().SetTitle( vl.varList[self.var]['yaxisbin'] )
                else:
                    asymhisto.GetYaxis().SetTitle( vl.varList[self.var]['yaxis_particle'] )
            
            asymhisto.GetXaxis().SetRangeUser(histo.GetXaxis().GetBinLowEdge(1),
                                              histo.GetXaxis().GetBinUpEdge(histo.GetNbinsX()))
            #print histo.GetXaxis().GetBinUpEdge(histo.GetNbinsX())

            asymhisto.GetXaxis().SetTitleFont(43)
            asymhisto.GetXaxis().SetTitleSize(22)
            asymhisto.GetXaxis().SetTitleOffset(1.4 if "unc" not in self.name else 1.1)
            asymhisto.GetXaxis().SetLabelFont(43)
            asymhisto.GetXaxis().SetLabelSize(22)
            asymhisto.GetXaxis().SetLabelOffset(0.007)
            asymhisto.GetXaxis().SetNdivisions(510, True* ("DPhi" not in self.var and "MT_LLMETB" not in self.var))
            if "Lep1Lep2BJet1BJet2_M" in self.var: asymhisto.GetXaxis().SetNdivisions(505, True)
            #asymhisto.GetXaxis().SetNdivisions(505, False)
            
            asymhisto.GetYaxis().SetTitleFont(43)
            asymhisto.GetYaxis().SetTitleSize(22)
            asymhisto.GetYaxis().SetTitleOffset(self.yaxistitleoffset_wide if self.doWide else self.yaxistitleoffset_noratio if not self.doRatio else self.yaxistitleoffset)
            asymhisto.GetYaxis().SetLabelFont(43)
            asymhisto.GetYaxis().SetLabelSize(22)
            asymhisto.GetYaxis().SetLabelOffset(0.007)
            asymhisto.GetYaxis().SetNdivisions(510, True)
            #asymhisto.GetYaxis().SetNdivisions(505, False)
            asymhisto.GetYaxis().SetMaxDigits(self.maxdigits)
            
            if 'nomin' not in options:
                #asymhisto.SetMinimum(0. if not self.doLogY else 5e-7)
                print()
            else:
                options = options.replace('nomin', '')
            
            if self.doRatio:
                asymhisto.GetXaxis().SetLabelOffset(999)
                asymhisto.GetXaxis().SetLabelSize(0)
                asymhisto.GetXaxis().SetTitle(' ')
                
            # Apply user-requested y-axis limits; when using log scale ensure the pad
            # is in log mode and that the lower limit is positive (use a tiny floor).
            if self.doLogY:
                r.gPad.SetLogy(1)
                low = self.yaxislowlimit
                if low <= 0:
                    #low = 1e-9
                    print('> Warning: requested y-axis lower limit <= 0 with log scale; using tiny positive floor:', low)
                if self.yaxisuplimit != 0:
                    asymhisto.GetYaxis().SetRangeUser(low, self.yaxisuplimit)
            else:
                if self.yaxisuplimit != 0:
                    asymhisto.GetYaxis().SetRangeUser(self.yaxislowlimit, self.yaxisuplimit)

            print('> Drawing an asym.-unc. histogram with the following options:', options)
            asymhisto.Draw(options)
            self.objectsInLeg.append( (asymhisto, name, legOptions, idname) )
            if redrawaxis: asymhisto.Draw("axis,same")
        else:
            histo = histos
            if idname == "data" and "DPhi" not in self.var: #and False:
                self.graphForHorizontalBars = r.TGraphAsymmErrors()
                for bin in range(1, histo.GetNbinsX() + 1):
                    x = histo.GetBinCenter(bin)
                    y = histo.GetBinContent(bin)
                    # Set the error in y-axis to 0
                    eyl = 0
                    eyh = 0
                    # Set the error in x-axis to bin width
                    exl = histo.GetBinWidth(bin) / 2.0
                    exh = histo.GetBinWidth(bin) / 2.0
                    self.graphForHorizontalBars.SetPoint(bin - 1, x, y)
                    self.graphForHorizontalBars.SetPointError(bin - 1, exl, exh, eyl, eyh)
                self.graphForHorizontalBars.Draw("Psame")
                
            if self.var in vl.varList:
                histo.GetXaxis().SetTitle( vl.varList[self.var]['xaxis'] )
                if self.isLCurve:
                    histo.GetYaxis().SetTitle( vl.varList[self.var]['yaxis'] )
                elif self.isUncPlot:
                    histo.GetYaxis().SetTitle( self.yaxis_unclabel )
                elif not vl.doxsec or "detector" in self.name:
                    histo.GetYaxis().SetTitle( 'Events' )
                elif "fid" in self.name and not "bin" in self.name:
                    histo.GetYaxis().SetTitle( vl.varList[self.var]['yaxisfid'] )
                elif "bin" in self.name and "fid" in self.name:
                    histo.GetYaxis().SetTitle( vl.varList[self.var]['yaxisfidbin'] )
                elif "bin" in self.name:
                    histo.GetYaxis().SetTitle( vl.varList[self.var]['yaxisbin'] )
                else:
                    histo.GetYaxis().SetTitle( vl.varList[self.var]['yaxis_particle'] )

            histo.GetXaxis().SetTitleFont(43)
            histo.GetXaxis().SetTitleSize(22)
            histo.GetXaxis().SetTitleOffset(1.7 if (self.isLCurve) else 1.1 if "unc" in self.name else 1.4)
            histo.GetXaxis().SetLabelFont(43)
            histo.GetXaxis().SetLabelSize(13 if self.isLCurve else 22)
            histo.GetXaxis().SetLabelOffset(0.033 if self.isLCurve else 0.007)
            histo.GetXaxis().SetNdivisions(0o10 if self.isLCurve else 510, True* ("DPhi" not in self.var))
            if "Lep1Lep2BJet1BJet2_M" in self.var: histo.GetXaxis().SetNdivisions(505, True)
            #histo.GetXaxis().SetNdivisions(010 if self.isLCurve else 505, False)
            
            histo.GetYaxis().SetTitleFont(43)
            histo.GetYaxis().SetTitleSize(22)
            histo.GetYaxis().SetTitleOffset(self.yaxistitleoffset_wide if self.doWide else self.yaxistitleoffset_noratio if not self.doRatio else self.yaxistitleoffset)
            histo.GetYaxis().SetLabelFont(43)
            histo.GetYaxis().SetLabelSize(13 if self.isLCurve else 22)
            histo.GetYaxis().SetLabelOffset(0.007)
            histo.GetYaxis().SetNdivisions(310 if self.isLCurve else 510, True)
            histo.GetYaxis().SetMaxDigits(self.maxdigits)
            #histo.GetYaxis().SetNdivisions(310 if self.isLCurve else 505, False)
            
            if 'nomin' not in options:
                histo.SetMinimum(0. if not self.doLogY else 5e-6)
            else:
                options = options.replace('nomin', '')
            
            #if 'comp' in name:
                #if 'reg' not in name: histo.GetYaxis().SetRangeUser(0.96, 1.04)
                #else:
                    ##histo.GetYaxis().SetRangeUser(r.Double(0.999999), r.Double(1.000001)) # Primeras variaciones en plots de asimov.
                    #histo.GetYaxis().SetRangeUser(r.Double(0.99), r.Double(1.01))
                    ##histo.GetYaxis().SetLabelSize(15)
            if 'comp' in name and not self.isUncPlot:
                histo.GetYaxis().SetRangeUser(ctypes.c_double(0.98), ctypes.c_double(1.02))
            
            if self.isLCurve:
                for i in range(1, 25):
                    histo.GetXaxis().ChangeLabel(i, 45)
            #if 'reg' in name:
                #for i in range(1, 25):
                    #histo.GetYaxis().ChangeLabel(i, 45)
            
            if self.doRatio:
                histo.GetXaxis().SetLabelOffset(999)
                histo.GetXaxis().SetLabelSize(0)
                histo.GetXaxis().SetTitle(' ')
            
            # Before drawing, enforce log-y on the pad if requested and apply
            # explicit y-axis limits coming from the varList (yaxislowlimit/yaxisuplimit).
            if self.doLogY:
                r.gPad.SetLogy(1)
                low = self.yaxislowlimit
                if low <= 0:
                    #low = 1e-9
                    print('> Warning: requested y-axis lower limit <= 0 with log scale; using tiny positive floor:', low)
                if self.yaxisuplimit != 0:
                    try:
                        histo.GetYaxis().SetRangeUser(low, self.yaxisuplimit)
                    except Exception:
                        # Fall back to SetMinimum/SetMaximum if needed
                        histo.SetMinimum(low)
                        histo.SetMaximum(self.yaxisuplimit)
            else:
                if self.yaxisuplimit != 0:
                    try:
                        histo.GetYaxis().SetRangeUser(self.yaxislowlimit, self.yaxisuplimit)
                    except Exception:
                        histo.SetMinimum(self.yaxislowlimit)
                        histo.SetMaximum(self.yaxisuplimit)

        # Uncertainty plots
        if self._isUncLike():
            options, legOptions = self._uncDrawStyle(histo, options, name, legOptions)

            lname = name.lower().strip()

            # Total, statistical and systematic uncertainties retain their original drawing
            is_total = 'total' in lname or lname.startswith('tot')
            is_stat  = lname.startswith('stat')
            is_syst  = lname.startswith('syst')

            if not (is_total or is_stat or is_syst):

                # Create independent horizontal lines, one per bin
                if not hasattr(self, '_uncLines'):
                    self._uncLines = []

                for ibin in range(1, histo.GetNbinsX() + 1):
                    x1 = histo.GetXaxis().GetBinLowEdge(ibin)
                    x2 = histo.GetXaxis().GetBinUpEdge(ibin)
                    y  = histo.GetBinContent(ibin)

                    line = r.TLine(x1, y, x2, y)
                    line.SetLineColor(histo.GetLineColor())
                    line.SetLineWidth(histo.GetLineWidth())
                    line.SetLineStyle(histo.GetLineStyle())

                    line.Draw('same')
                    self._uncLines.append(line)

                # Keep the histogram as the legend entry
                self.objectsInLeg.append((histo, name, 'l', idname))

            else:
                histo.Draw(options)
                if not (idname == 'total' and any(it[3] == 'total' for it in self.objectsInLeg)):self.objectsInLeg.append((histo, name, legOptions, idname))
        else:
            histo.Draw(options)
            if not (idname == 'total' and any(it[3] == 'total' for it in self.objectsInLeg)):self.objectsInLeg.append((histo, name, legOptions, idname))

            if 'comp' in name and 'reg' in name:
                histo.Draw("axis,same")
            if redrawaxis:
                histo.Draw("axis,same")
        return
    
    
    def addHistoInPad(self, padnum, histos, options, name, legOptions):
        if not self.inited:
            self.initCanvasAndAll() # first one should be total number of supbad

        self.canvas.cd(padnum)
        histo = histos
        
        if self.var in vl.varList:
            histo.GetXaxis().SetTitle( vl.varList[self.var]['xaxis'] )
            if self.isUncPlot:
                histo.GetYaxis().SetTitle( self.yaxis_unclabel )
            elif "detector" in self.name:
                histo.GetYaxis().SetTitle( 'Events' )
            elif "fid" in self.var and not "bin" in self.var:
                histo.GetYaxis().SetTitle( vl.varList[self.var]['yaxisfid'] )
            elif "fid" in self.var and "bin" in self.var:
                histo.GetYaxis().SetTitle( vl.varList[self.var]['yaxisfidbin'] )
            elif "bin" in self.var:
                histo.GetYaxis().SetTitle( vl.varList[self.var]['yaxisbin'] )
            else:
                histo.GetYaxis().SetTitle( vl.varList[self.var]['yaxis_particle'] )

        histo.GetXaxis().SetTitleFont(43)
        histo.GetXaxis().SetTitleSize(22)
        histo.GetXaxis().SetTitleOffset(1.4)
        histo.GetXaxis().SetLabelFont(43)
        histo.GetXaxis().SetLabelSize(22)
        histo.GetXaxis().SetLabelOffset(0.007)
        
        histo.GetYaxis().SetTitleFont(43)
        histo.GetYaxis().SetTitleSize(22)
        histo.GetYaxis().SetTitleOffset(self.yaxistitleoffset_wide if self.doWide else self.yaxistitleoffset)
        histo.GetYaxis().SetLabelFont(43)
        histo.GetYaxis().SetLabelSize(22)
        histo.GetYaxis().SetLabelOffset(0.007)
        histo.GetYaxis().SetMaxDigits(self.maxdigits)
        histo.Draw(options)
        return
    
    
    def addTLatex(self, x1, y1, text, padnum = 1):
        if padnum:
            self.canvas.cd(padnum)
        else:
            self.canvas.cd()

        la = r.TLatex( x1, y1, text)
        if not hasattr(self, 'tlatex'):
            setattr(self, 'tlatex', [la])
        else:
            self.tlatex.append(la)
        
        la.SetNDC()
        la.SetTextAlign(22)
        la.SetTextFont(43)
        la.SetTextSizePixels(22)
        la.SetTextAngle(0)
        
        la.Draw()
        return


    def _multiColLegendGeometry(self, nentries, ncols):
        """Box and text size of the multi-column legend (uncertainty plots).
        With a ratio pad the main pad is shorter, so heights/text are rescaled to keep the same pixel size."""
        padfrac = (vl.plotlimits[3] - vl.plotlimits[1]) if self.doRatio else 1.
        nrows   = -(-nentries // ncols)
        x2, y2  = self.legUncAnchor
        x1      = x2 - self.legUncColWidth * ncols
        y1      = y2 - self.legUncRowHeight * nrows / padfrac
        return x1, y1, x2, y2, self.legUncTextSize / padfrac

    def saveCanvas(self, corner, suffix = '', leg = True):
        if self.doRatio: self.canvas.cd(1)
        else:            self.canvas.cd()
        
        # Draw legend
        #textSize = 0.022
        #textSize = 0.035 if "unc" in self.var else 0.0435

        # textSize = 0.0435
        
        textSize = 0.05616

        # Multi-column legend: only for uncertainty plots
        isUnc = self.isUncPlot or "unc" in self.var
        ncols = max(1, getattr(self, 'legNColumns', 1)) if isUnc else 1

        if isUnc: legWidth = 0.13 * ncols
        #else:    legWidth = 0.385 # this is tight
        else:     legWidth = 0.2
        nrows  = -(-len(self.objectsInLeg) // ncols)   # ceil division
        height = (.18 + textSize * max(nrows - 3, 0))
        
        if isinstance(corner, str):
            if corner == "TR":
                if "unc" in self.var: (x1,y1,x2,y2) = (0.93 - legWidth if self.doWide else .85 - legWidth, .9 - height, .865,         .9)
                else:                  (x1,y1,x2,y2) = (0.8  - legWidth if self.doWide else .72 - legWidth, .9 - height, .735,         .9)
            elif corner == "TC":
                (x1,y1,x2,y2) = (.5,                                             .9 - height, .55+legWidth, .9)
            elif corner == "TL":
                #(x1,y1,x2,y2) = (.18,                                            .835 - height, .18+legWidth, .835)
                (x1,y1,x2,y2) = (.18,                                            .78 - height, .18+legWidth, .78)
            elif corner == "MR":
                (x1,y1,x2,y2) = (.85 - legWidth,                                 .3 + height, .90,          .3)
            elif corner == "MC":
                (x1,y1,x2,y2) = (.5,                                             .3 + height, .5+legWidth,  .3)
            elif corner == "ML":
                (x1,y1,x2,y2) = (.18,                                            .3 + height, .18+legWidth, .3)
            elif corner == "BR":
                (x1,y1,x2,y2) = (.85 - legWidth,                                 .1 + height, .90,          .1)
            elif corner == "BC":
                (x1,y1,x2,y2) = (.5,                                             .1 + height, .5+legWidth,  .1)
            elif corner == "BL":
                (x1,y1,x2,y2) = (.18,                                            .1 + height, .18+legWidth,  .1)
        else:
            (x1, y1, x2, y2) = corner

        if isUnc and ncols > 1:
            x1, y1, x2, y2, textSize = self._multiColLegendGeometry(len(self.objectsInLeg), ncols)
        
        if leg:
            leg = r.TLegend(x1,y1,x2,y2)
            leg.SetNColumns(ncols)
            if ncols > 1:
                leg.SetColumnSeparation(0.05)
                leg.SetMargin(self.legUncMargin)
            leg.SetTextFont(42)
            leg.SetTextSize(textSize)
            leg.SetBorderSize(0)
            leg.SetFillColor(10)
            leg.SetFillStyle(0); # transparent legend!
            for obj,name,opt,idnam in self.objectsInLeg:
                if "data" in name.lower():
                    leg.AddEntry(obj, name, opt)
                
            for obj,name,opt,idnam in self.objectsInLeg:
                if opt and "data" not in name.lower():
                    leg.AddEntry(obj, name, opt)
            leg.Draw('same')

        if not hasattr(self, 'noCMS'):
            if self.displayedLumi >= 10**2:
                CMS_lumi.lumi_13TeV = "%.0f fb^{-1}" %(self.displayedLumi)
            else:
                CMS_lumi.lumi_13TeV = "%.1f fb^{-1}" %(self.displayedLumi)
            
            if self.doPreliminary:
                CMS_lumi.extraText  = 'Preliminary'
            else:
                CMS_lumi.extraText  = ''
            if self.extraLabel:
                extra_text = '#font[42]{%s}' % self.extraLabel
                if CMS_lumi.extraText:
                    CMS_lumi.extraText = '#splitline{%s}{%s}' % (CMS_lumi.extraText, extra_text)
                else:
                    CMS_lumi.extraText = extra_text
            #if self.doSupplementary: CMS_lumi.extraText  += 'Supplementary'
            CMS_lumi.lumi_sqrtS = '#sqrt{s} = 13 TeV'
            CMS_lumi.CMS_lumi(r.gPad, 4, 10, -0.005 if self.doWide and self.doRatio else 0.01 if self.doWide else 0.05)
                
        # Draw ratio if needed
        if self.doRatio:
            woUnc = False
            print('> Plotting ratio between prediction(s) and results')
            if 'data' not in [it[3] for it in self.objectsInLeg]: raise RuntimeError('There is not data to make a ratio plot as demanded.')
            if [it[3] for it in self.objectsInLeg].count('data') > 1: raise RuntimeError('There are more than one data histograms attached: multiple ratios are not implemented.')
            #if 'mc' not in [it[3] for it in self.objectsInLeg]: raise RuntimeError('There is not (at least) one prediction to make a ratio plot as demanded.')
            if 'unc' not in [it[3] for it in self.objectsInLeg]:
                woUnc = True
                #raise RuntimeError('There is not histogram with the total uncertainties to make a ratio plot as demanded.')
            if [it[3] for it in self.objectsInLeg].count('unc') > 1: raise RuntimeError('There are more than one total uncertainty histograms attached. Please add only one.')
            # Obtaining resources
            ratiohistos= []
            totalunc   = None
            
            datavalues = copy.deepcopy([it[0] for it in self.objectsInLeg if it[3] == 'data'][0])
            fitunc     = copy.deepcopy(datavalues.Clone('fitunc'))
            
            for bin in range(1, datavalues.GetNbinsX() + 1):
                datavalues.SetBinError(bin, 0.)
            for it in self.objectsInLeg:
                if it[3] == 'mc':
                    ratiohistos.append(copy.deepcopy(it[0].Clone(it[1])))
                    ratiohistos[-1].Divide(datavalues)
                if it[3] == 'unc' and not woUnc:
                    totalunc = copy.deepcopy(it[0].Clone(it[1]))
                    # Preserve per-bin textual labels from the original uncertainty histogram
                    try:
                        orig_unc = it[0]
                        if hasattr(orig_unc, 'GetNbinsX') and hasattr(totalunc, 'GetNbinsX'):
                            nb2 = min(orig_unc.GetNbinsX(), totalunc.GetNbinsX())
                            for ib2 in range(1, nb2 + 1):
                                lab2 = orig_unc.GetXaxis().GetBinLabel(ib2)
                                if lab2 and len(lab2.strip()) > 0:
                                    lab2 = lab2.replace('\\geq', '#geq').replace('\\text{', '').replace('}', '')
                                    totalunc.GetXaxis().SetBinLabel(ib2, lab2)
                    except Exception:
                        pass
                if woUnc and it[3] == 'data':
                    totalunc = copy.deepcopy(it[0].Clone(it[1]))
            xtemp = ctypes.c_double(0.)
            ytemp = ctypes.c_double(0.)
            for bin in range(1, datavalues.GetNbinsX() + 1):
                fitunc.SetBinError(bin, fitunc.GetBinError(bin)/fitunc.GetBinContent(bin))
                fitunc.SetBinContent(bin, 1.)
                if not woUnc:
                    totalunc.GetPoint(bin - 1, xtemp, ytemp)
                    totalunc.SetPointEYhigh(bin - 1, totalunc.GetErrorYhigh(bin - 1)/ytemp.value)
                    totalunc.SetPointEYlow(bin - 1,  totalunc.GetErrorYlow(bin - 1)/ytemp.value)
                    totalunc.SetPoint(bin - 1, xtemp, 1.)
                else:
                    totalunc.SetBinContent(bin, 1.)
                    totalunc.SetBinError(bin, fitunc.GetBinError(bin)/fitunc.GetBinContent(bin))
            
            # Setting options
            fitunc.SetFillColorAlpha(r.kAzure, 0.35)
            fitunc.SetLineColor(r.kBlack)
            fitunc.SetFillStyle(1001)
            fitunc.SetLineWidth(1)
            #fitunc.SetMarkerSize(0.)
            
            totalunc.SetLineColor(r.kBlack)
            totalunc.SetFillStyle(1001)
            totalunc.SetLineWidth(1)
            
            #if self.doFit: totalunc.GetXaxis().SetRangeUser(fitunc.GetXaxis().GetBinLowEdge(1), fitunc.GetXaxis().GetBinUpEdge(fitunc.GetNbinsX()))
            totalunc.GetXaxis().SetRangeUser(fitunc.GetXaxis().GetBinLowEdge(1), fitunc.GetXaxis().GetBinUpEdge(fitunc.GetNbinsX()))
            #else:          totalunc.GetXaxis().SetRangeUser(datavalues.GetXaxis().GetBinLowEdge(1), datavalues.GetXaxis().GetBinUpEdge(datavalues.GetNbinsX()))
            
            totalunc.GetXaxis().SetTitle(vl.varList[self.var]['xaxis'])
            totalunc.GetXaxis().SetTitleFont(43)
            totalunc.GetXaxis().SetTitleSize(22)
            totalunc.GetXaxis().SetTitleOffset(4)
            totalunc.GetXaxis().SetLabelFont(43)
            totalunc.GetXaxis().SetLabelSize(22)
            totalunc.GetXaxis().SetLabelOffset(0.007)
            #totalunc.GetXaxis().SetNdivisions(510, True * ("DPhi" not in self.var and "MT_LLMETB" not in self.var))
            totalunc.GetXaxis().SetNdivisions(510, True * ("DPhi" not in self.var))
            #totalunc.GetXaxis().SetNdivisions(505, False)
            if "DPhi"      in self.var: totalunc.GetXaxis().SetMaxDigits(self.maxdigits)     ### RESTAURARRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
            if "MT_LLMETB" in self.var: totalunc.GetXaxis().SetNdivisions(515, True)
            
            
            if   "yaxismax_ratio_fidbin" in vl.varList[self.var] and "fidbin" in self.name:
                totalunc.GetYaxis().SetRangeUser(max(2. - vl.varList[self.var]["yaxismax_ratio_fidbin"], 0.), vl.varList[self.var]["yaxismax_ratio_fidbin"])
            elif "yaxismax_ratio_bin" in vl.varList[self.var] and "bin" in self.name:
                totalunc.GetYaxis().SetRangeUser(max(2. - vl.varList[self.var]["yaxismax_ratio_bin"], 0.), vl.varList[self.var]["yaxismax_ratio_bin"])
            elif "yaxismax_ratio_particle" in vl.varList[self.var] and "particle" in self.name:
                totalunc.GetYaxis().SetRangeUser(max(2. - vl.varList[self.var]["yaxismax_ratio_particle"], 0.), vl.varList[self.var]["yaxismax_ratio_particle"])
            else:
                #totalunc.GetYaxis().SetRangeUser(0.5, 1.5)
                totalunc.GetYaxis().SetRangeUser(0.8, 1.2)

            totalunc.GetYaxis().SetTitle('Pred. / Data')
            totalunc.GetYaxis().SetTitleFont(43)
            totalunc.GetYaxis().SetTitleSize(22)
            totalunc.GetYaxis().SetTitleOffset(self.yaxistitleoffset_wide if self.doWide else self.yaxistitleoffset)
            totalunc.GetYaxis().CenterTitle(True)
            totalunc.GetYaxis().SetLabelFont(43)
            totalunc.GetYaxis().SetLabelSize(22)
            totalunc.GetYaxis().SetLabelOffset(0.007)
            #totalunc.GetYaxis().SetNdivisions(510, True)
            totalunc.GetYaxis().SetNdivisions(505, True)
            totalunc.GetYaxis().SetMaxDigits(self.maxdigits)
            totalunc.GetXaxis().SetTickLength(0.08)
            
            # Drawing
            self.canvas.cd(2)
            #totalunc.Draw('a2' if not woUnc else "a")
            #fitunc.Draw('P,E,same')
            if not woUnc:
                totalunc.Draw('a2')
                fitunc.Draw('P,E,same{s}'.format(s = ",X0" if "equalbinsunf" in vl.varList[self.var] else ""))
            else:
                totalunc.Draw('P,E')
            for el in ratiohistos:
                #print el.GetName()
                if "toy" in el.GetName().lower():
                    el.Draw('P,same')
                else:
                    el.Draw('L,same')
        
        # Save results
        self.canvas.SaveAs(self.plotspath + "/" + self.name + suffix + '.pdf')
        self.canvas.SaveAs(self.plotspath + "/" + self.name + suffix + '.png')
        self.canvas.SaveAs(self.plotspath + "/" + self.name + suffix + '.eps')
        self.canvas.SaveAs(self.plotspath + "/" + self.name + suffix + '.root')

        self.canvas.IsA().Destructor(self.canvas)



    def saveCanvasv2(self, corner, suffix = '', leg = True):
        if self.doRatio: self.canvas.cd(1)
        else:            self.canvas.cd()
        
        # Draw legend
        #textSize = 0.022
        #textSize = 0.035 #if "unc" in self.var else 0.0435
        # textSize = 0.0435
        
        textSize = 0.05616

        # Multi-column legend: only for uncertainty plots
        isUnc = self.isUncPlot or "unc" in self.var
        ncols = max(1, getattr(self, 'legNColumns', 1)) if isUnc else 1

        if isUnc: legWidth = 0.13 * ncols
        #else:    legWidth = 0.385 # this is tight
        else:     legWidth = 0.2
        nrows  = -(-len(self.objectsInLeg) // ncols)   # ceil division
        height = (.18 + textSize * max(nrows - 3, 0))
        
        if isinstance(corner, str):
            if corner == "TR":
                if "unc" in self.var: (x1,y1,x2,y2) = (0.93 - legWidth if self.doWide else .85 - legWidth, .9 - height, .865,         .9)
                else:                  (x1,y1,x2,y2) = (0.8  - legWidth if self.doWide else .72 - legWidth, .9 - height, .735,         .9)
            elif corner == "TC":
                (x1,y1,x2,y2) = (.5,                                             .9 - height, .55+legWidth, .9)
            elif corner == "TL":
                #(x1,y1,x2,y2) = (.18,                                            .835 - height, .18+legWidth, .835)
                (x1,y1,x2,y2) = (.18,                                            .78 - height, .18+legWidth, .78)
            elif corner == "MR":
                (x1,y1,x2,y2) = (.85 - legWidth,                                 .3 + height, .90,          .3)
            elif corner == "MC":
                (x1,y1,x2,y2) = (.5,                                             .3 + height, .5+legWidth,  .3)
            elif corner == "ML":
                (x1,y1,x2,y2) = (.18,                                            .3 + height, .18+legWidth, .3)
            elif corner == "BR":
                (x1,y1,x2,y2) = (.85 - legWidth,                                 .1 + height, .90,          .1)
            elif corner == "BC":
                (x1,y1,x2,y2) = (.5,                                             .1 + height, .5+legWidth,  .1)
            elif corner == "BL":
                (x1,y1,x2,y2) = (.18,                                            .1 + height, .18+legWidth,  .1)
        else:
            (x1, y1, x2, y2) = corner

        if isUnc and ncols > 1:
            x1, y1, x2, y2, textSize = self._multiColLegendGeometry(len(self.objectsInLeg), ncols)
        
        if leg:
            leg = r.TLegend(x1,y1,x2,y2)
            leg.SetNColumns(ncols)
            if ncols > 1:
                leg.SetColumnSeparation(0.05)
                leg.SetMargin(self.legUncMargin)
            leg.SetTextFont(42)
            leg.SetTextSize(textSize)
            leg.SetBorderSize(0)
            leg.SetFillColor(10)
            leg.SetFillStyle(0); # transparent legend!
            for obj,name,opt,idnam in self.objectsInLeg:
                if "data" in name.lower():
                    leg.AddEntry(obj, name, opt)
                
            for obj,name,opt,idnam in self.objectsInLeg:
                if opt and "data" not in name.lower():
                    leg.AddEntry(obj, name, opt)
            leg.Draw('same')

        if not hasattr(self, 'noCMS'):
            if self.displayedLumi >= 10**2:
                CMS_lumi.lumi_13TeV = "%.0f fb^{-1}" %(self.displayedLumi)
            else:
                CMS_lumi.lumi_13TeV = "%.1f fb^{-1}" %(self.displayedLumi)
            
            if self.doPreliminary:
                CMS_lumi.extraText  = 'Preliminary'
            else:
                CMS_lumi.extraText  = ''
            if self.extraLabel:
                extra_text = '#font[42]{%s}' % self.extraLabel
                if CMS_lumi.extraText:
                    CMS_lumi.extraText = '#splitline{%s}{%s}' % (CMS_lumi.extraText, extra_text)
                else:
                    CMS_lumi.extraText = extra_text
            #if self.doSupplementary: CMS_lumi.extraText  += 'Supplementary'
            CMS_lumi.lumi_sqrtS = '#sqrt{s} = 13 TeV'
            CMS_lumi.CMS_lumi(r.gPad, 4, 10, -0.005 if self.doWide and self.doRatio else 0.01 if self.doWide else 0.05)
        
        # Draw ratio if needed
        if self.doRatio:
            woUnc = False
            print('> Plotting ratio between prediction(s) and results')
            if 'data' not in [it[3] for it in self.objectsInLeg]: raise RuntimeError('There is not data to make a ratio plot as demanded.')
            if [it[3] for it in self.objectsInLeg].count('data') > 1: raise RuntimeError('There are more than one data histograms attached: multiple ratios are not implemented.')
            #if 'mc' not in [it[3] for it in self.objectsInLeg]: raise RuntimeError('There is not (at least) one prediction to make a ratio plot as demanded.')
            if 'total' not in [it[3] for it in self.objectsInLeg]:
                woUnc = True
                #raise RuntimeError('There is not histogram with the total uncertainties to make a ratio plot as demanded.')
            print('DEBUG objectsInLeg:')
            for it in self.objectsInLeg:
                print('  name =', it[1], '| idname =', it[3], '| class =', it[0].ClassName())  

            if [it[3] for it in self.objectsInLeg].count('total') > 1: raise RuntimeError('There are more than one total uncertainty histograms attached. Please add only one.')
          
            # Obtaining resources
            ratiohistos= []
            totalunc   = None
            
            datavalues = copy.deepcopy([it[0] for it in self.objectsInLeg if it[3] == 'data'][0])
            #fitunc     = copy.deepcopy(datavalues.Clone('fitunc'))
            #print self.objectsInLeg
            fitunc     = copy.deepcopy([it[0] for it in self.objectsInLeg if it[3] == 'stat'][0])
            
            for bin in range(1, datavalues.GetNbinsX() + 1):
                datavalues.SetBinError(bin, 0.)
            for it in self.objectsInLeg:
                if it[3] == 'mc':
                    ratiohistos.append(copy.deepcopy(it[0].Clone(it[1])))
                    ratiohistos[-1].Divide(datavalues)
                if it[3] == 'total' and not woUnc:
                    totalunc = copy.deepcopy(it[0].Clone(it[1]))
                if woUnc and it[3] == 'data':
                    totalunc = copy.deepcopy(it[0].Clone(it[1]))
            xtemp = ctypes.c_double(0.)
            ytemp = ctypes.c_double(0.)
            for bin in range(1, datavalues.GetNbinsX() + 1):
                if not woUnc:
                    totalunc.GetPoint(bin - 1, xtemp, ytemp)
                    totalunc.SetPointEYhigh(bin - 1, totalunc.GetErrorYhigh(bin - 1)/ytemp.value)
                    totalunc.SetPointEYlow(bin - 1,  totalunc.GetErrorYlow(bin - 1)/ytemp.value)
                    totalunc.SetPoint(bin - 1, xtemp, 1.)

                    fitunc.GetPoint(bin - 1, xtemp, ytemp)
                    fitunc.SetPointEYhigh(bin - 1, fitunc.GetErrorYhigh(bin - 1)/ytemp.value)
                    fitunc.SetPointEYlow(bin - 1,  fitunc.GetErrorYlow(bin - 1)/ytemp.value)
                    fitunc.SetPoint(bin - 1, xtemp, 1.)
                else:
                    totalunc.SetBinContent(bin, 1.)
                    totalunc.SetBinError(bin, fitunc.GetBinError(bin)/fitunc.GetBinContent(bin))
                    fitunc.SetBinError(bin, fitunc.GetBinError(bin)/fitunc.GetBinContent(bin))
                    fitunc.SetBinContent(bin, 1.)
            
            
            print("\n========== UNCERTAINTY BANDS ==========")

            for ibin in range(1, datavalues.GetNbinsX() + 1):
                i = ibin - 1  # TGraphAsymmErrors uses zero-based point indices

                stat_low  = fitunc.GetErrorYlow(i)
                stat_high = fitunc.GetErrorYhigh(i)

                total_low  = totalunc.GetErrorYlow(i)
                total_high = totalunc.GetErrorYhigh(i)

                print("Bin {:2d} | Stat: -{:7.4f} / +{:7.4f} | ""Total: -{:7.4f} / +{:7.4f}".format(ibin, stat_low, stat_high, total_low, total_high))

            print("=======================================\n")
            # Setting options
            """
            fitunc.SetFillColorAlpha(r.kGray + 1, 0.35)
            fitunc.SetLineColor(r.kBlack)
            fitunc.SetFillStyle(1001)
            fitunc.SetLineWidth(0.)
            fitunc.SetMarkerSize(0.)
            """

            datavalues.SetMarkerSize(0.)
            datavalues.SetLineWidth(0)

            totalunc.SetLineColor(r.kBlack)
            totalunc.SetFillStyle(1001)
            totalunc.SetLineWidth(1)
            
            totalunc.GetXaxis().SetRangeUser(datavalues.GetXaxis().GetBinLowEdge(1), datavalues.GetXaxis().GetBinUpEdge(datavalues.GetNbinsX()))
            fitunc.GetXaxis().SetRangeUser(datavalues.GetXaxis().GetBinLowEdge(1), datavalues.GetXaxis().GetBinUpEdge(datavalues.GetNbinsX()))
            datavalues.GetXaxis().SetRangeUser(datavalues.GetXaxis().GetBinLowEdge(1), datavalues.GetXaxis().GetBinUpEdge(datavalues.GetNbinsX()))

            #totalunc.GetXaxis().SetRange(1, datavalues.GetNbinsX())
            #fitunc.GetXaxis().SetRange(1, datavalues.GetNbinsX())

            #print datavalues.GetXaxis().GetBinUpEdge(datavalues.GetNbinsX())
            
            totalunc.GetXaxis().SetTitle(vl.varList[self.var]['xaxis'])
            totalunc.GetXaxis().SetTitleFont(43)
            totalunc.GetXaxis().SetTitleSize(22)
            totalunc.GetXaxis().SetTitleOffset(1)
            totalunc.GetXaxis().SetLabelFont(43)
            totalunc.GetXaxis().SetLabelSize(22)
            totalunc.GetXaxis().SetLabelOffset(0.007)
            #totalunc.GetXaxis().SetNdivisions(510, True * ("DPhi" not in self.var and "MT_LLMETB" not in self.var))
            totalunc.GetXaxis().SetNdivisions(510, True * ("DPhi" not in self.var))
            #totalunc.GetXaxis().SetNdivisions(505, False)
            if "DPhi"      in self.var: totalunc.GetXaxis().SetMaxDigits(self.maxdigits)     ### RESTAURARRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
            if "MT_LLMETB" in self.var: totalunc.GetXaxis().SetNdivisions(515, True)
            if "Lep1Lep2BJet1BJet2_M" in self.var: totalunc.GetXaxis().SetNdivisions(505, True);totalunc.GetXaxis().ChangeLabel(-1, -1, -1, 31, -1, -1, "");  # align=31: right/top
            
            
            if   "yaxismax_ratio_fidbin" in vl.varList[self.var] and "fidbin" in self.name:
                totalunc.GetYaxis().SetRangeUser(max(2. - vl.varList[self.var]["yaxismax_ratio_fidbin"], 0.), vl.varList[self.var]["yaxismax_ratio_fidbin"])
            elif "yaxismax_ratio_bin" in vl.varList[self.var] and "bin" in self.name:
                totalunc.GetYaxis().SetRangeUser(max(2. - vl.varList[self.var]["yaxismax_ratio_bin"], 0.), vl.varList[self.var]["yaxismax_ratio_bin"])
            elif   "yaxismax_ratio_particle" in vl.varList[self.var] and ("minimax_ATLAS" in self.name or "NBJets" in self.name):
                totalunc.GetYaxis().SetRangeUser(max(2. - vl.varList[self.var]["yaxismax_ratio_particle"], 0.), vl.varList[self.var]["yaxismax_ratio_particle"])
            else:
                #totalunc.GetYaxis().SetRangeUser(0.5, 1.5)
                totalunc.GetYaxis().SetRangeUser(0.8, 1.2)
                #totalunc.GetYaxis().SetRangeUser(0, 2)

            totalunc.GetYaxis().SetTitle('Pred. / Data  ')
            #totalunc.GetYaxis().SetTitle('v1 / v2  ')
            totalunc.GetYaxis().SetTitleFont(43)
            totalunc.GetYaxis().SetTitleSize(22)
            totalunc.GetYaxis().SetTitleOffset(self.yaxistitleoffset_wide if self.doWide else self.yaxistitleoffset)
            totalunc.GetYaxis().CenterTitle(True)
            totalunc.GetYaxis().SetLabelFont(43)
            totalunc.GetYaxis().SetLabelSize(22)
            totalunc.GetYaxis().SetLabelOffset(0.007)
            #totalunc.GetYaxis().SetNdivisions(510, True)
            #totalunc.GetYaxis().SetNdivisions(505, True)
            totalunc.GetYaxis().SetNdivisions(503, True)
            totalunc.GetYaxis().SetMaxDigits(self.maxdigits)
            totalunc.GetYaxis().SetMaxDigits(2)
            totalunc.GetYaxis().SetDecimals(True) 
            totalunc.GetXaxis().SetTickLength(0.08)
            

            datavalues.GetXaxis().SetTitle(vl.varList[self.var]['xaxis'])
            datavalues.GetXaxis().SetTitleFont(43)
            datavalues.GetXaxis().SetTitleSize(22)
            datavalues.GetXaxis().SetTitleOffset(4)
            datavalues.GetXaxis().SetLabelFont(43)
            datavalues.GetXaxis().SetLabelSize(22)
            datavalues.GetXaxis().SetLabelOffset(0.007)
            #datavalues.GetXaxis().SetNdivisions(510, True * ("DPhi" not in self.var and "MT_LLMETB" not in self.var))
            datavalues.GetXaxis().SetNdivisions(510, True * ("DPhi" not in self.var))
            #datavalues.GetXaxis().SetNdivisions(505, False)
            if "DPhi"      in self.var: datavalues.GetXaxis().SetMaxDigits(self.maxdigits)     ### RESTAURARRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
            if "MT_LLMETB" in self.var: datavalues.GetXaxis().SetNdivisions(515, True)
            if "Lep1Lep2BJet1BJet2_M" in self.var: datavalues.GetXaxis().SetNdivisions(505, True);

            if   "yaxismax_ratio_fidbin" in vl.varList[self.var] and "fidbin" in self.name:
                totalunc.GetYaxis().SetRangeUser(max(2. - vl.varList[self.var]["yaxismax_ratio_fidbin"], 0.), vl.varList[self.var]["yaxismax_ratio_fidbin"])
            elif "yaxismax_ratio_bin" in vl.varList[self.var] and "bin" in self.name:
                totalunc.GetYaxis().SetRangeUser(max(2. - vl.varList[self.var]["yaxismax_ratio_bin"], 0.), vl.varList[self.var]["yaxismax_ratio_bin"])
            elif   "yaxismax_ratio_particle" in vl.varList[self.var] : #and ("minimax_ATLAS" in self.name or "NBJets" in self.name)
                totalunc.GetYaxis().SetRangeUser(max(2. - vl.varList[self.var]["yaxismax_ratio_particle"], 0.), vl.varList[self.var]["yaxismax_ratio_particle"])
            else:
                #datavalues.GetYaxis().SetRangeUser(0.5, 1.5)
                datavalues.GetYaxis().SetRangeUser(0.8, 1.2)

            datavalues.GetYaxis().SetTitle('Pred. / Data')
            datavalues.GetYaxis().SetTitleFont(43)
            datavalues.GetYaxis().SetTitleSize(22)
            datavalues.GetYaxis().SetTitleOffset(self.yaxistitleoffset_wide if self.doWide else self.yaxistitleoffset)
            datavalues.GetYaxis().CenterTitle(True)
            datavalues.GetYaxis().SetLabelFont(43)
            datavalues.GetYaxis().SetLabelSize(22)
            datavalues.GetYaxis().SetLabelOffset(0.007)
            #datavalues.GetYaxis().SetNdivisions(510, True)
            datavalues.GetYaxis().SetNdivisions(503, True)
            #datavalues.GetYaxis().SetNdivisions(503)
            datavalues.GetYaxis().SetMaxDigits(self.maxdigits)
            datavalues.GetYaxis().SetMaxDigits(2)
            datavalues.GetYaxis().SetDecimals(True)

            """
            # Drawing
            self.canvas.cd(2)
            #totalunc.Draw('a2' if not woUnc else "a")
            #fitunc.Draw('P,E,same')
            if not woUnc:
                totalunc.Draw('A2')
                #fitunc.Draw('A2,same{s}'.format(s = ",X0" if "equalbinsunf" in vl.varList[self.var] else ""))
                fitunc.Draw('2,same')
                datavalues.Draw("axis,same")
            else:
                totalunc.Draw('a2')
            for el in ratiohistos:
                el.Draw('L,same')
                #el.Draw('histE1,same')
            """
            # Check if this variable/plot wants custom centered axis labels
            cax = vl.varList[self.var].get('customaxis', {}).get(self._plotKind())
            hidedefault = bool(cax and cax.get('usecenters', False))
            if hidedefault:
                totalunc.GetXaxis().SetLabelSize(0)
                fitunc.GetXaxis().SetLabelSize(0)
                datavalues.GetXaxis().SetLabelSize(0)

            # Drawing
            self.canvas.cd(2)
            if not woUnc:
                totalunc.Draw('A2')
                fitunc.Draw('2,same')
                datavalues.Draw("axis,same")
            else:
                totalunc.Draw('a2')
            for el in ratiohistos:
                el.Draw('L,same')

            if hidedefault:
                self._paintCustomAxisLabels(datavalues.GetXaxis(), self.canvas.GetPad(2), cax)
        # Save results
        """
        if self.doLogY:
            self.canvas.cd(1)
            r.gPad.SetLogy()
            self.canvas.cd(2)
        """
        r.gPad.SetTickx()
        r.gPad.SetTicky()
        r.gPad.RedrawAxis()

        # Final enforcement of user-requested y-axis limits on drawn primitives.
        # This ensures any earlier SetMinimum(5e-6) does not persist when the
        # user requested a different lower limit. Non-disruptive: only runs
        # when a user limit is set.
        try:
            if (hasattr(self, 'yaxisuplimit') and self.yaxisuplimit != 0) or (hasattr(self, 'yaxislowlimit') and self.yaxislowlimit != 0):
                try:
                    # If we have subpads (ratio), target pad 1 (main plot). Otherwise use current pad.
                    if self.doRatio and hasattr(self.canvas, 'GetPad'):
                        pad = self.canvas.GetPad(1)
                    else:
                        pad = r.gPad
                except Exception:
                    pad = None
                if pad:
                    # respect log-y if requested
                    if self.doLogY:
                        try:
                            pad.SetLogy(1)
                        except Exception:
                            pass
                    low_req = getattr(self, 'yaxislowlimit', 0)
                    high_req = getattr(self, 'yaxisuplimit', 0)
                    for prim in pad.GetListOfPrimitives():
                        try:
                            # TH1-like objects
                            if prim.InheritsFrom('TH1'):
                                if high_req != 0:
                                    prim.SetMaximum(high_req)
                                if low_req != 0:
                                    low = low_req
                                    if self.doLogY and low <= 0:
                                        low = 1e-9
                                    prim.SetMinimum(low)
                            # TGraph-like objects: apply to their internal histogram if available
                            elif prim.InheritsFrom('TGraph'):
                                try:
                                    hist = prim.GetHistogram()
                                except Exception:
                                    hist = None
                                if hist:
                                    if high_req != 0:
                                        hist.SetMaximum(high_req)
                                    if low_req != 0:
                                        low = low_req
                                        if self.doLogY and low <= 0:
                                            low = 1e-9
                                        hist.SetMinimum(low)
                        except Exception:
                            # ignore any primitive we can't manipulate
                            pass
        except Exception:
            pass

        try:
            r.gPad.Modified()
            r.gPad.Update()
        except Exception:
            pass

        self.canvas.SaveAs(self.plotspath + "/" + self.name + suffix + '.pdf')
        self.canvas.SaveAs(self.plotspath + "/" + self.name + suffix + '.png')
        self.canvas.SaveAs(self.plotspath + "/" + self.name + suffix + '.eps')
        self.canvas.SaveAs(self.plotspath + "/" + self.name + suffix + '.root')

        self.canvas.IsA().Destructor(self.canvas)
