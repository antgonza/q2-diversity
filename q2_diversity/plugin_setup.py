# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import (Plugin, Str, Properties, Choices, Int, Bool, Range,
                           Float, Set, Visualization, Metadata, MetadataColumn,
                           Categorical, Numeric, Citations)

import q2_diversity
from q2_diversity import _alpha as alpha
from q2_diversity import _beta as beta
from q2_types.feature_table import FeatureTable, Frequency, RelativeFrequency
from q2_types.distance_matrix import DistanceMatrix
from q2_types.sample_data import AlphaDiversity, SampleData
from q2_types.tree import Phylogeny, Rooted
from q2_types.ordination import PCoAResults

citations = Citations.load('citations.bib', package='q2_diversity')

sklearn_n_jobs_description = (
    'The number of jobs to use for the computation. This works by breaking '
    'down the pairwise matrix into n_jobs even slices and computing them in '
    'parallel. If -1 all CPUs are used. If 1 is given, no parallel computing '
    'code is used at all, which is useful for debugging. For n_jobs below -1, '
    '(n_cpus + 1 + n_jobs) are used. Thus for n_jobs = -2, all CPUs but one '
    'are used. (Description from sklearn.metrics.pairwise_distances)'
)

plugin = Plugin(
    name='diversity',
    version=q2_diversity.__version__,
    website='https://github.com/qiime2/q2-diversity',
    package='q2_diversity',
    description=('This QIIME 2 plugin supports metrics for calculating '
                 'and exploring community alpha and beta diversity through '
                 'statistics and visualizations in the context of sample '
                 'metadata.'),
    short_description='Plugin for exploring community diversity.',
)


plugin.methods.register_function(
    function=q2_diversity.beta_phylogenetic,
    inputs={'table': FeatureTable[Frequency],
            'phylogeny': Phylogeny[Rooted]},
    parameters={'metric': Str % Choices(beta.phylogenetic_metrics()),
                'n_jobs': Int,
                'variance_adjusted': Bool,
                'alpha': Float % Range(0, 1, inclusive_end=True),
                'bypass_tips': Bool},
    outputs=[('distance_matrix', DistanceMatrix % Properties('phylogenetic'))],
    input_descriptions={
        'table': ('The feature table containing the samples over which beta '
                  'diversity should be computed.'),
        'phylogeny': ('Phylogenetic tree containing tip identifiers that '
                      'correspond to the feature identifiers in the table. '
                      'This tree can contain tip ids that are not present in '
                      'the table, but all feature ids in the table must be '
                      'present in this tree.')
    },
    parameter_descriptions={
        'metric': 'The beta diversity metric to be computed.',
        'n_jobs': 'The number of workers to use.',
        'variance_adjusted': ('Perform variance adjustment based on Chang et '
                              'al. BMC Bioinformatics 2011. Weights distances '
                              'based on the proportion of the relative '
                              'abundance represented between the samples at a'
                              ' given node under evaluation.'),
        'alpha': ('This parameter is only used when the choice of metric is '
                  'generalized_unifrac. The value of alpha controls importance'
                  ' of sample proportions. 1.0 is weighted normalized UniFrac.'
                  ' 0.0 is close to unweighted UniFrac, but only if the sample'
                  ' proportions are dichotomized.'),
        'bypass_tips': ('In a bifurcating tree, the tips make up about 50% of '
                        'the nodes in a tree. By ignoring them, specificity '
                        'can be traded for reduced compute time. This has the'
                        ' effect of collapsing the phylogeny, and is analogous'
                        ' (in concept) to moving from 99% to 97% OTUs')
    },
    output_descriptions={'distance_matrix': 'The resulting distance matrix.'},
    name='Beta diversity (phylogenetic)',
    description=("Computes a user-specified phylogenetic beta diversity metric"
                 " for all pairs of samples in a feature table."),
    citations=[
        citations['lozupone2005unifrac'],
        citations['lozupone2007quantitative'],
        citations['chang2011variance'],
        citations['chen2012associating'],
        citations['mcdonald2018unifrac']]
)

