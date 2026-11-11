
import ROOT as r
import math
import re
from collections import OrderedDict


pathOfCards = "/mnt_pool/c3_users/user/jriego/bb4l/CMSSW_13_3_3/src/CMGTools/TTHAnalysis/python/plotter/temp_Run2_cards_diff/2026-08-04_Decorrelatingunclustered/run2/minimax_geq2j2b/sigextr_fit_combine/bincards/"

fitDiagnosticsName = "fitDiagnosticsTest.root"
cardName = "card_minimax_geq2j2b.txt"


translateDict_processes = OrderedDict([
    ("bb4l",    "bb4l"),
    ("dy",      "dy"),
    ("vvttv",   "VV{+}ttV"),
    ("nonworz", "nonWZ"),
    ("total",   "Total"),
    ("data",    "Data"),
])


bb4l_processes = [
    "bb4l_partbin0",
    "bb4l_partbin1",
    "bb4l_partbin2",
    "bb4l_partbin3",
    "bb4l_partbin4",
    "bb4l_partbin5",
    "bb4l_partbin6",
    "bb4l_partbin7",
    "bb4l_partbin8",
    "bb4l_partbin9",    
    "bb4l_partbin10",
    "bb4l_partbin11",
    "bb4l_bkg",
]


# =========================================================
# Simple integer rounding
# =========================================================

def round_value_unc(value, unc):
    return round(value), round(unc)


# =========================================================
# Integral of a histogram
# =========================================================

def integral(h):
    return h.Integral()


# =========================================================
# MC statistical uncertainty
# =========================================================

def statistical_uncertainty(h):

    unc2 = 0.

    for i in range(1, h.GetNbinsX() + 1):
        unc2 += h.GetBinError(i) ** 2

    return math.sqrt(unc2)


# =========================================================
# Read the datacard
#
# Returns:
#
# nuisances[nuisance] = {
#     "type": "shape" or "lnN",
#     "values": [value for each process]
# }
# =========================================================

def read_datacard(card_file):

    nuisances = {}

    with open(card_file) as f:
        lines = f.readlines()

    # Find the process names line
    process_line = None

    for line in lines:
        if line.strip().startswith("process"):

            values = line.split()[1:]

            # First "process" line contains names,
            # second one contains process IDs.
            if values and not all(
                re.match(r"^-?\d+$", x) for x in values
            ):
                process_line = values
                break

    if process_line is None:
        raise RuntimeError("Could not find process line in datacard")

    processes = process_line

    # Read nuisance lines
    for line in lines:

        line = line.strip()

        if not line or line.startswith("#"):
            continue

        fields = line.split()

        if len(fields) < 3:
            continue

        nuisance = fields[0]
        nuisance_type = fields[1]

        if nuisance_type not in ["shape", "lnN"]:
            continue

        values = fields[2:]

        if len(values) != len(processes):
            continue

        nuisances[nuisance] = {
            "type": nuisance_type,
            "values": values,
        }

    return processes, nuisances


# =========================================================
# Calculate uncertainty for one process
# =========================================================

def process_yield_uncertainty(
        root_file,
        channel,
        process,
        nuisances,
        process_index,
):

    nominal = channel.Get(process)

    if not nominal:
        raise RuntimeError(
            "Could not find nominal histogram " + process
        )

    nominal_yield = integral(nominal)

    # Start with MC statistical uncertainty
    stat_unc2 = statistical_uncertainty(nominal) ** 2

    # Total systematic uncertainty squared
    syst_unc2 = 0.

    for nuisance, info in nuisances.items():

        value = info["values"][process_index]

        # ---------------------------------------------
        # Nuisance does not affect this process
        # ---------------------------------------------

        if value == "-":
            continue


        # =============================================
        # Shape uncertainty
        # =============================================

        if info["type"] == "shape":

            up_name = "x_%s_%sUp" % (process, nuisance)
            down_name = "x_%s_%sDown" % (process, nuisance)

            up = root_file.Get(up_name)
            down = root_file.Get(down_name)

            if not up or not down:
                print(
                    "WARNING: missing shape variation:",
                    process,
                    nuisance
                )
                continue

            up_yield = integral(up)
            down_yield = integral(down)

            delta_up = abs(up_yield - nominal_yield)
            delta_down = abs(down_yield - nominal_yield)

            # Symmetric uncertainty: take the larger variation
            delta = max(delta_up, delta_down)

            syst_unc2 += delta ** 2


        # =============================================
        # lnN uncertainty
        # =============================================

        elif info["type"] == "lnN":

            # Symmetric lnN, e.g. 1.05
            if "/" not in value:

                factor = float(value)

                delta = abs(factor - 1.) * nominal_yield

            # Asymmetric lnN, e.g. 0.95/1.05
            else:

                down_factor, up_factor = map(
                    float,
                    value.split("/")
                )

                delta_down = abs(
                    down_factor - 1.
                ) * nominal_yield

                delta_up = abs(
                    up_factor - 1.
                ) * nominal_yield

                # Use the larger side
                delta = max(
                    delta_down,
                    delta_up
                )

            syst_unc2 += delta ** 2


    total_unc = math.sqrt(
        stat_unc2 + syst_unc2
    )

    return nominal_yield, total_unc


# =========================================================
# Calculate bb4l uncertainty
#
# Important:
# For each nuisance we first sum the bb4l components
# and then calculate the effect of the nuisance.
# =========================================================

