Tool use is blocked, so all four artifacts are inline below. One honest caveat up front: I cannot execute SHA-256 without tools, so `prereg_commit.sha256` contains an exact, deterministic canonicalization recipe instead of a fabricated hex digest — a guessed digest would be guaranteed not to match at campaign close.

`axis_declaration.json`
```json
{
  "artifact": "axis_declaration",
  "version": "1.0",
  "committed_utc": "2026-11-08",
  "scored_axis": {
    "name": "template-directed-ness of in-cis nucleotide addition",
    "my_words": "Given a single DNA substrate that already carries an annealed strand positioned to instruct the next addition, what fraction of residues this enzyme adds to the 3'-OH are the ones that strand dictates, versus residues chosen without reference to it.",
    "operational_readout": "per-position identity concordance between added residue and the instructing base on the same molecule, measured on one substrate class, at fixed metal and nucleotide pools",
    "why_this_axis": "It is the only axis the campaign brief names as differing between the pair, and it is a property of synthesis in cis rather than of partners, localisation, or downstream processing."
  },
  "scoped_out_axes": [
    {
      "axis": "dRP-lyase / 5'-deoxyribose-phosphate excision activity of the small N-terminal domain",
      "reason_out": "a separate chemical reaction (lyase, not transferase); I will not measure, model, or argue from it"
    },
    {
      "axis": "protein-protein recruitment via the N-terminal BRCT module (end-joining partner binding, complex assembly, in-trans synapsis)",
      "reason_out": "in-trans partner biology; the scored axis is explicitly in cis"
    },
    {
      "axis": "tissue-restricted expression, developmental timing, and subcellular localisation of each paralog",
      "reason_out": "organismal/regulatory, not an enzymological property of the catalytic cycle"
    },
    {
      "axis": "thermal and chemical stability of the folded protein (Tm, aggregation, protease sensitivity)",
      "reason_out": "a construct-quality control variable, not a mechanism I will interpret"
    },
    {
      "axis": "oligomerisation state and concentration-dependent self-association",
      "reason_out": "not implicated in per-residue instruction use; will not be invoked as an explanation"
    },
    {
      "axis": "post-translational modification and regulated turnover of either paralog",
      "reason_out": "cellular regulation layer, outside the in-vitro in-cis axis"
    }
  ],
  "explicitly_retained_as_in_scope_supporting_variables": [
    "catalytic competence controls (any mutant must still add residues at all)",
    "substrate architecture (gapped vs recessed vs blunt vs single-stranded 3' overhang) as the independent variable defining 'in cis instruction available'"
  ],
  "note": "Supporting variables are listed so that using them later is not mistaken for re-opening a scoped-out axis."
}
```