plugin.methods.register_function(
    function=q2_diversity.beta,
    inputs={'table': FeatureTable[Frequency]},
    parameters={'metric': Str % Choices(beta.non_phylogenetic_metrics()),
                'pseudocount': Int % Range(1, None),
                'n_jobs': Int},
    outputs=[('distance_matrix', DistanceMatrix)],
    input_descriptions={
        'table': ('The feature table containing the samples over which beta '
                  'diversity should be computed.')
    },
    parameter_descriptions={
        'metric': 'The beta diversity metric to be computed.',
        'pseudocount': ('A pseudocount to handle zeros for compositional '
                        'metrics.  This is ignored for other metrics.'),
        'n_jobs': sklearn_n_jobs_description
    },
    output_descriptions={'distance_matrix': 'The resulting distance matrix.'},
    name='Beta diversity',
    description=("Computes a user-specified beta diversity metric for all "
                 "pairs of samples in a feature table."),
    citations=[
        citations['Faith1987']]
)

plugin.methods.register_function(
    function=q2_diversity.alpha_phylogenetic,
    inputs={'table': FeatureTable[Frequency],
            'phylogeny': Phylogeny[Rooted]},
    parameters={'metric': Str % Choices(alpha.phylogenetic_metrics())},
    outputs=[('alpha_diversity',
              SampleData[AlphaDiversity] % Properties('phylogenetic'))],
    input_descriptions={
        'table': ('The feature table containing the samples for which alpha '
                  'diversity should be computed.'),
        'phylogeny': ('Phylogenetic tree containing tip identifiers that '
                      'correspond to the feature identifiers in the table. '
                      'This tree can contain tip ids that are not present in '
                      'the table, but all feature ids in the table must be '
                      'present in this tree.')
    },
    parameter_descriptions={
        'metric': 'The alpha diversity metric to be computed.'
    },
    output_descriptions={
        'alpha_diversity': 'Vector containing per-sample alpha diversities.'
    },
    name='Alpha diversity (phylogenetic)',
    description=("Computes a user-specified phylogenetic alpha diversity "
                 "metric for all samples in a feature table."),
    citations=[
        citations['faith1992conservation']]
)

plugin.methods.register_function(
    function=q2_diversity.alpha,
    inputs={'table': FeatureTable[Frequency]},
    parameters={'metric': Str % Choices(alpha.non_phylogenetic_metrics())},
    outputs=[('alpha_diversity', SampleData[AlphaDiversity])],
    input_descriptions={
        'table': ('The feature table containing the samples for which alpha '
                  'diversity should be computed.')
    },
    parameter_descriptions={
        'metric': 'The alpha diversity metric to be computed.'
    },
    output_descriptions={
        'alpha_diversity': 'Vector containing per-sample alpha diversities.'
    },
    name='Alpha diversity',
    description=("Computes a user-specified alpha diversity metric for all "
                 "samples in a feature table.")
)

plugin.methods.register_function(
    function=q2_diversity.pcoa,
    inputs={'distance_matrix': DistanceMatrix},
    parameters={
        'number_of_dimensions': Int % Range(1, None)
    },
    outputs=[('pcoa', PCoAResults)],
    input_descriptions={
        'distance_matrix': ('The distance matrix on which PCoA should be '
                            'computed.')
    },
    parameter_descriptions={
        'number_of_dimensions': "Dimensions to reduce the distance matrix to. "
                                "This number determines how many "
                                "eigenvectors and eigenvalues are returned,"
                                "and influences the choice of algorithm used "
                                "to compute them. "
                                "By default, uses the default "
                                "eigendecomposition method, SciPy's eigh, "
                                "which computes all eigenvectors "
                                "and eigenvalues in an exact manner. For very "
                                "large matrices, this is expected to be slow. "
                                "If a value is specified for this parameter, "
                                "then the fast, heuristic "
                                "eigendecomposition algorithm fsvd "
                                "is used, which only computes and returns the "
                                "number of dimensions specified, but suffers "
                                "some degree of accuracy loss, the magnitude "
                                "of which varies across different datasets."
    },
    output_descriptions={'pcoa': 'The resulting PCoA matrix.'},
    name='Principal Coordinate Analysis',
    description=("Apply principal coordinate analysis."),
    citations=[citations['legendrelegendre'],
               citations['halko2010']]
)

