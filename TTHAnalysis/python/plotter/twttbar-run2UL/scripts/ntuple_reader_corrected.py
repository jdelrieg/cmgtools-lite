""" General class to read ntuples for quick checks """
import ROOT as r
from copy import deepcopy
import os
from array import array

class ntuple_reader:
    def __init__(self, samplename, friends, ftreename):
        """
        samplename : list of main "Events" tree paths (one per file)
        friends    : list of "stages"; each stage is itself a list of friend files,
                     with EXACTLY the same length and file order as `samplename`.
                     e.g. friends = [stage0_files, stage1_files, ...]
                     where stage0_files[i] is the friend file for samplename[i].
        ftreename  : name of the tree inside each friend file (e.g. "Friends")
        """
        self.samplename = samplename
        self.friends = friends
        self.open_tree()
        for stage_files in self.friends:
            self.add_friend(stage_files, ftreename)
        return

    def open_tree(self):
        """ Open the tree """
        if isinstance(self.samplename, list):
            self.files = []
            self.tree = r.TChain()
            self.runs = r.TChain()
            print(" >> Creating chain")
            for sample in self.samplename:
                print(f"   o Adding {sample} -- total entries {self.tree.GetEntries()}")
                self.tree.Add(sample)
                self.runs.Add(sample.replace("Events", "Runs"))
            print(f"  o Total entries: {self.tree.GetEntries()}")

        else:
            self.rf = r.TFile.Open(self.samplename, "READ")
            self.tree = self.rf.Get("Events")
            self.runs = self.rf.Get("Runs")

    def add_friend(self, friend_files, ftreename):
        """
        Add one friend "stage" as a TChain aligned entry-by-entry with the main chain.
        friend_files must have exactly the same length and file order as self.samplename,
        i.e. friend_files[i] must correspond to the same original event file as
        self.samplename[i].
        """
        if isinstance(self.samplename, list):
            if len(friend_files) != len(self.samplename):
                raise ValueError(
                    f"Friend stage has {len(friend_files)} files but the main chain has "
                    f"{len(self.samplename)} files -- they must match 1-to-1, in the same order. "
                    f"(ftreename={ftreename})"
                )
            fchain = r.TChain(ftreename)
            for f in friend_files:
                fchain.Add(f)

            n_main = self.tree.GetEntries()
            n_friend = fchain.GetEntries()
            if n_friend != n_main:
                print(f"   !! WARNING: friend chain '{ftreename}' has {n_friend} entries "
                      f"but main chain has {n_main} -- friend/main are NOT aligned, "
                      f"results will be wrong for events beyond the shorter chain.")
            else:
                print(f"   o Friend chain '{ftreename}' OK: {n_friend} entries match main chain")

            self.tree.AddFriend(fchain)

        else:
            # single-file case: friend_files is expected to be a single file path
            self.tree.AddFriend(ftreename, r.TFile.Open(friend_files))

    def add_ntuple(self, ntuple):
        """ Basically adds the tree of another ntuple """
        self.tree.Add(ntuple.get_tree())
        return

    def get_tree(self):
        return self.tree

    def _treeSum(self, varNormToGenSum):

        # Method with Runs tree
        if self.runs.GetEntries() == 0: return 0.
        r.gROOT.cd()
        if r.gROOT.FindObject("dummy") != None: r.gROOT.FindObject("dummy").Delete()
        histo = r.TH1D("dummy", "dummy", 1, 0.0, 1.0); histo.Sumw2()
        self.runs.Draw("0.5>>dummy", varNormToGenSum, "goff")
        ret = histo.GetBinContent(1)

        return ret

    def draw(self, what, binning, selection, name,
             normToGenSum=True, varNormToGenSum="genEventSumw"):

        # --- Uniform binning (string or tuple of 3 numbers)
        if isinstance(binning, str) or (isinstance(binning, (list, tuple)) and len(binning) == 3):

            if not isinstance(binning, str): binning = f"{int(binning[0])},{binning[1]},{binning[2]}"

            self.tree.Draw(f"{what} >> {name}({binning})", selection, "hist")
            histo = r.gDirectory.Get(name)

        # --- Variable binning (list of edges)
        else:

            edges = array('d', binning)
            histo = r.TH1F(name, "", len(edges) - 1, edges)
            histo.Sumw2()
            self.tree.Project(name, what, selection)
            histo.SetDirectory(0)

        # --- Normalization
        if normToGenSum:
            gsw = self._treeSum(varNormToGenSum)
            histo.Scale(1 / gsw)

        return deepcopy(histo)

    def scan(self, what, selection):
        """ Scans a tree of this root file """
        self.tree.Scan(f"{what}", selection)