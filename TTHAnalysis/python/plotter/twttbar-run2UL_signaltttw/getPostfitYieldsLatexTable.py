import ROOT as r
import math
from collections import OrderedDict


pathOfCards = "/mnt_pool/c3_users/user/jriego/bb4l/CMSSW_13_3_3/src/CMGTools/TTHAnalysis/python/plotter/temp_Run2_cards_diff/2026-08-05_Unblinding/run2/NJetsNBJets/sigextr_fit_combine/bincards/"

fitDiagnosticsName = "fitDiagnosticsTest.root"


translateDict_processes = OrderedDict([
    ("bb4l",    "bb4l"),
    ("dy",      "dy"),
    ("vvttv",   "VV{+}ttV"),
    ("nonworz", "nonWZ"),
    ("total",   "Total"),
    ("data",    "Data"),
])


# ---------------------------------------------------------
# Round numbers to integers
# ---------------------------------------------------------
def round_value_unc(value, unc):
    return round(value), round(unc)


# ---------------------------------------------------------
# Get yield and uncertainty from a histogram
# ---------------------------------------------------------
def get_yield_unc(h):

    yield_value = h.Integral()

    unc2 = sum(
        h.GetBinError(i) ** 2
        for i in range(1, h.GetNbinsX() + 1)
    )

    return yield_value, math.sqrt(unc2)


# ---------------------------------------------------------
# Make table
# ---------------------------------------------------------
def getYieldLaTeXtables(shape):

    table = (
        "\\begin{tabular}{lr@{${}\\pm{}$}l}\n"
        "Process & \\multicolumn{2}{c}{Inclusive} \\\\ \\hline\n"
    )

    f = r.TFile.Open(pathOfCards + fitDiagnosticsName)
    shapes = f.Get(shape)

    channel = shapes.Get("card_NJetsNBJets")


    # =====================================================
    # bb4l
    # =====================================================

    bb4l_yield = 0.
    bb4l_unc2 = 0.

    for process in [
        "bb4l_partbin0",
        "bb4l_partbin1",
        "bb4l_partbin2",
        "bb4l_partbin3",
        "bb4l_partbin4",
        "bb4l_partbin5",
        "bb4l_partbin6",
        "bb4l_bkg",
    ]:

        h = channel.Get(process)

        if not h:
            print("WARNING: missing", process)
            continue

        yield_value, unc = get_yield_unc(h)

        # Add yields normally
        bb4l_yield += yield_value

        # Add uncertainties in quadrature
        bb4l_unc2 += unc ** 2

    bb4l_unc = math.sqrt(bb4l_unc2)

    bb4l_yield, bb4l_unc = round_value_unc(
        bb4l_yield,
        bb4l_unc
    )

    table += (
        "%25s & %s & %s \\\\\n"
        % ("bb4l", f"{bb4l_yield:,}", f"{bb4l_unc:,}")
    )


    # =====================================================
    # Other MC processes
    # =====================================================

    for process in [
        "dy",
        "vvttv",
        "nonworz",
        "total",
    ]:

        h = channel.Get(process)

        if not h:
            print("WARNING: missing", process)
            continue

        yield_value, unc = get_yield_unc(h)

        yield_value, unc = round_value_unc(
            yield_value,
            unc
        )

        table += (
            "%25s & %s & %s \\\\\n"
            % (
                translateDict_processes[process],
                f"{yield_value:,}",
                f"{unc:,}"
            )
        )


    # =====================================================
    # Data
    # =====================================================

    h = channel.Get("data")

    if h:

        data = int(sum(h.GetY()))

        table += (
            "%25s & %s \\\\\n"
            % ("Data", f"{data:,}")
        )


    # =====================================================
    # Finish table
    # =====================================================

    table += "\\end{tabular}\n"

    output = pathOfCards + shape + "_Table.tex"

    with open(output, "w") as f_out:
        f_out.write(table)

    print("Wrote:", output)

    f.Close()

    return table


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

if __name__ == "__main__":

    #prefit = getYieldLaTeXtables("shapes_prefit")

    postfit = getYieldLaTeXtables("shapes_fit_s")