plugin.methods.register_function(
    function=q2_diversity.pcoa_biplot,
    inputs={'pcoa': PCoAResults,
            'features': FeatureTable[RelativeFrequency]},
    parameters={},
    outputs=[('biplot', PCoAResults % Properties('biplot'))],
    input_descriptions={
        'pcoa': 'The PCoA where the features will be projected onto.',
        'features': 'Variables to project onto the PCoA matrix'
    },
    parameter_descriptions={},
    output_descriptions={'biplot': 'The resulting PCoA matrix.'},
    name='Principal Coordinate Analysis Biplot',
    description="Project features into a principal coordinates matrix. The "
                "features used should be the features used to compute the "
                "distance matrix. It is recommended that these variables be"
                " normalized in cases of dimensionally heterogeneous physical"
                " variables.",
    citations=[citations['legendrelegendre']]
)

plugin.methods.register_function(
    function=q2_diversity.procrustes_analysis,
    inputs={'reference': PCoAResults, 'other': PCoAResults},
    parameters={'dimensions': Int % Range(1, None)},
    outputs=[
        ('transformed_reference', PCoAResults),
        ('transformed_other', PCoAResults)
    ],
    input_descriptions={
        'reference': ('The ordination matrix to which data is fitted to.'),
        'other': ("The ordination matrix that's fitted to the reference "
                  "ordination.")
    },
    parameter_descriptions={},
    output_descriptions={
        'transformed_reference': 'A normalized version of the "reference" '
                                 'ordination matrix.',
        'transformed_other': 'A normalized and fitted version of the "other" '
                             'ordination matrix.'},
    name='Procrustes Analysis',
    description='Fit two ordination matrices with Procrustes analysis'
)

