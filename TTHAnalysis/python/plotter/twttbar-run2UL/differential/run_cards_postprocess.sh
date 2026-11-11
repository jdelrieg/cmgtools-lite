#!/usr/bin/env bash
# Post-process combine bincards: symmetrize CR colour-reconnection uncertainties,
# apply LOWESS smoothing, and add the non-fiducial modelling.
#
# Usage: ./run_cards_postprocess.sh [TAG] [SRC_TAG]
#   TAG      defaults to 2026-10-29_hdamp (e.g. ./run_cards_postprocess.sh 2026-11-05_other)
#   SRC_TAG  (optional) tag from which the 'nonfiducial_modelling' line of each
#            card_<observable>.txt is taken and written into the .txt of TAG.
#            If not given, the .txt step is skipped.
set -euo pipefail

TAG="${1:-prueba_bash_script}"
SRC_TAG="${2:-2026-10-29_hdamp}"

BASE=/nfs/fanae/user/jriego/bb4l/CMSSW_13_3_3/src/CMGTools/TTHAnalysis/python/plotter
DIFF=$BASE/twttbar-run2UL/differential
CARDS=$BASE/temp_Run2_cards_diff/$TAG
SRC_CARDS=$BASE/temp_Run2_cards_diff/$SRC_TAG

SIMM=$DIFF/simmetrizator.py
LOWESS=$DIFF/lowessizator.py
NONFID=$DIFF/nonfiducial_modelling.py
NONFID_BIS=$DIFF/nonfiducial_modelling_bis.py

SYST="colour_rec_cr1 colour_rec_cr2 colour_rec_erdon"
SYST2="colour_rec_cr1 colour_rec_cr2 colour_rec_erdon hdamp"

# copy_nonfid_line <dir> <card_name>
#   Takes the line(s) starting with 'nonfiducial_modelling' from
#   $SRC_CARDS/run2/<dir>/sigextr_fit_combine/bincards/card_<card_name>.txt
#   and puts them in the card_<card_name>.txt of the current tag (cwd must be
#   the bincards dir). Any existing 'nonfiducial_modelling' line in the
#   destination is replaced, so the step is safe to re-run.
copy_nonfid_line() {
    local dir="$1" card="$2"
    [[ -z "$SRC_TAG" ]] && return 0
 
    local src="$SRC_CARDS/run2/$dir/sigextr_fit_combine/bincards/card_${card}.txt"
    local dst="card_${card}.txt"
 
    if [[ ! -f "$src" ]]; then
        echo "  [WARN] source txt not found: $src" >&2
        return 0
    fi
    if [[ ! -f "$dst" ]]; then
        echo "  [WARN] destination txt not found: $PWD/$dst" >&2
        return 0
    fi
 
    local line
    line=$(grep '^nonfiducial_modelling' "$src" || true)
    if [[ -z "$line" ]]; then
        echo "  [WARN] no 'nonfiducial_modelling' line in $src" >&2
        return 0
    fi
 
    # keep a backup of the untouched txt (only the first time)
    [[ -f "card_${card}_original.txt" ]] || cp "$dst" "card_${card}_original.txt"
 
    # drop any previous nonfiducial_modelling line (makes the step idempotent)
    grep -v '^nonfiducial_modelling' "$dst" > "$dst.tmp" || true
 
    if ! grep -q '^bb4l_pdf1' "$dst.tmp"; then
        echo "  [WARN] no line starting with 'bb4l_pdf1' in $dst; left untouched" >&2
        rm -f "$dst.tmp"
        return 0
    fi
 
    # insert it as the first uncertainty: right before the first 'bb4l_pdf1' line
    # (i.e. between the '##-----' separator and bb4l_pdf1)
    NONFID_LINE="$line" awk '
        !done && /^bb4l_pdf1/ { print ENVIRON["NONFID_LINE"]; done = 1 }
        { print }
    ' "$dst.tmp" > "$dst"
    rm -f "$dst.tmp"
    echo "  nonfiducial_modelling line copied from [$SRC_TAG] into $dst"
}

