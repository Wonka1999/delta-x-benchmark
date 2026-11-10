Three artifacts below. The design decision worth flagging up front: one step (S4, coevolution) carries an adequacy threshold that I expect my own data to **fail** — 322 sequences over ~500 aa cannot reach Meff/L ≥ 5 — and I am registering it anyway so the abandon fires on the record rather than being quietly dropped.

**method_plan.json**

```json
{
  "schema": "dx02.method_plan.v1",
  "registered_at": "2026-11-08",
  "upstream": "DX01 hypotheses H1-H5, H0. Identifiers used here refer to that frozen record.",
  "input_inventory_assumed": {
    "subfamily_A_n": 322,
    "subfamily_B_n": 165,
    "species_unique": true,
    "length_range_aa": [451, 620],
    "reference_sequences": 7
  },
  "global_notes": [
    "Subfamily assignment to 'template-dependent' vs 'template-independent' is NOT assumed; A and B are label-neutral until DX03 evidence assigns them.",
    "Every differential step below uses at least one non-reshuffle null. The split-half null (NULL-SH) is the calibration backbone: it measures how much two arbitrary halves of the SAME subfamily differ, which is the honest floor for 'A differs from B'.",
    "Adequacy checks are all computable on the input alone, before the main statistic is produced."
  ],

  "nulls_defined_once": {
    "NULL-SH": {
      "name": "Within-subfamily split-half calibration null",
      "construction": "Partition subfamily A (n=322) into two disjoint halves of 161 by a phylogeny-aware split (cut the A-only tree at its deepest bipartition, then at the next deepest, generating several non-random splits), and independently by 200 random splits. Run the IDENTICAL pipeline on half-A1 vs half-A2 as on A vs B. Repeat for subfamily B (n=165, halves of 82).",
      "why_it_is_not_a_label_reshuffle": "It never mixes A and B sequences. It asks: when two groups are known to share the functional property under test, how large a differential statistic does the pipeline still report? That is the chance level for the effect, including all pipeline-induced bias.",
      "use": "The A-vs-B statistic must exceed the 95th percentile of the pooled split-half distribution. Deep-bipartition splits are reported separately from random splits, because they bound the phylogenetic contribution."
    },
    "NULL-PHYLO": {
      "name": "Simulated-evolution null under shared ancestry",
      "construction": "Infer one tree over all 487 sequences. Simulate sequence evolution down that exact tree under a site-homogeneous substitution model with empirical rate heterogeneity and indel rates matched to the observed alignment (Seq-Gen / INDELible). Re-split the simulated sequences by the SAME A/B tip partition and rerun the pipeline.",
      "why_it_is_not_a_label_reshuffle": "Sequences are generated afresh with zero functional divergence, but retain the real phylogenetic structure, the real tree depth, and the real A/B clade imbalance. Any A-vs-B signal it produces is pure genealogy.",
      "use": "200 simulation replicates; A-vs-B statistic compared to the simulated distribution."
    },
    "NULL-FAM": {
      "name": "Unrelated-pair background null (structural steps only)",
      "construction": "Compute the same structural statistic over pairs of proteins drawn from different, functionally unrelated families of comparable length, and over paralog pairs from families with no known functional divergence on this axis.",
      "use": "Establishes what TM-score / cavity-difference magnitudes mean when nothing functional is at stake."
    }
  },

  "steps": [
    {
      "id": "S1",
      "question": "Foundational — supports H1, H2, H3, H4. Produces the alignment every downstream step consumes. Not itself differential.",
      "tool": "MAFFT",
      "exact_invocation": "mafft --localpair --maxiterate 1000 --reorder --anysymbol all_487.fasta > all_487.aln.fasta   # fallback for runtime: mafft --auto --maxiterate 1000",
      "statistic": "Per-column Transitive Consistency Score (TCS) from T-Coffee evaluation of the MAFFT alignment, plus fraction of columns with gap occupancy < 50%.",
      "null": "Not applicable — this step produces no differential statistic. Its output is gated by the adequacy check below, not by a null.",
      "adequacy_check": {
        "measure": "TCS column score, computed as: t_coffee -infile all_487.aln.fasta -evaluate -output=score_ascii",
        "numeric_threshold": "Retain only columns with TCS >= 5 (0-9 scale). The alignment as a whole is adequate only if >= 60% of columns in the catalytic-core region reach TCS >= 5, and the whole-alignment TCS >= 50 (0-100 scale).",
        "source": "Chang, Di Tommaso & Notredame 2014, Mol Biol Evol 31:1625 — TCS; the paper's own benchmark shows columns below TCS 5 degrade downstream phylogenetic and positional inference, and is the basis for their recommended filtering.",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "If whole-alignment TCS < 50, or fewer than 60% of catalytic-core columns reach TCS >= 5 even after realignment with --genafpair and after removing the longest 5% of sequences, I abandon all residue- and column-level steps (S2, S3, S7) and report positional analysis as not supportable by this input. Domain-level steps (S5, S6) may continue on structure, not alignment.",
      "expected_result_if_H_true": "Not hypothesis-specific. Expect core columns to align well (TCS >= 5) and the insertion regions relevant to H1 to be exactly where TCS collapses — a predicted, interpretable failure, not a surprise.",
      "expected_result_if_H_false": "Diffuse low TCS across the whole alignment with no structured high-confidence core, indicating the two sets are too diverged for cis-alignment inference."
    },

    {
      "id": "S2",
      "question": "H3 — does the nucleotide-contacting pocket differ between subfamilies? Also bears on H1 if the discriminating columns localise to an insertion boundary.",
      "tool": "HMMER (hmmbuild / hmmemit / per-column relative entropy) ",
      "exact_invocation": "hmmbuild --amino --informat afa --cpu 8 A.hmm A_322.aln.fasta ; hmmbuild --amino --informat afa --cpu 8 B.hmm B_165.aln.fasta ; hmmlogo A.hmm > A.logo ; hmmlogo B.hmm > B.logo   # per-column emission vectors extracted from the HMM files and compared",
      "statistic": "Per-column Jensen-Shannon divergence (bits) between the A and B emission probability vectors, over the 20 amino acids, restricted to columns passing S1's TCS gate. Reported as a vector over columns plus the count of columns exceeding the null threshold.",
      "null": "NULL-SH (primary) and NULL-PHYLO (secondary). A column is called differential only if its JSD exceeds the 95th percentile of the pooled within-subfamily split-half JSD distribution AND the 95th percentile of the simulated-evolution distribution for that same column.",
      "adequacy_check": {
        "measure": "Effective sequence number per subfamily HMM, read from hmmbuild's own output (the 'eff_nseq' field) under its default entropy-weighting, cross-checked by clustering at 62% identity (cd-hit -c 0.62) and counting clusters.",
        "numeric_threshold": "eff_nseq >= 25 for BOTH subfamilies. Derivation: estimating a 20-category emission distribution per column at a precision where a JSD difference is not dominated by sampling noise requires on the order of 1 effective observation per category plus margin; 25 is that floor with ~25% headroom. Cross-check: HMMER's default prior mixture (Dirichlet, Sjolander et al. 1996) dominates the posterior below roughly this count, meaning columns would report the prior, not the data.",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "If eff_nseq < 25 for either subfamily (most plausibly B, n=165, if it is phylogenetically redundant), I abandon per-column JSD entirely and fall back to region-level aggregate divergence only, reporting the eff_nseq number as the reason. Additionally: if the number of columns exceeding the NULL-SH 95th percentile is not greater than the number expected by construction (5% of tested columns), I report S2 as a negative — no positional signal above within-subfamily background — and do not proceed to interpret individual columns.",
      "expected_result_if_H_true": "A small, spatially clustered set of columns (I expect on the order of 5-30) with JSD well above both nulls, concentrated near the catalytic core and the incoming-nucleotide pocket.",
      "expected_result_if_H_false": "Differential columns scattered uniformly across the length with no clustering, and in number not exceeding the split-half background — i.e. the subfamilies differ everywhere a bit and nowhere specifically."
    },

    {
      "id": "S3",
      "question": "H1 — is there a subfamily-specific insertion near the active site that could occlude an instructing strand?",
      "tool": "MAFFT alignment (from S1) + indel extraction script + HMMER for boundary confirmation",
      "exact_invocation": "esl-alistat --amino all_487.aln.fasta ; esl-alimask --gapthresh 0.5 ... ; custom pass over the S1 alignment computing, per alignment block, the fraction of A sequences and of B sequences with non-gap occupancy; blocks with |occupancy_A - occupancy_B| >= 0.8 and run length >= 4 columns called subfamily-specific indels",
      "statistic": "For each candidate indel block: run length in columns, occupancy difference between subfamilies, and the mean inserted-segment length in residues within the subfamily that carries it.",
      "null": "NULL-SH — run the identical indel caller on split-halves of each subfamily. This gives the distribution of apparent 'subfamily-specific' indel blocks that arise between two halves of one subfamily (driven by clade-restricted indels and alignment error). NULL-PHYLO with matched indel rates gives a second distribution under pure genealogy. A candidate indel counts only if its run length exceeds the 95th percentile of both.",
      "adequacy_check": {
        "measure": "Alignment column confidence at the indel boundaries: TCS score of the 5 columns flanking each candidate block on each side, from S1.",
        "numeric_threshold": "Both flanks must have mean TCS >= 5. Also require per-subfamily occupancy to be estimable: the block must be covered by >= 90% of sequences in the subfamily that carries it (otherwise it is a sub-clade feature, not a subfamily feature).",
        "source": "Chang et al. 2014 (TCS, as S1). The 90% occupancy criterion is derived, not cited: below it, the block is present in a minority clade and the A/B contrast is confounded with within-subfamily structure, which NULL-SH would then not bound correctly.",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "If no candidate block survives both nulls with TCS-adequate flanks, I report H1 as unsupported at the sequence level and say so with the longest surviving block's run length and its null percentile. This is reachable: a plausible outcome is that every A-vs-B indel block is matched in length by blocks found between split-halves of A, in which case the number I report is 'largest A/B block = k columns, 95th percentile of split-half blocks = k' or larger.',",
      "expected_result_if_H_true": "At least one contiguous block of >= 8 columns, occupancy difference >= 0.8, TCS-adequate flanks, longer than anything seen in either split-half distribution, and located adjacent to the catalytic core in the structure from S5.",
      "expected_result_if_H_false": "Candidate blocks exist but are no longer than split-half artefacts, or sit far from the catalytic core, or have ragged low-TCS boundaries indicating alignment error rather than a real insertion."
    },

    {
      "id": "S4",
      "question": "H2 and H4 — do the accessory/DNA-binding modules show coevolutionary coupling to the catalytic core differently between subfamilies?",
      "tool": "Coevolution package (CCMpred, or GREMLIN)",
      "exact_invocation": "ccmpred -t 8 -n 100 A_322.aln.a3m A_coupling.mat ; ccmpred -t 8 -n 100 B_165.aln.a3m B_coupling.mat   # Meff computed first via: hhfilter -i aln.a3m -o filt.a3m -id 90 -cov 75 and sequence reweighting at 80% identity",
      "statistic": "Top-L/2 coupling scores (APC-corrected) and the inter-module coupling density between the accessory region and the catalytic core, per subfamily.",
      "null": "NULL-SH applied to coupling density; NULL-PHYLO to confirm couplings are not purely phylogenetic. But see abandon condition — I expect this step to terminate at adequacy.",
      "adequacy_check": {
        "measure": "Meff / L, where Meff is the number of effective sequences after reweighting at 80% sequence identity and L is the number of alignment columns with < 25% gaps.",
        "numeric_threshold": "Meff / L >= 5. Below this, contact predictions are not reliable.",
        "source": "Marks et al. 2011 PLoS ONE 6:e28766 and Morcos et al. 2011 PNAS 108:E1293 establish the >= 5L sequences requirement for direct-coupling contact prediction; Kamisetty, Ovchinnikov & Baker 2013 PNAS 110:15674 quantify precision degradation as a function of Meff/L and show it collapsing in the low-Meff regime.",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "If Meff / L < 5 for either subfamily, I abandon the coevolution step entirely and report it as a declared negative with the computed Meff/L number, making NO coupling-based claim about H2 or H4. **I expect this to trigger.** With n=322 and L in the 451-620 range, Meff/L has a hard ceiling of 322/451 = 0.71 even before redundancy reweighting, and for subfamily B the ceiling is 165/451 = 0.37. Both are an order of magnitude below the threshold. I am registering this step precisely so that its failure is on the record as a pre-declared outcome rather than a silent omission, and I will not rescue it by lowering the threshold, by pooling A and B (which would destroy the differential), or by padding with homologs outside the stated inventory.",
      "expected_result_if_H_true": "Not reachable with this input. If the threshold were met, H2-true would show denser accessory-to-core coupling in the template-dependent subfamily.",
      "expected_result_if_H_false": "Not reachable with this input."
    },

    {
      "id": "S5",
      "question": "H1 and H4 — does the predicted structure of the candidate insertion occupy the space an annealed instructing strand would need, and do the two subfamilies differ in substrate-channel architecture?",
      "tool": "Structure predictor (AlphaFold2 / ColabFold or ESMFold) + structural aligner (TM-align)",
      "exact_invocation": "colabfold_batch --num-recycle 5 --num-models 5 --model-type auto reps.fasta out_structs/   # reps = the 7 reference sequences plus subfamily consensus/centroid sequences ; then: TMalign out_structs/A_rep.pdb out_structs/B_rep.pdb -a",
      "statistic": "(a) TM-score between A and B representative models; (b) per-residue RMSD after superposition, aggregated by region; (c) occupancy of the modelled insertion relative to the position of the instructing strand as inferred from the superposed reference structures.",
      "null": "NULL-FAM for TM-score interpretation (what TM-score do functionally undifferentiated paralog pairs of this length give?) and NULL-SH applied to models built from two split-half consensus sequences of the SAME subfamily — if two consensus models from within A differ structurally as much as A differs from B, the structural difference is not functional.",
      "adequacy_check": {
        "measure": "Per-residue pLDDT from the predictor, evaluated specifically over the candidate insertion region and the catalytic core, plus PAE between the insertion and the core.",
        "numeric_threshold": "Mean pLDDT >= 70 over the region being interpreted, and no interpreted residue below pLDDT 50. Inter-domain PAE <= 10 Angstrom before any claim about the insertion's position RELATIVE to the core. For the TM-align step: TM-score >= 0.5 required to assert the two models share a fold at all.",
        "source": "Jumper et al. 2021 Nature 596:583 — pLDDT < 50 indicates likely disorder and should not be interpreted structurally; 70-90 is the 'confident backbone' band. PAE is the AlphaFold-stated measure for relative domain placement confidence. Xu & Zhang 2010 Bioinformatics 26:889 establish TM-score 0.5 as the fold-sameness threshold (TM-score > 0.5 implies same fold with high posterior).",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "If the candidate insertion region predicts at mean pLDDT < 70, I report its position as undeterminable and make no occlusion claim — H1 goes untested structurally and I say so with the pLDDT number. If inter-domain PAE > 10 Angstrom, I may report the insertion's local fold but NOT its position relative to the active site, which is the only thing H1 actually needs — so that outcome is a functional abandon for H1. If TM-score < 0.5 between A and B representatives, the whole structural comparison is void and I report that instead.",
      "expected_result_if_H_true": "TM-score 0.6-0.9 (same fold), core superposing tightly, and a confidently-modelled (pLDDT >= 70) insertion in one subfamily sitting in or adjacent to the channel occupied by the instructing strand in the reference structures, with the within-A split-half consensus models showing no such difference.",
      "expected_result_if_H_false": "Either the insertion models as low-confidence disorder (pLDDT < 50 — H1 untestable, reported as such), or it models confidently but points away from the substrate channel, or the within-A split-half models show comparable structural divergence, voiding the contrast."
    },

    {
      "id": "S6",
      "question": "H2 — do the subfamilies differ in the presence or integrity of accessory substrate-binding modules outside the catalytic core?",
      "tool": "HMMER (hmmscan against Pfam) + domain architecture comparison",
      "exact_invocation": "hmmscan --cut_ga --domtblout arch_A.tbl Pfam-A.hmm A_322.fasta ; hmmscan --cut_ga --domtblout arch_B.tbl Pfam-A.hmm B_165.fasta",
      "statistic": "Per-subfamily frequency of each detected accessory domain, and the per-sequence domain-architecture string; differential statistic is the difference in domain presence frequency between subfamilies.",
      "null": "NULL-SH — domain-presence frequency difference between split-halves of the same subfamily. This matters because clade-restricted domain loss is common and would otherwise read as a subfamily difference. NULL-PHYLO is not informative here (simulation does not create or destroy domains) and I will not use it for this step.",
      "adequacy_check": {
        "measure": "Detection sensitivity floor: fraction of sequences in each subfamily in which the CATALYTIC core domain itself is detected at the gathering threshold.",
        "numeric_threshold": "The core domain must be detected in >= 95% of sequences in each subfamily. If the core — which I am confident is present in all of them — is detected in fewer, the scan's sensitivity is inadequate for calling accessory-domain ABSENCE, and any absence call would be a detection artefact.",
        "source": "Derived, using Pfam's own curated gathering thresholds (--cut_ga; Finn et al., Pfam) as the detection criterion. The logic is an internal positive control: a domain known a priori to be universal in the family calibrates the false-negative rate of the scan. Eddy 2011 PLoS Comput Biol 7:e1002195 for HMMER3 sensitivity behaviour.",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "If core-domain detection falls below 95% in either subfamily, I abandon all domain-ABSENCE claims (presence claims remain usable) and report the detection rate as the reason. Separately: if the accessory-domain frequency difference between A and B does not exceed the split-half frequency difference, I report H2 as unsupported at the architecture level with both numbers.",
      "expected_result_if_H_true": "One or more accessory domains present in >80% of one subfamily and <20% of the other, with split-half differences for those same domains under 10 percentage points.",
      "expected_result_if_H_false": "Identical architectures in both subfamilies, or frequency differences no larger than the split-half background — meaning any H2 effect is sub-domain and not architectural."
    },

    {
      "id": "S7",
      "question": "Validity gate for H1-H5, and the only direct test of DX01's low-prior element E6 (loss of catalytic chemistry).",
      "tool": "HMMER-derived alignment columns + reference-structure mapping",
      "exact_invocation": "Map the catalytic carboxylate positions from each of the 7 reference sequences onto the S1 alignment columns; compute per-subfamily conservation (fraction of sequences with an acidic residue) at those columns.",
      "statistic": "Per-subfamily conservation fraction at each catalytic column.",
      "null": "NULL-SH for the conservation difference; but the primary use is absolute, not differential — the question is whether conservation approaches 1.0 in both.",
      "adequacy_check": {
        "measure": "TCS at the catalytic columns (from S1), and agreement among the 7 reference sequences on which alignment column each catalytic position maps to.",
        "numeric_threshold": "TCS >= 7 at every catalytic column (stricter than the general >= 5 gate, because a single-column mapping error here invalidates the step), and all 7 references must map to the same column — 7/7 agreement, no exceptions.",
        "source": "Chang et al. 2014 for TCS. The 7/7 agreement requirement is derived: with fewer than unanimous agreement I cannot distinguish a real column from an alignment shift, and there is no statistical remedy at n=7.",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "If TCS < 7 at any catalytic column, or references disagree on the mapping, I drop that column from analysis. If this removes all catalytic columns, S7 is abandoned and reported as a negative. Substantively: if conservation is >= 0.95 in BOTH subfamilies, I report E6 as refuted — which is the outcome I expect and which is still a reportable result.",
      "expected_result_if_H_true": "Conservation >= 0.95 in both subfamilies — catalytic chemistry shared — which SUPPORTS the shared-core premise underlying H1-H4 and refutes E6.",
      "expected_result_if_H_false": "Degraded conservation in one subfamily, which would mean the difference involves chemistry and would substantially reweight the whole DX01 prior toward H0."
    }
  ],

  "steps_deliberately_not_proposed": [
    {
      "method": "Ancestral sequence reconstruction of the pre-duplication enzyme followed by inference about which subfamily retained the ancestral state.",
      "reason": "I cannot interpret its output under this evidence budget. With no outgroup specified in the inventory and no calibration, reconstructed ancestral states at the positions of interest would carry posterior probabilities I have no way to validate, and the DX01 brief forbids proposing a method whose output I have declared I cannot interpret."
    },
    {
      "method": "Molecular dynamics of the substrate channel.",
      "reason": "Not in the supplied tool list, and sampling adequacy could not be checked before the main analysis."
    }
  ]
}
```

