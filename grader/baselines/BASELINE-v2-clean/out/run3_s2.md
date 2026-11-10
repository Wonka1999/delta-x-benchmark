`method_plan.json`
```json
{
  "artifact": "method_plan",
  "version": "1.0",
  "binds_to": "DX01 hypotheses.json v1.0",
  "inputs_assumed": {
    "subfamily_A": "322 species-unique sequences, 451-620 aa (template-dependent paralog per DX01 sealed_prior)",
    "subfamily_B": "165 species-unique sequences, 451-620 aa (template-independent paralog)",
    "references": "7 reference sequences",
    "L_alignment_estimate": "assumed 500-700 alignment columns; every threshold below that depends on L is written as a formula in L, not as a frozen integer"
  },
  "global_preconditions": {
    "id": "S0",
    "name": "input sanity and redundancy audit, run before every other step",
    "tool": "cd-hit + seqkit",
    "exact_invocation": "seqkit stats -a A.fasta B.fasta && cd-hit -i A.fasta -o A.c90 -c 0.90 -n 5 -d 0 -M 8000 && cd-hit -i B.fasta -o B.c90 -c 0.90 -n 5 -d 0 -M 8000",
    "statistic": "N_unique_90 for each subfamily; fraction of sequences with internal X/ambiguity > 2 percent; length outliers outside 451-620",
    "adequacy_check": {
      "threshold": "N_unique_90 >= 100 for subfamily A and >= 60 for subfamily B; ambiguous-residue sequences < 5 percent of set",
      "source": "derived: per-column amino-acid frequency estimate with multinomial standard error sqrt(p(1-p)/Neff) <= 0.05 at p=0.5 requires Neff >= 100; the 60 floor for B is the same derivation at SE <= 0.065, accepted because B is the smaller set by design",
      "computable_before_main_analysis": true
    },
    "abandon_condition": "If N_unique_90 < 60 in either subfamily, every per-column frequency statistic in this plan (S3, S5, S6) is dropped and reported as under-powered; only presence/absence steps (S4) and structure steps (S7, S8) proceed.",
    "note": "This step produces no hypothesis verdict. It gates the rest."
  },
  "steps": [
    {
      "step_id": "S1",
      "question": "none directly — alignment is the shared substrate for S3, S5, S6, S9; included because its adequacy gates them",
      "tool": "MAFFT, then GUIDANCE2",
      "exact_invocation": "mafft --localpair --maxiterate 1000 --reorder --anysymbol --thread 8 AB_combined.fasta > AB.aln.fasta  # then: guidance.pl --seqFile AB_combined.fasta --msaProgram MAFFT --seqType aa --outDir guidance_out --bootstraps 100 --MSA_Param '\\--localpair --maxiterate 1000'",
      "statistic": "GUIDANCE2 column score (CS) per alignment column; alignment-level mean CS; fraction of columns with CS >= 0.93; per-column occupancy (fraction of the 487 sequences with a non-gap character)",
      "null": "Not a differential statistic — no null. Calibration instead: the same GUIDANCE2 procedure run on subfamily A alone and on subfamily B alone, so that the combined-alignment CS is read against each subfamily's own internally-achievable CS rather than against an absolute ideal.",
      "adequacy_check": {
        "threshold": "mean pairwise identity within each subfamily >= 25 percent (computed with esl-alipid from the HMMER/Easel suite); and >= 60 percent of columns in the region of interest reaching GUIDANCE2 CS >= 0.93",
        "source": "25 percent is the twilight-zone floor below which pairwise protein alignments are unreliable (Rost 1999, Protein Eng 12:85, 'Twilight zone of protein sequence alignments'); 0.93 is the GUIDANCE2 default column-removal cutoff (Sela et al. 2015, NAR 43:W7)",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "If mean within-subfamily pairwise identity < 25 percent, or fewer than 60 percent of columns clear CS 0.93, the single combined alignment is abandoned; I fall back to two separate within-subfamily alignments linked only through HMM-to-HMM comparison (S5), and every per-column claim is demoted to region granularity in granularity_declaration.json.",
      "expected_result_if_H_true": "n/a (not a hypothesis test). Expectation: mean CS around 0.85-0.95 in the structured catalytic core, markedly lower (plausibly < 0.6) in the lineage-specific loop region — which is itself informative and is why S2 does not depend on columnwise alignment of that loop.",
      "expected_result_if_H_false": "n/a"
    },
    {
      "step_id": "S2",
      "question": "DX01-H1",
      "tool": "seqkit + custom length extraction anchored on HMMER-defined flanks (no reliance on within-loop column homology)",
      "exact_invocation": "hmmsearch --domtblout core.domtbl -E 1e-5 --domE 1e-5 polx_core.hmm AB_combined.fasta  # extract, per sequence, the residue distance between the two flanking core-HMM match states that bracket the lineage-specific insertion; report as insertion_length",
      "statistic": "difference in median insertion length between subfamily B and subfamily A, in residues (delta_L), plus the overlap coefficient of the two length distributions",
      "null": "Two nulls, both required. (a) Within-subfamily split-half: 1000 random species-stratified bipartitions of subfamily A alone (and separately of B alone), recomputing delta_L between the two halves — this calibrates how large a median length difference arises between two groups of this size that differ for no functional reason. (b) Phylogeny-matched indel null: all other inter-core-match-state gap regions across the same alignment, each scored for its own A-vs-B median length difference, giving an empirical distribution of 'how different are A and B at an arbitrary indel region'. The reported delta_L must exceed the 99th percentile of BOTH null distributions.",
      "adequacy_check": {
        "threshold": "the two flanking core-HMM match states must be assigned with per-residue posterior >= 0.9 in >= 90 percent of all 487 sequences (HMMER --domtblout plus alignment posterior from hmmalign)",
        "source": "0.9 posterior is HMMER's own reliability annotation cutoff for confidently aligned match states (Eddy 2011, PLoS Comput Biol 7:e1002195; HMMER3 user guide posterior-probability banding)",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "Abandon if either flank fails the 0.9-posterior/90-percent criterion (the insertion has no stable anchor, so its length is not measurable), OR if delta_L falls below the 99th percentile of the within-subfamily split-half null — in which case I report: the loop length difference is within the range two arbitrary halves of one subfamily produce, and H1's sequence-level signature is absent.",
      "expected_result_if_H_true": "delta_L on the order of 10 or more residues with distribution overlap coefficient < 0.2, exceeding the 99th percentile of both nulls; the split-half null centred near 0 with a spread of only a few residues.",
      "expected_result_if_H_false": "delta_L of a few residues, overlap coefficient > 0.5, inside the split-half null — the insertion is not subfamily-diagnostic in length."
    },
    {
      "step_id": "S3",
      "question": "DX01-H1 and DX01-H3 jointly — which alignment positions carry subfamily-diagnostic character at all",
      "tool": "custom per-column Jensen-Shannon divergence between subfamily-A and subfamily-B amino-acid frequency vectors, with Henikoff position-based sequence weighting",
      "exact_invocation": "esl-weight -p AB.aln.fasta > AB.weighted.sto  # then per column c: JSD(f_A(c) || f_B(c)) using weighted frequencies, BLOSUM62 background pseudocount of 1/sqrt(Neff) per Capra-Singh",
      "statistic": "per-column JSD, and the rank of the loop-region columns and the templating-pocket columns within the genome-wide (alignment-wide) JSD distribution",
      "null": "Three-tier. (a) Within-subfamily split-half null (required): 1000 species-stratified random bipartitions of subfamily A alone, computing per-column JSD between the halves — this is the central calibration, because two halves of one subfamily differ for no functional reason but still differ. (b) Phylogenetically-structured split-half: instead of random halves, split A at its deepest tree bipartition (FastTree -lg AB.aln.fasta), which produces the maximum JSD achievable from shared ancestry alone and is a strictly harder null than random halves. (c) Simulation null: sequences evolved along the inferred A+B tree under a site-homogeneous LG+G model with no subfamily-specific shift (pyvolve or INDELible), recomputing per-column JSD — this null can plausibly produce column-level A-vs-B divergence purely from tree shape and rate heterogeneity.",
      "adequacy_check": {
        "threshold": "per-column effective sample size Neff(c) >= 25 in BOTH subfamilies at that column, where Neff is the Henikoff-weighted count of non-gap sequences; columns failing this are not scored",
        "source": "derived: a 20-category frequency vector estimated from Neff observations has multinomial SE sqrt(p(1-p)/Neff); at Neff=25 and p=0.5 the SE is 0.10, which is the largest error for which a JSD difference of 0.2 remains distinguishable from zero at 2 SE. Consistent with the sequence-count guidance in Capra & Singh 2007 (Bioinformatics 23:1875) that conservation scoring degrades sharply below a few tens of effective sequences.",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "Abandon the per-column JSD step entirely if fewer than 50 percent of core columns reach Neff(c) >= 25 in both subfamilies. Abandon any individual column's claim if its JSD does not exceed the 99th percentile of the phylogenetically-structured split-half null (b). If NO column in the loop region or pocket region clears (b), report: subfamily-diagnostic positions are not separable from ancestry-driven divergence at this depth.",
      "expected_result_if_H_true": "a small, spatially clustered set of columns (loop flanks and/or pocket) with JSD above the 99th percentile of all three nulls; split-half null (a) centred low with a tight tail.",
      "expected_result_if_H_false": "loop and pocket columns sit inside the bulk of the alignment-wide JSD distribution and inside the structured split-half null — no diagnostic positions recoverable."
    },
    {
      "step_id": "S4",
      "question": "DX01-H2 — is the downstream-anchoring module present and intact in each subfamily",
      "tool": "HMMER profile search for the small N-terminal 5'-phosphate-binding domain and the helix-hairpin-helix motifs",
      "exact_invocation": "hmmscan --domtblout anchor.domtbl -E 1e-5 --domE 1e-5 --cpu 8 Pfam-A.hmm AB_combined.fasta  # score presence/absence and domain bit score per sequence for the 8kDa-type and HhH-containing models",
      "statistic": "fraction of sequences in each subfamily with a significant match to the anchoring domain model; difference in median domain bit score between subfamilies",
      "null": "Within-subfamily split-half null on bit score (1000 random bipartitions of A, and of B, recomputing the median bit-score difference), plus a decoy-domain null: the same presence/absence and bit-score contrast computed for 50 unrelated Pfam models that match neither subfamily preferentially, giving the distribution of apparent A-vs-B domain-score differences expected from composition and length alone.",
      "adequacy_check": {
        "threshold": "domain-level E-value <= 1e-5 and the per-domain bias-corrected bit score must exceed the model's own trusted cutoff (TC) where Pfam supplies one; model coverage of the matched region >= 70 percent of model length",
        "source": "E <= 1e-5 is a standard conservative domain-annotation cutoff and Pfam TC is the curated per-model threshold (Eddy 2011, PLoS Comput Biol 7:e1002195; Mistry et al. 2021, NAR 49:D412)",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "Abandon if no Pfam/custom model for the anchoring domain reaches E <= 1e-5 in the majority of EITHER subfamily — i.e. the domain is not detectable by profile methods at this divergence, so presence/absence cannot be called and H2 gets no sequence-level verdict. Also abandon the differential claim if the bit-score difference falls inside the split-half null.",
      "expected_result_if_H_true": "near-universal confident detection in subfamily A; markedly lower detection fraction or systematically lower bit score in subfamily B, outside both nulls.",
      "expected_result_if_H_false": "the anchoring domain is detected at comparable rates and scores in both subfamilies — anchoring presence does not distinguish them, and H2 must be tested structurally (S8) or not at all."
    },
    {
      "step_id": "S5",
      "question": "DX01-H1 and DX01-H3 — subfamily-specific profile divergence localised without assuming a single combined alignment is correct",
      "tool": "HMMER (hmmbuild per subfamily) plus HH-suite profile-profile comparison",
      "exact_invocation": "hmmbuild --amino --cpu 8 A.hmm A.aln.sto && hmmbuild --amino --cpu 8 B.hmm B.aln.sto && hhmake -i A.a3m -o A.hhm && hhmake -i B.a3m -o B.hhm && hhalign -i A.hhm -t B.hhm -o AvsB.hhr -glob",
      "statistic": "per-match-state profile dissimilarity along the A-to-B profile alignment; count and location of match states present in one profile and absent (insert/delete) in the other",
      "null": "Within-subfamily split-half null: build profiles from two random halves of subfamily A, hhalign them to each other, and take the resulting per-match-state dissimilarity distribution as the calibration for 'how different are two profiles built from the same subfamily'. Repeated 200 times. A claimed A-vs-B divergence at a match state must exceed the 99th percentile of this distribution.",
      "adequacy_check": {
        "threshold": "each subfamily profile must be built from Neff >= 10 effective sequences as reported by hhmake's own Neff field, and the A-vs-B profile alignment must reach HH-suite probability >= 95 percent with coverage >= 80 percent of the shorter profile",
        "source": "HH-suite documentation treats probability >= 95 percent as confident homology and reports Neff as the profile-diversity statistic; Neff >= 10 is the diversity floor below which HHM profiles approach single-sequence behaviour (Steinegger et al. 2019, BMC Bioinformatics 20:473; Soding 2005, Bioinformatics 21:951)",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "Abandon if the A-vs-B profile alignment probability < 95 percent or coverage < 80 percent (profiles too diverged to align reliably, so per-match-state claims are meaningless), or if no match state exceeds the split-half 99th percentile.",
      "expected_result_if_H_true": "confident global profile alignment with a contiguous insert region in one profile corresponding to the lineage-specific loop, plus a handful of high-dissimilarity match states near the pocket, both outside the split-half null.",
      "expected_result_if_H_false": "dissimilarity is diffuse and everywhere inside the split-half envelope; the only structured difference is the loop insert and nothing localises near the pocket."
    },
    {
      "step_id": "S6",
      "question": "DX01-H3 — are there specificity-determining positions independent of the loop",
      "tool": "GroupSim (or SDPfox) specificity-determining-position scoring on the combined alignment with the two subfamilies as the groups",
      "exact_invocation": "python group_sim_sdp.py -c 0 -m blosum62.mat AB.aln.fasta A_ids.txt B_ids.txt > sdp.scores",
      "statistic": "per-column SDP score and its rank; number of SDP-positive columns outside the loop region",
      "null": "Within-subfamily split-half null (required): run the identical GroupSim procedure using two random halves of subfamily A as the two 'groups', 1000 times, to obtain the distribution of top SDP scores achievable when there is no functional distinction whatsoever. Plus the phylogenetic split-half variant (deepest bipartition of A) as the harder null, since SDP methods are known to report ancestry structure as specificity.",
      "adequacy_check": {
        "threshold": "both groups must have Neff >= 25 at the scored column (same Henikoff-weighted criterion and derivation as S3), and the between-group mean pairwise identity must be below the within-group mean pairwise identity by at least 10 percentage points (esl-alipid), otherwise the groups are not separable and group-based scoring is undefined",
        "source": "Neff derivation as in S3; the group-separation requirement follows the stated applicability condition of group-based SDP scoring that the partition must correspond to real sequence structure (Capra & Singh 2008, Bioinformatics 24:1473)",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "Abandon if the within-subfamily split-half null produces top SDP scores at or above the real A-vs-B top scores — meaning the method cannot distinguish function from arbitrary partition at this sample size. This is a reachable and, given 322 and 165 sequences with strong phylogenetic structure, a genuinely plausible outcome; it would be reported as a negative result for the method, not for H3.",
      "expected_result_if_H_true": "at least one non-loop column with SDP score above the 99th percentile of both split-half nulls, located in or adjacent to the templating-base pocket.",
      "expected_result_if_H_false": "no non-loop column clears the structured split-half null; all apparent specificity is loop-associated or ancestry-driven."
    },
    {
      "step_id": "S7",
      "question": "DX01-H5 — is there coupling between loop positions and pocket positions",
      "tool": "coevolution analysis (GREMLIN / CCMpred / plmDCA)",
      "exact_invocation": "ccmpred -t 8 AB.aln.a3m ccm.mat  # or: gremlin_cpp -i AB.aln.a3m -o gremlin.out -max_iter 100",
      "statistic": "APC-corrected coupling strength between loop-region columns and pocket columns, ranked against all column pairs at equal sequence separation",
      "null": "Within-subfamily split-half null plus a shuffled-MSA null in which each column is independently permuted across sequences, destroying coupling while preserving column composition and overall sequence entropy; the reported coupling must exceed the 99th percentile of both.",
      "adequacy_check": {
        "threshold": "Nf = Neff / sqrt(L) >= 64, where Neff is the number of sequences clustered at 80 percent identity and L is the number of scored columns",
        "source": "Ovchinnikov et al. 2017, Science 355:294, which establishes Nf >= 64 as the alignment-depth regime in which coevolution-derived contacts are reliable; corroborated by the ~5L sequence requirement for DCA contact recovery in Morcos et al. 2011, PNAS 108:E1293",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "Abandon if Nf < 64. I state in advance that I expect this step to be abandoned: with at most 487 combined sequences and L on the order of 500-700, Nf is approximately 487/sqrt(600) = 19.9, roughly three-fold below threshold, and the per-subfamily values (13.1 for A, 6.7 for B) are far worse. I am including this step with its threshold precisely so that the abandonment is a declared, computable outcome rather than a silent omission; the planned report is 'coevolution not attempted, Nf = <value> against a required 64'. H5 therefore receives no sequence-coupling verdict and is deferred to the experimental matrix registered in DX01.",
      "expected_result_if_H_true": "not reachable at this depth",
      "expected_result_if_H_false": "not reachable at this depth"
    },
    {
      "step_id": "S8",
      "question": "DX01-H1 and DX01-H2 — structural occlusion of the instructing-strand channel, and intactness of the anchoring pocket",
      "tool": "structure predictor (AlphaFold2/3 or ESMFold) on the 7 reference sequences, then structural alignment",
      "exact_invocation": "colabfold_batch --num-recycle 6 --num-models 5 --amber refs.fasta af_out/  # then: USalign -mm 0 -ter 1 A_ref.pdb B_ref.pdb -o aln  (TM-score normalised by the shorter chain)",
      "statistic": "(i) TM-score between the catalytic cores of an A-reference and a B-reference model; (ii) minimum heavy-atom distance from the modelled loop to the putative instructing-strand channel axis, defined geometrically by superposing a known Pol-X ternary complex; (iii) per-residue pLDDT over the loop and over the anchoring pocket",
      "null": "Within-subfamily structural split-half: pairwise TM-scores and loop-to-channel distances among the A-references alone, and among the B-references alone, giving the within-subfamily spread against which the A-vs-B difference is read. A cross-subfamily difference must exceed the within-subfamily maximum.",
      "adequacy_check": {
        "threshold": "mean pLDDT >= 70 over the region being interpreted, and strictly: no claim about loop position where loop pLDDT < 70; TM-score >= 0.5 required before two models are treated as the same fold",
        "source": "pLDDT > 70 is the AlphaFold confidence band for correct backbone, < 50 indicates likely disorder (Jumper et al. 2021, Nature 596:583; Tunyasuvunakool et al. 2021, Nature 596:590); TM-score >= 0.5 as the same-fold boundary (Xu & Zhang 2010, Bioinformatics 26:889)",
        "computable_before_main_analysis": true
      },
      "abandon_condition": "Abandon the occlusion geometry claim if loop pLDDT < 70 — which for a long lineage-specific insertion is a genuinely likely outcome, and would be reported as 'the element H1 names is predicted with confidence too low to place in or out of the channel'. Abandon the fold-comparison claim if TM-score < 0.5. Neither abandonment falsifies H1; both are reported as method negatives.",
      "expected_result_if_H_true": "catalytic cores superpose at TM-score well above 0.5; the B-reference loop is modelled with pLDDT >= 70 and occupies the channel region, while the A-reference loop does not; cross-subfamily loop-position difference exceeds the within-subfamily spread.",
      "expected_result_if_H_false": "loops in both subfamilies are modelled away from the channel, or the cross-subfamily loop-position difference falls inside the within-subfamily spread."
    },
    {
      "step_id": "S9",
      "question": "DX01-H4 — kinetic competition rather than structural exclusion",
      "tool": "none proposed",
      "exact_invocation": "n/a — deliberately not proposed",
      "statistic": "n/a",
      "null": "n/a",
      "adequacy_check": {
        "threshold": "n/a",
        "source": "n/a",
        "computable_before_main_analysis": true,
        "note": "H4 is a statement about relative rates in a reaction with a diffusing, annealing substrate. No sequence or static-structure method in the DX03/DX04 inventory produces a quantity I have declared I can interpret as a rate ratio. Per section 5 of this brief, proposing a method whose output I cannot interpret is disallowed, so I propose none."
      },
      "abandon_condition": "n/a — the step is declined in advance rather than abandoned mid-stream. H4 remains testable only by the constrained-substrate experiment registered in DX01, and will receive no computational verdict in this campaign.",
      "expected_result_if_H_true": "n/a",
      "expected_result_if_H_false": "n/a"
    }
  ]
}
```

