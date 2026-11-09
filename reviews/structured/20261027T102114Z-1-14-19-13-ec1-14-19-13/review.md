# Review of acyl-CoA 15-desaturase

- Review: 20261027T102114Z-1-14-19-13-ec1-14-19-13
- Repository: CultureBotAI/proteintraitsmech
- Started UTC: 2026-10-27T09:41:56Z
- Finished UTC: 2026-10-27T10:21:14Z
- Reviewer: Codex (unknown)
- Completion: completed
- Verdict: needs_curation
- Scientific review: true

## Summary

The C16 terminal desaturation, official GO association and SbDES3 example are supported. Reconcile the upstream-shared 15Z product label with the terminal-alkene structure, repair the split CoA token, and correct automatic curator-signoff status.

## Scope And Provenance

Field-by-field scientific review of one complete ProteinTraitRecord.

Selection: Path-order position 6 in batch 165. Fresh main inventory has 429394 records. Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d; batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a; batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc; batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5; batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618; batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5; batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb; batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50; batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9; batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87; batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df; batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242; batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98) cover 266 record paths. Including validated unpublished local review commit(s) da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd; f67243be00c3d9c891c24c22a32c932ea7bee099; 55a71f32ee7c35ceb6449d1bd1d85954b9609d18; ac3fcf7c6a5710b240a7aa0db1d09bcb2f09529b; 00702985331951f0990ffdc7b352b5a1657160b7; b6ee361647a739487903ad0d184297a280189333; 94d787f848b7b9a1c123f7ae54f1cacedd7f55eb; c6dacdf0e1f79554d56ebfff47b08d3ef1f4c585; 2713fb4cb42716b649bb40a055bf29cf2138dca4; 756ecaf67cacd45cb5bf9d7b5666b4fbde632e96; 6a22474e153e8283e66d85844806dbc27784eebb; ee9a05771251fd84096ca40cfee30ea23e064f91; c589a5515b45e7337f41a032609859f3a20fb7f9; b87f4bd08683d7d13c943c409fd2fc191918135b; 43b6868b10bbbe28d4030e9eaf0a06a4400f47dd; 95ad98ca67c636454fb543a53f9157b574d64cb6; 538ccd21f618ad8ae64adfe2667af153feae8ff1; 08a4a1d5e2d7457ce4696303db2cb67cf3f5f752; 68138e97c6706d7c0fbb0ab30f58d5fd179b6661; 8f8d7bc536c122a1caa0f9fe02bd19aa3af2e79b; 896749322d48bf0a8efd3b822d34ff9f6ada7ffc; 2d4dd0983f0604f70a485c085e43942b24e520ac; 6f9ec803cc5193aa056ad3e7b42678d05a11e1ad; cad414749af988265991078a351e7bff329f012f; decc32c20475e07ec196d4fb3c930979344ca1f3; 00f14ceee7dff47cc5ebdea68fc434e6433bebba; 19ec1cc7e4b21f351a5cdc2b18611dd7361b088e; e12f670fd4896cdce45b65eab2547ef679ef1cf7; 2af17182bdaaee828e308b030b76a675442fba5c; 18d3c2d4119314ba267f54e08397c1c889f6407c; 028198be440bc2ac7e50245c4444c30425798739; 8130eea18e4e9234bccbc8af19d08f040a3645c8; 0089dcf1bc90bc2737892baa2670dbe64b214810; 91b6b1b722fd89902ef210ed30beda1c94a5bd5f; 99d0578fb48bc77c11102c40e2989aa30b2a0dac; 2ba88a35fdb646bbe295cdad6c62826e0a187f44; 2f4bacaeedd95045a5e15c309d43c033e408e325; ef616d50f93f5715042a1cd3562d34b2d7f9a127; f4cb59c32d03a12ea6736f618de5acf20a4439d6; ff23e5df0c3487e32ffb957c67675c67c16b41c2; 75ad3a291726b092c359f97917a71cfe8e2e6af8; 02b349a5fd82cfb33d9194b5cc7a40ff50f366fd; cfb19dc9d57ec551c66101215d03f6e1d43d0eff; c3d9c57c6538a844da118acc99853d274d0a4806; 8abfd5711bfe4893ca2a72758d6ed38497200e1b; 8dd1ec15880ec4357357dac79943ea67382c19bd; 612a48f9fee6d2a47670d8a9dcba8ba7a4a3ef17; 9b575fbbb6874c6a70f7461b3fce32d06141cf7a; c022030b5e1a201b57819eb42bb559638014fe9e; b1d3cd26d82f923901ad03edbd671c0756d0ecbd; c95fe22c3576a31202663b274ea8ab708796f5b3; 83b626799fbe7a712b670a6cde18587c03c9b642; 67c32e6581cd85d000e501335ed1cea86edb64fd; 544e1d260461741d6e33957881d9397ee07b4159; fbc8060b3f156689ff1c9187c0a4f8fb58f02b54; 162ff91cc410b6d11c2a228a74fa1763d24eec61; f52add53b1d8cc6ce345f604c076223b6534aba3; 751989196f24b1f2a0c1fb0701d8a0812072232f; 5f2e76e40a672c9cff0869bd1603d3696314e210; c2806d7e525fa0f7eb1c525da8c0a811f2a84f4d; 64b8692fe04e57d6de5e8f64d89d69fcf88f5cd6; 156c17ab70a878767ae231ed5f823055993c5a39; eec5f399f735fb4e6cfe372a210a6091b8af2509; 916ca112e82b09cf0741f3bedace363e4c164cdf; 1094e78cebf5eb94d5757d7a36ebdf535cb11704; 403388fd601f7e516781e19472be7d418ef9c678; 83cbeeb06066f2ae99b9e6239078863103e97e85; 4274276609c085aa059b09669b018cb10b7113da; feaa20463c425a3fcdcc782599f5ff3133a19067; fcee8eb7470aeb0738fb65262f7c7bd82cf9a34e; 577ae0e39e5bde0e4da363cf41f9f39a37afb356; 850a910aabc759168f0e749d313e4c21fb2387ec; 3e66545b045adc938bf9b0b1471532cc0ae266c4; 817d5e6fe5d4ca5a9c4cd88ee035c6a3b5de5436; 39e70039bc443da8955862c4a845defe88c5c385; e3e294c90026f72ef87acb583aef9b435dc08d8f; 853e2ca43ae9dc1812a20a68ccecfda15061109d; f99a413f3ac540b5526af7d65c0fea82bb11c881; d03ea4ee80be28aa2fb34602f730170c9541a666; 2618b15c61d1e4061f3674a249db897d257b5a9e; 00a57e8acb204780df68a3d9d8429cbd43086c16; ef0d145e14270698802dd649a9c346bab53ed2ca; aadecba057531eff15d0117aa957d71b6efbdcc7; c2283b6ba39c7f66e7eede2a166c94c4692a3ff9; 2a98cb4271fbe15a6280c3039e86243248b7076f; aade04271813734e76a5f381c5e6aa11c48c4586; 33622742735c62c57d5a2356634b6fc922db6f6f; e9e6f0d1043c65d8302c284f41fda4a27fb7b873; 955219ebb51f49d6efeeaff398883ed6c96834a2; 81a8175da6a3f1e6fb5f4b4935657190723f9aa0; 272c2a8bd759243561d08a515732c631c8a91540; bef507f5b340a81db4212994a8b0b91f37d806d3; 0eb23e8c8f3888995462c1f1b97cbd44694a823a; 42e54e3e2797a3a7b51417dbcebb0b9c4a7b0cf6; 4848fbf8933e623045babe4baed8e4e7c54f6230; 43eb98cf14f2542c7e7f602651ccf204a54da0f6; c6737819b8f5bd1a06ddd6853432cdee1bd1bfe0; 354bfc21667fb534f5eef295984647af689f6447; c38451d06601b7a1197e7a6962fe21ebf96e0fef; aa7698d0ed63abad4280ed1bd0cdcabe114ed3c2; 83fa541c35bbc36c57ba253240b01ff6b5feade1; 036c6b1118d17a5cc3515176f914ef6bb0ec14d7; 40d259197445aa2f47c10bf4058835e362528019; 332dc98b4b9fdbedec00b1c809f18f03a630945c; 3f3d5320fdb0f5dbd33ea70f3d7a164eff403575; 71b0d4586ae89d103ce97b8e4289f07cb66dc249; 40156bc2beacbb7d4f4a88eea25bb8e63fce6fad; f7235e5f4b93a3ef0a4d541180c1f7ef8fea00a3; 20085d9e39447af672fef4875299f6b8a921e34a; e57f7a6fcdc244ee2c841c7bea6816fc21debd01; 2d3659a9e0f4b900b54ed58d6864f4c8c2685a73; 17fab5aa093f688b7742ad179f9c7ff49bbcf01e; 03fe3b878d21da8cf4309a6acfc1c04269daa216; 50e8fbee6f1ac7b66da1f68998cd0edbbed8b876; bdab443a280b4395e8ba21cef021465ae13475cc; f6a810c1fb200ac9437dd7d4384ee11a65b8da34; ce1b420fc27a19254091e1be9e09b0113daa4ee5; b553b959240a1f20c73054385ed1c5c034604b29; d17da9f5c93efb7ed50684364197776fcae59560; 51f60c7644920159d535217eeee96381a648646a; 3ca593a22c594f6071bb4e47ac3e99c98942bd64; b2b89b7d3e2a195949c1dacb6ac82b9b0082f424; f83270ba96807bf8c58e206407a6b460a97f469a; 954dcd112c976a5ae0cc551e121f2f38cc57e469; c11015c15fefb635760fab2097c5eb94fecd4a73; 0d273e27cb68c70fcac80432fb25bcb436e6474e; b22e81db4c56b009c01e69fc35aac44fe8bcb810; 21a97e06f9e3d1642378903bbb0f46eeeea6cbe6; 8a7064ff6bae6e80524b23b2226166c1468b3215; efb75211d4fe2244704e320456e1df86ee7b6ccc; 36c078b072e242d60b41b7745ea853f2ceb91978; 21cda0d469da7ea3344e2cff639769d3666bd720; 0b51d7ca3b8efacd55d046462e8724758561e762; 19944f198684bd9a58538009588bfbdc8984ec9d; 985c86c62e2f6efc63016a0199a9e70dd944e9ff; f54bcd34f1d157dd2c670b2886de595577078992; 0ed5bdc586987619444370d7c764c83b5797f2e0; 6dab4d17475702064cc410ed6371922af04ccc30, the union covers 1656 record paths, leaving 427738 before this batch. 165 inventories were combined. Unpublished local coverage is explicitly not published or merged main coverage. Snapshot-row context paths are excluded.
Coverage: full; 1 reviewed / 1 in the declared population.
Source: working_tree at Git base c4147394c698324ae537c0c63c2c9f6647c4f4fc.
Working-tree hashes do not imply those bytes were committed.

| Target | Path / selector | Kind | Label |
| --- | --- | --- | --- |
| EC:1.14.19.13 | data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml | generated | acyl-CoA 15-desaturase |

## Validation

| Check | Status | Required | Targets | Result |
| --- | --- | --- | --- | --- |
| Closed schema | passed | True | EC:1.14.19.13 | Single target validated in closed mode. |
| Closed schema and applicable source semantics | passed | True | EC:1.14.19.13 | One shared invocation scanned all ten listed batch targets; target SHA256 matches before and after execution. Source-specific checks apply where implemented; this gate does not establish scientific class semantics or independently qualify every legacy protein example. |
| Causal graph integrity | passed | True | EC:1.14.19.13 | Structural causal-graph integrity was checked on the exact target; deterministic checks do not independently verify the scientific claims. |
| Curation history validity | passed | True | EC:1.14.19.13 | Full curation-history gate; this review adds no history event. |
| Source reference inspection | passed | True | EC:1.14.19.13 | Current native inputs and successful source tuples were hash-checked. All current captured inputs and complete selected Rhea closures were independently checked. Local references were read at the explicit defining-field scope. |

