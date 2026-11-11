""" Macro to uniformize canvas for WZ analysis """
import ROOT as r
from copy import deepcopy

parameters_canvas = {
    1 : {
        "size" : (600, 600)
    },
    2 : {
        "size" : (600, 600),
        "p1" : (0, 0.35, 1, 0.95),
        "p2" : (0, 0.1, 1, 0.35),
        "p1_topMargin" : 0.1,
        "p1_bottomMargin" : 0.02,
        "p2_topMargin" : 0.02,
        "p2_bottomMargin" : 0.25
    }
}


def new_legend(pos = (0.15, 0.7, 0.25, 0.8), nCols = 1):
    """ Create a new legend """
    x1,y1,x2,y2 = pos
    l = r.TLegend(x1,y1,x2,y2)
    l.SetBorderSize(0)
    l.SetTextSize(0.02)
    l.SetNColumns(nCols)
    l.SetFillColor(0)
    l.SetShadowColor(0)
    l.SetFillStyle(0)
    l.SetTextFont(42)
    return l
_noDelete = {}
def add_text(text, coords, textSize = 0.07):
    x1, y1, x2, y2 = coords
    align=12
    note = r.TPaveText(x1, y1, x2, y2,"NDC");
    note.SetTextSize(textSize)
    note.SetFillColor(0)
    note.SetFillStyle(0)
    note.SetLineStyle(2)
    note.SetLineColor(0)
    note.SetTextAlign(align)
    note.SetTextFont(42)
    note.AddText(text)
    _noDelete[text] = note; ## so it doesn't get deleted by PyROOT
    return note

def new_canvas(name, nPads = 2):
    """ This function creates a new canvas whose style is uniform depending on the number of PADs """
    meta = parameters_canvas[nPads]

    wide, height = meta["size"]
    c = r.TCanvas('c_%s'%name, '', 10, 10, wide, height)

    if nPads == 2:
        c.Divide(1, nPads)
        p1x1, p1y1, p1x2, p1y2 = meta["p1"]
        p2x1, p2y1, p2x2, p2y2 = meta["p2"]
        p1top = meta["p1_topMargin"]
        p1bot = meta["p1_bottomMargin"]
        p2top = meta["p2_topMargin"]
        p2bot = meta["p2_bottomMargin"]

        p1 = c.GetPad(1)

        p1.SetPad(p1x1, p1y1, p1x2, p1y2)
        p1.SetTopMargin(p1top)
        p1.SetBottomMargin(p1bot)

        p2 = c.GetPad(2)
        p2.SetPad(p2x1, p2y1, p2x2, p2y2)
        p2.SetTopMargin(p2top)
        p2.SetBottomMargin(p2bot)

        return c, p1, p2    
    
    return c

def get_aux_histo(h):
    """ Returns an empty copy of the histogram, to be used as auxiliar plotting handle """
    hcopy = deepcopy(h)
    for bini in range(1, 1+h.GetNbinsX()):
        hcopy.SetBinContent(bini, 0)
        hcopy.SetBinError(bini, 0)
    return hcopy