plugin.pipelines.register_function(
    function=q2_diversity.core_metrics_phylogenetic,
    inputs={
        'table': FeatureTable[Frequency],
        'phylogeny': Phylogeny[Rooted]
    },
    parameters={
        'sampling_depth': Int % Range(1, None),
        'metadata': Metadata,
        'n_jobs': Int % Range(0, None),
    },
    outputs=[
        ('rarefied_table', FeatureTable[Frequency]),
        ('faith_pd_vector', SampleData[AlphaDiversity]),
        ('observed_otus_vector', SampleData[AlphaDiversity]),
        ('shannon_vector', SampleData[AlphaDiversity]),
        ('evenness_vector', SampleData[AlphaDiversity]),
        ('unweighted_unifrac_distance_matrix', DistanceMatrix),
        ('weighted_unifrac_distance_matrix', DistanceMatrix),
        ('jaccard_distance_matrix', DistanceMatrix),
        ('bray_curtis_distance_matrix', DistanceMatrix),
        ('unweighted_unifrac_pcoa_results', PCoAResults),
        ('weighted_unifrac_pcoa_results', PCoAResults),
        ('jaccard_pcoa_results', PCoAResults),
        ('bray_curtis_pcoa_results', PCoAResults),
        ('unweighted_unifrac_emperor', Visualization),
        ('weighted_unifrac_emperor', Visualization),
        ('jaccard_emperor', Visualization),
        ('bray_curtis_emperor', Visualization),
    ],
    input_descriptions={
        'table': 'The feature table containing the samples over which '
                 'diversity metrics should be computed.',
        'phylogeny': 'Phylogenetic tree containing tip identifiers that '
                     'correspond to the feature identifiers in the table. '
                     'This tree can contain tip ids that are not present in '
                     'the table, but all feature ids in the table must be '
                     'present in this tree.'
    },
    parameter_descriptions={
        'sampling_depth': 'The total frequency that each sample should be '
                          'rarefied to prior to computing diversity metrics.',
        'metadata': 'The sample metadata to use in the emperor plots.',
        'n_jobs': '[beta/beta-phylogenetic methods only, excluding weighted_'
                  'unifrac] - %s' % sklearn_n_jobs_description
    },
    output_descriptions={
        'rarefied_table': 'The resulting rarefied feature table.',
        'faith_pd_vector': 'Vector of Faith PD values by sample.',
        'observed_otus_vector': 'Vector of Observed OTUs values by sample.',
        'shannon_vector': 'Vector of Shannon diversity values by sample.',
        'evenness_vector': 'Vector of Pielou\'s evenness values by sample.',
        'unweighted_unifrac_distance_matrix':
            'Matrix of unweighted UniFrac distances between pairs of samples.',
        'weighted_unifrac_distance_matrix':
            'Matrix of weighted UniFrac distances between pairs of samples.',
        'jaccard_distance_matrix':
            'Matrix of Jaccard distances between pairs of samples.',
        'bray_curtis_distance_matrix':
            'Matrix of Bray-Curtis distances between pairs of samples.',
        'unweighted_unifrac_pcoa_results':
            'PCoA matrix computed from unweighted UniFrac distances between '
            'samples.',
        'weighted_unifrac_pcoa_results':
            'PCoA matrix computed from weighted UniFrac distances between '
            'samples.',
        'jaccard_pcoa_results':
            'PCoA matrix computed from Jaccard distances between '
            'samples.',
        'bray_curtis_pcoa_results':
            'PCoA matrix computed from Bray-Curtis distances between '
            'samples.',
        'unweighted_unifrac_emperor':
            'Emperor plot of the PCoA matrix computed from unweighted'
            ' UniFrac.',
        'weighted_unifrac_emperor':
            'Emperor plot of the PCoA matrix computed from weighted UniFrac.',
        'jaccard_emperor':
            'Emperor plot of the PCoA matrix computed from Jaccard.',
        'bray_curtis_emperor':
            'Emperor plot of the PCoA matrix computed from Bray-Curtis.',
    },
    name='Core diversity metrics (phylogenetic and non-phylogenetic)',
    description="Applies a collection of diversity metrics (both "
                "phylogenetic and non-phylogenetic) to a feature table."
)

plugin.pipelines.register_function(
    function=q2_diversity.core_metrics,
    inputs={
        'table': FeatureTable[Frequency],
    },
    parameters={
        'sampling_depth': Int % Range(1, None),
        'metadata': Metadata,
        'n_jobs': Int % Range(0, None),
    },
    outputs=[
        ('rarefied_table', FeatureTable[Frequency]),
        ('observed_otus_vector', SampleData[AlphaDiversity]),
        ('shannon_vector', SampleData[AlphaDiversity]),
        ('evenness_vector', SampleData[AlphaDiversity]),
        ('jaccard_distance_matrix', DistanceMatrix),
        ('bray_curtis_distance_matrix', DistanceMatrix),
        ('jaccard_pcoa_results', PCoAResults),
        ('bray_curtis_pcoa_results', PCoAResults),
        ('jaccard_emperor', Visualization),
        ('bray_curtis_emperor', Visualization),
    ],
    input_descriptions={
        'table': 'The feature table containing the samples over which '
                 'diversity metrics should be computed.',
    },
    parameter_descriptions={
        'sampling_depth': 'The total frequency that each sample should be '
                          'rarefied to prior to computing diversity metrics.',
        'metadata': 'The sample metadata to use in the emperor plots.',
        'n_jobs': '[beta methods only] - %s' % sklearn_n_jobs_description
    },
    output_descriptions={
        'rarefied_table': 'The resulting rarefied feature table.',
        'observed_otus_vector': 'Vector of Observed OTUs values by sample.',
        'shannon_vector': 'Vector of Shannon diversity values by sample.',
        'evenness_vector': 'Vector of Pielou\'s evenness values by sample.',
        'jaccard_distance_matrix':
            'Matrix of Jaccard distances between pairs of samples.',
        'bray_curtis_distance_matrix':
            'Matrix of Bray-Curtis distances between pairs of samples.',
        'jaccard_pcoa_results':
            'PCoA matrix computed from Jaccard distances between samples.',
        'bray_curtis_pcoa_results':
            'PCoA matrix computed from Bray-Curtis distances between samples.',
        'jaccard_emperor':
            'Emperor plot of the PCoA matrix computed from Jaccard.',
        'bray_curtis_emperor':
            'Emperor plot of the PCoA matrix computed from Bray-Curtis.',
    },
    name='Core diversity metrics (non-phylogenetic)',
    description=("Applies a collection of diversity metrics "
                 "(non-phylogenetic) to a feature table.")
)