def bb4l_yield_uncertainty(
        root_file,
        channel,
        nuisances,
        process_indices,
):

    # ---------------------------------------------
    # Nominal bb4l yield
    # ---------------------------------------------

    nominal_yield = 0.
    stat_unc2 = 0.

    for process in bb4l_processes:

        h = channel.Get(process)

        if not h:
            print("WARNING: missing", process)
            continue

        nominal_yield += integral(h)
        stat_unc2 += statistical_uncertainty(h) ** 2


    # ---------------------------------------------
    # Systematic uncertainties
    # ---------------------------------------------

    syst_unc2 = 0.

    for nuisance, info in nuisances.items():

        # Which bb4l components are affected by this nuisance?
        affected = []

        for process in bb4l_processes:

            index = process_indices[process]
            value = info["values"][index]

            if value != "-":
                affected.append((process, value))


        if not affected:
            continue


        # =============================================
        # Shape uncertainty
        # =============================================

        if info["type"] == "shape":

            up_yield = 0.
            down_yield = 0.

            for process, value in affected:

                up = root_file.Get(
                    "x_%s_%sUp" % (process, nuisance)
                )

                down = root_file.Get(
                    "x_%s_%sDown" % (process, nuisance)
                )

                if not up or not down:
                    print(
                        "WARNING: missing shape variation:",
                        process,
                        nuisance
                    )
                    break

                up_yield += integral(up)
                down_yield += integral(down)

            else:

                delta_up = abs(
                    up_yield - nominal_yield
                )

                delta_down = abs(
                    down_yield - nominal_yield
                )

                delta = max(
                    delta_up,
                    delta_down
                )

                syst_unc2 += delta ** 2


        # =============================================
        # lnN uncertainty
        # =============================================

        elif info["type"] == "lnN":

            down_yield = nominal_yield
            up_yield = nominal_yield

            for process, value in affected:

                h = channel.Get(process)
                process_yield = integral(h)

                if "/" not in value:

                    factor = float(value)

                    down_yield += (
                        process_yield * (factor - 1.)
                    )

                    up_yield += (
                        process_yield * (factor - 1.)
                    )

                else:

                    down_factor, up_factor = map(
                        float,
                        value.split("/")
                    )

                    down_yield += (
                        process_yield *
                        (down_factor - 1.)
                    )

                    up_yield += (
                        process_yield *
                        (up_factor - 1.)
                    )

            delta_down = abs(
                down_yield - nominal_yield
            )

            delta_up = abs(
                up_yield - nominal_yield
            )

            delta = max(
                delta_down,
                delta_up
            )

            syst_unc2 += delta ** 2


    total_unc = math.sqrt(
        stat_unc2 + syst_unc2
    )

    return nominal_yield, total_unc


# =========================================================
# Make LaTeX table
# =========================================================

def getYieldLaTeXtables(shape):

    root_path = pathOfCards + fitDiagnosticsName
    card_path = pathOfCards + cardName

    # ---------------------------------------------
    # Read datacard
    # ---------------------------------------------

    processes, nuisances = read_datacard(card_path)

    process_indices = {
        process: i
        for i, process in enumerate(processes)
    }

    # ---------------------------------------------
    # Open ROOT file
    # ---------------------------------------------

    f = r.TFile.Open(root_path)

    if not f or f.IsZombie():
        raise RuntimeError(
            "Could not open " + root_path
        )

    shapes = f.Get(shape)

    if not shapes:
        raise RuntimeError(
            "Could not find " + shape
        )

    channel = shapes.Get("card_minimax_geq2j2b")

    if not channel:
        raise RuntimeError(
            "Could not find card_NJetsNBJets"
        )


    # ---------------------------------------------
    # Table header
    # ---------------------------------------------

    table = (
        "\\begin{tabular}{lr@{${}\\pm{}$}l}\n"
        "Process & \\multicolumn{2}{c}{Inclusive} \\\\ \\hline\n"
    )


    # =================================================
    # bb4l
    # =================================================

    bb4l_yield, bb4l_unc = bb4l_yield_uncertainty(
        f,
        channel,
        nuisances,
        process_indices
    )

    table += (
        "%25s & %s & %s \\\\\n"
        % (
            "bb4l",
            f"{round(bb4l_yield):,}",
            f"{round(bb4l_unc):,}"
        )
    )


    # =================================================
    # Other processes
    # =================================================

    for process in [
        "dy",
        "vvttv",
        "nonworz",
    ]:

        if process not in process_indices:
            continue

        value, unc = process_yield_uncertainty(
            f,
            channel,
            process,
            nuisances,
            process_indices[process]
        )

        table += (
            "%25s & %s & %s \\\\\n"
            % (
                translateDict_processes[process],
                f"{round(value):,}",
                f"{round(unc):,}"
            )
        )


    # =================================================
    # Total
    # =================================================

    total = channel.Get("total")

    if total:

        total_yield = total.Integral()

        table += (
            "%25s & %s & %s \\\\\n"
            % (
                "Total",
                f"{round(total_yield):,}",
                "-"
            )
        )


    # =================================================
    # Data
    # =================================================

    data = channel.Get("data")

    if data:

        data_yield = int(sum(data.GetY()))

        table += (
            "%25s & %s \\\\\n"
            % (
                "Data",
                f"{data_yield:,}"
            )
        )


    # =================================================
    # Finish
    # =================================================

    table += "\\end{tabular}\n"

    output = pathOfCards + shape + "_Table.tex"

    with open(output, "w") as out:
        out.write(table)

    print("Wrote:", output)

    f.Close()

    return table


# =========================================================
# Main
# =========================================================

if __name__ == "__main__":

    prefit = getYieldLaTeXtables("shapes_prefit")

    #postfit = getYieldLaTeXtables("shapes_fit_s")