# process_var <dir> <card_name> <x_name> <nonfid_script> <extra_nonfid_flags> <values...>
#   <dir>       directory under $CARDS/run2/ (also used to build card_<card_name>.root)
#   <card_name> card name (card_<card_name>.root)
#   <x_name>    value passed to -x
process_var() {
    local dir="$1" card="$2" xname="$3" script="$4" extra="$5"
    shift 5
    local values=("$@")

    echo "=== [$TAG] $dir ==="
    cd "$CARDS/run2/$dir/sigextr_fit_combine/bincards"

    cp "card_${card}.root" "card_${card}_original.root"

    python3 "$SIMM" -i "card_${card}.root" -o "card_${card}_CRsimm.root" -u $SYST

    python3 "$LOWESS" "card_${card}_CRsimm.root" -s $SYST2 --copy-all

    # shellcheck disable=SC2086
    python3 "$script" -i "card_${card}_CRsimm_lowess.root" -o "card_${card}.root" \
        -x "$xname" $extra -v "${values[@]}"

    # take the nonfiducial_modelling line from the txt of the other tag
    copy_nonfid_line "$dir" "$card"
}

# process_fiducial <full_dir_to_bincards>
process_fiducial() {
    local sub="$1"
    echo "=== [$TAG] $sub ==="
    cd "$CARDS/$sub/run2/Fiducial/sigextr_fit_combine/bincards"

    cp card_Fiducial.root card_Fiducial_original.root
    python3 "$SIMM" -i card_Fiducial.root -o card_Fiducial_bis.root -u $SYST
    mv card_Fiducial_bis.root card_Fiducial.root
}

# ---------------------------------------------------------------- differential
process_var minimax_geq2j2b_bjetspt_short minimax_geq2j2b_bjetspt_short minimax_geq2j2b_short "$NONFID" "" \
    2.1 0.3 1.2 1.2 1.4 0.8 9.4 8.7 7.3 10.9 7.1

process_var NJets NJets NJets "$NONFID" "" \
    13.1 9.0 8.8 9.5 9.3 11.7

process_var NBJets NBJets NBJets "$NONFID" "" \
    23.6 7.2 2.1 2.9

process_var Lep1Lep2_DPhi Lep1Lep2_DPhi Lep1Lep2_DPhi "$NONFID" "" \
    1.4 1.5 0.5 0.5 0.5 0.2

process_var Lep1Lep2BJet1BJet2MET_Pt_atlasbin Lep1Lep2BJet1BJet2MET_Pt_atlasbin Lep1Lep2BJet1BJet2MET_Pt_atlasbin "$NONFID" "" \
    2.2 1.4 4.3 4.1 1.2 2.6 2.8 5.4 12.9

process_var Lep1Lep2BJet1BJet2MET_Mt_atlasbin Lep1Lep2BJet1BJet2MET_Mt_atlasbin Lep1Lep2BJet1BJet2MET_Mt_atlasbin "$NONFID" "" \
    0.9 0.3 0.4 0.7 0.5 1.2 0.5 1.0 2.2 5.3 4.7 6.5 4.6

process_var Lep1Lep2BJet1BJet2_Pt_ATLAS Lep1Lep2BJet1BJet2_Pt_ATLAS Lep1Lep2BJet1BJet2_Pt_ATLAS "$NONFID" "" \
    0.6 0.2 0.5 0 0.4 0.3 0.2 2.5 0.9 4.5 14.3

process_var Lep1Lep2BJet1BJet2_M Lep1Lep2BJet1BJet2_M Lep1Lep2BJet1BJet2_M "$NONFID" "" \
    0.1 0.7 1.2 0.6 0.7 0.5 0.6 1.5 1.0 4.3 7.2 6.3 7.4 4.3

process_var Jet1_Pt Jet1_Pt Jet1_Pt "$NONFID" "" \
    3.3 0.9 0.06 1.2 0.6 2.2 2.8 0.8 2.2

process_var NJetsNBJets NJetsNBJets NJetsNBJets "$NONFID" "" \
    13.1 19.5 3.6 34.9 8.8 4.0 9.6

# these two use nonfiducial_modelling_bis.py with --straddle weighted
process_var Lep1_Pt Lep1_Pt Lep1_Pt "$NONFID_BIS" "--straddle weighted" \
    0.6 0 0.2 0 0.04 0.7 0.6 0.4 0.8 3.3 11.2

process_var BJet1BJet2_Pt BJet1BJet2_Pt BJet1BJet2_Pt "$NONFID_BIS" "--straddle weighted" \
    0.09 1 1.2 0.8 0.2 0.4 1.8 6.7 16.2

# -------------------------------------------------------------------- fiducial
process_fiducial Fiducial_2j2t
process_fiducial Fiducial_geq2j2t
process_fiducial Fiducial_nojets

echo "Done for TAG=$TAG"
if [[ -z "$SRC_TAG" ]]; then
    echo "No SRC_TAG given: the .txt files were NOT updated."
    echo "acuerdate de hacer cp de los .txt para incluir nonfiducial en el txt (o pasa SRC_TAG como 2o argumento)"
fi