plugin.pipelines.register_function(
    function=q2_diversity.beta_correlation,
    inputs={'distance_matrix': DistanceMatrix},
    parameters={
        'metadata': MetadataColumn[Numeric],
        'method': Str % Choices(['spearman', 'pearson']),
        'permutations': Int % Range(0, None),
        'intersect_ids': Bool,
        'label1': Str,
        'label2': Str
    },
    outputs=[('metadata_distance_matrix', DistanceMatrix),
             ('mantel_scatter_visualization', Visualization)],
    input_descriptions={
        'distance_matrix': 'Matrix of distances between pairs of samples.'},
    parameter_descriptions={
        'metadata': 'Numeric metadata column from which to compute pairwise '
                    'Euclidean distances',
        'method': 'The correlation test to be applied in the Mantel test.',
        'permutations': 'The number of permutations to be run when computing '
                        'p-values. Supplying a value of zero will disable '
                        'permutation testing and p-values will not be '
                        'calculated (this results in *much* quicker execution '
                        'time if p-values are not desired).',
        'intersect_ids': 'If supplied, IDs that are not found in both '
                         'distance matrices will be discarded before applying '
                         'the Mantel test. Default behavior is to error on '
                         'any mismatched IDs.',
        'label1': 'Label for `distance_matrix` in the output visualization.',
        'label2': 'Label for `metadata_distance_matrix` in the output '
                  'visualization.'
    },
    output_descriptions={
        'metadata_distance_matrix': 'The Distance Matrix produced from the '
                                    'metadata column and used in the mantel '
                                    'test',
        'mantel_scatter_visualization': 'Scatter plot rendering of the mantel'
                                        'test results'},
    name='Beta diversity correlation',
    description=('Create a distance matrix from a numeric metadata column and '
                 'apply a two-sided Mantel test to identify correlation '
                 'between two distance matrices. Actions used internally: '
                 '`distance-matrix` from q2-metadata and `mantel` from '
                 'q2-diversity.')
)

plugin.methods.register_function(
    function=q2_diversity.filter_distance_matrix,
    inputs={
        'distance_matrix': DistanceMatrix
    },
    parameters={
        'metadata': Metadata,
        'where': Str,
        'exclude_ids': Bool
    },
    outputs=[
        ('filtered_distance_matrix', DistanceMatrix)
    ],
    name="Filter samples from a distance matrix.",
    description="Filter samples from a distance matrix, retaining only the "
                "samples matching search criteria specified by "
                "`metadata` and `where` parameters (or retaining only the "
                "samples not matching that criteria, if `exclude_ids` is "
                "True). See the filtering tutorial on "
                "https://docs.qiime2.org for additional details.",
    input_descriptions={
        'distance_matrix': 'Distance matrix to filter by sample.'
    },
    parameter_descriptions={
        'metadata': 'Sample metadata used with `where` parameter when '
                    'selecting samples to retain, or with `exclude_ids` '
                    'when selecting samples to discard.',
        'where': 'SQLite WHERE clause specifying sample metadata criteria '
                 'that must be met to be included in the filtered distance '
                 'matrix. If not provided, all samples in `metadata` that are '
                 'also in the input distance matrix will be retained.',
        'exclude_ids': 'If `True`, the samples selected by `metadata` or '
                       '`where` parameters will be excluded from the filtered '
                       'distance matrix instead of being retained.'
    },
    output_descriptions={
        'filtered_distance_matrix': 'Distance matrix filtered to include '
                                    'samples matching search criteria'
    }
)

