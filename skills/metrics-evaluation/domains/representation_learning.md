# Domain Guide: Representation Learning

## Define the Claim First

| Claim | Appropriate evidence |
|---|---|
| Linear accessibility | Frozen-backbone linear probe |
| Neighborhood quality | Exact k-NN or retrieval |
| Transferability | Multiple controlled downstream tasks |
| Novel-class few-shot adaptation | Class-disjoint episodic evaluation |
| Clustering structure | Label-blind clustering, then external evaluation |
| Open-set verification | TAR at predeclared FAR and calibration |
| Robustness | Corruption, shift, and subgroup evaluation |
| Efficiency | Quality versus dimension, storage, latency, and compute |

Do not issue a general representation-quality conclusion from one task, probe, seed, or
embedding-geometry statistic.

## Evaluation Matrix

A narrow claim may use one protocol matched to that claim. A broad generality claim
requires predeclared evidence across multiple materially distinct tasks or datasets,
domains or shifts, and label regimes, with at least two complementary evaluation
families: frozen linear probe, k-NN or retrieval, controlled fine-tuning, few-shot
transfer, robustness/shift, and geometry or collapse diagnostics. Geometry supports
diagnosis but does not establish downstream utility.
*(linear-evaluation and controlled-transfer provenance: `references/citations.md`)*

## Frozen Probe

Freeze the encoder and state feature layer, pooling, normalization, classifier, optimizer,
regularization, schedule, augmentation, early stopping, and search budget. Tune only on
development data and use identical budgets across encoders. Report multiple probe seeds,
accuracy/balanced accuracy or macro F1 as appropriate, per-class recall, probability
quality when relevant, and paired test-unit differences.

## Retrieval and Verification

Use this section when retrieval supports a representation or encoder claim. Generic
search or ranking evaluation uses the core ranking guidance without implying a
representation-quality conclusion.

Freeze query/gallery definitions, positives, self-match exclusion, group separation,
similarity, normalization, cutoff when applicable, gallery size, duplicate policy, and
exact versus approximate search. Apply `topics/core/evaluator_semantics.md` for ties,
MAP/NDCG definitions, and no-positive-query handling. Report Recall@K, Precision@K, mAP,
MRR, or NDCG only as appropriate to the relevance definition.

For verification, define genuine/impostor construction and report TAR at deployment-
relevant FAR values, with thresholds selected on validation data. Bootstrap identities
or acquisition sessions, not correlated pairs. EER is secondary to the operating FAR.
Report impostor trials, effective independent identities/sessions, score direction, and
tail intervals. Do not extrapolate or report a false-accept rate below the resolution
supported by observed impostors; mark that operating point inconclusive.

## Clustering

Fit and tune clustering without test labels. Freeze feature normalization, distance,
cluster-count selection, initialization/restart budget, and noise/unassigned-point
handling. Evaluate externally with adjusted Rand index or adjusted mutual information,
plus cluster-count mismatch and stability across seeds/resamples. Labels may evaluate a
frozen clustering but must not select its hyperparameters. Clustering compatibility with
one label partition does not establish general representation quality.

## Controlled Fine-Tuning and Few-Shot Evaluation

Keep architecture changes, augmentation, optimizer, schedule, search budget, label
budgets, and compute comparable. Report multiple seeds, training-from-scratch and strong
pretrained baselines, and distinguish full from parameter-efficient tuning. For few-shot
novel-class claims, use class-disjoint train/development/test pools and state `N`-way, `K`-shot,
queries, episode sampler, class-pool size, and hierarchical uncertainty. Repeated episodes
from a small class pool are not independent evidence.

## Geometry and Collapse Diagnostics

Inspect per-dimension variance, covariance eigenspectrum, effective rank, near-zero
dimensions, norm and cosine distributions, alignment, uniformity, hubness, and nearest-
neighbor purity against an incumbent and random encoder. Low rank can mean collapse or
legitimate compression; anisotropy is not automatically harmful; alignment can result
from duplicate leakage.

## Leakage and Contamination

Audit exact and near duplicates, shared identity/scene/document/capture bursts, labels or
metadata encoded in inputs, benchmark content in pretraining, augmented test variants,
and illegitimate query-gallery duplicates. Record contamination status as `CLEARED`,
`DETECTED`, `UNRESOLVED`, or `NOT APPLICABLE` for each benchmark. Unknown pretraining
provenance makes benchmark-specific validity unresolved and blocks broad generality
claims unless confirmed on post-training or access-controlled evaluation data.

## Diagnostics, Uncertainty, and Reporting

Segment by task/dataset, class frequency, label budget, source/domain, corruption,
in-distribution versus shift, seen versus novel classes, gallery size, embedding
dimension, and layer. A nuisance probe shows information is decodable; it does not prove
the primary predictor uses it.

Separate paired test-unit uncertainty, encoder-seed variance, probe/fine-tuning-seed
variance, class/task episode variance, approximate-search effects, and dataset breadth.
For multi-dataset claims, show every dataset and summarize at dataset level rather than
pooling all examples. Report search budget, storage, index quality, and latency when the
representation serves retrieval.
