#!/usr/bin/env python3

import argparse
import ROOT
import shutil
import os
import re


def modify_root(rootfile):

    f = ROOT.TFile.Open(rootfile, "UPDATE")
    if not f or f.IsZombie():
        raise RuntimeError(f"Cannot open {rootfile}")

    h_mc = f.Get("x_MCfalso")
    if not h_mc:
        raise RuntimeError("Histogram x_MCfalso not found")

    # Clone and detach from the file
    new_data = h_mc.Clone()
    new_data.SetName("x_data_obs")
    new_data.SetDirectory(0)

    # Delete the old histogram
    f.Delete("x_data_obs;*")
    f.Delete("x_MCfalso;*")

    # Write the new one
    f.cd()
    new_data.Write()

    f.Close()


def modify_card(cardfile):

    with open(cardfile) as f:
        lines = f.readlines()

    # Find the rate line
    rate_value = None
    for line in lines:
        if line.lstrip().startswith("rate"):
            m = re.search(r'(\S+)\s*$', line.rstrip("\n"))
            if m:
                rate_value = m.group(1)
                break

    if rate_value is None:
        raise RuntimeError("Could not find the rate line.")

    new_lines = []

    for i, line in enumerate(lines):

        # Replace observation value while preserving indentation
        if line.lstrip().startswith("observation"):
            m = re.match(r'^(\s*observation\s+)\S+(.*)$', line.rstrip("\n"))
            if m:
                new_lines.append(f"{m.group(1)}{rate_value}{m.group(2)}\n")
            else:
                new_lines.append(line)
            continue

        # Leave the first 7 lines untouched
        if i < 7:
            new_lines.append(line)
            continue

        if line.lstrip().startswith("* autoMCStats"):
            new_lines.append(line)
            continue

        # Remove only the last column, preserving all spacing
        if line.strip():
            newline = re.sub(r'\s+\S+\s*$', '', line.rstrip("\n"))
            new_lines.append(newline + "\n")
        else:
            new_lines.append(line)

    shutil.copy(cardfile, cardfile + ".bak")

    with open(cardfile, "w") as f:
        f.writelines(new_lines)


def modify_root_particle(rootfile):

    f = ROOT.TFile.Open(rootfile, "UPDATE")
    if not f or f.IsZombie():
        raise RuntimeError(f"Cannot open {rootfile}")

    h_mc = f.Get("x_twttbardr")
    if not h_mc:
        raise RuntimeError("Histogram x_twttbardr not found")

    # Clone and detach from the file
    new_data = h_mc.Clone()
    new_data.SetName("x_data_obs")
    new_data.SetDirectory(0)

    # Delete the old histogram
    f.Delete("x_data_obs;*")

    # Write the new one
    f.cd()
    new_data.Write()

    f.Close()

def modify_card_particle(cardfile, process_name="twttbardr"):

    with open(cardfile) as f:
        lines = f.readlines()

    process_line = None
    rate_line = None

    # Find the process names line and the rate line
    for line in lines:
        tokens = line.split()
        if not tokens:
            continue

        if tokens[0] == "process":
            # Keep only the process-name line (not the numeric one)
            if len(tokens) > 1 and not re.fullmatch(r"-?\d+", tokens[1]):
                process_line = tokens

        elif tokens[0] == "rate":
            rate_line = tokens

    if process_line is None:
        raise RuntimeError("Could not find the process-name line.")

    if rate_line is None:
        raise RuntimeError("Could not find the rate line.")

    if process_name not in process_line:
        raise RuntimeError(f"Process '{process_name}' not found.")

    # Position of the desired process
    idx = process_line.index(process_name) - 1
    value = rate_line[idx + 1]

    new_lines = []

    for line in lines:
        if line.lstrip().startswith("observation"):
            m = re.match(r'^(\s*observation\s+)\S+(.*)$', line.rstrip("\n"))
            if m:
                new_lines.append(f"{m.group(1)}{value}{m.group(2)}\n")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    shutil.copy(cardfile, cardfile + ".bak")

    with open(cardfile, "w") as f:
        f.writelines(new_lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("card")
    parser.add_argument("rootfile")
    args = parser.parse_args()

    if not os.path.isfile(args.card):
        raise FileNotFoundError(args.card)

    if not os.path.isfile(args.rootfile):
        raise FileNotFoundError(args.rootfile)

    
    if args.rootfile == 'particle.root': modify_root_particle(args.rootfile)
    if args.card == 'particle.txt': modify_card_particle(args.card)
    
    print("Modifying ROOT file...")
    if args.rootfile != 'particle.root': modify_root(args.rootfile)

    print("Modifying datacard...")
    if args.card != 'particle.txt':modify_card(args.card)

    print("Done.")
    #print(f"Backup of datacard saved as {args.card}.bak")


if __name__ == "__main__":
    ROOT.gROOT.SetBatch(True)
    main()