plugin.visualizers.register_function(
    function=q2_diversity.alpha_group_significance,
    inputs={'alpha_diversity': SampleData[AlphaDiversity]},
    parameters={'metadata': Metadata},
    input_descriptions={
        'alpha_diversity': 'Vector of alpha diversity values by sample.'
    },
    parameter_descriptions={
        'metadata': 'The sample metadata.'
    },
    name='Alpha diversity comparisons',
    description=("Visually and statistically compare groups of alpha diversity"
                 " values."),
    citations=[citations['kruskal1952use']]
)

plugin.visualizers.register_function(
    function=q2_diversity.bioenv,
    inputs={'distance_matrix': DistanceMatrix},
    parameters={'metadata': Metadata},
    input_descriptions={
        'distance_matrix': 'Matrix of distances between pairs of samples.'
    },
    parameter_descriptions={
        'metadata': 'The sample metadata.'
    },
    name='bioenv',
    description=("Find the subsets of variables in metadata whose Euclidean "
                 "distances are maximally rank-correlated with distance "
                 "matrix. All numeric variables in metadata will be "
                 "considered, and samples which are missing data will be "
                 "dropped. The output visualization will indicate how many "
                 "samples were dropped due to missing data, if any were "
                 "dropped."),
    citations=[citations['clarke1993method']]
)

beta_group_significance_methods = \
    list(q2_diversity._beta._visualizer._beta_group_significance_fns)

plugin.visualizers.register_function(
    function=q2_diversity.beta_group_significance,
    inputs={'distance_matrix': DistanceMatrix},
    parameters={'method': Str % Choices(beta_group_significance_methods),
                'permutations': Int,
                'metadata': MetadataColumn[Categorical],
                'pairwise': Bool},
    input_descriptions={
        'distance_matrix': 'Matrix of distances between pairs of samples.'
    },
    parameter_descriptions={
        'method': 'The group significance test to be applied.',
        'permutations': ('The number of permutations to be run when computing '
                         'p-values.'),
        'metadata': 'Categorical sample metadata column.',
        'pairwise': ('Perform pairwise tests between all pairs of groups '
                     'in addition to the test across all groups. '
                     'This can be very slow if there are a lot of groups '
                     'in the metadata column.')
    },
    name='Beta diversity group significance',
    description=('Determine whether groups of samples are significantly '
                 'different from one another using a permutation-based '
                 'statistical test.'),
    citations=[citations['anderson2001new']]
)

plugin.visualizers.register_function(
    function=q2_diversity.mantel,
    inputs={'dm1': DistanceMatrix,
            'dm2': DistanceMatrix},
    parameters={'permutations': Int % Range(0, None),
                'method': Str % Choices(['spearman', 'pearson']),
                'intersect_ids': Bool,
                'label1': Str,
                'label2': Str},
    name='Apply the Mantel test to two distance matrices',
    description='Apply a two-sided Mantel test to identify correlation '
                'between two distance matrices.\n\nNote: the directionality '
                'of the comparison has no bearing on the results. Thus, '
                'comparing distance matrix X to distance matrix Y is '
                'equivalent to comparing Y to X.\n\nNote: the order of '
                'samples within the two distance matrices does not need to be '
                'the same; the distance matrices will be reordered before '
                'applying the Mantel test.\n\nSee the scikit-bio docs for '
                'more details about the Mantel test:\n\n'
                'http://scikit-bio.org/docs/latest/generated/generated/'
                'skbio.stats.distance.mantel.html',
    input_descriptions={
        'dm1': 'Matrix of distances between pairs of samples.',
        'dm2': 'Matrix of distances between pairs of samples.'
    },
    parameter_descriptions={
        'method': 'The correlation test to be applied in the Mantel test.',
        'permutations': 'The number of permutations to be run when computing '
                        'p-values. Supplying a value of zero will disable '
                        'permutation testing and p-values will not be '
                        'calculated (this results in *much* quicker execution '
                        'time if p-values are not desired).',
        'intersect_ids': 'If supplied, IDs that are not found in both '
                         'distance matrices will be discarded before applying '
                         'the Mantel test. Default behavior is to error on '
                         'any mismatched IDs.',
        'label1': 'Label for `dm1` in the output visualization.',
        'label2': 'Label for `dm2` in the output visualization.'
    },
    citations=[
        citations['mantel1967detection'],
        citations['pearson1895note'],
        citations['spearman1904proof']]
)

