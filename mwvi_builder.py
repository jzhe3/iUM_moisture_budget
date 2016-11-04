import omnium as om
import iris


def get_cube(cubes, section, item):
    for cube in cubes:
        STASH = cube.attributes['STASH']
        if STASH.section == section and STASH.item == item:
            return cube
    return None


def cube_iter(config, g2, g3, section, item):
    for n2, n3 in zip(g2.nodes, g3.nodes):
	print((n2, n3))
	cbs2 = iris.load(n2.filename(config))
	cbs3 = iris.load(n3.filename(config))
	rho_R2 = get_cube(cbs2, 0, 253)
	cube = get_cube(cbs3, section, item)
	yield rho_R2, cube


def main1():
    config, process_classes, dag, proc_eng, stash = om.init()
    MWVI = process_classes['mass_weighted_vertical_integral']

    expts = ['MC_on', 'MC_off']
    for expt in expts:
	out_g = dag.get_group('surf_timeseries_{}'.format(expt))

	g2 = dag.get_group('nc2_{}'.format(expt))
	g3 = dag.get_group('nc3_{}'.format(expt))

	for qvar in ['q', 'qcl', 'qcf', 'qrain', 'qgraup']:
	    print(qvar)
	    sec, item = config['variables'][qvar]['section'], config['variables'][qvar]['item']

	    node = dag._create_node('mwvi_{}.nc'.format(qvar), out_g, section=sec, item=item)
	    # N.B. not used, but done for completeness.
	    node.from_nodes.extend(g2.nodes)
	    node.from_nodes.extend(g3.nodes)
	    dag.commit()

	    mwvi = MWVI(config, node)
	    mwvi.load_modules()
	    mwvi.data = cube_iter(config, g2, g3, sec, item)
	    mwvi.run()
	    mwvi.save()
	    mwvi.done()
	    dag.verify_status(True)

def main2():
    config, process_classes, dag, proc_eng, stash = om.init()
    DomMean = process_classes['domain_mean']

    expts = ['MC_on', 'MC_off']
    for expt in expts:
	out_g = dag.get_group('surf_timeseries_{}'.format(expt))

	for qvar in ['q', 'qcl', 'qcf', 'qrain', 'qgraup']:
	    print(qvar)
	    sec, item = config['variables'][qvar]['section'], config['variables'][qvar]['item']

	    from_node = None
	    for node in out_g.nodes:
		if node.name == 'mwvi_{}.nc'.format(qvar):
		    from_node = node
		    print('Found')
		    break

	    new_node = dag._create_node('dom_mean_mwvi_{}.nc'.format(qvar), out_g, section=sec, item=item)
	    print(new_node)
	    new_node.from_nodes.append(from_node)
	    dag.commit()

	    dm = DomMean(config, new_node)
	    dm.load_modules()
	    dm.load_upstream()
	    dm.run()
	    dm.save()
	    dm.done()
	dag.verify_status(True)

def main3():
    config, process_classes, dag, proc_eng, stash = om.init()
    PlotQvars = process_classes['plot_qvars']

    expts = ['MC_on', 'MC_off']
    for expt in expts:
	in_g = dag.get_group('surf_timeseries_{}'.format(expt))
	out_g = dag.get_group('surf_ts_plots_{}'.format(expt))

	qvar_plots = dag._create_node('qvar_plots_{}.png'.format(expt), out_g)
	for qvar in ['q', 'qcl', 'qcf', 'qrain', 'qgraup']:
	    print(qvar)
	    sec, item = config['variables'][qvar]['section'], config['variables'][qvar]['item']

	    from_node = None
	    for node in in_g.nodes:
		if node.name == 'dom_mean_mwvi_{}.nc'.format(qvar):
		    from_node = node
		    print('Found')
		    break

	    print(qvar_plots)
	    qvar_plots.from_nodes.append(from_node)
	dag.commit()

	pq = PlotQvars(config, qvar_plots)
	pq.load_modules()
	pq.load_upstream()
	pq.run()
	pq.save()
	pq.done()
	dag.verify_status(True)

if __name__ == '__main__':
    #main1()
    #main2()
    main3()
