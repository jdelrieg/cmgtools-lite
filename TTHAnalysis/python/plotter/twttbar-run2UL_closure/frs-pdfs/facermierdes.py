import os

nweights = 103

scaff = """weight : Alt$(LHEPdfWeight[{w}],1)
alt-norm : Alt$(LHEPdfSumw[{w}]/LHEScaleSumw[4],1)"""

for iW in range(nweights):
    with open("./fr-pdf_" + str(iW) + ".txt", "w") as f:
        f.write(scaff.format(w = iW))
