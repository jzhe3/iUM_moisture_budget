# Demonstration omni_conf.py file.
# Please replace all values.
from collections import OrderedDict as odict

settings = {
    'ignore_warnings': True,
}

computer_name = open('computer.txt').read().strip()
computers = {
    'nxnode': {
        'remote': 'rdf-comp',
        'remote_address': 'mmuetz@login.rdf.ac.uk',
        'remote_path': '/nerc/n02/n02/mmuetz/omnis/iUM_moisture_budget',
        'dirs': {
            'output': '/home/hb865130/omni_output/iUM_moisture_budget/output'
        }
    },
    'zerogravitas': {
        'remote': 'rdf-comp',
        'remote_address': 'mmuetz@login.rdf.ac.uk',
        'remote_path': '/nerc/n02/n02/mmuetz/omnis/iUM_moisture_budget',
        'dirs': {
            'output': '/home/markmuetz/omni_output/iUM_moisture_budget/output'
        }
    },
    'rdf-comp': {
        'dirs': {
            'output': '/nerc/n02/n02/mmuetz/omni_output/iUM_moisture_budget/output',
        }
    },
    'archer': {
        'dirs': {
            'output': '/home/n02/n02/mmuetz/nerc/omni_output/iUM_moisture_budget/output',
        }
    }
}

expts = ['MC_on', 'MC_off']
#expts = ['MC_on']
comp = computers['rdf-comp']
for expt in expts:
    comp['dirs']['work_' + expt] = '/nerc/n02/n02/mmuetz/um10.5_runs/20day/iUM_moisture_budget_{}/work'.format(expt)
    comp['dirs']['results_' + expt] = '/nerc/n02/n02/mmuetz/omni_output/iUM_moisture_budget/results_{}'.format(expt)

comp = computers['archer']
for expt in expts:
    comp['dirs']['work_' + expt] = '/home/n02/n02/mmuetz/nerc/um10.5_runs/20day/iUM_moisture_budget_{}/work'.format(expt)
    comp['dirs']['results_' + expt] = '/home/n02/n02/mmuetz/nerc/omni_output/iUM_moisture_budget/results_{}'.format(expt)

comp = computers['nxnode']
for expt in expts:
    comp['dirs']['work_' + expt] = '/home/hb865130/omni_output/iUM_moisture_budget/work_{}'.format(expt)
    comp['dirs']['results_' + expt] = '/home/hb865130/omni_output/iUM_moisture_budget/results_{}'.format(expt)

comp = computers['zerogravitas']
for expt in expts:
    comp['dirs']['work_' + expt] = '/home/markmuetz/omni_output/iUM_moisture_budget/work_{}'.format(expt)
    comp['dirs']['results_' + expt] = '/home/markmuetz/omni_output/iUM_moisture_budget/results_{}'.format(expt)


batches = odict(('batch{}'.format(i), {'index': i}) for i in range(6))
groups = odict()
ngroups = odict()
nodes = odict()
nnodes = odict()