`sealed_prior.json`
```json
{
  "artifact": "sealed_prior",
  "version": "1.0",
  "epistemic_status_legend": {
    "FACT_CLAIM": "I assert this as established in the field and expect it to survive checking",
    "BELIEF": "my working expectation, not verified here",
    "GUESS": "low-information hunch, stated so it can be scored against",
    "UNKNOWN": "I am declaring ignorance rather than interpolating"
  },
  "system_model_before_evidence": {
    "family_belief": {
      "status": "BELIEF",
      "text": "The pair are two paralogs of the eukaryotic Pol X (family X DNA polymerase) branch of the polymerase-beta-like nucleotidyltransferase superfamily: one a template-dependent gap-filling polymerase used in non-homologous end joining, the other a template-independent terminal transferase used to diversify antigen-receptor junctions."
    },
    "architecture_belief": {
      "status": "BELIEF",
      "text": "Both share the same domain layout N- to C-terminal: a BRCT module, a proline/serine-rich linker, a small 8-kDa-type domain with a 5'-phosphate binding pocket, then fingers-palm-thumb of the Pol-beta-like catalytic core, with a three-carboxylate two-metal-ion active site."
    },
    "sequence_identity_belief": {
      "status": "GUESS",
      "text": "Pairwise identity over the catalytic region is high for paralogs — my band is roughly 40-55 percent — which is why I expect the difference to localise to a small number of insertions rather than to a global fold change."
    }
  },
  "ranked_candidate_elements": [
    {
      "rank": 1,
      "element": "Loop1 — the lineage-specific insertion between the two strands of the beta-sheet preceding the catalytic palm, long and ordered in the template-independent paralog, shorter/more mobile in the template-dependent one",
      "claim": "In the template-independent paralog this loop folds back into the channel that an instructing strand would otherwise occupy, so the enzyme cannot accommodate a downstream duplex at the insertion site and selects nucleotides without instruction.",
      "confidence_band": "high (I would put 0.70-0.85 on this being the single largest contributor, and higher still on it being a contributor)",
      "status": "BELIEF",
      "transferability_prediction": "swapping this loop between the paralogs should transfer a substantial, measurable share of the phenotype in both directions"
    },
    {
      "rank": 2,
      "element": "8-kDa domain 5'-phosphate binding pocket plus the helix-hairpin-helix motifs that grip the downstream duplex backbone",
      "claim": "In-cis template use on a short gap requires anchoring the downstream 5'-phosphate; the template-dependent paralog has a functional pocket, and loss or degradation of this anchoring in the other paralog removes the geometric requirement to read the instructing base.",
      "confidence_band": "moderate (0.35-0.55 as an independent contributor, higher as a modifier of rank 1)",
      "status": "BELIEF"
    },
    {
      "rank": 3,
      "element": "side chains lining the templating-base pocket itself (the residues that would stack on and hydrogen-bond-position the instructing base opposite the incoming nucleotide)",
      "claim": "The template-independent paralog substitutes one or more of these for residues that occupy or collapse the pocket, so even a presented base is not productively positioned.",
      "confidence_band": "moderate-low (0.25-0.40)",
      "status": "BELIEF"
    },
    {
      "rank": 4,
      "element": "the second lineage-specific loop / thumb-subdomain insertions flanking Loop1",
      "claim": "These act epistatically with Loop1 — they set the loop's rigidity and register, so single-element swaps give partial rather than full conversion.",
      "confidence_band": "moderate-low (0.25-0.45 that swaps are visibly non-additive)",
      "status": "GUESS"
    },
    {
      "rank": 5,
      "element": "the conserved basic motif immediately preceding the catalytic aspartates, contacting the primer 3' terminus",
      "claim": "Contributes to holding the primer end in a template-free register in the terminal-transferase paralog.",
      "confidence_band": "low (0.10-0.25)",
      "status": "GUESS"
    }
  ],
  "prior_predictions_about_phenotype": [
    {
      "status": "BELIEF",
      "text": "The distinction is quantitative, not absolute: the template-independent paralog retains measurable template-directed fill-in on a short gapped substrate under permissive conditions, and the template-dependent one performs some untemplated addition on substrates lacking an instructing base."
    },
    {
      "status": "BELIEF",
      "text": "Substrate architecture modulates the phenotype more strongly than any single point substitution: gap length and presence of a downstream 5'-phosphate will shift template-directed fraction by more than most single mutants do."
    },
    {
      "status": "GUESS",
      "text": "Loop deletion in the template-independent paralog gains template-directed fill-in but does not reach the template-dependent paralog's level; full conversion needs loop replacement plus at least one additional element."
    }
  ],
  "numbering_uncertainty_declaration": {
    "policy": "Residue integers are optional in this artifact and I am deliberately keeping structural claims numbering-free so that they cannot be scored as correct-by-coincidence.",
    "if_numbers_are_needed_later": "Any integer I state downstream will be accompanied by species and accession. The accessions I would intend to anchor to are the human UniProt entries for the two Pol X paralogs; I am NOT asserting their identifiers from memory here, and I am NOT asserting any Loop1 residue range. Status: UNKNOWN until an accession is supplied.",
    "known_hazard": "Published loop boundaries for this family differ between papers by several residues and between species by more; an unanchored integer is uninterpretable."
  },
  "what_i_do_not_know": [
    "the actual magnitude of template-directed fraction for either paralog under any specified condition",
    "whether reported loop swaps converted the phenotype fully or partially",
    "whether the 8-kDa pocket is intact in the template-independent paralog",
    "any structure-derived distance or occupancy measurement"
  ]
}
```