`granularity_declaration.json`
```json
{
  "artifact": "granularity_declaration",
  "version": "1.0",
  "rule_committed": "No step may report at residue granularity unless its own separability test, named below and computed on the real data, passes. Failing the separability test does not invalidate the step; it demotes the report one level (residue -> region -> domain -> none). Demotion is recorded, not hidden.",
  "separability_test_definition": {
    "name": "adjacent-column separability under sequence bootstrap",
    "procedure": "Resample sequences (not columns) with replacement 1000 times, stratified by subfamily. Recompute the step's per-column statistic. A column c is separable from its neighbours if (i) the 95 percent bootstrap interval of statistic(c) does not overlap the 95 percent interval of statistic(c-1) or statistic(c+1), and (ii) the lag-1 autocorrelation of the statistic along the alignment, estimated over the scored region, is below 0.5 — if neighbouring columns move together, a single column is not an independent unit of claim.",
    "threshold": "both conditions required; region granularity is used otherwise, where a region is the maximal run of columns whose intervals mutually overlap, reported with its column range and its boundary uncertainty",
    "source": "sequence-level (not column-level) bootstrap is the resampling unit that respects the actual independent observations in an MSA (Felsenstein 1985, Evolution 39:783, applied to sequences rather than sites); the lag-1 autocorrelation criterion is a derived requirement that a per-residue claim must not be a smoothed copy of its neighbour"
  },
  "per_step": [
    {
      "step_id": "S0",
      "finest_permitted_granularity": "none",
      "establishing_measurement": "n/a — a whole-set audit, reports one number per subfamily"
    },
    {
      "step_id": "S1",
      "finest_permitted_granularity": "column (reported as region)",
      "establishing_measurement": "GUIDANCE2 per-column score already carries a bootstrap over alignment perturbations; columns are reported in contiguous CS >= 0.93 blocks, never as isolated single-column confidence claims"
    },
    {
      "step_id": "S2",
      "finest_permitted_granularity": "region — the insertion as a whole, with its flanking anchor positions",
      "establishing_measurement": "None attempted at residue level and none possible: the statistic is a length, which has no within-loop positional resolution by construction. I commit in advance not to report any residue-level claim inside the loop from S2, regardless of what the alignment appears to show."
    },
    {
      "step_id": "S3",
      "finest_permitted_granularity": "residue, CONDITIONAL on the separability test above passing at that column; otherwise region",
      "establishing_measurement": "adjacent-column separability under sequence bootstrap, 1000 resamples, both conditions (non-overlapping 95 percent intervals with both neighbours, and lag-1 autocorrelation < 0.5). Columns failing either condition are merged into the enclosing region and reported with a column range."
    },
    {
      "step_id": "S4",
      "finest_permitted_granularity": "domain",
      "establishing_measurement": "the statistic is domain presence/absence and a domain-level bit score; HMMER domain boundaries carry envelope coordinates that routinely differ from alignment coordinates by several residues, so no sub-domain claim is permitted. The envelope-versus-alignment coordinate spread in the domtblout will be reported as the boundary uncertainty."
    },
    {
      "step_id": "S5",
      "finest_permitted_granularity": "region (match-state block)",
      "establishing_measurement": "profile-profile match states are themselves a many-to-one summary of columns; separability would require the bootstrap test above applied to per-match-state dissimilarity. I declare in advance that S5 reports only contiguous blocks of >= 3 match states that jointly exceed the split-half null, never a single match state."
    },
    {
      "step_id": "S6",
      "finest_permitted_granularity": "residue, CONDITIONAL on the same separability test as S3, AND on the column clearing the structured split-half null in S6's own null set",
      "establishing_measurement": "adjacent-column separability under sequence bootstrap. SDP scores are known to be spatially smeared by local conservation gradients, so the lag-1 autocorrelation condition is expected to bind here; if it does, S6 reports pocket-adjacent regions, not positions."
    },
    {
      "step_id": "S7",
      "finest_permitted_granularity": "none",
      "establishing_measurement": "the step is expected to be abandoned on its Nf adequacy threshold before producing output; if abandoned, no granularity is claimed at all."
    },
    {
      "step_id": "S8",
      "finest_permitted_granularity": "region, with a per-residue confidence overlay that is reported but not interpreted as a positional claim",
      "establishing_measurement": "per-residue pLDDT is the measurement; it establishes confidence, not separability. A residue-level structural claim would additionally require the predicted-aligned-error (PAE) between the loop residue and the channel-defining core residues to be below 5 angstroms, which I commit to reporting; absent that, loop placement is reported as a region-level geometric statement with an explicit distance uncertainty."
    },
    {
      "step_id": "S9",
      "finest_permitted_granularity": "none",
      "establishing_measurement": "n/a — no method proposed"
    }
  ]
}
```