alpha_correlation_methods = \
    list(q2_diversity._alpha._visualizer._alpha_correlation_fns)

plugin.visualizers.register_function(
    function=q2_diversity.alpha_correlation,
    inputs={'alpha_diversity': SampleData[AlphaDiversity]},
    parameters={'method': Str % Choices(alpha_correlation_methods),
                'metadata': Metadata},
    input_descriptions={
        'alpha_diversity': 'Vector of alpha diversity values by sample.'
    },
    parameter_descriptions={
        'method': 'The correlation test to be applied.',
        'metadata': 'The sample metadata.'
    },
    name='Alpha diversity correlation',
    description=('Determine whether numeric sample metadata columns are '
                 'correlated with alpha diversity.'),
    citations=[citations['pearson1895note'], citations['spearman1904proof']]
)

_metric_set = Set[Str % Choices(alpha.alpha_rarefaction_supported_metrics)]
plugin.visualizers.register_function(
    function=q2_diversity.alpha_rarefaction,
    inputs={'table': FeatureTable[Frequency],
            'phylogeny': Phylogeny[Rooted]},
    parameters={'metrics': _metric_set,
                'metadata': Metadata,
                'min_depth': Int % Range(1, None),
                'max_depth': Int % Range(1, None),
                'steps': Int % Range(2, None),
                'iterations': Int % Range(1, None)},
    input_descriptions={
        'table': 'Feature table to compute rarefaction curves from.',
        'phylogeny': 'Optional phylogeny for phylogenetic metrics.',
    },
    parameter_descriptions={
        'metrics': ('The metrics to be measured. By default computes '
                    'observed_otus, shannon, and if phylogeny is '
                    'provided, faith_pd.'),
        'metadata': 'The sample metadata.',
        'min_depth': 'The minimum rarefaction depth.',
        'max_depth': ('The maximum rarefaction depth. '
                      'Must be greater than min_depth.'),
        'steps': ('The number of rarefaction depths to include '
                  'between min_depth and max_depth.'),
        'iterations': ('The number of rarefied feature tables to '
                       'compute at each step.'),
    },
    name='Alpha rarefaction curves',
    description=('Generate interactive alpha rarefaction curves by computing '
                 'rarefactions between `min_depth` and `max_depth`. The '
                 'number of intermediate depths to compute is controlled by '
                 'the `steps` parameter, with n `iterations` being computed '
                 'at each rarefaction depth. If sample metadata is provided, '
                 'samples may be grouped based on distinct values within a '
                 'metadata column.'),
)

_beta_rarefaction_color_schemes = [
    'BrBG', 'BrBG_r', 'PRGn', 'PRGn_r', 'PiYG', 'PiYG_r',
    'PuOr', 'PuOr_r', 'RdBu', 'RdBu_r', 'RdGy', 'RdGy_r',
    'RdYlBu', 'RdYlBu_r', 'RdYlGn', 'RdYlGn_r']