## Scientific And Domain Assessments

### Source identity and protein-trait scope

identity: supported. Targets: EC:1.14.19.13.

The EC class, FUNCTION/class placement, C16 diene-to-terminal-triene transformation, Q594P3 example and official GO association are supported. The terminal product name requires a bounded nomenclature reconciliation: ChEBI identifies a terminal C15=C16 bond and omits 15Z in its preferred name, while several upstream descriptions retain it.

### Defining representation and axis/category

representation: supported. Targets: EC:1.14.19.13.

The molecular-function, protein-example and chemical-participant types are appropriate. Rhea 37599 uses charged acyl-CoA species and generic redox donor AH2/A. The terminal stereodescriptor issue concerns labels rather than a different chemical identifier, substrate chain length or reaction direction.

### Trait hierarchy and source relationships

consistency: concern. Targets: EC:1.14.19.13.

The target faithfully inherits 15Z from ENZYME/IUBMB and the UniProt/Rhea reaction label, so this is not an extraction-only defect. ChEBI 85914 has a terminal alkene structure and a preferred name without 15Z. The same three prose fields also contain a line-wrap split before CoA. These concerns are distinct from the valid class and mapping association.

### Maintained trait emitter

ownership: supported. Targets: EC:1.14.19.13.

The EC importer, general/mechanistic definition writers and graph builder are the durable routes. Current captured hashes match the actual owner scopes read for this review. Bounded ignored-inclusive discovery supports ownership attribution without reconstructing every historical invocation.

### Source grounding and trait associations

grounding: supported. Targets: EC:1.14.19.13.

Q594P3 has direct current catalytic evidence from PMID 17178719, whose yeast-expression abstract supports the C16:2-to-C16:3 terminal 15–16 transformation. PMID 15361534 is separately retained as transcript/pathway context. The indexed catalytic abstract alone does not establish the physiological acyl-carrier form as free acid, CoA or another lipid-bound intermediate.

### Causal mechanism evidence

graph: concern. Targets: EC:1.14.19.13.

All eight edges correspond to current sources. Rhea 37599 balances formally at C37H60N7O19P3RS and charge −4 on each side. The product ChEBI identity and direction are positive, but its unqualified 15Z label needs reconciliation against the terminal structure. Generic AH2/A does not name a physiological electron donor.

### Class-level evidence and scientific scope

evidence: supported. Targets: EC:1.14.19.13.

Current ENZYME, IUBMB, both complete GO responses, UniProt and the indexed catalytic paper support the class association. ChEBI preferred naming and structure establish the terminal-alkene naming tension. Separate transcript evidence is explicitly context-only, and the unacquired OLS Rhea crossreference is not used to infer a mapping defect.

### Protein trait class completeness

completeness: concern. Targets: EC:1.14.19.13.

The record has its mapped reaction, a positive GO association and a directly supported example. Required content work is limited to terminal-product nomenclature and the split CoA token, alongside status provenance. No unsupported physiological carrier assignment is added.

### Source attribution and release provenance

provenance: concern. Targets: EC:1.14.19.13.

The target retains an LLM-assisted graph-generation event and automatic SEEDED-to-REVIEWED transition. Current owner/schema reading distinguishes this enrichment from documented curator sign-off. Raw successful source tuples retain their original HTTP instants, normalized to UTC Z only in review evidence. This review does not confer human sign-off.

## Findings

### F1: Graph generation does not establish curator sign-off

major / open / confirmed; issue key: ec-1-14-19-13-automatic-reviewed-promotion.

The current target records a July 30 LLM-assisted graph-generation event that promoted SEEDED to REVIEWED. The maintained graph builder implements that automatic transition, whereas REVIEWED denotes curator sign-off on label, definition and parents. The observed route does not establish that sign-off. This is not a global claim that no human has ever reviewed the record.

### F2: Repair the split CoA product token

minor / open / confirmed; issue key: ec-1-14-19-13-split-coa-token.

The definition, mechanistic definition and graph description spell the product with a line-wrap join as hexadecatrienoyl- CoA, separating a chemical token.

### F3: Reconcile the terminal-double-bond stereodescriptor

minor / open / confirmed; issue key: ec-1-14-19-13-terminal-product-nomenclature.

The C16 product has a terminal C15=C16 double bond, for which an E/Z designation is not applicable. ChEBI 85914 preferred naming omits 15Z and its structure begins with a terminal alkene, while the target and several current upstream reaction descriptions retain 15Z. The primary indexed study supports the same terminal 15–16 reaction. This is an upstream nomenclature tension, not evidence of a different transformation.

## Recommended Actions And Acceptance Checks

### A1

Remove automatic curator-signoff promotion from the maintained graph-writing route and reconcile this target status/history through its owners. Preserve the actual graph-generation event and positive source support; record REVIEWED only when the defined curator sign-off is documented.

- Graph generation alone no longer assigns curator-signoff status.
- The target status and history truthfully distinguish source enrichment from curator review.
- Supported chemistry and protein associations remain intact.

### A2

Repair the maintained EC line-wrap joins and regenerate or reconcile all three affected prose fields while preserving source attribution and chemical identity.

- All three fields use an intact acyl-CoA token.
- Coefficients and reaction direction remain unchanged.

### A3

Use a chemically valid terminal-product name in curated prose and graph labels, preserving 9Z and 12Z, the ChEBI identifier, chain length and reaction direction. Keep any verbatim upstream 15Z wording clearly attributed and record the unresolved source nomenclature discrepancy.

- Curated terminal-product labels do not assign E/Z at C15=C16.
- Source quotations remain faithful and explicitly attributed.
- The supported EC, GO, Rhea and protein associations are preserved.

## Category Boundaries


## Evidence