**granularity_declaration.json**

```json
{
  "schema": "dx02.granularity_declaration.v1",
  "registered_at": "2026-11-08",
  "rule_accepted": "No step may report at residue granularity unless this file names, in advance, the measurement that demonstrates one alignment position is separable from its immediate neighbours. Reporting finer than the declared granularity is a violation I do not get to repair after evidence release.",

  "separability_test_definition": {
    "id": "SEP-TEST",
    "name": "Adjacent-column separability test",
    "statement": "A column i may be reported as an individual residue-level finding only if ALL THREE of the following hold:",
    "criteria": [
      "(1) Column stability: column i retains its residue composition in >= 90% of 100 alignment perturbation replicates (realignment of bootstrap-resampled sequence sets, and realignment under --genafpair vs --localpair). Source: the column-support logic of Penn et al. 2010 (GUIDANCE, NAR 38:W23), which resamples to produce per-column confidence; 0.90 is GUIDANCE's own commonly applied column-filtering cutoff.",
      "(2) Neighbour independence: the step's statistic at column i remains above its null threshold when columns i-1 and i+1 are masked and the statistic recomputed. If masking a neighbour abolishes the signal, the signal belongs to the local region, not to position i.",
      "(3) Local TCS: columns i-1, i, i+1 each have TCS >= 7 (Chang et al. 2014)."
    ],
    "consequence_of_failure": "The finding is reported at the next coarser granularity declared for that step. It is not discarded — it is reported coarsely, which is a result, not a failure."
  },

  "per_step_granularity": [
    {
      "step": "S1",
      "finest_reportable_granularity": "none",
      "rationale": "S1 produces an alignment and a quality gate, not a spatial finding. Its TCS scores are reported per column but only as a gate on other steps, never as a result about the enzymes."
    },
    {
      "step": "S2",
      "finest_reportable_granularity": "residue — CONDITIONAL on SEP-TEST passing for the specific column.",
      "establishing_measurement": "SEP-TEST, all three criteria, applied per candidate column. Columns passing are reported as individual positions (as alignment columns, with the reference sequence and its accession named for each — never as bare integers). Columns failing any criterion are collapsed into the smallest contiguous region containing them and reported at region granularity.",
      "default_if_untested": "region",
      "expected_outcome": "I expect a minority of candidate columns to pass all three. Most will be reported as regions. I am declaring that in advance so that a region-level result is not read as a retreat."
    },
    {
      "step": "S3",
      "finest_reportable_granularity": "region",
      "establishing_measurement": "Indel block boundaries are defined by occupancy transitions, which are inherently a region-level observable. The block is reported as a contiguous column range with its run length and both flanking TCS scores. I explicitly do NOT claim residue granularity for which specific inserted residue does the occluding — the alignment cannot support that for a subfamily-specific insertion, since the insertion is by definition unalignable to the other subfamily.",
      "default_if_untested": "region"
    },
    {
      "step": "S4",
      "finest_reportable_granularity": "none",
      "rationale": "Expected to abandon at adequacy (Meff/L below threshold). If abandoned, the only output is the Meff/L number itself, which has no spatial granularity. Declaring 'residue-pair' here would be claiming granularity for a step I expect not to run."
    },
    {
      "step": "S5",
      "finest_reportable_granularity": "region (structural)",
      "establishing_measurement": "Granularity is bounded by model confidence, not by alignment. A region may be reported when mean pLDDT >= 70 across it and inter-domain PAE <= 10 Angstrom. Residue-level structural claims (e.g. 'this specific side chain contacts the instructing strand') would additionally require per-residue pLDDT >= 90 across the contacting residue and its neighbours — the AlphaFold 'very high' band (Jumper et al. 2021) — and I expect loop insertions not to reach it. Absent pLDDT >= 90, all structural statements are about regions and channel occupancy, not about residues.",
      "default_if_untested": "domain"
    },
    {
      "step": "S6",
      "finest_reportable_granularity": "domain",
      "establishing_measurement": "hmmscan domain boundaries at Pfam gathering thresholds. Domain presence/absence is the native granularity of this measurement; sub-domain claims from a domain scan would be unsupported by construction.",
      "default_if_untested": "domain"
    },
    {
      "step": "S7",
      "finest_reportable_granularity": "residue — CONDITIONAL on the stricter S7 adequacy gate.",
      "establishing_measurement": "The S7 gate already requires 7/7 reference agreement on the column mapping plus TCS >= 7, which is a stronger positional claim than SEP-TEST criterion (3). SEP-TEST criteria (1) and (2) must also pass. Catalytic positions are the one place I expect residue granularity to be genuinely achievable, because the references anchor them and the columns are near-invariant.",
      "numbering_discipline": "Any position reported at residue granularity is stated as: alignment column index + the residue in a NAMED reference sequence + that reference's species and accession. No free-floating integers. This carries forward the DX01 numbering declaration unchanged.",
      "default_if_untested": "region"
    }
  ],

  "summary_table": {
    "residue_conditional": ["S2", "S7"],
    "region": ["S3", "S5"],
    "domain": ["S6"],
    "none": ["S1", "S4"]
  }
}
```