`recognition_declaration.json`
```json
{
  "artifact": "recognition_declaration",
  "version": "1.0",
  "recognised": true,
  "recognition_point": {
    "sentence": "Section 2 of the brief, the sentence beginning 'two paralogous enzymes of one eukaryotic nucleotidyltransferase family differ in one property'; identification was complete by the end of the following clause 'the other adds residues largely without such instruction'.",
    "trigger_features": [
      "'eukaryotic nucleotidyltransferase family' plus 'paralogous' narrows to a small number of families",
      "the contrast template-dependent primer extension versus largely untemplated addition on the same fold is the textbook signature of the Pol X family",
      "'in cis' excludes RNA 3'-end-addition enzymes acting on separate substrates and points at gap filling versus terminal transfer on DNA"
    ]
  },
  "identification_claimed": {
    "family": "eukaryotic DNA polymerase family X (Pol beta-like nucleotidyltransferase superfamily)",
    "pair": "the NHEJ gap-filling template-dependent paralog and the terminal deoxynucleotidyl transferase paralog (in human nomenclature, DNA polymerase mu and TdT)",
    "confidence_band": "high on the family; high on the pair identity; the alternative I considered and down-weighted was polymerase lambda versus TdT, which I judge less likely because polymerase lambda is not usually described as the untemplated member and the brief's contrast is a one-property contrast"
  },
  "prior_knowledge_i_am_importing": [
    "general Pol X domain architecture",
    "the existence of a lineage-specific loop insertion discussed as a template-occlusion element",
    "the existence of published loop-swap chimera experiments between these paralogs, whose quantitative outcomes I cannot recall reliably"
  ],
  "provenance_note": "Recorded for net-of-recognition crediting. No claim of blindness is made and none should be inferred; everything above was available to me before any evidence release."
}
```

