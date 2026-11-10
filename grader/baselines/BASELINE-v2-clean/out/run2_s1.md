Tool use is blocked, so §3.5 cannot be satisfied with a genuine digest — I state that in the artifact rather than fabricate a hex string that would guarantee a mismatch at close. Everything else is below.

`axis_declaration.json`
```json
{
  "artifact": "axis_declaration",
  "version": "1.0",
  "date_utc": "2026-11-08",
  "scored_axis": {
    "id": "AX-TEMPLATE-DEPENDENCE",
    "name_in_own_words": "Whether nucleotide addition onto a primer 3'-OH is instructed in cis by a base-paired templating strand, or proceeds without such instruction",
    "operational_readout": "Ratio of extension rate/efficiency on a primer-template (annealed downstream/templating strand present) versus a single-stranded primer of identical sequence, plus whether the identity of the added nucleotide tracks the templating base.",
    "why_single_axis": "The campaign brief states the pair differs in exactly this property; all mechanistic work registered here aims at explaining that one difference."
  },
  "scoped_out_axes": [
    {
      "id": "OUT-FIDELITY",
      "name": "Nucleotide insertion fidelity / misincorporation spectrum on a templated substrate",
      "reason_out": "A quantitative error-rate axis, separable from whether a template is used at all."
    },
    {
      "id": "OUT-PROCESSIVITY",
      "name": "Processivity and product-length distribution per binding event",
      "reason_out": "Distributive-vs-processive behaviour is measurable independently of template instruction."
    },
    {
      "id": "OUT-PARTNERS",
      "name": "Protein-protein recruitment and complex membership (scaffold/partner binding by accessory domains)",
      "reason_out": "An interaction axis; I will not argue from partner identity to catalytic template use."
    },
    {
      "id": "OUT-EXPRESSION",
      "name": "Tissue/developmental expression pattern, abundance, and subcellular localisation",
      "reason_out": "Organismal-level axis, orthogonal to in-cis chemistry."
    },
    {
      "id": "OUT-STABILITY",
      "name": "Thermal/conformational stability, aggregation, and recombinant expression behaviour",
      "reason_out": "Biophysical handling axis with no claimed bearing on template-dependence."
    },
    {
      "id": "OUT-SECONDARY-CATALYSIS",
      "name": "Any secondary enzymatic activity carried by an accessory domain that is not primer extension (e.g. an excision/lyase-type activity)",
      "reason_out": "A distinct chemical reaction; I will not use it as evidence on the scored axis."
    }
  ],
  "commitment": "If downstream analysis touches any scoped_out axis, that is a self-declared scoring error and is to be recorded as such."
}
```