| Evidence | Reference / locator | Support | Observation |
| --- | --- | --- | --- |
| target | data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml; Entire target YAML. | supports | The complete current target records identity, definitions, all exemplars and graph content, status and history. |
| seeder | scripts/seed_ec.py; EC parsing, record creation and example construction. | supports | The EC importer supplies nomenclature and legacy ENZYME DR-associated examples. |
| general-writer | scripts/enrich_ec_general_defs.py; Classification lookup and GENERAL definition construction. | supports | The maintained definition writer derives hierarchy prose. |
| mechanistic-writer | scripts/enrich_mechanistic_defs.py; EC equation parsing and MECHANISTIC definition construction. | supports | The maintained definition writer derives catalytic-equation prose. |
| writer | scripts/build_ec_causal_graphs.py; Graph construction, existing-graph skip, status promotion and history append. | supports | The graph builder writes source-linked edges, an introduction, history and automatic SEEDED-to-REVIEWED promotion. |
| record-io | scripts/record_io.py; Lines 420–490 merge policy entry and 725–799 complete write_validated_record/write_record. | supports | The shared writer separates reseeding merge policy from in-place replacement and offers atomic strict validation. |
| rhea-writer | scripts/build_rhea_causal_graphs.py; Participant and reactive-part construction, lines 157–300. | supports | The reaction graph route constructs generic participants and reactive-part nodes; current iron-ion reactive parts are evaluated against their actual chemistry. |
| schema | src/proteintraitsmech/schema/proteintraitsmech.yaml; Mapping status 1482–1495; CanonicalExample 1648–1715; MappingStatusEnum, ExampleSourceEnum and GroundingQualification 3473–3529; complete CausalNodeTypeEnum 3586–3627. | supports | The schema defines REVIEWED as curator sign-off and distinguishes class activities, proteins, chemical species and residues. |
| review-contract | docs/record-review-profile.md; Complete record-review profile. | supports | The profile separates source evidence, review outcomes and human sign-off. |
| checklist | .claude/skills/curate-yaml-record/references/review-checklist.md; Complete review checklist. | supports | The checklist provides identity, ownership, evidence and completeness review criteria. |
| ancestor-1 | data/traits/function/enzymatic_activity/ec/1-14-19-ec1-14-19--.yaml; Complete ancestor records, including defining fields, hierarchy, mappings, examples and graphs; examples and graphs used only as ancestor context. | supports | The selected ancestor defining fields supply hierarchy and class context. Its examples and graphs were read only as ancestor context, not treated as target evidence. |
| ancestor-2 | data/traits/function/enzymatic_activity/ec/1-14-ec1-14----.yaml; Complete ancestor records, including defining fields, hierarchy, mappings, examples and graphs; examples and graphs used only as ancestor context. | supports | The selected ancestor defining fields supply hierarchy and class context. Its examples and graphs were read only as ancestor context, not treated as target evidence. |
| ancestor-3 | data/traits/function/enzymatic_activity/ec/1-ec1------.yaml; Complete ancestor records, including defining fields, hierarchy, mappings, examples and graphs; examples and graphs used only as ancestor context. | supports | The selected ancestor defining fields supply hierarchy and class context. Its examples and graphs were read only as ancestor context, not treated as target evidence. |
| context-1 | data/traits/function/molecular_function/go/acyl-coa-15-desaturase-activity-go0102988.yaml; Identifier, label, definition/source, axis/category/kind/status, definitions, synonyms, parents and mappings; neighboring examples and graphs excluded. | supports | The local GO or Rhea defining fields provide a comparison of names, reaction scope and mappings. |
| context-2 | data/traits/function/enzymatic_activity/rhea/9z-12z-hexadecadienoyl-coa-ah2-o2-9z-12z-15z-hexadecatrienoyl-coa-a-2--rhea37599.yaml; Identifier, label, definition/source, axis/category/kind/status, definitions, synonyms, parents and mappings; neighboring examples and graphs excluded. | supports | The local GO or Rhea defining fields provide a comparison of names, reaction scope and mappings. |
| enzyme | https://ftp.expasy.org/databases/enzyme/enzyme.dat; Complete EC 1.14.19.13 stanza. | supports | The complete ENZYME entry gives the acyl-CoA 15-desaturase reaction with a C16 diene substrate, a product labelled 9Z,12Z,15Z, generic AH2/A and water. Its comments describe sorghum root hairs, a terminal double bond and cis wording at carbon 15; Q594P3 is the listed protein association. |
| classification | https://ftp.expasy.org/databases/enzyme/enzclass.txt; Exact EC 1, 1.14 and selected donor-subclass classification lines, including the parent entry when applicable. | supports | The exact EC 1, 1.14 and 1.14.19 classification lines place these activities among oxidoreductases acting on paired donors, with donor oxidation reducing molecular oxygen to two molecules of water. |
| rhea2ec | https://ftp.expasy.org/databases/rhea/tsv/rhea2ec.tsv; All exact rows for EC 1.14.19.13. | supports | The selected mapping rows assign Rhea 37599 to this EC class. |
| ec2go | https://current.geneontology.org/ontology/external2go/ec2go; Exact EC 1.14.19.13 lookup. | supports | The exact mapping row associates GO:0102988 with this EC class. |
| rhea-rdf | https://ftp.expasy.org/databases/rhea/rdf/rhea.rdf.gz; Complete closures for Rhea 37599, including all directions, sides, compounds and participants. | supports | The complete selected recursive RDF supplies directions, participants, coefficients, formulas, charges, citations and reaction hierarchy. |
| iubmb | https://iubmb.qmul.ac.uk/enzyme/EC1/14/19/13.html; Complete normalized EC 1.14.19.13 HTML text and bibliography, excluding script/style. | supports | The complete IUBMB entry gives the C16 acyl-CoA equation using a 15Z product label and describes insertion of a terminal double bond with cis wording at carbon 15. It supplies the sorghum desaturase study as the focal reference. |
| go-quickgo | https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0102988; Complete delivered GO:0102988 JSON. | supports | The complete QuickGO term GO:0102988 assigns acyl-CoA 15-desaturase activity and gives a C16 diene-to-triene equation with generic reduced and oxidized electron acceptors, oxygen and water. Its product is written as 9,12,15-cis-hexadecatrienoyl-CoA, retaining upstream terminal 15-cis wording. |
| go-ols | https://www.ebi.ac.uk/ols4/api/ontologies/go/terms?obo_id=GO:0102988; Complete delivered GO:0102988 term JSON and relation scopes. | supports | The complete OLS term preserves the focal GO/EC identity and reaction text, including the product wording 9,12,15-cis-hexadecatrienoyl-CoA. It also lists Rhea 46232 as a crossreference; that separate reaction closure is outside the acquired scope. |
| enzyme-policy | https://ftp.expasy.org/databases/enzyme/enzuser.txt; Complete user manual. | supports | The ENZYME manual distinguishes names, catalytic information and DR crossreferences. |
| rhea-release | https://ftp.expasy.org/databases/rhea/rhea-release.properties; Complete two-line properties file. | supports | The delivered properties file records Rhea release number 142 and release date 2026-09-02. |
| rhea-license | https://ftp.expasy.org/databases/rhea/LICENSE.txt; Complete delivered license. | supports | The delivered license states CC BY 4.0. |
| skos-policy | https://www.w3.org/TR/skos-reference/; Complete Section 10 Mapping Properties. | supports | SKOS Section 10 distinguishes closeMatch and narrowMatch relations. |
| predicate-RO_0002233 | https://www.ebi.ac.uk/ols4/api/ontologies/ro/properties?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002233; Complete delivered property JSON. | supports | The delivered property response defines has input. |
| predicate-RO_0002234 | https://www.ebi.ac.uk/ols4/api/ontologies/ro/properties?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002234; Complete delivered property JSON. | supports | The delivered property response defines has output. |
| predicate-RO_0002327 | https://www.ebi.ac.uk/ols4/api/ontologies/ro/properties?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002327; Complete delivered property JSON. | supports | The delivered property response defines enables. |
| predicate-BFO_0000050 | https://www.ebi.ac.uk/ols4/api/ontologies/ro/properties?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_0000050; Complete delivered property JSON. | supports | The delivered property response defines part of. |
| chemical-85914 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/85914/; Identity, definition, all names, chemical_data, default_structure and secondary IDs; unrelated ontology/roles lists excluded. | supports | The selected ChEBI identity, names, formula, charge and structure establish the actual chemical identity; metal-ion and protein-host typing are assessed separately. |
| chemical-76552 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/76552/; Identity, definition, all names, chemical_data, default_structure and secondary IDs; unrelated ontology/roles lists excluded. | supports | The selected ChEBI identity, names, formula, charge and structure establish the actual chemical identity; metal-ion and protein-host typing are assessed separately. |
| chemical-13193 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/13193/; Identity, definition, all names, chemical_data, default_structure and secondary IDs; unrelated ontology/roles lists excluded. | supports | The selected ChEBI identity, names, formula, charge and structure establish the actual chemical identity; metal-ion and protein-host typing are assessed separately. |
| chemical-17499 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/17499/; Identity, definition, all names, chemical_data, default_structure and secondary IDs; unrelated ontology/roles lists excluded. | supports | The selected ChEBI identity, names, formula, charge and structure establish the actual chemical identity; metal-ion and protein-host typing are assessed separately. |
| chemical-15377 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/15377/; Identity, definition, all names, chemical_data, default_structure and secondary IDs; unrelated ontology/roles lists excluded. | supports | The selected ChEBI identity, names, formula, charge and structure establish the actual chemical identity; metal-ion and protein-host typing are assessed separately. |
| chemical-15379 | https://www.ebi.ac.uk/chebi/backend/api/public/compound/15379/; Identity, definition, all names, chemical_data, default_structure and secondary IDs; unrelated ontology/roles lists excluded. | supports | The selected ChEBI identity, names, formula, charge and structure establish the actual chemical identity; metal-ion and protein-host typing are assessed separately. |
| protein-Q594P3 | https://rest.uniprot.org/uniprotkb/Q594P3.json; Q594P3: identity/audit/organism/names/genes/existence/length; complete FUNCTION, CATALYTIC ACTIVITY, COFACTOR, CAUTION, SIMILARITY, SUBUNIT and BIOPHYSICOCHEMICAL PROPERTIES comments; material family crossreferences. Complete matching citation IDs, titles, DOIs, publication metadata and referencePositions for sources tagged in selected comments. Complete reference array including authors, referencePositions and reference comments additionally read for this accession. Other comments, GO/other crossreferences, sequence residues/features and API extras excluded. | supports | Current reviewed UniProt identifies sorghum SbDES3 and assigns the focal catalytic activity with ECO:0000269 from PMID 17178719. FUNCTION describes terminal C16 desaturation and additional linoleate-to-alpha-linolenate activity, while retaining the transcript/root-hair reference PMID 15361534. The catalytic annotation uses the upstream 15Z product label; its evidence tier does not resolve that nomenclature tension. |
| primary-17178719 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:17178719%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Complete delivered indexed bibliography, abstract or explicit null, correction list and separately read pubTypeList; no full article. | supports | The indexed primary research abstract reports that sorghum SbDES2 converts 16:1 delta9 to 16:2 delta9,12 and SbDES3 converts that diene to 16:3 delta9,12,15 in heterologous yeast. The SbDES3 reaction creates a terminal carbon 15–carbon 16 double bond. The abstract also reports root-hair expression; it does not directly establish a physiological CoA versus other acyl-carrier substrate step. |
| primary-15361534 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:15361534%20AND%20SRC:MED&amp;format=json&amp;resultType=core; Complete delivered indexed bibliography, abstract, pubTypeList and correction list; no full article. | context_only | The indexed research abstract reports root-hair-enriched sorghum transcripts and cloning of SOR1. Similarity to desaturases and expression patterns suggest a role in sorgoleone biosynthesis; this abstract supplies transcript/pathway context rather than a direct focal SbDES3 catalytic assay. |
| provenance-search | /private/tmp/ptm-record-reviews-20261021/batch-165/independent-provenance-search-evidence.json; Position 6: exact commands, times and complete stdout/stderr. | context_only | Both recorded searches returned no matches within the stated ignored-inclusive owner/history scope. This does not establish global absence of human review. |
| validation-1 | just validate data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml; Executed 2026-10-27T09:42:34Z through 2026-10-27T09:42:35Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      1<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv |
| validation-2 | just validate-all data/traits/function/enzymatic_activity/ec/1-14-18-ec1-14-18--.yaml data/traits/function/enzymatic_activity/ec/1-14-19-1-ec1-14-19-1.yaml data/traits/function/enzymatic_activity/ec/1-14-19-10-ec1-14-19-10.yaml data/traits/function/enzymatic_activity/ec/1-14-19-11-ec1-14-19-11.yaml data/traits/function/enzymatic_activity/ec/1-14-19-12-ec1-14-19-12.yaml data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml data/traits/function/enzymatic_activity/ec/1-14-19-14-ec1-14-19-14.yaml data/traits/function/enzymatic_activity/ec/1-14-19-15-ec1-14-19-15.yaml data/traits/function/enzymatic_activity/ec/1-14-19-16-ec1-14-19-16.yaml data/traits/function/enzymatic_activity/ec/1-14-19-17-ec1-14-19-17.yaml; Executed 2026-10-27T09:42:27Z through 2026-10-27T09:43:31Z; exit 0 | supports | === validate-strict summary ===<br>  files scanned:      10<br>  files with ERROR:   0<br>  total ERROR rows:   0<br>  TSV:                reports/instance_validation_failures.tsv<br>files scanned: 10<br>registry proteins: 13208<br>source evidence objects: 22314<br>qualified record bindings: 22314<br>UniProt membership objects: 431<br>hierarchy records: 0<br>semantic findings: 0<br>TSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv |
| validation-3 | just audit-graphs data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml; Executed 2026-10-27T09:42:35Z through 2026-10-27T09:42:35Z; exit 0 | supports | causal-graph audit: 1 records, 1 graphs, 9 nodes, 8 edges &#124; grounded nodes 9/9, snippet-cited edges 8/8 &#124; 0 errors, 0 warnings |
| validation-4 | just validate-history; Executed 2026-10-27T09:43:31Z through 2026-10-27T09:43:33Z; exit 0 | supports | No issues found |

## Limits And Additional Notes

- The 15Z wording is shared upstream; the review does not attribute it solely to local extraction or reject the reaction identity.
- The primary indexed abstract supports terminal C16 desaturation but does not settle the physiological CoA versus other acyl-carrier step.
- The OLS Rhea 46232 crossreference was read as metadata; its reaction closure was not acquired or compared.
- Rhea uses symbolic R in generic AH2/A formulas whereas ChEBI uses A; these formal placeholder conventions are retained without assigning a specific donor.
- Literature reading covers complete delivered indexed bibliography, abstracts, publication types and correction lists. No full original article, supplementary figure, sequence-residue inspection or undeclared API field is claimed.
- No trait edit, human sign-off or publication is performed.

## Complete Structured Record

The sibling review.yaml is authoritative.