for expt in expts:
    for i in range(1, 4):
	groups['pp{}_{}'.format(i, expt)] = {
		'type': 'init',
		'base_dir': 'work_' + expt,
		'batch': 'batch0',
		'filename_glob': '2000??????????/atmos/atmos.???.pp{}'.format(i),
		}

	groups['nc{}_{}'.format(i, expt)] = {
	    'type': 'group_process',
	    'from_group': 'pp{}_{}'.format(i, expt),
	    'base_dir': 'results_' + expt,
	    'batch': 'batch1',
	    'process': 'convert_pp_to_nc',
	}

    for i in range(4, 7):
	groups['pp{}_{}'.format(i, expt)] = {
		'type': 'init',
		'base_dir': 'work_' + expt,
		'batch': 'batch0',
		'filename_glob': '2000??????????/atmos/atmos.pp{}'.format(i),
		}

	groups['nc{}_{}'.format(i, expt)] = {
	    'type': 'group_process',
	    'from_group': 'pp{}_{}'.format(i, expt),
	    'base_dir': 'results_' + expt,
	    'batch': 'batch1',
	    'process': 'convert_pp_to_nc',
	}

    base_vars = ['q_incr_ls_rain', 'q_incr_bl_plus_cloud', 'q_incr_adv', 'q_incr_total',
	         'q']
    base_nodes = [bv + '_profile' for bv in base_vars]

    groups['profiles_' + expt] = {
        'type': 'nodes_process',
        'base_dir': 'results_' + expt,
        'batch': 'batch2',
        'nodes': [bn + '_' + expt for bn in base_nodes],
    }

    groups['profile_plots_' + expt] = {
        'type': 'nodes_process',
        'base_dir': 'output',
        'batch': 'batch3',
        'nodes': ['moist_profile_plots_' + expt],
    }

    for bn, bv in zip(base_nodes, base_vars):
	nodes[bn + '_' + expt] = {
	    'type': 'from_group',
	    'from_group': 'nc3_' + expt,
	    'variable': bv,
	    'process': 'domain_mean',
	}

    nodes['moist_profile_plots_' + expt] = {
        'type': 'from_nodes',
        'from_nodes': [bn + '_' + expt for bn in base_nodes],
        'process': 'plot_moist_profile',
	'process_kwargs': {'start_index': -24, 'end_index':None},
    }

    surf_base_nodes = ['precip_ts', 'shf_ts', 'lhf_ts', 'precip_conv_ts']
    surf_base_vars = ['precip', 'shf', 'lhf']

    groups['surf_timeseries_' + expt] = {
        'type': 'nodes_process',
        'base_dir': 'results_' + expt,
        'batch': 'batch4',
        'nodes': [bn + '_' + expt for bn in surf_base_nodes],
    }

    groups['surf_ts_plots_' + expt] = {
        'type': 'nodes_process',
        'base_dir': 'output',
        'batch': 'batch5',
        'nodes': ['surf_ts_plots_' + expt],
    }

    groups['surf_ts_means_' + expt] = {
        'type': 'nodes_process',
        'base_dir': 'output',
        'batch': 'batch5',
        'nodes': ['surf_ts_means_' + expt],
    }

    for bn, bv in zip(surf_base_nodes, surf_base_vars):
	nodes[bn + '_' + expt] = {
	    'type': 'from_group',
	    'from_group': 'nc1_' + expt,
	    'variable': bv,
	    'process': 'domain_mean',
	}

    nodes['precip_conv_ts_' + expt] = {
        'type': 'from_nodes',
        'from_nodes': ['precip_ts_' + expt],
        'process': 'convert_mass_to_energy_flux',
    }
    nodes['surf_ts_plots_' + expt] = {
        'type': 'from_nodes',
        'from_nodes': ['precip_conv_ts_' + expt, 'shf_ts_' + expt, 'lhf_ts_' + expt],
        'process': 'plot_sensitivity_surf_timeseries',
    }
    nodes['surf_ts_means_' + expt] = {
        'type': 'from_nodes',
        'from_nodes': ['precip_conv_ts_' + expt, 'shf_ts_' + expt, 'lhf_ts_' + expt],
        'process': 'last_five_day_mean',
    }

variables = {
    'q': {
	'section': 0,
	'item': 10,
    },
    'q_incr_ls_rain': {
	'section': 4,
	'item': 182,
    },
    'q_incr_bl_plus_cloud': {
	'section': 9,
	'item': 182,
    },
    'q_incr_adv': {
	'section': 12,
	'item': 182,
    },
    'q_incr_total': {
	'section': 30,
	'item': 182,
    },
    'precip': {
        'section': 4,
        'item': 203,
    },
    'shf': {
        'section': 3,
        'item': 217,
    },
    'lhf': {
        'section': 3,
        'item': 234,
    },
}
    
process_options = {
}