`sealed_prior.json`
```json
{
  "artifact": "sealed_prior",
  "version": "1.0",
  "date_utc": "2026-11-08",
  "epistemic_status_note": "Every entry below is BELIEF held before evidence release, not established fact for this campaign. Factual claims drawn from background knowledge are tagged source='background_knowledge'; everything else is tagged 'conjecture'.",
  "system_model_prior": {
    "family_guess": {
      "claim": "The pair are two members of a eukaryotic polymerase-X-type nucleotidyltransferase family (pol-beta-like superfamily), in which one paralog performs gap-filling/primer extension on a duplex substrate and its closest paralog adds nucleotides to a single-stranded 3' end without instruction.",
      "confidence_band": "high (0.75-0.9)",
      "source": "background_knowledge"
    },
    "shared_architecture": {
      "claim": "Both paralogs share a two-metal-ion nucleotidyltransferase fold with 8 kDa, fingers, palm and thumb subdomains and conserved acidic carboxylate triad coordinating metal A and metal B; the catalytic core is NOT where they differ.",
      "confidence_band": "high (0.7-0.9)",
      "source": "background_knowledge"
    },
    "locus_of_difference": {
      "claim": "The difference is dominated by a non-catalytic, paralog-specific insertion/loop element near the template-strand channel rather than by substitutions in the metal-binding carboxylates.",
      "confidence_band": "medium-high (0.6-0.8)",
      "source": "conjecture built on background_knowledge"
    }
  },
  "ranked_candidate_elements": [
    {
      "rank": 1,
      "element": "A paralog-specific insertion loop (commonly called 'Loop1') between the fingers/palm region of the template-independent enzyme, which folds into the space a templating strand would occupy.",
      "predicted_role": "Steric and entropic occlusion of the template channel; also provides a surface that stabilises the primer 3' terminus by itself.",
      "confidence_band": "high (0.65-0.85)"
    },
    {
      "rank": 2,
      "element": "Residues of the template-strand-binding surface (fingers-subdomain helix facing the templating base) that are basic/aromatic in the template-dependent paralog and neutral/shortened in the other.",
      "predicted_role": "Loss of grip on the templating base; template becomes tolerated rather than required.",
      "confidence_band": "medium (0.45-0.65)"
    },
    {
      "rank": 3,
      "element": "A single bulky/aromatic or His-type side chain stacking on the incoming nucleotide in the template-independent enzyme that substitutes for the base-pairing partner.",
      "predicted_role": "Surrogate for the templating base; preorganises the nucleotide for catalysis without pairing.",
      "confidence_band": "medium (0.35-0.6)"
    },
    {
      "rank": 4,
      "element": "The 8 kDa / 5'-phosphate-recognition subdomain and its linker rigidity.",
      "predicted_role": "In the template-dependent paralog it anchors a downstream duplex (gap substrate); weaker or differently oriented anchoring removes the requirement for a second strand.",
      "confidence_band": "medium-low (0.3-0.55)"
    },
    {
      "rank": 5,
      "element": "Divalent metal preference coupling (a paralog that is markedly more active with Mn2+ tolerates unpaired geometry better).",
      "predicted_role": "Relaxed geometric checkpoint at the metal-A site permits uninstructed addition.",
      "confidence_band": "low-medium (0.2-0.45)"
    },
    {
      "rank": 6,
      "element": "Interdomain linker length controlling closure of the fingers subdomain onto the nascent pair.",
      "predicted_role": "Determines whether closure requires a correct base pair as a trigger.",
      "confidence_band": "low (0.15-0.35)"
    }
  ],
  "numbering_uncertainty_declaration": {
    "statement": "No accession has been supplied. I therefore commit NO residue integers. All elements above are named by structural role and by motif/loop identity only. If a residue integer appears anywhere downstream, it must be introduced together with species and accession, and it carries no credit here.",
    "residue_integers_stated": []
  },
  "quantitative_priors": [
    {
      "quantity": "Fold-preference of the template-dependent paralog for primer-template over single-stranded primer",
      "prior_belief": "large, >=10-fold",
      "confidence_band": "medium-high (0.6-0.8)"
    },
    {
      "quantity": "Residual templated-mode activity of the template-independent paralog when a duplex is offered",
      "prior_belief": "non-zero but minor; it does not become a faithful copier",
      "confidence_band": "medium (0.5-0.7)"
    },
    {
      "quantity": "Sequence identity between the two paralogs in the catalytic core",
      "prior_belief": "roughly 40-60 percent",
      "confidence_band": "medium-low (0.3-0.55)"
    },
    {
      "quantity": "Whether a single loop swap fully inverts the phenotype",
      "prior_belief": "partial inversion expected, full inversion unlikely",
      "confidence_band": "medium (0.45-0.65)"
    }
  ],
  "known_unknowns": [
    "Whether the difference is primarily steric occlusion or primarily loss of template affinity.",
    "Whether the template-independent paralog is an evolutionary gain of occlusion or a loss of template grip.",
    "Whether substrate channel differences are visible in apo structures or only in ternary complexes."
  ]
}
```