plugin.visualizers.register_function(
    function=q2_diversity._beta.beta_rarefaction,
    inputs={
        'table': FeatureTable[Frequency],
        'phylogeny': Phylogeny[Rooted]},
    parameters={
        'metric': Str % Choices(beta.all_metrics()),
        'clustering_method': Str % Choices({'nj', 'upgma'}),
        'metadata': Metadata,
        'sampling_depth': Int % Range(1, None),
        # Need at least two iterations to do a comparison.
        'iterations': Int % Range(2, None),
        'correlation_method': Str % Choices({'spearman', 'pearson'}),
        'color_scheme': Str % Choices(_beta_rarefaction_color_schemes)
    },
    input_descriptions={
        'table': 'Feature table upon which to perform beta diversity '
                 'rarefaction analyses.',
        'phylogeny': 'Phylogenetic tree containing tip identifiers that '
                     'correspond to the feature identifiers in the table. '
                     'This tree can contain tip ids that are not present in '
                     'the table, but all feature ids in the table must be '
                     'present in this tree. [required for phylogenetic '
                     'metrics]'
    },
    parameter_descriptions={
        'metric': 'The beta diversity metric to be computed.',
        'sampling_depth': 'The total frequency that each sample should be '
                          'rarefied to prior to computing the diversity '
                          'metric.',
        'clustering_method': 'Samples can be clustered with neighbor joining '
                             'or UPGMA. An arbitrary rarefaction trial will '
                             'be used for the tree, and the remaining trials '
                             'are used to calculate the support of the '
                             'internal nodes of that tree.',
        'metadata': 'The sample metadata used for the Emperor jackknifed PCoA '
                    'plot.',
        'iterations': 'Number of times to rarefy the feature table at a given '
                      'sampling depth.',
        'correlation_method': 'The Mantel correlation test to be applied when '
                              'computing correlation between beta diversity '
                              'distance matrices.',
        'color_scheme': 'The matplotlib color scheme to generate the heatmap '
                        'with.',
    },
    name='Beta diversity rarefaction',
    description='Repeatedly rarefy a feature table to compare beta diversity '
                'results within a given rarefaction depth.\n\n'
                'For a given beta diversity metric, this visualizer will '
                'provide: an Emperor jackknifed PCoA plot, samples clustered '
                'by UPGMA or neighbor joining with support calculation, and '
                'a heatmap showing the correlation between rarefaction trials '
                'of that beta diversity metric.',
    citations=[
        citations['mantel1967detection'],
        citations['pearson1895note'],
        citations['spearman1904proof']]
)

plugin.visualizers.register_function(
    function=q2_diversity.adonis,
    inputs={'distance_matrix': DistanceMatrix},
    parameters={'metadata': Metadata,
                'formula': Str,
                'permutations': Int % Range(1, None),
                'n_jobs': Int % Range(1, None)},
    input_descriptions={
        'distance_matrix': 'Matrix of distances between pairs of samples.'
    },
    parameter_descriptions={
        'metadata': 'Sample metadata containing formula terms.',
        'formula': 'Model formula containing only independent terms contained '
                   'in the sample metadata. These can be continuous variables '
                   'or factors, and they can have interactions as in a '
                   'typical R formula. E.g., the formula "treatment+block" '
                   'would test whether the input distance matrix partitions '
                   'based on "treatment" and "block" sample metadata. The '
                   'formula "treatment*block" would test both of those '
                   'effects as well as their interaction. Enclose formulae in '
                   'quotes to avoid unpleasant surprises.',
        'permutations': 'The number of permutations to be run when computing '
                        'p-values.',
        'n_jobs': 'Number of parallel processes to run.'
    },
    name='adonis PERMANOVA test for beta group significance',
    description=('Determine whether groups of samples are significantly '
                 'different from one another using the ADONIS permutation-'
                 'based statistical test in vegan-R. The function partitions '
                 'sums of squares of a multivariate data set, and is directly '
                 'analogous to MANOVA (multivariate analysis of variance). '
                 'This action differs from beta_group_signficance in that it '
                 'accepts R formulae to perform multi-way ADONIS tests; '
                 'beta_group_signficance only performs one-way tests. For '
                 'more details see http://cc.oulu.fi/~jarioksa/softhelp/vegan/'
                 'html/adonis.html'),
    citations=[citations['anderson2001new'], citations['Oksanen2018']]
)