`hypotheses.json`
```json
{
  "artifact": "hypotheses",
  "version": "1.0",
  "immutability_note": "Statements and predictions below are frozen. Any change is published as hypotheses.json version 1.1+ with a changelog, never as an edit to this record.",
  "hypotheses": [
    {
      "id": "DX01-H1",
      "label": "steric occlusion by the lineage-specific loop",
      "statement_immutable": "The template-independent paralog loses in-cis template direction principally because its lineage-specific loop insertion physically occupies the channel that an annealed instructing strand must occupy downstream of the insertion site; the template-dependent paralog's shorter loop leaves that channel open.",
      "testable_prediction": "Replacing that loop in the template-independent scaffold with the template-dependent paralog's loop produces a catalytically active enzyme whose template-directed fraction on a short gapped substrate rises substantially toward the template-dependent paralog; the reciprocal swap lowers it.",
      "discriminating_intervention": "reciprocal loop-replacement chimeras, assayed on a matched pair of substrates that differ only in whether an instructing base is presented in cis",
      "validity_conditions": [
        "both chimeras must retain measurable nucleotidyl transfer on a template-free substrate (catalytic competence control)",
        "both chimeras must be folded and monodisperse by the same criterion applied to wild types",
        "the same nucleotide pool, metal, and substrate batch used across all constructs"
      ],
      "falsification_clause": {
        "construct_class": "reciprocal loop-replacement chimeras that remain catalytically active",
        "inverting_verdict": "If the loop-swapped template-independent scaffold retains the untemplated verdict (added residues remain predominantly non-concordant with the presented instructing base) while still adding residues, and the reciprocal chimera retains the template-directed verdict, then occlusion by this loop is not the principal determinant and H1 is falsified as the lead explanation."
      },
      "relation_to_others": "overlaps with H5 by construction; H1 claims this loop is sufficient on its own, H5 denies sufficiency"
    },
    {
      "id": "DX01-H2",
      "label": "downstream-duplex anchoring sets whether a template can be read in cis",
      "statement_immutable": "In-cis template direction depends on anchoring the downstream segment of the same molecule — the 5'-phosphate pocket of the small N-terminal domain together with the backbone-gripping helix-hairpin-helix contacts. Where that anchoring is absent or non-functional, the instructing base is never held in register, regardless of loop length.",
      "testable_prediction": "On the template-dependent paralog, removing the downstream 5'-phosphate, or lengthening the gap beyond what the anchor can span, collapses template-directed fraction toward the untemplated paralog's value; conversely the untemplated paralog shows no such dependence because it never used the anchor.",
      "discriminating_intervention": "substrate series varying gap length and 5'-phosphate presence, crossed with pocket-ablating substitutions in the anchoring domain",
      "validity_conditions": [
        "substrate series must be otherwise sequence-identical",
        "pocket-ablating constructs must retain template-directed synthesis on a non-gapped primer-template, proving the catalytic core is intact",
        "absence of effect in the untemplated paralog is only interpretable if the positive control (template-dependent paralog, same substrates) shows the predicted collapse"
      ],
      "falsification_clause": {
        "construct_class": "5'-phosphate-pocket-ablated template-dependent paralog, catalytically intact on primer-template",
        "inverting_verdict": "If that construct retains the template-directed verdict on a short gapped substrate at essentially the wild-type level, anchoring is not required for in-cis template reading and H2 is falsified as a determinant of the scored axis."
      },
      "relation_to_others": "can be jointly true with H1; distinguishable because H2 predicts a substrate-architecture dependence that H1 does not require"
    },
    {
      "id": "DX01-H3",
      "label": "templating-base pocket chemistry, not bulk occlusion",
      "statement_immutable": "The difference is encoded in a small set of side chains that stack on and position the instructing base opposite the incoming nucleotide; in the untemplated paralog these are substituted such that even a presented base is not productively positioned, independent of any loop insertion.",
      "testable_prediction": "A minimal point-substitution set converting those pocket positions in the untemplated scaffold — with the lineage-specific loop left entirely unchanged — raises template-directed fraction measurably.",
      "discriminating_intervention": "loop-invariant pocket point-substitution panel, compared head-to-head against the H1 loop swap on the same substrates",
      "validity_conditions": [
        "loop sequence and length verified unchanged in every pocket mutant",
        "each mutant retains untemplated addition activity",
        "the H1 loop-swap chimera is run in the same experiment as the comparator"
      ],
      "falsification_clause": {
        "construct_class": "loop-invariant pocket-converted mutants of the untemplated paralog that remain catalytically active",
        "inverting_verdict": "If the full pocket-conversion panel leaves the untemplated verdict intact while the loop swap alone inverts it, pocket chemistry is not an independent determinant and H3 is falsified."
      },
      "relation_to_others": "mutually informative with H1; both can contribute, but H3 asserts a loop-independent path that H1 does not"
    },
    {
      "id": "DX01-H4",
      "label": "kinetic competition rather than structural exclusion",
      "statement_immutable": "Both paralogs can in principle accommodate an instructing strand; the untemplated paralog differs because template-free extension at its primer terminus is fast relative to the annealing and registration of the downstream strand, so instruction is outrun rather than excluded.",
      "testable_prediction": "Presenting the instructing strand pre-registered and conformationally constrained — so that annealing and registration are no longer rate-contributing — substantially raises the untemplated paralog's template-directed fraction without any mutation at all.",
      "discriminating_intervention": "pre-annealed, constrained or covalently tethered downstream strand substrates, assayed on wild-type enzymes only",
      "validity_conditions": [
        "the constrained substrate must be shown to support normal template-directed synthesis by the template-dependent paralog",
        "constraint chemistry must not itself block the active site (tested by a catalytic-competence control)",
        "comparison made at matched enzyme occupancy, not matched total protein"
      ],
      "falsification_clause": {
        "construct_class": "wild-type untemplated paralog on a pre-registered constrained-template substrate",
        "inverting_verdict": "If that enzyme still returns the untemplated verdict on a substrate the other paralog copies faithfully, the difference is not kinetic competition and H4 is falsified; a structural-exclusion account (H1/H3) is favoured."
      },
      "relation_to_others": "the principal alternative to H1; H1 predicts no rescue from pre-registration, H4 predicts rescue"
    },
    {
      "id": "DX01-H5",
      "label": "distributed and epistatic determination",
      "statement_immutable": "No single element carries the phenotype; template-dependence emerges from the joint configuration of the lineage-specific loop, its flanking thumb insertions, and the anchoring domain, such that single-element transplants give only partial, non-additive conversion.",
      "testable_prediction": "A combinatorial transplant series shows that the measured conversion of the multi-element chimera exceeds the sum of the single-element conversions, with at least one single-element transplant giving near-zero effect alone but a large effect in combination.",
      "discriminating_intervention": "combinatorial chimera matrix (each element alone, in pairs, and all together) scored on one substrate class",
      "validity_conditions": [
        "all matrix members assayed in one batch on one substrate lot",
        "every member retains catalytic competence",
        "additivity assessed on a stated scale declared before the data are seen (log-odds of template-directed fraction)"
      ],
      "falsification_clause": {
        "construct_class": "the full combinatorial chimera matrix with all members catalytically active",
        "inverting_verdict": "If the all-element chimera's conversion is matched, within the matrix's own replicate spread, by the best single-element transplant — i.e. the verdict for the combination is no different from the verdict for one element alone — then determination is not distributed and H5 is falsified."
      },
      "relation_to_others": "competes with H1 and H3 on sufficiency; compatible with all of them on contribution"
    }
  ],
  "residual_hypothesis": {
    "id": "H0",
    "statement_immutable": "The true determinant of in-cis template-dependence in this paralog pair may lie wholly or partly outside DX01-H1 through DX01-H5 — for example in a structural element I have not named, in a property of the substrate-enzyme encounter I have not modelled, or in a framing of 'template-dependence' that the eventual measurement does not match.",
    "how_h0_is_credited": "H0 is favoured if every primary hypothesis meets its own inverting verdict, or if the released evidence identifies a determinant not nameable as a refinement of H1-H5.",
    "note": "H0 is not a hedge against being wrong on detail; it is a standing claim that the hypothesis set may be incomplete, and it is scored as such."
  },
  "general_interpretation_rules_committed_now": [
    "Absence of an effect falsifies nothing on its own; a falsification requires the named construct class to be catalytically competent and the matched positive control in the same experiment to show the expected verdict.",
    "Verdicts are categorical (template-directed versus untemplated, by the concordance readout declared in axis_declaration.json). No p-value is part of any falsification clause.",
    "Hypotheses may overlap; where two are jointly supported I will report both contributions rather than forcing an exclusive winner."
  ]
}
```