`recognition_declaration.json`
```json
{
  "artifact": "recognition_declaration",
  "version": "1.0",
  "date_utc": "2026-11-08",
  "recognised": true,
  "recognition_point": {
    "sentence": "Section 2, Given, first bullet: 'two paralogous enzymes of one eukaryotic nucleotidyltransferase family differ in one property — template-dependence of synthesis in cis.'",
    "sentences_consumed": 1
  },
  "recognition_basis": [
    "The phrase 'eukaryotic nucleotidyltransferase family' plus 'paralogous' plus a clean template-dependent / template-independent split is a near-unique description of the polymerase X family.",
    "'Adds residues largely without such instruction' matches a terminal-transferase-type activity; 'extends a primer using an annealed complementary strand' matches a gap-filling polymerase of the same family."
  ],
  "identification_committed": {
    "primary": "A polymerase-X family pair: a template-independent terminal transferase (TdT-type) and its closest template-dependent paralog (Pol mu-type).",
    "confidence_band": "medium-high (0.6-0.8)",
    "alternative_1": "Pol lambda paired with the terminal-transferase paralog, if the brief's 'template-dependent' member is the strictly gap-filling one.",
    "confidence_band_alternative_1": "medium-low (0.2-0.4)",
    "alternative_2": "A non-PolX pair, e.g. an RNA nucleotidyltransferase pair in which one member uses an internal template; considered unlikely because the brief says the instruction strand is annealed and complementary.",
    "confidence_band_alternative_2": "low (0.05-0.15)"
  },
  "note": "Recorded for provenance only. Downstream credit should be computed net of everything stated in this file and in sealed_prior.json."
}
```