**power_budget.json**

```json
{
  "schema": "dx02.power_budget.v1",
  "registered_at": "2026-11-08",
  "scope": "All sequence-statistical steps: S2, S3, S4, S6, S7. S1 is a gate and S5 is structural (n=7 references plus consensus models), both handled separately at the end of this file.",

  "why_raw_n_is_not_the_sample_size": "n=322 and n=165 are species-unique but NOT independent: they are tips on a tree and share ancestry. The effective sample size is the number of independent observations after discounting phylogenetic redundancy, and it is the only count I will use for power statements. Reporting 322 as a sample size would overstate power by an unknown but certainly large factor.",

  "per_step_budget": [
    {
      "step": "S2",
      "statistic": "per-column Jensen-Shannon divergence between subfamily emission vectors",
      "effective_sample_size_measure": "eff_nseq as computed by hmmbuild under its default entropy-weighting (read directly from the HMM file header), cross-checked by two independent measures: (a) number of clusters at 62% identity from cd-hit -c 0.62, (b) number of clusters at 80% identity from cd-hit -c 0.80.",
      "expected_eff_n": {
        "subfamily_A": "Expect eff_nseq in the range 40-150 from 322 species-unique sequences. The width of that band is itself an admission: I do not know the phylogenetic depth of the sampling, and if the 322 are concentrated in one well-sampled clade the figure could fall near the low end.",
        "subfamily_B": "Expect eff_nseq in the range 25-90 from 165. This is the one most at risk of failing the threshold.",
        "uncertainty_marking": "These are predictions, not facts. They will be replaced by measured values in DX03."
      },
      "threshold": "eff_nseq >= 25 per subfamily (derivation and source in method_plan.json S2).",
      "action_if_below_threshold": "Do NOT proceed to per-column JSD. Instead: (1) report the measured eff_nseq as the headline negative result for S2; (2) fall back to region-aggregated divergence, where the 20-category estimation problem is replaced by a far coarser one; (3) explicitly downgrade S2's granularity declaration from 'residue-conditional' to 'region'; (4) do not attempt to rescue power by adding sequences outside the stated inventory, which would change the input and void the comparison with the registered plan.",
      "multiple_testing": "Columns tested ~ the number passing the S1 TCS gate, expected 300-500. Control by the NULL-SH empirical distribution rather than by a parametric correction: the split-half null is run on the same number of columns, so its 95th percentile is already a per-column-family-corrected threshold. Report additionally the Benjamini-Hochberg FDR at q=0.05 against the NULL-PHYLO distribution."
    },
    {
      "step": "S3",
      "statistic": "subfamily-specific indel block run length and occupancy difference",
      "effective_sample_size_measure": "Number of independent clades carrying the indel, measured as the number of distinct deepest-level clades in the subfamily tree in which the indel is present, not the number of sequences carrying it.",
      "expected_eff_n": "If an insertion is a genuine subfamily synapomorphy it should be present across essentially all clades of its subfamily. Expect clade-count equal to the full clade count of that subfamily. A clade count of 1-2 would mean a lineage-specific insertion masquerading as a subfamily feature.",
      "threshold": "The indel must be present in >= 90% of sequences AND in >= 3 independent deep clades of its subfamily. The 3-clade floor is derived: with fewer, the observation is not replicated across independent evolutionary histories and a single ancestral insertion event cannot be distinguished from a clade-restricted one.",
      "action_if_below_threshold": "Report the indel as clade-restricted rather than subfamily-defining, with the clade count. This materially weakens H1 and I will say so rather than presenting the block as a subfamily feature."
    },
    {
      "step": "S4",
      "statistic": "APC-corrected coupling scores",
      "effective_sample_size_measure": "Meff after 80%-identity reweighting, divided by L (columns with <25% gaps).",
      "expected_eff_n": "Meff/L <= 0.71 for A and <= 0.37 for B, as hard ceilings from raw counts before any redundancy discount. Realistically I expect 0.1-0.4 for A and 0.05-0.2 for B.",
      "threshold": "Meff/L >= 5 (Marks 2011; Morcos 2011; Kamisetty 2013).",
      "action_if_below_threshold": "Abandon the step. Report the measured Meff/L alongside the threshold and the citation. Make no coupling-based claim about H2 or H4. **I am stating in advance that I expect this action to be the one taken** — the deficit is roughly 10-50x and is not closeable by any choice of flags. I will not substitute a method with a weaker adequacy requirement and present it as equivalent evidence; if I use anything else for H2 it will be S6, which is registered separately with its own gate.",
      "note": "This step is in the plan specifically to make the power deficit a registered, reportable number rather than an unexplained gap in DX03."
    },
    {
      "step": "S6",
      "statistic": "accessory-domain presence frequency difference between subfamilies",
      "effective_sample_size_measure": "Number of independent deep clades per subfamily (as S3), since domain presence is strongly clade-correlated; plus the raw per-subfamily counts for the binomial confidence interval.",
      "expected_eff_n": "Clade counts unknown in advance. For the binomial interval, raw n=322 and n=165 give 95% Wilson intervals on a presence frequency of roughly +/-0.05 and +/-0.08 respectively at p near 0.5 — adequate for detecting the large (>60 percentage point) differences H2 predicts, inadequate for small ones.",
      "threshold": "A frequency difference is reportable only if its Wilson 95% interval excludes the 95th percentile of the NULL-SH split-half frequency-difference distribution, AND the difference is supported in >= 3 independent deep clades per subfamily.",
      "action_if_below_threshold": "Report the difference as clade-confounded and not subfamily-general, with the clade count. Do not claim architectural divergence."
    },
    {
      "step": "S7",
      "statistic": "catalytic-column conservation fraction per subfamily",
      "effective_sample_size_measure": "Raw per-subfamily n for the binomial interval, with the caveat that phylogenetic non-independence inflates apparent precision. Because the expected value is near 1.0, I will report the one-sided Wilson lower bound rather than a symmetric interval.",
      "expected_eff_n": "n=322 and n=165. At an observed conservation of 1.0, the 95% one-sided Wilson lower bounds are approximately 0.991 and 0.982 respectively — ample to distinguish 'universally conserved' from 'degraded in one subfamily'.",
      "threshold": "Conservation lower bound >= 0.95 to call a catalytic position conserved; <= 0.80 point estimate in one subfamily to call it degraded. The band between 0.80 and 0.95 is declared in advance as indeterminate and will be reported as such rather than forced into a call.",
      "action_if_below_threshold": "If a catalytic column lands in the indeterminate band, report it as indeterminate with the number. Do not round toward the hypothesis."
    }
  ],

  "non_sequence_steps": {
    "S5": {
      "sample_size_reality": "n=7 reference sequences plus a small number of consensus/centroid models. This is not a statistical sample and I will not compute p-values over it.",
      "how_power_is_handled_instead": "By per-model confidence (pLDDT, PAE) and by the NULL-FAM and split-half-consensus comparisons, which supply a scale for what structural differences mean. Any S5 claim is a confidence-gated structural observation, explicitly labelled as such and never as a statistically powered result.",
      "action_if_inadequate": "Report pLDDT/PAE numbers and decline the structural claim. See S5 abandon condition."
    },
    "S1": {
      "role": "Gate, not inference. No power budget applies.",
      "action_if_inadequate": "Cascading abandon of S2, S3, S7 as specified in S1's abandon condition."
    }
  },

  "campaign_level_commitment": {
    "statement": "If three or more of S2, S3, S6, S7 abandon at their adequacy gates, I will report that the supplied input cannot discriminate the DX01 hypotheses at the registered standards, and I will report that as the campaign's finding rather than lowering a threshold to produce a positive. The thresholds in this file are frozen on the same terms as the DX01 predictions: revisable only as an explicit new version, never as an edit.",
    "expected_abandons": "At minimum S4. I am on record predicting that one before seeing any data."
  }
}
```

Two things I want visible rather than buried. **S4 is registered to fail** — the Meff/L requirement for coevolution is roughly 10–50× what 322 and 165 sequences can supply, and I would rather that deficit appear as a pre-declared number than as a method quietly missing from DX03. **The split-half null is doing the real work** across S2, S3, S5 and S6: comparing two halves of one subfamily is the only way I can tell how much two groups of these enzymes differ for no functional reason at all, and every differential claim is thresholded against it.