`power_budget.json`
```json
{
  "artifact": "power_budget",
  "version": "1.0",
  "effective_sample_size_definition": {
    "primary": "Neff computed as the sum of Henikoff position-based sequence weights (esl-weight -p), reported per subfamily and per column",
    "secondary": "Nclust80 — number of clusters at 80 percent sequence identity (cd-hit -c 0.80), used for the coevolution Nf statistic to match the convention of the cited source",
    "why_both": "Henikoff weights are the right currency for per-column frequency estimates; 80-percent clustering is the currency in which the published coevolution depth threshold was derived. Mixing them would make the threshold uninterpretable."
  },
  "nominal_counts": {
    "subfamily_A": 322,
    "subfamily_B": 165,
    "combined": 487,
    "L_assumed_for_arithmetic": 600,
    "caveat": "L is assumed, not measured. All Nf values below will be recomputed with the observed L before any threshold decision."
  },
  "per_step_budget": [
    {
      "step_id": "S0",
      "statistic_requiring_power": "N_unique_90",
      "expected_effective_n": "A: 200-300 after 90-percent clustering (species-unique input makes heavy redundancy unlikely but not impossible in recently radiated clades); B: 110-160",
      "measurement": "cd-hit -c 0.90 cluster count",
      "threshold": "A >= 100, B >= 60",
      "action_if_below": "drop all per-column frequency steps (S3, S5, S6) and report the campaign as presence/absence plus structure only"
    },
    {
      "step_id": "S2",
      "statistic_requiring_power": "median insertion-length difference",
      "expected_effective_n": "number of sequences with both anchors confidently assigned; expected >= 90 percent of each set, so roughly 290 (A) and 148 (B)",
      "measurement": "count of sequences passing the 0.9-posterior anchor criterion",
      "threshold": "at least 100 anchored sequences in A and 50 in B; derived from the requirement that a median's bootstrap 95 percent interval be narrower than half the effect size I would call meaningful (5 residues), which for a length distribution with SD of about 8 residues needs n >= 40 per group, with a 2x safety margin applied because the split-half null must also be estimated from the same data",
      "action_if_below": "report the length comparison with an explicitly widened interval and demote the claim from 'subfamily-diagnostic' to 'suggestive'; if below 40 in either group, abandon S2"
    },
    {
      "step_id": "S3",
      "statistic_requiring_power": "per-column JSD",
      "expected_effective_n": "Henikoff Neff typically falls to 30-60 percent of raw count in a phylogenetically structured set; my advance expectation is Neff(A) around 100-190 and Neff(B) around 50-100, with per-column values lower still in gappy regions",
      "measurement": "esl-weight -p, summed weights overall and per column among non-gap sequences",
      "threshold": "Neff(c) >= 25 in both subfamilies per column (derivation in method_plan S3 adequacy_check); alignment-level Neff(B) >= 40",
      "action_if_below": "columns below threshold are masked and the masked fraction is reported as a headline number. If Neff(B) < 40 overall, the per-column differential is abandoned and replaced by the profile-level comparison in S5, which tolerates lower diversity."
    },
    {
      "step_id": "S4",
      "statistic_requiring_power": "domain detection fraction and bit-score difference",
      "expected_effective_n": "full 322 and 165 — presence/absence is per-sequence and does not require diversity",
      "measurement": "count of sequences with domain E <= 1e-5",
      "threshold": "a detection-fraction difference of 10 percentage points between subfamilies is resolvable at these n with a binomial 95 percent interval half-width of about 5 points for A and 8 for B; differences smaller than 15 points will not be claimed",
      "action_if_below": "n/a — this step is not sample-limited; the binding constraint is model sensitivity, handled by S4's abandon condition"
    },
    {
      "step_id": "S5",
      "statistic_requiring_power": "profile Neff as reported by hhmake",
      "expected_effective_n": "hhmake Neff for a 322-sequence diverse family typically lands between 6 and 11; for 165 sequences, between 5 and 10. This is uncomfortably near the floor and I am stating so in advance.",
      "measurement": "the Neff field in the .hhm header",
      "threshold": "Neff >= 10 per profile",
      "action_if_below": "If one profile has Neff between 7 and 10, proceed but report the per-match-state claims as region-level only with the Neff shortfall stated beside every claim. If Neff < 7 for either profile, abandon S5. I flag now that abandonment here is a realistic outcome for subfamily B."
    },
    {
      "step_id": "S6",
      "statistic_requiring_power": "SDP score and the split-half null distribution",
      "expected_effective_n": "same Henikoff Neff as S3, but the split-half null halves it: each pseudo-group in the within-A null has Neff of roughly 50-95",
      "measurement": "esl-weight -p on each bootstrap half",
      "threshold": "each null half must retain Neff >= 25, otherwise the null is computed at lower power than the real comparison and would be biased toward making the real result look significant",
      "action_if_below": "If the split-half halves cannot reach Neff >= 25, replace the 50/50 split with a 50-percent subsample of A matched in size and Neff to subfamily B, so that null and observation are power-matched. If even that fails, abandon S6 — a null computed at lower power than the test is worse than no null."
    },
    {
      "step_id": "S7",
      "statistic_requiring_power": "Nf = Nclust80 / sqrt(L)",
      "expected_effective_n": "computed in advance from the stated counts: combined Nf = 487/sqrt(600) = 19.9; subfamily A alone = 322/sqrt(600) = 13.1; subfamily B alone = 165/sqrt(600) = 6.7. Nclust80 will be lower than the raw count, so these are upper bounds.",
      "measurement": "cd-hit -c 0.80 cluster count divided by sqrt(observed L)",
      "threshold": "Nf >= 64 (Ovchinnikov et al. 2017, Science 355:294)",
      "action_if_below": "Abandon S7 and report the shortfall numerically. To reach Nf = 64 at L = 600 would require about 1568 clustered sequences, roughly 3.2x what the campaign supplies; even pooling both subfamilies and all homologs available in the inventory does not close that gap. This is declared now so that the abandonment at DX03/DX04 is a pre-registered prediction, not a retrospective excuse."
    },
    {
      "step_id": "S8",
      "statistic_requiring_power": "per-residue pLDDT and cross-reference TM-score spread",
      "expected_effective_n": "7 reference structures total; with an unknown A/B split, the within-subfamily null may rest on as few as 3 structures per side, giving 3 pairwise comparisons",
      "measurement": "count of reference models per subfamily passing mean pLDDT >= 70 over the catalytic core",
      "threshold": "at least 3 confident models per subfamily, giving >= 3 within-subfamily pairs per side; this is the minimum at which a 'within-subfamily spread' is a range rather than a single number",
      "action_if_below": "If fewer than 3 confident models exist on either side, the within-subfamily structural null cannot be formed. In that case I report the cross-subfamily structural difference as an uncalibrated observation explicitly labelled as having no null, and it carries no verdict for H1 or H2. I will not substitute a literature-reported spread for a measured one."
    }
  ],
  "campaign_level_statement": "Two steps (S7 certainly, S5 plausibly for subfamily B) are predicted to abandon on their own pre-declared thresholds given the sequence counts stated in the brief. Reporting those abandonments with their numbers is the intended output of this plan, not a shortfall of it."
}
```

Nine steps, one declined outright (H4 — no tool in the inventory yields a rate ratio I can interpret). Every step carries a sourced numeric adequacy threshold, and every differential statistic carries a within-subfamily split-half null plus a harder phylogenetically-structured or simulation null. Two abandon conditions are predicted to fire from the stated counts alone: coevolution at Nf ≈ 19.9 against a required 64, and possibly the subfamily-B profile at Neff < 7. Those numbers are registered now so the negatives are predictions, not excuses.