`hypotheses.json`
```json
{
  "artifact": "hypotheses",
  "version": "1.0",
  "date_utc": "2026-11-08",
  "immutability_note": "Statements and predictions below are frozen. Any change is published as hypotheses.json v2.0 with a changelog, never as an edit.",
  "hypotheses": [
    {
      "id": "HX-OCCLUDE",
      "label": "Steric occlusion of the template channel by a paralog-specific loop",
      "statement_immutable": "The template-independent paralog carries an extra, paralog-specific loop insertion that folds into the volume a complementary templating strand would otherwise occupy, so template use is physically blocked rather than merely unnecessary.",
      "testable_prediction": "Removing or shortening that loop in the template-independent enzyme increases its preference for a primer-template substrate over a single-stranded primer, and grafting the loop into the template-dependent paralog reduces that preference.",
      "discriminating_intervention": "Reciprocal loop swap and loop deletion constructs of both paralogs, assayed side by side on a matched primer-template versus single-stranded primer pair.",
      "validity_conditions": [
        "Both constructs fold and retain measurable catalytic activity on at least one substrate.",
        "Substrates are sequence-matched; only the presence of the annealed strand differs.",
        "Identical metal and nucleotide conditions across constructs."
      ],
      "falsification_clause": {
        "construct_class": "Loop-deleted template-independent paralog and loop-grafted template-dependent paralog.",
        "inverting_verdict": "FALSIFIED if the loop-deleted enzyme remains as template-indifferent as wild type while still catalytically active, AND the loop-grafted enzyme retains full template-dependence. Mere loss of activity in one construct does not falsify."
      }
    },
    {
      "id": "HX-NO-GRIP",
      "label": "Erosion of the template-strand binding surface (loss of positive selection, not steric block)",
      "statement_immutable": "The template-independent paralog has lost the side-chain contacts that grip and position the templating base; the channel is open but unattractive, so a template confers no kinetic advantage.",
      "testable_prediction": "The template-independent enzyme binds a primer-template duplex with affinity similar to, or weaker than, a single-stranded primer, whereas the template-dependent paralog binds the duplex substantially more tightly; restoring the contact residues raises duplex affinity without needing any loop change.",
      "discriminating_intervention": "Binding measurements (anisotropy/EMSA-class) on duplex versus single-strand for both wild types, plus a contact-restoring point-substitution panel in the template-independent enzyme that leaves the loop intact.",
      "validity_conditions": [
        "Binding and catalysis measured on the same substrate set.",
        "Loop remains unmodified in the substitution panel, so the result separates from HX-OCCLUDE.",
        "Protein concentrations verified active-site titrated or at minimum normalised by activity."
      ],
      "falsification_clause": {
        "construct_class": "Loop-intact, contact-restoring point-substitution panel of the template-independent paralog.",
        "inverting_verdict": "FALSIFIED if restoring the full contact set leaves duplex affinity and template preference indistinguishable from wild type while the loop-only intervention of HX-OCCLUDE does shift them."
      }
    },
    {
      "id": "HX-SURROGATE",
      "label": "Active-site preorganisation substitutes for the templating base",
      "statement_immutable": "In the template-independent paralog the incoming nucleotide is positioned for in-line attack by protein side chains alone, so correct base pairing is not required to reach a catalytically competent geometry; the template is permissive rather than instructive.",
      "testable_prediction": "The template-independent enzyme shows little discrimination in incorporation rate between a nucleotide complementary to an offered templating base and a non-complementary one, while the template-dependent paralog discriminates strongly; removing the surrogate stacking/positioning side chain collapses single-strand activity far more than duplex activity.",
      "discriminating_intervention": "Single-nucleotide incorporation comparisons across all four nucleotides on a defined templating base, run for wild type and for a surrogate-residue substitution panel.",
      "validity_conditions": [
        "A single defined templating base is presented, not a mixed template.",
        "Reactions are in the initial-rate regime; no multiple turnovers masking selection.",
        "The surrogate-residue construct is shown to be folded."
      ],
      "falsification_clause": {
        "construct_class": "Surrogate-stacking-residue substitution panel of the template-independent paralog.",
        "inverting_verdict": "FALSIFIED if that panel loses single-strand and duplex activity in equal proportion AND the wild-type enzyme, when given a defined templating base, selects the complementary nucleotide as sharply as the template-dependent paralog does."
      }
    },
    {
      "id": "HX-ANCHOR",
      "label": "Second-strand anchoring requirement, not template reading, is the discriminator",
      "statement_immutable": "The template-dependent paralog requires a second, downstream duplex anchor for productive binding; its apparent template-dependence is partly a substrate-architecture requirement, while the template-independent paralog productively engages a free 3' end.",
      "testable_prediction": "Offering the template-dependent paralog a template strand that lacks the downstream anchoring feature reduces its activity sharply, more than offering the template-independent paralog the same substrate; the template-independent enzyme's activity is largely insensitive to downstream architecture.",
      "discriminating_intervention": "A substrate ladder that varies downstream duplex presence and 5'-end chemistry independently of the templating base, assayed on both wild types and on an anchoring-subdomain-deleted construct.",
      "validity_conditions": [
        "The templating base is held constant across the substrate ladder.",
        "Anchoring-subdomain deletion construct retains core catalytic activity on at least one substrate.",
        "Effects reported as relative, since absence of an effect on one substrate is not by itself falsification."
      ],
      "falsification_clause": {
        "construct_class": "Anchoring-subdomain-deleted template-dependent paralog, assayed across the downstream-architecture substrate ladder.",
        "inverting_verdict": "FALSIFIED if that deletion construct still requires an annealed templating strand to the same degree as wild type, showing template-dependence survives removal of the anchor."
      }
    },
    {
      "id": "HX-CHECKPOINT",
      "label": "Relaxed geometric checkpoint at the catalytic metal site",
      "statement_immutable": "The template-independent paralog tolerates catalytically competent geometry over a wider range of nucleotide positions because its metal-site checkpoint is relaxed, which is what permits uninstructed addition; the template-dependent paralog enforces a narrow geometry that only a correct pair satisfies.",
      "testable_prediction": "Conditions or substitutions that relax geometric stringency push the template-dependent paralog toward uninstructed addition on a single-stranded primer, whereas conditions that tighten geometry push the template-independent paralog toward requiring a template.",
      "discriminating_intervention": "Matched perturbation of the metal/geometry environment applied identically to both paralogs, with the template-preference ratio as the readout.",
      "validity_conditions": [
        "The same perturbation set is applied to both enzymes.",
        "Readout is the ratio of templated to untemplated activity within each enzyme, not absolute rate.",
        "Perturbations verified not to unfold either protein."
      ],
      "falsification_clause": {
        "construct_class": "Metal-site/geometry-perturbed wild-type pair assayed as a matched set.",
        "inverting_verdict": "FALSIFIED if the template-preference ratio of each enzyme is invariant across the whole perturbation set while loop or contact constructs from HX-OCCLUDE / HX-NO-GRIP do move it."
      }
    }
  ],
  "H0": {
    "id": "H0-RESIDUAL",
    "statement_immutable": "The true explanation of the template-dependence difference may lie wholly or partly outside HX-OCCLUDE, HX-NO-GRIP, HX-SURROGATE, HX-ANCHOR and HX-CHECKPOINT — for example in a structural element, dynamic mode, cofactor, post-translational modification, or substrate context not anticipated here.",
    "how_H0_gains_weight": "H0 is favoured if every primary hypothesis fails its own falsification clause, or if the observed determinant maps to a structural element absent from the ranked_candidate_elements list in sealed_prior.json.",
    "no_falsification_clause_rationale": "H0 is residual by construction and is not itself a falsifiable mechanism."
  },
  "distinguishability_matrix_note": "HX-OCCLUDE and HX-NO-GRIP are both channel hypotheses but are separated by the loop-intact substitution panel; HX-SURROGATE is separated by nucleotide-selection readout at a defined templating base; HX-ANCHOR is separated by downstream architecture held against a constant templating base; HX-CHECKPOINT is separated by ratio-invariance under matched perturbation. Overlap is expected and permitted; each clause names a construct class that can invert that hypothesis alone."
}
```