`prereg_commit.sha256`
```json
{
  "artifact": "prereg_commit",
  "version": "1.0",
  "digest_algorithm": "SHA-256",
  "digest_hex": null,
  "digest_status": "NOT_COMPUTED",
  "why_not_computed": "Tool use is blocked at the harness level for this task and I cannot execute SHA-256. Emitting a hex string I did not compute would be a fabricated commitment that is certain to mismatch at campaign close, which is worse than an explicit null.",
  "canonicalization_recipe_deterministic": {
    "step_1_inputs": [
      "axis_declaration.json",
      "sealed_prior.json",
      "recognition_declaration.json",
      "hypotheses.json"
    ],
    "step_2_order": "exactly the order listed in step_1_inputs (the order the brief lists them), not sorted by name or by hash",
    "step_3_bytes": "for each file, take the exact bytes of the fenced block body as emitted in this reply: everything after the newline following the opening fence line and before the newline preceding the closing fence line, UTF-8, LF line endings, no BOM, no trailing newline added or removed",
    "step_4_separator": "concatenate the four byte strings with a single LF (0x0A) between consecutive files; no separator before the first or after the last",
    "step_5_exclusion": "prereg_commit.sha256 is not an input to itself",
    "step_6": "SHA-256 over the concatenation; report lowercase hex"
  },
  "reference_implementation": "printf '%s\\n%s\\n%s\\n%s' \"$(cat axis_declaration.json)\" \"$(cat sealed_prior.json)\" \"$(cat recognition_declaration.json)\" \"$(cat hypotheses.json)\" | sha256sum   # note: use a byte-exact reader if any file lacks a trailing newline",
  "binding_statement": "The four files above as emitted in this transcript are the committed record. The recipe is deterministic, so any party with the transcript derives the same digest; verification at campaign close should recompute from the transcript bytes rather than from a self-reported hex value.",
  "repair_window_note": "Per brief section 4, a schema repair supplying the computed hex is permissible before evidence release and would be published as prereg_commit v1.1 with the file bytes unchanged."
}
```

Registered: one scored axis (in-cis template-directed fraction), six scoped-out axes, a ranked prior led by the lineage-specific loop, explicit recognition of the Pol X pair at the brief's first descriptive sentence, five primary hypotheses plus H0 — each with a construct class and an inverting verdict rather than a threshold. Residue integers are deliberately withheld pending an accession.

The one gap you should decide on: the digest is null because I cannot hash without tools. If that blocks the gate, re-run this task with tool use enabled, or compute it from the recipe and file it as v1.1 before evidence release.