```yaml
schema_version: 1.0.0
review_id: 20261027T102114Z-1-14-19-13-ec1-14-19-13
kind: record
repository: CultureBotAI/proteintraitsmech
title: Review of acyl-CoA 15-desaturase
started_at: '2026-10-27T09:41:56Z'
finished_at: '2026-10-27T10:21:14Z'
reviewer:
  identity: Codex
  kind: agent
  independence: unknown
  independence_basis: Unchanged target bytes assessed against inspected primary sources
    and repository rules, with independent source-acquisition and scope checks. Prior
    authorship independence is not established; this is not human sign-off.
skill: .claude/skills/review-yaml-record/SKILL.md
completion: completed
verdict: needs_curation
scientific_review: true
summary: The C16 terminal desaturation, official GO association and SbDES3 example
  are supported. Reconcile the upstream-shared 15Z product label with the terminal-alkene
  structure, repair the split CoA token, and correct automatic curator-signoff status.
source:
  git_revision: c4147394c698324ae537c0c63c2c9f6647c4f4fc
  state: working_tree
  inputs:
  - path: .claude/skills/curate-yaml-record/SKILL.md
    sha256: f28b4fb7ad5b2891ba8569b2f923559e99cec7b18dd42557b6b0e4becb8f4762
    role: context
  - path: .claude/skills/curate-yaml-record/references/review-checklist.md
    sha256: 59f39fad3e6447e7be30da72667befd3d2e383b68bea5f497952f2ab080da90d
    role: context
  - path: .claude/skills/review-yaml-record/SKILL.md
    sha256: ac1094d8aef512845dbe56ee041e62e62aeeed32326578ff3f7dd8455495f303
    role: context
  - path: CLAUDE.md
    sha256: 0fe3358571b7e3fc0016a94bd514719202ddfb6b8ea020df4431348ed518bc42
    role: context
  - path: LICENSE
    sha256: d920683ada4ab4646467cbe49944e08172d8f10c92ce3e631d6f3460b4b40a52
    role: context
  - path: LICENSE-DATA
    sha256: 9e5f1b3c610b9c2da5c313bf81d577a7d1acec686bdb0384edefa6df0f90cd94
    role: context
  - path: conf/record_review.yaml
    sha256: d3fd2e272546bf2505ded4ef86f7340753c4e422c691bd69f8e79f577b2c5f59
    role: context
  - path: data/grounding/README.md
    sha256: 83155f235a0cefa98dfaf88ea888f4d65a1ba056587f9869b4fbbd92df1a91c3
    role: context
  - path: data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml
    sha256: 3e9ddd70a9981591e07e3598571dc79c89e7bc07176eba298638c0ba71e90151
    role: target
  - path: data/traits/function/enzymatic_activity/ec/1-14-19-ec1-14-19--.yaml
    sha256: 91b7864a16b00e95945ba96928ef4853428330e44f0c284f0f436af0adca95af
    role: context
  - path: data/traits/function/enzymatic_activity/ec/1-14-ec1-14----.yaml
    sha256: e48a177015965d9d40ebfb80643e1d914cf2a6362d3d47b94b6f301096158165
    role: context
  - path: data/traits/function/enzymatic_activity/ec/1-ec1------.yaml
    sha256: f61053223eeff4b7f57499893ab0f080ddfe2b3b145b52d47b58cfcaee9267b4
    role: context
  - path: data/traits/function/enzymatic_activity/rhea/9z-12z-hexadecadienoyl-coa-ah2-o2-9z-12z-15z-hexadecatrienoyl-coa-a-2--rhea37599.yaml
    sha256: fb67db21fd5336242163fcf67cdc32be26986d1aeeab3c8feebcc5af021d00be
    role: context
  - path: data/traits/function/molecular_function/go/acyl-coa-15-desaturase-activity-go0102988.yaml
    sha256: f0220191f32e2aa562432507be21f116fc50cc1578159dfde2ba2ee3200ed8e6
    role: context
  - path: docs/fetch-migration.md
    sha256: 11718531ccc1346002cfafbe62e8cfdc3859271ded178c34a17e26dabc70b55c
    role: context
  - path: docs/record-review-profile.md
    sha256: 06cec6693ded193231a378bba04e7c1ad3e295f88903ee8b7c30b3238daab9df
    role: context
  - path: docs/record-reviews.md
    sha256: 452a19ab688276747b7c4308523a14d4d99c1c39ef6909ae8a90b85b7a9b3e9b
    role: context
  - path: download.yaml
    sha256: 63a62092f919dc534d7b5d9087ada35dea39ed88579f3fd281f8f0ffe6ef4417
    role: context
  - path: history/README.md
    sha256: db3db1da49f08244c863689856f31bc764aadb6e629b25aff45b3b4598dbef2c
    role: context
  - path: justfile
    sha256: 090b16ab565dbc137f589ab913e57efac5cb37bb7511547391267ba6ea96dd5b
    role: context
  - path: research/uniprot-organism-protein-grounding-plan.md
    sha256: 99f0eded9310561155198b863c6c9ea05aeb145b1d4f76109df000646d2b1a7f
    role: context
  - path: schema/record_review.yaml
    sha256: 229baf9b69118a1fe318e4c31085c0820e4e3d1365e7b04d6ace451b7c35f9bb
    role: context
  - path: scripts/build_docs_index.py
    sha256: 6d1f4b70648cddb3147fe22233c1111e51ac514552444f193c4f2f03dfa6c1ea
    role: context
  - path: scripts/build_ec_causal_graphs.py
    sha256: d5fdfc7fab74cc3b50b3707669bddd6e58b58299a0178528c6748c6f05f37a2d
    role: context
  - path: scripts/build_rhea_causal_graphs.py
    sha256: ac1785a1d65e4f747f3e0f6661a2c97cea8df20aefdbab9bbe12c7e236ded5f8
    role: context
  - path: scripts/deflib.py
    sha256: 5dbb70e6812fef6a19b77b044235cfe31c88369078e2399efa32cfec0aafd929
    role: context
  - path: scripts/enrich_ec_general_defs.py
    sha256: 45708aa03e049d2ab395e6be0d5f5b1816c9ae4707a478a9e3b321ebb675ad97
    role: context
  - path: scripts/enrich_mechanistic_defs.py
    sha256: e4238b8bffc0de3ce84ad0cec3691e0a1af5d45ee6553fca92a21ef04c3afdf3
    role: context
  - path: scripts/record_io.py
    sha256: ebe9153319474f2c7333b8b4709f32b00eddae1d2abe3d6a1420c74356e585bf
    role: context
  - path: scripts/rhea_rdf.py
    sha256: 4a7a05bfdedce442e38cd3da5d4dc83ea5c2796ea1099c6fc804321c4a4c5af9
    role: context
  - path: scripts/seed_ec.py
    sha256: 606eac99b5465ec95f40071de6421c79adcd0394e71d9e7acd7d92eb2b98c98e
    role: context
  - path: scripts/yaml_emit.py
    sha256: 2507aaa5ed8f44634082183aecdde91f259b5700b6530f55a133507a2ca0a388
    role: context
  - path: src/proteintraitsmech/schema/proteintraitsmech.yaml
    sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
    role: context
scope:
  description: Field-by-field scientific review of one complete ProteinTraitRecord.
  selection: Path-order position 6 in batch 165. Fresh main inventory has 429394 records.
    Main and validated published review heads (batch-001 at b36c4b5ad6c1ee1f31f1cc8c4da5cad94651719d;
    batch-002 at 357a22ff037976ab142a6bf2267191b5f4a98d21; batch-003 at cc32a8c59ea04af980930b521773705380a9d85a;
    batch-004 at 23d5cee9fdad2ee701ca7d5cadfc76b54df242ca; batch-005 at 678797be94bf7bcf5673a5c9dcd2e779ec1c76cc;
    batch-006 at 1696e53c414be3be3641f470a8eade2ec004b6b1; batch-007 at ecd1ed5f09754b6cee1695d813f62f9b23b6ccf5;
    batch-008 at 914248190c8fd158835c16572946efde3dd87af4; batch-009 at 12d47e9145517b395c6ffdacd172003af66f5618;
    batch-010 at d51f823a5de8645ec50586992dc9e2e27fdef83f; batch-011 at 3f0697b8989b56af606b2eee7248b55fa21cd4f5;
    batch-012 at 86f94d00a00a8b0fbaa16d5301a35ff03fa8abc0; batch-013 at ef73f3abddbb3786a9d95cc0e4616aeaea5ca3fb;
    batch-014 at dc70a3cb9267c42c78bc4c356ec28109fb45114f; batch-015 at 10d0148878b3b2e203d2f368ac3b3fd48c8b0e50;
    batch-016 at 8a2bb4c2441c87fb0eeda6e7623c87c0e0a6c1fd; batch-017 at 952d4d2227f24b9d7a96481536971328f8c9e7c9;
    batch-018 at 63c8c7d6546a6e5e23c634b191f7dbb9791c6a3c; batch-019 at a14da7a2c18c5f53a33fb69c8556ca6de9526a87;
    batch-020 at 58ea13ba743688b992e16e34888a75384d259bc7; batch-021 at 27121a6951a72021e2037a04ee1e1424215a61df;
    batch-022 at 484164d64a30c3578caabf4600044501f6c73ce5; batch-023 at bf8f281b87817f23531ae0fdd2aefa452f4c9242;
    batch-024 at 01f60cc4160c18fe3e62768ca960a8c76bb60616; batch-025 at 0246872bdbfd520403011891f03194457ebd2b98)
    cover 266 record paths. Including validated unpublished local review commit(s)
    da9c0fc6fbdf249f87d3cceba1b83c6cb2ac975d; 2e4943d62d132241cbbe931c3347abb8e45719bd;
    f67243be00c3d9c891c24c22a32c932ea7bee099; 55a71f32ee7c35ceb6449d1bd1d85954b9609d18;
    ac3fcf7c6a5710b240a7aa0db1d09bcb2f09529b; 00702985331951f0990ffdc7b352b5a1657160b7;
    b6ee361647a739487903ad0d184297a280189333; 94d787f848b7b9a1c123f7ae54f1cacedd7f55eb;
    c6dacdf0e1f79554d56ebfff47b08d3ef1f4c585; 2713fb4cb42716b649bb40a055bf29cf2138dca4;
    756ecaf67cacd45cb5bf9d7b5666b4fbde632e96; 6a22474e153e8283e66d85844806dbc27784eebb;
    ee9a05771251fd84096ca40cfee30ea23e064f91; c589a5515b45e7337f41a032609859f3a20fb7f9;
    b87f4bd08683d7d13c943c409fd2fc191918135b; 43b6868b10bbbe28d4030e9eaf0a06a4400f47dd;
    95ad98ca67c636454fb543a53f9157b574d64cb6; 538ccd21f618ad8ae64adfe2667af153feae8ff1;
    08a4a1d5e2d7457ce4696303db2cb67cf3f5f752; 68138e97c6706d7c0fbb0ab30f58d5fd179b6661;
    8f8d7bc536c122a1caa0f9fe02bd19aa3af2e79b; 896749322d48bf0a8efd3b822d34ff9f6ada7ffc;
    2d4dd0983f0604f70a485c085e43942b24e520ac; 6f9ec803cc5193aa056ad3e7b42678d05a11e1ad;
    cad414749af988265991078a351e7bff329f012f; decc32c20475e07ec196d4fb3c930979344ca1f3;
    00f14ceee7dff47cc5ebdea68fc434e6433bebba; 19ec1cc7e4b21f351a5cdc2b18611dd7361b088e;
    e12f670fd4896cdce45b65eab2547ef679ef1cf7; 2af17182bdaaee828e308b030b76a675442fba5c;
    18d3c2d4119314ba267f54e08397c1c889f6407c; 028198be440bc2ac7e50245c4444c30425798739;
    8130eea18e4e9234bccbc8af19d08f040a3645c8; 0089dcf1bc90bc2737892baa2670dbe64b214810;
    91b6b1b722fd89902ef210ed30beda1c94a5bd5f; 99d0578fb48bc77c11102c40e2989aa30b2a0dac;
    2ba88a35fdb646bbe295cdad6c62826e0a187f44; 2f4bacaeedd95045a5e15c309d43c033e408e325;
    ef616d50f93f5715042a1cd3562d34b2d7f9a127; f4cb59c32d03a12ea6736f618de5acf20a4439d6;
    ff23e5df0c3487e32ffb957c67675c67c16b41c2; 75ad3a291726b092c359f97917a71cfe8e2e6af8;
    02b349a5fd82cfb33d9194b5cc7a40ff50f366fd; cfb19dc9d57ec551c66101215d03f6e1d43d0eff;
    c3d9c57c6538a844da118acc99853d274d0a4806; 8abfd5711bfe4893ca2a72758d6ed38497200e1b;
    8dd1ec15880ec4357357dac79943ea67382c19bd; 612a48f9fee6d2a47670d8a9dcba8ba7a4a3ef17;
    9b575fbbb6874c6a70f7461b3fce32d06141cf7a; c022030b5e1a201b57819eb42bb559638014fe9e;
    b1d3cd26d82f923901ad03edbd671c0756d0ecbd; c95fe22c3576a31202663b274ea8ab708796f5b3;
    83b626799fbe7a712b670a6cde18587c03c9b642; 67c32e6581cd85d000e501335ed1cea86edb64fd;
    544e1d260461741d6e33957881d9397ee07b4159; fbc8060b3f156689ff1c9187c0a4f8fb58f02b54;
    162ff91cc410b6d11c2a228a74fa1763d24eec61; f52add53b1d8cc6ce345f604c076223b6534aba3;
    751989196f24b1f2a0c1fb0701d8a0812072232f; 5f2e76e40a672c9cff0869bd1603d3696314e210;
    c2806d7e525fa0f7eb1c525da8c0a811f2a84f4d; 64b8692fe04e57d6de5e8f64d89d69fcf88f5cd6;
    156c17ab70a878767ae231ed5f823055993c5a39; eec5f399f735fb4e6cfe372a210a6091b8af2509;
    916ca112e82b09cf0741f3bedace363e4c164cdf; 1094e78cebf5eb94d5757d7a36ebdf535cb11704;
    403388fd601f7e516781e19472be7d418ef9c678; 83cbeeb06066f2ae99b9e6239078863103e97e85;
    4274276609c085aa059b09669b018cb10b7113da; feaa20463c425a3fcdcc782599f5ff3133a19067;
    fcee8eb7470aeb0738fb65262f7c7bd82cf9a34e; 577ae0e39e5bde0e4da363cf41f9f39a37afb356;
    850a910aabc759168f0e749d313e4c21fb2387ec; 3e66545b045adc938bf9b0b1471532cc0ae266c4;
    817d5e6fe5d4ca5a9c4cd88ee035c6a3b5de5436; 39e70039bc443da8955862c4a845defe88c5c385;
    e3e294c90026f72ef87acb583aef9b435dc08d8f; 853e2ca43ae9dc1812a20a68ccecfda15061109d;
    f99a413f3ac540b5526af7d65c0fea82bb11c881; d03ea4ee80be28aa2fb34602f730170c9541a666;
    2618b15c61d1e4061f3674a249db897d257b5a9e; 00a57e8acb204780df68a3d9d8429cbd43086c16;
    ef0d145e14270698802dd649a9c346bab53ed2ca; aadecba057531eff15d0117aa957d71b6efbdcc7;
    c2283b6ba39c7f66e7eede2a166c94c4692a3ff9; 2a98cb4271fbe15a6280c3039e86243248b7076f;
    aade04271813734e76a5f381c5e6aa11c48c4586; 33622742735c62c57d5a2356634b6fc922db6f6f;
    e9e6f0d1043c65d8302c284f41fda4a27fb7b873; 955219ebb51f49d6efeeaff398883ed6c96834a2;
    81a8175da6a3f1e6fb5f4b4935657190723f9aa0; 272c2a8bd759243561d08a515732c631c8a91540;
    bef507f5b340a81db4212994a8b0b91f37d806d3; 0eb23e8c8f3888995462c1f1b97cbd44694a823a;
    42e54e3e2797a3a7b51417dbcebb0b9c4a7b0cf6; 4848fbf8933e623045babe4baed8e4e7c54f6230;
    43eb98cf14f2542c7e7f602651ccf204a54da0f6; c6737819b8f5bd1a06ddd6853432cdee1bd1bfe0;
    354bfc21667fb534f5eef295984647af689f6447; c38451d06601b7a1197e7a6962fe21ebf96e0fef;
    aa7698d0ed63abad4280ed1bd0cdcabe114ed3c2; 83fa541c35bbc36c57ba253240b01ff6b5feade1;
    036c6b1118d17a5cc3515176f914ef6bb0ec14d7; 40d259197445aa2f47c10bf4058835e362528019;
    332dc98b4b9fdbedec00b1c809f18f03a630945c; 3f3d5320fdb0f5dbd33ea70f3d7a164eff403575;
    71b0d4586ae89d103ce97b8e4289f07cb66dc249; 40156bc2beacbb7d4f4a88eea25bb8e63fce6fad;
    f7235e5f4b93a3ef0a4d541180c1f7ef8fea00a3; 20085d9e39447af672fef4875299f6b8a921e34a;
    e57f7a6fcdc244ee2c841c7bea6816fc21debd01; 2d3659a9e0f4b900b54ed58d6864f4c8c2685a73;
    17fab5aa093f688b7742ad179f9c7ff49bbcf01e; 03fe3b878d21da8cf4309a6acfc1c04269daa216;
    50e8fbee6f1ac7b66da1f68998cd0edbbed8b876; bdab443a280b4395e8ba21cef021465ae13475cc;
    f6a810c1fb200ac9437dd7d4384ee11a65b8da34; ce1b420fc27a19254091e1be9e09b0113daa4ee5;
    b553b959240a1f20c73054385ed1c5c034604b29; d17da9f5c93efb7ed50684364197776fcae59560;
    51f60c7644920159d535217eeee96381a648646a; 3ca593a22c594f6071bb4e47ac3e99c98942bd64;
    b2b89b7d3e2a195949c1dacb6ac82b9b0082f424; f83270ba96807bf8c58e206407a6b460a97f469a;
    954dcd112c976a5ae0cc551e121f2f38cc57e469; c11015c15fefb635760fab2097c5eb94fecd4a73;
    0d273e27cb68c70fcac80432fb25bcb436e6474e; b22e81db4c56b009c01e69fc35aac44fe8bcb810;
    21a97e06f9e3d1642378903bbb0f46eeeea6cbe6; 8a7064ff6bae6e80524b23b2226166c1468b3215;
    efb75211d4fe2244704e320456e1df86ee7b6ccc; 36c078b072e242d60b41b7745ea853f2ceb91978;
    21cda0d469da7ea3344e2cff639769d3666bd720; 0b51d7ca3b8efacd55d046462e8724758561e762;
    19944f198684bd9a58538009588bfbdc8984ec9d; 985c86c62e2f6efc63016a0199a9e70dd944e9ff;
    f54bcd34f1d157dd2c670b2886de595577078992; 0ed5bdc586987619444370d7c764c83b5797f2e0;
    6dab4d17475702064cc410ed6371922af04ccc30, the union covers 1656 record paths,
    leaving 427738 before this batch. 165 inventories were combined. Unpublished local
    coverage is explicitly not published or merged main coverage. Snapshot-row context
    paths are excluded.
  coverage: full
  population_size: 1
  reviewed_target_ids:
  - EC:1.14.19.13
targets:
- target_id: EC:1.14.19.13
  path: data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml
  label: acyl-CoA 15-desaturase
  record_class: ProteinTraitRecord
  kind: generated
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_ec.py
    role: Maintained EC seed identity, base definition, synonyms, mapping and legacy
      example emitter
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_ec_general_defs.py
    role: Maintained GENERAL definition composer from the EC hierarchy
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_mechanistic_defs.py
    role: Maintained MECHANISTIC layer composer from the existing reaction definition
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/build_ec_causal_graphs.py
    role: Maintained reaction chemistry, mapping and exemplar graph builder with status/history
      emission
checks:
- check_id: gate-1
  name: Closed schema
  command: just validate data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Single target validated in closed mode.
  target_ids:
  - EC:1.14.19.13
  evidence_ids:
  - validation-1
- check_id: gate-2
  name: Closed schema and applicable source semantics
  command: just validate-all data/traits/function/enzymatic_activity/ec/1-14-18-ec1-14-18--.yaml
    data/traits/function/enzymatic_activity/ec/1-14-19-1-ec1-14-19-1.yaml data/traits/function/enzymatic_activity/ec/1-14-19-10-ec1-14-19-10.yaml
    data/traits/function/enzymatic_activity/ec/1-14-19-11-ec1-14-19-11.yaml data/traits/function/enzymatic_activity/ec/1-14-19-12-ec1-14-19-12.yaml
    data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml data/traits/function/enzymatic_activity/ec/1-14-19-14-ec1-14-19-14.yaml
    data/traits/function/enzymatic_activity/ec/1-14-19-15-ec1-14-19-15.yaml data/traits/function/enzymatic_activity/ec/1-14-19-16-ec1-14-19-16.yaml
    data/traits/function/enzymatic_activity/ec/1-14-19-17-ec1-14-19-17.yaml
  exit_code: 0
  status: passed
  required: true
  summary: One shared invocation scanned all ten listed batch targets; target SHA256
    matches before and after execution. Source-specific checks apply where implemented;
    this gate does not establish scientific class semantics or independently qualify
    every legacy protein example.
  target_ids:
  - EC:1.14.19.13
  evidence_ids:
  - validation-2
- check_id: gate-3
  name: Causal graph integrity
  command: just audit-graphs data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml
  exit_code: 0
  status: passed
  required: true
  summary: Structural causal-graph integrity was checked on the exact target; deterministic
    checks do not independently verify the scientific claims.
  target_ids:
  - EC:1.14.19.13
  evidence_ids:
  - validation-3
- check_id: gate-4
  name: Curation history validity
  command: just validate-history
  exit_code: 0
  status: passed
  required: true
  summary: Full curation-history gate; this review adds no history event.
  target_ids:
  - EC:1.14.19.13
  evidence_ids:
  - validation-4
- check_id: source-resolution
  name: Source reference inspection
  status: passed
  required: true
  summary: Current native inputs and successful source tuples were hash-checked. All
    current captured inputs and complete selected Rhea closures were independently
    checked. Local references were read at the explicit defining-field scope.
  target_ids:
  - EC:1.14.19.13
  evidence_ids:
  - target
  - classification
  - ec2go
  - enzyme
  - iubmb
  - rhea2ec
  - rhea-rdf
  - go-quickgo
  - go-ols
  - protein-Q594P3
  - primary-17178719
  - primary-15361534
evidence:
- evidence_id: target
  kind: record_content
  reference: data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml
  snapshot_sha256: 3e9ddd70a9981591e07e3598571dc79c89e7bc07176eba298638c0ba71e90151
  accessed_at: '2026-10-27T10:19:55.423803Z'
  locator: Entire target YAML.
  summary: The complete current target records identity, definitions, all exemplars
    and graph content, status and history.
  support: supports
- evidence_id: seeder
  kind: record_content
  reference: scripts/seed_ec.py
  snapshot_sha256: 606eac99b5465ec95f40071de6421c79adcd0394e71d9e7acd7d92eb2b98c98e
  accessed_at: '2026-10-27T10:19:55.423831Z'
  locator: EC parsing, record creation and example construction.
  summary: The EC importer supplies nomenclature and legacy ENZYME DR-associated examples.
  support: supports
- evidence_id: general-writer
  kind: record_content
  reference: scripts/enrich_ec_general_defs.py
  snapshot_sha256: 45708aa03e049d2ab395e6be0d5f5b1816c9ae4707a478a9e3b321ebb675ad97
  accessed_at: '2026-10-27T10:19:55.423851Z'
  locator: Classification lookup and GENERAL definition construction.
  summary: The maintained definition writer derives hierarchy prose.
  support: supports
- evidence_id: mechanistic-writer
  kind: record_content
  reference: scripts/enrich_mechanistic_defs.py
  snapshot_sha256: e4238b8bffc0de3ce84ad0cec3691e0a1af5d45ee6553fca92a21ef04c3afdf3
  accessed_at: '2026-10-27T10:19:55.423871Z'
  locator: EC equation parsing and MECHANISTIC definition construction.
  summary: The maintained definition writer derives catalytic-equation prose.
  support: supports
- evidence_id: writer
  kind: record_content
  reference: scripts/build_ec_causal_graphs.py
  snapshot_sha256: d5fdfc7fab74cc3b50b3707669bddd6e58b58299a0178528c6748c6f05f37a2d
  accessed_at: '2026-10-27T10:19:55.423894Z'
  locator: Graph construction, existing-graph skip, status promotion and history append.
  summary: The graph builder writes source-linked edges, an introduction, history
    and automatic SEEDED-to-REVIEWED promotion.
  support: supports
- evidence_id: record-io
  kind: record_content
  reference: scripts/record_io.py
  snapshot_sha256: ebe9153319474f2c7333b8b4709f32b00eddae1d2abe3d6a1420c74356e585bf
  accessed_at: '2026-10-27T10:19:55.423925Z'
  locator: Lines 420–490 merge policy entry and 725–799 complete write_validated_record/write_record.
  summary: The shared writer separates reseeding merge policy from in-place replacement
    and offers atomic strict validation.
  support: supports
- evidence_id: rhea-writer
  kind: record_content
  reference: scripts/build_rhea_causal_graphs.py
  snapshot_sha256: ac1785a1d65e4f747f3e0f6661a2c97cea8df20aefdbab9bbe12c7e236ded5f8
  accessed_at: '2026-10-27T10:19:55.423950Z'
  locator: Participant and reactive-part construction, lines 157–300.
  summary: The reaction graph route constructs generic participants and reactive-part
    nodes; current iron-ion reactive parts are evaluated against their actual chemistry.
  support: supports
- evidence_id: schema
  kind: record_content
  reference: src/proteintraitsmech/schema/proteintraitsmech.yaml
  snapshot_sha256: 7d29139f696497dffa018b8d68b3f72d4e1adbadd4f67f7904ddbb4b12275418
  accessed_at: '2026-10-27T10:19:55.424021Z'
  locator: Mapping status 1482–1495; CanonicalExample 1648–1715; MappingStatusEnum,
    ExampleSourceEnum and GroundingQualification 3473–3529; complete CausalNodeTypeEnum
    3586–3627.
  summary: The schema defines REVIEWED as curator sign-off and distinguishes class
    activities, proteins, chemical species and residues.
  support: supports
- evidence_id: review-contract
  kind: record_content
  reference: docs/record-review-profile.md
  snapshot_sha256: 06cec6693ded193231a378bba04e7c1ad3e295f88903ee8b7c30b3238daab9df
  accessed_at: '2026-10-27T10:19:55.424044Z'
  locator: Complete record-review profile.
  summary: The profile separates source evidence, review outcomes and human sign-off.
  support: supports
- evidence_id: checklist
  kind: record_content
  reference: .claude/skills/curate-yaml-record/references/review-checklist.md
  snapshot_sha256: 59f39fad3e6447e7be30da72667befd3d2e383b68bea5f497952f2ab080da90d
  accessed_at: '2026-10-27T10:19:55.424069Z'
  locator: Complete review checklist.
  summary: The checklist provides identity, ownership, evidence and completeness review
    criteria.
  support: supports
- evidence_id: ancestor-1
  kind: record_content
  reference: data/traits/function/enzymatic_activity/ec/1-14-19-ec1-14-19--.yaml
  snapshot_sha256: 91b7864a16b00e95945ba96928ef4853428330e44f0c284f0f436af0adca95af
  accessed_at: '2026-10-27T10:19:55.424091Z'
  locator: Complete ancestor records, including defining fields, hierarchy, mappings,
    examples and graphs; examples and graphs used only as ancestor context.
  summary: The selected ancestor defining fields supply hierarchy and class context.
    Its examples and graphs were read only as ancestor context, not treated as target
    evidence.
  support: supports
- evidence_id: ancestor-2
  kind: record_content
  reference: data/traits/function/enzymatic_activity/ec/1-14-ec1-14----.yaml
  snapshot_sha256: e48a177015965d9d40ebfb80643e1d914cf2a6362d3d47b94b6f301096158165
  accessed_at: '2026-10-27T10:19:55.424113Z'
  locator: Complete ancestor records, including defining fields, hierarchy, mappings,
    examples and graphs; examples and graphs used only as ancestor context.
  summary: The selected ancestor defining fields supply hierarchy and class context.
    Its examples and graphs were read only as ancestor context, not treated as target
    evidence.
  support: supports
- evidence_id: ancestor-3
  kind: record_content
  reference: data/traits/function/enzymatic_activity/ec/1-ec1------.yaml
  snapshot_sha256: f61053223eeff4b7f57499893ab0f080ddfe2b3b145b52d47b58cfcaee9267b4
  accessed_at: '2026-10-27T10:19:55.424133Z'
  locator: Complete ancestor records, including defining fields, hierarchy, mappings,
    examples and graphs; examples and graphs used only as ancestor context.
  summary: The selected ancestor defining fields supply hierarchy and class context.
    Its examples and graphs were read only as ancestor context, not treated as target
    evidence.
  support: supports
- evidence_id: context-1
  kind: record_content
  reference: data/traits/function/molecular_function/go/acyl-coa-15-desaturase-activity-go0102988.yaml
  snapshot_sha256: f0220191f32e2aa562432507be21f116fc50cc1578159dfde2ba2ee3200ed8e6
  accessed_at: '2026-10-27T10:19:55.424311Z'
  locator: Identifier, label, definition/source, axis/category/kind/status, definitions,
    synonyms, parents and mappings; neighboring examples and graphs excluded.
  summary: The local GO or Rhea defining fields provide a comparison of names, reaction
    scope and mappings.
  support: supports
- evidence_id: context-2
  kind: record_content
  reference: data/traits/function/enzymatic_activity/rhea/9z-12z-hexadecadienoyl-coa-ah2-o2-9z-12z-15z-hexadecatrienoyl-coa-a-2--rhea37599.yaml
  snapshot_sha256: fb67db21fd5336242163fcf67cdc32be26986d1aeeab3c8feebcc5af021d00be
  accessed_at: '2026-10-27T10:19:55.424444Z'
  locator: Identifier, label, definition/source, axis/category/kind/status, definitions,
    synonyms, parents and mappings; neighboring examples and graphs excluded.
  summary: The local GO or Rhea defining fields provide a comparison of names, reaction
    scope and mappings.
  support: supports
- evidence_id: enzyme
  kind: authority
  reference: https://ftp.expasy.org/databases/enzyme/enzyme.dat
  snapshot_sha256: 6e1f553fcaa15ba7018344d4181012002547cf15febeb9d3a03dacdd75963001
  accessed_at: '2026-10-21T18:41:16.449142Z'
  locator: Complete EC 1.14.19.13 stanza.
  summary: The complete ENZYME entry gives the acyl-CoA 15-desaturase reaction with
    a C16 diene substrate, a product labelled 9Z,12Z,15Z, generic AH2/A and water.
    Its comments describe sorghum root hairs, a terminal double bond and cis wording
    at carbon 15; Q594P3 is the listed protein association.
  support: supports
- evidence_id: classification
  kind: authority
  reference: https://ftp.expasy.org/databases/enzyme/enzclass.txt
  snapshot_sha256: a7e77777ac5260f6c86e6127211f036f202cbfb8e11bcc5e638979e538a14782
  accessed_at: '2026-10-21T18:41:14.445710Z'
  locator: Exact EC 1, 1.14 and selected donor-subclass classification lines, including
    the parent entry when applicable.
  summary: The exact EC 1, 1.14 and 1.14.19 classification lines place these activities
    among oxidoreductases acting on paired donors, with donor oxidation reducing molecular
    oxygen to two molecules of water.
  support: supports
- evidence_id: rhea2ec
  kind: authority
  reference: https://ftp.expasy.org/databases/rhea/tsv/rhea2ec.tsv
  snapshot_sha256: 33a62d491eb9f56b4e9e9a5ec2e0b27f5d92432d1afcd3afe101a4b36df331f8
  accessed_at: '2026-10-21T18:41:14.769302Z'
  locator: All exact rows for EC 1.14.19.13.
  summary: The selected mapping rows assign Rhea 37599 to this EC class.
  support: supports
- evidence_id: ec2go
  kind: authority
  reference: https://current.geneontology.org/ontology/external2go/ec2go
  snapshot_sha256: 1df1674cdc5547d4d25e6a744f628710daa89c52f406374e9174c4f5c4fe6aed
  accessed_at: '2026-10-21T18:41:13.615524Z'
  locator: Exact EC 1.14.19.13 lookup.
  summary: The exact mapping row associates GO:0102988 with this EC class.
  support: supports
- evidence_id: rhea-rdf
  kind: database
  reference: https://ftp.expasy.org/databases/rhea/rdf/rhea.rdf.gz
  snapshot_sha256: 8ee48d7044cf3eef1001fa730dae2a491902ab25b259b519d6826796bb8acedf
  accessed_at: '2026-10-21T18:42:30.539193Z'
  locator: Complete closures for Rhea 37599, including all directions, sides, compounds
    and participants.
  summary: The complete selected recursive RDF supplies directions, participants,
    coefficients, formulas, charges, citations and reaction hierarchy.
  support: supports
- evidence_id: iubmb
  kind: authority
  reference: https://iubmb.qmul.ac.uk/enzyme/EC1/14/19/13.html
  snapshot_sha256: 9ab01c77afb955b414bf369c70f780f966c357c36c39dd94318be4fa6b4e05d9
  accessed_at: '2026-10-27T09:47:14.980514Z'
  locator: Complete normalized EC 1.14.19.13 HTML text and bibliography, excluding
    script/style.
  summary: The complete IUBMB entry gives the C16 acyl-CoA equation using a 15Z product
    label and describes insertion of a terminal double bond with cis wording at carbon
    15. It supplies the sorghum desaturase study as the focal reference.
  support: supports
- evidence_id: go-quickgo
  kind: authority
  reference: https://www.ebi.ac.uk/QuickGO/services/ontology/go/terms/GO:0102988
  snapshot_sha256: 3b52f6e33b160abd1ba2af38dd073563b4b7442da59018bbb0406dd27c526564
  accessed_at: '2026-10-27T09:47:16.949469Z'
  locator: Complete delivered GO:0102988 JSON.
  summary: The complete QuickGO term GO:0102988 assigns acyl-CoA 15-desaturase activity
    and gives a C16 diene-to-triene equation with generic reduced and oxidized electron
    acceptors, oxygen and water. Its product is written as 9,12,15-cis-hexadecatrienoyl-CoA,
    retaining upstream terminal 15-cis wording.
  support: supports
- evidence_id: go-ols
  kind: authority
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/go/terms?obo_id=GO:0102988
  snapshot_sha256: c3d0865b66c4ed53b97abe9abe1f0e8700362142760ba5f5d4f2206c45a03612
  accessed_at: '2026-10-27T09:47:17.218678Z'
  locator: Complete delivered GO:0102988 term JSON and relation scopes.
  summary: The complete OLS term preserves the focal GO/EC identity and reaction text,
    including the product wording 9,12,15-cis-hexadecatrienoyl-CoA. It also lists
    Rhea 46232 as a crossreference; that separate reaction closure is outside the
    acquired scope.
  support: supports
- evidence_id: enzyme-policy
  kind: authority
  reference: https://ftp.expasy.org/databases/enzyme/enzuser.txt
  snapshot_sha256: 60d7858058e9a18441be2aa389cbc1c65beef9e9e1b62e03369bbdc43a7a1b53
  accessed_at: '2026-10-21T18:41:48.862549Z'
  locator: Complete user manual.
  summary: The ENZYME manual distinguishes names, catalytic information and DR crossreferences.
  support: supports
- evidence_id: rhea-release
  kind: authority
  reference: https://ftp.expasy.org/databases/rhea/rhea-release.properties
  snapshot_sha256: 4259110467406048a19f7dd797bc3f0506736d1cf2a8327f67ec7b10043fc5d4
  accessed_at: '2026-10-21T18:47:36.398577Z'
  locator: Complete two-line properties file.
  summary: The delivered properties file records Rhea release number 142 and release
    date 2026-09-02.
  support: supports
- evidence_id: rhea-license
  kind: authority
  reference: https://ftp.expasy.org/databases/rhea/LICENSE.txt
  snapshot_sha256: b9df4c23b425e50676352ec3c4cf1ae753d70ab339a8b5b9ae631f5418acf03e
  accessed_at: '2026-10-21T18:47:36.432764Z'
  locator: Complete delivered license.
  summary: The delivered license states CC BY 4.0.
  support: supports
- evidence_id: skos-policy
  kind: authority
  reference: https://www.w3.org/TR/skos-reference/
  snapshot_sha256: 3aa00cd16ee4d86d3a19b75501bb317d0b0c134e1f4029e9f3098c4dd3669e4c
  accessed_at: '2026-10-21T18:47:36.600445Z'
  locator: Complete Section 10 Mapping Properties.
  summary: SKOS Section 10 distinguishes closeMatch and narrowMatch relations.
  support: supports
- evidence_id: predicate-RO_0002233
  kind: authority
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/ro/properties?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002233
  snapshot_sha256: 517a4b1a0e53d9cfb54d4125d6ac5eb27642d4865487edcd529b96cbfdfb3471
  accessed_at: '2026-10-21T18:48:12.705565Z'
  locator: Complete delivered property JSON.
  summary: The delivered property response defines has input.
  support: supports
- evidence_id: predicate-RO_0002234
  kind: authority
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/ro/properties?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002234
  snapshot_sha256: dce63cc8c8ebf5b8ec0f524b69eb8c3067ac8a38fb123b7aa4c87b22db632025
  accessed_at: '2026-10-21T18:48:12.705846Z'
  locator: Complete delivered property JSON.
  summary: The delivered property response defines has output.
  support: supports
- evidence_id: predicate-RO_0002327
  kind: authority
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/ro/properties?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FRO_0002327
  snapshot_sha256: 5bbceaccdeae417c68a2344aac455d7a7607b3f29b5295d909a16de496b49419
  accessed_at: '2026-10-21T18:48:12.705614Z'
  locator: Complete delivered property JSON.
  summary: The delivered property response defines enables.
  support: supports
- evidence_id: predicate-BFO_0000050
  kind: authority
  reference: https://www.ebi.ac.uk/ols4/api/ontologies/ro/properties?iri=http%3A%2F%2Fpurl.obolibrary.org%2Fobo%2FBFO_0000050
  snapshot_sha256: 5edb2a13402e9c1754585f30bd6cae1dd6fe956362c49f3a2e0fd738dd161098
  accessed_at: '2026-10-21T18:48:12.705225Z'
  locator: Complete delivered property JSON.
  summary: The delivered property response defines part of.
  support: supports
- evidence_id: chemical-85914
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/85914/
  snapshot_sha256: 1a1d25b32da5f6a38b2d747baa0b3c1b0f770ba24b71a9fbde48c0bb5ae306c0
  accessed_at: '2026-10-27T09:47:14.072006Z'
  locator: Identity, definition, all names, chemical_data, default_structure and secondary
    IDs; unrelated ontology/roles lists excluded.
  summary: The selected ChEBI identity, names, formula, charge and structure establish
    the actual chemical identity; metal-ion and protein-host typing are assessed separately.
  support: supports
- evidence_id: chemical-76552
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/76552/
  snapshot_sha256: afe0a3f4099365f04d7de0d7ecd44277fdd7325304f368d906cea9252b427eed
  accessed_at: '2026-10-27T09:47:14.559627Z'
  locator: Identity, definition, all names, chemical_data, default_structure and secondary
    IDs; unrelated ontology/roles lists excluded.
  summary: The selected ChEBI identity, names, formula, charge and structure establish
    the actual chemical identity; metal-ion and protein-host typing are assessed separately.
  support: supports
- evidence_id: chemical-13193
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/13193/
  snapshot_sha256: e57168d9187cf60eb00866c7ffb8ac67d50cf33a8894f84531ce2f20a9c20a77
  accessed_at: '2026-10-27T09:47:13.432224Z'
  locator: Identity, definition, all names, chemical_data, default_structure and secondary
    IDs; unrelated ontology/roles lists excluded.
  summary: The selected ChEBI identity, names, formula, charge and structure establish
    the actual chemical identity; metal-ion and protein-host typing are assessed separately.
  support: supports
- evidence_id: chemical-17499
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/17499/
  snapshot_sha256: 5366edd079e14f4e2e1ed0cd571d14cef7c53ea852747f3e7e71c119c0115ea2
  accessed_at: '2026-10-27T09:47:14.349492Z'
  locator: Identity, definition, all names, chemical_data, default_structure and secondary
    IDs; unrelated ontology/roles lists excluded.
  summary: The selected ChEBI identity, names, formula, charge and structure establish
    the actual chemical identity; metal-ion and protein-host typing are assessed separately.
  support: supports
- evidence_id: chemical-15377
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/15377/
  snapshot_sha256: 10be65941e4382a24e25a481b4d950f5f26355a62e1a203bf5c3cca77bd84ab0
  accessed_at: '2026-10-26T07:14:50.561656Z'
  locator: Identity, definition, all names, chemical_data, default_structure and secondary
    IDs; unrelated ontology/roles lists excluded.
  summary: The selected ChEBI identity, names, formula, charge and structure establish
    the actual chemical identity; metal-ion and protein-host typing are assessed separately.
  support: supports
- evidence_id: chemical-15379
  kind: database
  reference: https://www.ebi.ac.uk/chebi/backend/api/public/compound/15379/
  snapshot_sha256: a15dbd09b583cbc98eaf2714ea76e97924513693f5a652ceaa3e3a3f3616677a
  accessed_at: '2026-10-26T07:14:50.611769Z'
  locator: Identity, definition, all names, chemical_data, default_structure and secondary
    IDs; unrelated ontology/roles lists excluded.
  summary: The selected ChEBI identity, names, formula, charge and structure establish
    the actual chemical identity; metal-ion and protein-host typing are assessed separately.
  support: supports
- evidence_id: protein-Q594P3
  kind: database
  reference: https://rest.uniprot.org/uniprotkb/Q594P3.json
  snapshot_sha256: 812b6f4cdbe1d73b48cb4dad236df7716d6e183eb272730da4ff1fec225b9194
  accessed_at: '2026-10-27T09:47:15.626287Z'
  locator: 'Q594P3: identity/audit/organism/names/genes/existence/length; complete
    FUNCTION, CATALYTIC ACTIVITY, COFACTOR, CAUTION, SIMILARITY, SUBUNIT and BIOPHYSICOCHEMICAL
    PROPERTIES comments; material family crossreferences. Complete matching citation
    IDs, titles, DOIs, publication metadata and referencePositions for sources tagged
    in selected comments. Complete reference array including authors, referencePositions
    and reference comments additionally read for this accession. Other comments, GO/other
    crossreferences, sequence residues/features and API extras excluded.'
  summary: Current reviewed UniProt identifies sorghum SbDES3 and assigns the focal
    catalytic activity with ECO:0000269 from PMID 17178719. FUNCTION describes terminal
    C16 desaturation and additional linoleate-to-alpha-linolenate activity, while
    retaining the transcript/root-hair reference PMID 15361534. The catalytic annotation
    uses the upstream 15Z product label; its evidence tier does not resolve that nomenclature
    tension.
  support: supports
- evidence_id: primary-17178719
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:17178719%20AND%20SRC:MED&format=json&resultType=core
  snapshot_sha256: 2bccfce75187be03be899f0daa2c227a8491ec5d593efe9abafec193324fdd34
  accessed_at: '2026-10-27T09:47:16.588213Z'
  locator: Complete delivered indexed bibliography, abstract or explicit null, correction
    list and separately read pubTypeList; no full article.
  summary: The indexed primary research abstract reports that sorghum SbDES2 converts
    16:1 delta9 to 16:2 delta9,12 and SbDES3 converts that diene to 16:3 delta9,12,15
    in heterologous yeast. The SbDES3 reaction creates a terminal carbon 15–carbon
    16 double bond. The abstract also reports root-hair expression; it does not directly
    establish a physiological CoA versus other acyl-carrier substrate step.
  support: supports
- evidence_id: primary-15361534
  kind: primary_source
  reference: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:15361534%20AND%20SRC:MED&format=json&resultType=core
  snapshot_sha256: b1335b1fd352afacc5958d43d3ff8d45d3f35524f17b97648a8b8dd03ce67f39
  accessed_at: '2026-10-27T09:55:43.112799Z'
  locator: Complete delivered indexed bibliography, abstract, pubTypeList and correction
    list; no full article.
  summary: The indexed research abstract reports root-hair-enriched sorghum transcripts
    and cloning of SOR1. Similarity to desaturases and expression patterns suggest
    a role in sorgoleone biosynthesis; this abstract supplies transcript/pathway context
    rather than a direct focal SbDES3 catalytic assay.
  support: context_only
- evidence_id: provenance-search
  kind: search
  reference: /private/tmp/ptm-record-reviews-20261021/batch-165/independent-provenance-search-evidence.json
  snapshot_sha256: 9067c674a2e71335037a54bd9fec7ccba9ae49e93e144d5a6eedecf32320d25e
  accessed_at: '2026-10-27T09:44:03.467355Z'
  locator: 'Position 6: exact commands, times and complete stdout/stderr.'
  summary: Both recorded searches returned no matches within the stated ignored-inclusive
    owner/history scope. This does not establish global absence of human review.
  support: context_only
  search_scope: Owned checkout scripts, conf, data/mappings and history with rg --no-ignore
    --hidden; other directories, raw releases and sibling checkouts excluded.
- evidence_id: validation-1
  kind: validation
  reference: just validate data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml
  locator: Executed 2026-10-27T09:42:34Z through 2026-10-27T09:42:35Z; exit 0
  accessed_at: '2026-10-27T09:42:35Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      1\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv"
- evidence_id: validation-2
  kind: validation
  reference: just validate-all data/traits/function/enzymatic_activity/ec/1-14-18-ec1-14-18--.yaml
    data/traits/function/enzymatic_activity/ec/1-14-19-1-ec1-14-19-1.yaml data/traits/function/enzymatic_activity/ec/1-14-19-10-ec1-14-19-10.yaml
    data/traits/function/enzymatic_activity/ec/1-14-19-11-ec1-14-19-11.yaml data/traits/function/enzymatic_activity/ec/1-14-19-12-ec1-14-19-12.yaml
    data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml data/traits/function/enzymatic_activity/ec/1-14-19-14-ec1-14-19-14.yaml
    data/traits/function/enzymatic_activity/ec/1-14-19-15-ec1-14-19-15.yaml data/traits/function/enzymatic_activity/ec/1-14-19-16-ec1-14-19-16.yaml
    data/traits/function/enzymatic_activity/ec/1-14-19-17-ec1-14-19-17.yaml
  locator: Executed 2026-10-27T09:42:27Z through 2026-10-27T09:43:31Z; exit 0
  accessed_at: '2026-10-27T09:43:31Z'
  support: supports
  summary: "=== validate-strict summary ===\n  files scanned:      10\n  files with\
    \ ERROR:   0\n  total ERROR rows:   0\n  TSV:                reports/instance_validation_failures.tsv\n\
    files scanned: 10\nregistry proteins: 13208\nsource evidence objects: 22314\n\
    qualified record bindings: 22314\nUniProt membership objects: 431\nhierarchy records:\
    \ 0\nsemantic findings: 0\nTSV: /private/tmp/ptm-record-reviews-20261021/repo/reports/uniprot-grounding/validation.tsv"
- evidence_id: validation-3
  kind: validation
  reference: just audit-graphs data/traits/function/enzymatic_activity/ec/1-14-19-13-ec1-14-19-13.yaml
  locator: Executed 2026-10-27T09:42:35Z through 2026-10-27T09:42:35Z; exit 0
  accessed_at: '2026-10-27T09:42:35Z'
  support: supports
  summary: 'causal-graph audit: 1 records, 1 graphs, 9 nodes, 8 edges | grounded nodes
    9/9, snippet-cited edges 8/8 | 0 errors, 0 warnings'
- evidence_id: validation-4
  kind: validation
  reference: just validate-history
  locator: Executed 2026-10-27T09:43:31Z through 2026-10-27T09:43:33Z; exit 0
  accessed_at: '2026-10-27T09:43:33Z'
  support: supports
  summary: No issues found
assessments:
- area: identity
  outcome: supported
  summary: 'The EC class, FUNCTION/class placement, C16 diene-to-terminal-triene transformation,
    Q594P3 example and official GO association are supported. The terminal product
    name requires a bounded nomenclature reconciliation: ChEBI identifies a terminal
    C15=C16 bond and omits 15Z in its preferred name, while several upstream descriptions
    retain it.'
  evidence_ids:
  - target
  - classification
  - ec2go
  - enzyme
  - iubmb
  - rhea2ec
  - rhea-rdf
  - go-quickgo
  - go-ols
  - protein-Q594P3
  - primary-17178719
  - primary-15361534
  target_ids:
  - EC:1.14.19.13
  assessment_id: assessment-1
  topic: Source identity and protein-trait scope
- area: representation
  outcome: supported
  summary: The molecular-function, protein-example and chemical-participant types
    are appropriate. Rhea 37599 uses charged acyl-CoA species and generic redox donor
    AH2/A. The terminal stereodescriptor issue concerns labels rather than a different
    chemical identifier, substrate chain length or reaction direction.
  evidence_ids:
  - target
  - schema
  - classification
  - rhea-rdf
  - chemical-85914
  - chemical-76552
  - chemical-13193
  - chemical-17499
  - chemical-15377
  - chemical-15379
  target_ids:
  - EC:1.14.19.13
  assessment_id: assessment-2
  topic: Defining representation and axis/category
- area: consistency
  outcome: concern
  summary: The target faithfully inherits 15Z from ENZYME/IUBMB and the UniProt/Rhea
    reaction label, so this is not an extraction-only defect. ChEBI 85914 has a terminal
    alkene structure and a preferred name without 15Z. The same three prose fields
    also contain a line-wrap split before CoA. These concerns are distinct from the
    valid class and mapping association.
  evidence_ids:
  - target
  - classification
  - ec2go
  - enzyme
  - iubmb
  - rhea2ec
  - rhea-rdf
  - go-quickgo
  - go-ols
  - protein-Q594P3
  - primary-17178719
  - primary-15361534
  - ancestor-1
  - ancestor-2
  - ancestor-3
  - context-1
  - context-2
  target_ids:
  - EC:1.14.19.13
  assessment_id: assessment-3
  topic: Trait hierarchy and source relationships
- area: ownership
  outcome: supported
  summary: The EC importer, general/mechanistic definition writers and graph builder
    are the durable routes. Current captured hashes match the actual owner scopes
    read for this review. Bounded ignored-inclusive discovery supports ownership attribution
    without reconstructing every historical invocation.
  evidence_ids:
  - seeder
  - general-writer
  - mechanistic-writer
  - writer
  - record-io
  - review-contract
  - provenance-search
  target_ids:
  - EC:1.14.19.13
  assessment_id: assessment-4
  topic: Maintained trait emitter
- area: grounding
  outcome: supported
  summary: Q594P3 has direct current catalytic evidence from PMID 17178719, whose
    yeast-expression abstract supports the C16:2-to-C16:3 terminal 15–16 transformation.
    PMID 15361534 is separately retained as transcript/pathway context. The indexed
    catalytic abstract alone does not establish the physiological acyl-carrier form
    as free acid, CoA or another lipid-bound intermediate.
  evidence_ids:
  - target
  - classification
  - ec2go
  - enzyme
  - iubmb
  - rhea2ec
  - rhea-rdf
  - go-quickgo
  - go-ols
  - protein-Q594P3
  - primary-17178719
  - primary-15361534
  target_ids:
  - EC:1.14.19.13
  assessment_id: assessment-5
  topic: Source grounding and trait associations
- area: graph
  outcome: concern
  summary: All eight edges correspond to current sources. Rhea 37599 balances formally
    at C37H60N7O19P3RS and charge −4 on each side. The product ChEBI identity and
    direction are positive, but its unqualified 15Z label needs reconciliation against
    the terminal structure. Generic AH2/A does not name a physiological electron donor.
  evidence_ids:
  - target
  - classification
  - ec2go
  - enzyme
  - iubmb
  - rhea2ec
  - rhea-rdf
  - go-quickgo
  - go-ols
  - protein-Q594P3
  - primary-17178719
  - primary-15361534
  - schema
  - skos-policy
  - predicate-RO_0002233
  - predicate-RO_0002234
  - predicate-RO_0002327
  - predicate-BFO_0000050
  - chemical-85914
  - chemical-76552
  - chemical-13193
  - chemical-17499
  - chemical-15377
  - chemical-15379
  target_ids:
  - EC:1.14.19.13
  assessment_id: assessment-6
  topic: Causal mechanism evidence
- area: evidence
  outcome: supported
  summary: Current ENZYME, IUBMB, both complete GO responses, UniProt and the indexed
    catalytic paper support the class association. ChEBI preferred naming and structure
    establish the terminal-alkene naming tension. Separate transcript evidence is
    explicitly context-only, and the unacquired OLS Rhea crossreference is not used
    to infer a mapping defect.
  evidence_ids:
  - target
  - classification
  - ec2go
  - enzyme
  - iubmb
  - rhea2ec
  - rhea-rdf
  - go-quickgo
  - go-ols
  - protein-Q594P3
  - primary-17178719
  - primary-15361534
  - enzyme-policy
  target_ids:
  - EC:1.14.19.13
  assessment_id: assessment-7
  topic: Class-level evidence and scientific scope
- area: completeness
  outcome: concern
  summary: The record has its mapped reaction, a positive GO association and a directly
    supported example. Required content work is limited to terminal-product nomenclature
    and the split CoA token, alongside status provenance. No unsupported physiological
    carrier assignment is added.
  evidence_ids:
  - target
  - checklist
  - schema
  - iubmb
  - protein-Q594P3
  target_ids:
  - EC:1.14.19.13
  assessment_id: assessment-8
  topic: Protein trait class completeness
- area: provenance
  outcome: concern
  summary: The target retains an LLM-assisted graph-generation event and automatic
    SEEDED-to-REVIEWED transition. Current owner/schema reading distinguishes this
    enrichment from documented curator sign-off. Raw successful source tuples retain
    their original HTTP instants, normalized to UTC Z only in review evidence. This
    review does not confer human sign-off.
  evidence_ids:
  - target
  - writer
  - schema
  - review-contract
  - provenance-search
  - rhea-release
  - rhea-license
  target_ids:
  - EC:1.14.19.13
  assessment_id: assessment-9
  topic: Source attribution and release provenance
findings:
- issue_key: ec-1-14-19-13-automatic-reviewed-promotion
  category: provenance
  severity: major
  certainty: confirmed
  title: Graph generation does not establish curator sign-off
  description: The current target records a July 30 LLM-assisted graph-generation
    event that promoted SEEDED to REVIEWED. The maintained graph builder implements
    that automatic transition, whereas REVIEWED denotes curator sign-off on label,
    definition and parents. The observed route does not establish that sign-off. This
    is not a global claim that no human has ever reviewed the record.
  field_paths:
  - mapping_status
  - curation_history
  evidence_ids:
  - target
  - writer
  - schema
  - review-contract
  - provenance-search
  finding_id: F1
  status: open
  target_ids:
  - EC:1.14.19.13
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_ec.py
    role: Maintained EC seed identity, base definition, synonyms, mapping and legacy
      example emitter
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_ec_general_defs.py
    role: Maintained GENERAL definition composer from the EC hierarchy
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_mechanistic_defs.py
    role: Maintained MECHANISTIC layer composer from the existing reaction definition
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/build_ec_causal_graphs.py
    role: Maintained reaction chemistry, mapping and exemplar graph builder with status/history
      emission
  rule_id: ProteinTraitRecord field checklist
  native_severity: major
  normalization_reason: The finding materially changes the meaning, scope, grounding
    or representation of a defining assertion.
- issue_key: ec-1-14-19-13-split-coa-token
  category: consistency
  severity: minor
  certainty: confirmed
  title: Repair the split CoA product token
  description: The definition, mechanistic definition and graph description spell
    the product with a line-wrap join as hexadecatrienoyl- CoA, separating a chemical
    token.
  field_paths:
  - definition
  - definitions[1].text
  - causal_graphs[0].description
  evidence_ids:
  - target
  - enzyme
  - seeder
  - mechanistic-writer
  - writer
  finding_id: F2
  status: open
  target_ids:
  - EC:1.14.19.13
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_ec.py
    role: Maintained EC seed identity, base definition, synonyms, mapping and legacy
      example emitter
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_ec_general_defs.py
    role: Maintained GENERAL definition composer from the EC hierarchy
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_mechanistic_defs.py
    role: Maintained MECHANISTIC layer composer from the existing reaction definition
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/build_ec_causal_graphs.py
    role: Maintained reaction chemistry, mapping and exemplar graph builder with status/history
      emission
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
  normalization_reason: The core identity is intact; bounded wording, completeness
    or interpretation needs follow-up.
- issue_key: ec-1-14-19-13-terminal-product-nomenclature
  category: nomenclature
  severity: minor
  certainty: confirmed
  title: Reconcile the terminal-double-bond stereodescriptor
  description: The C16 product has a terminal C15=C16 double bond, for which an E/Z
    designation is not applicable. ChEBI 85914 preferred naming omits 15Z and its
    structure begins with a terminal alkene, while the target and several current
    upstream reaction descriptions retain 15Z. The primary indexed study supports
    the same terminal 15–16 reaction. This is an upstream nomenclature tension, not
    evidence of a different transformation.
  field_paths:
  - definition
  - definitions[1].text
  - causal_graphs[0].description
  - causal_graphs[0].nodes[4].label
  - causal_graphs[0].edges[3].description
  evidence_ids:
  - target
  - enzyme
  - iubmb
  - rhea-rdf
  - chemical-85914
  - protein-Q594P3
  - primary-17178719
  - seeder
  - mechanistic-writer
  - writer
  finding_id: F3
  status: open
  target_ids:
  - EC:1.14.19.13
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_ec.py
    role: Maintained EC seed identity, base definition, synonyms, mapping and legacy
      example emitter
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_ec_general_defs.py
    role: Maintained GENERAL definition composer from the EC hierarchy
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_mechanistic_defs.py
    role: Maintained MECHANISTIC layer composer from the existing reaction definition
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/build_ec_causal_graphs.py
    role: Maintained reaction chemistry, mapping and exemplar graph builder with status/history
      emission
  rule_id: ProteinTraitRecord field checklist
  native_severity: minor
  normalization_reason: The core identity is intact; bounded wording, completeness
    or interpretation needs follow-up.
actions:
- action_id: A1
  description: Remove automatic curator-signoff promotion from the maintained graph-writing
    route and reconcile this target status/history through its owners. Preserve the
    actual graph-generation event and positive source support; record REVIEWED only
    when the defined curator sign-off is documented.
  finding_ids:
  - F1
  target_ids:
  - EC:1.14.19.13
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_ec.py
    role: Maintained EC seed identity, base definition, synonyms, mapping and legacy
      example emitter
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_ec_general_defs.py
    role: Maintained GENERAL definition composer from the EC hierarchy
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_mechanistic_defs.py
    role: Maintained MECHANISTIC layer composer from the existing reaction definition
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/build_ec_causal_graphs.py
    role: Maintained reaction chemistry, mapping and exemplar graph builder with status/history
      emission
  acceptance_checks:
  - Graph generation alone no longer assigns curator-signoff status.
  - The target status and history truthfully distinguish source enrichment from curator
    review.
  - Supported chemistry and protein associations remain intact.
- action_id: A2
  description: Repair the maintained EC line-wrap joins and regenerate or reconcile
    all three affected prose fields while preserving source attribution and chemical
    identity.
  finding_ids:
  - F2
  target_ids:
  - EC:1.14.19.13
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_ec.py
    role: Maintained EC seed identity, base definition, synonyms, mapping and legacy
      example emitter
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_ec_general_defs.py
    role: Maintained GENERAL definition composer from the EC hierarchy
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_mechanistic_defs.py
    role: Maintained MECHANISTIC layer composer from the existing reaction definition
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/build_ec_causal_graphs.py
    role: Maintained reaction chemistry, mapping and exemplar graph builder with status/history
      emission
  acceptance_checks:
  - All three fields use an intact acyl-CoA token.
  - Coefficients and reaction direction remain unchanged.
- action_id: A3
  description: Use a chemically valid terminal-product name in curated prose and graph
    labels, preserving 9Z and 12Z, the ChEBI identifier, chain length and reaction
    direction. Keep any verbatim upstream 15Z wording clearly attributed and record
    the unresolved source nomenclature discrepancy.
  finding_ids:
  - F3
  target_ids:
  - EC:1.14.19.13
  owner_paths:
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/seed_ec.py
    role: Maintained EC seed identity, base definition, synonyms, mapping and legacy
      example emitter
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_ec_general_defs.py
    role: Maintained GENERAL definition composer from the EC hierarchy
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/enrich_mechanistic_defs.py
    role: Maintained MECHANISTIC layer composer from the existing reaction definition
  - repository: CultureBotAI/proteintraitsmech
    path: scripts/build_ec_causal_graphs.py
    role: Maintained reaction chemistry, mapping and exemplar graph builder with status/history
      emission
  acceptance_checks:
  - Curated terminal-product labels do not assign E/Z at C15=C16.
  - Source quotations remain faithful and explicitly attributed.
  - The supported EC, GO, Rhea and protein associations are preserved.
limitations:
- The 15Z wording is shared upstream; the review does not attribute it solely to local
  extraction or reject the reaction identity.
- The primary indexed abstract supports terminal C16 desaturation but does not settle
  the physiological CoA versus other acyl-carrier step.
- The OLS Rhea 46232 crossreference was read as metadata; its reaction closure was
  not acquired or compared.
- Rhea uses symbolic R in generic AH2/A formulas whereas ChEBI uses A; these formal
  placeholder conventions are retained without assigning a specific donor.
- Literature reading covers complete delivered indexed bibliography, abstracts, publication
  types and correction lists. No full original article, supplementary figure, sequence-residue
  inspection or undeclared API field is claimed.
- No trait edit, human sign-off or publication is performed.
tags:
- unreviewed-path-order
- batch-165
- ec
```