`prereg_commit.sha256`
```json
{
  "artifact": "prereg_commit",
  "version": "1.0",
  "date_utc": "2026-11-08",
  "digest_algorithm": "SHA-256",
  "digest_hex": null,
  "digest_status": "NOT_COMPUTED",
  "reason_not_computed": "Tool use is blocked at the harness level for this task, so no hashing function was available. A hex string is deliberately not fabricated: an invented digest could not match at campaign close and would be a false record. This field is the only unsatisfied schema element and is offered for schema repair before evidence release.",
  "canonicalisation_rule_committed": {
    "input_files_in_order": [
      "axis_declaration.json",
      "sealed_prior.json",
      "recognition_declaration.json",
      "hypotheses.json"
    ],
    "excluded": "prereg_commit.sha256 itself",
    "encoding": "UTF-8, no BOM",
    "per_file_normalisation": "Bytes exactly as emitted in this reply's fenced blocks, with a single trailing newline (0x0A) appended to each file if absent; LF line endings only.",
    "concatenation": "Files concatenated in the order listed, with no separator bytes beyond each file's own trailing newline.",
    "digest": "SHA-256 over the concatenated byte stream, lowercase hex."
  },
  "verification_instruction": "sha256sum of: cat axis_declaration.json sealed_prior.json recognition_declaration.json hypotheses.json  (files written byte-identical to the blocks above). Whatever value that produces is the committed digest; it is fixed by the rule above even though the hex was not computable here.",
  "immutability": "The four input files are frozen as of this reply. Any later change is published as a new version with its own commit record, never as an edit."
}
```

Gate items: scored axis declared, 5 falsifiable hypotheses + H0 present, six axes scoped out. The hash is the single gap — the canonicalisation rule pins the digest deterministically, but the hex itself needs one hashing call I was not permitted to make.