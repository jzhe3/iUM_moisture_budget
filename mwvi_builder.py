"""Simple script to build nodes in a way that is not currently allowed by omnium

Important part is that build_mwvi_nodes builds nodes that depend on 2 groups"""
import omnium as om


class CustomBuilder(object):
    def __init__(self):
        self.config, self.process_classes, self.dag, self.proc_eng, self.stash = om.init()
        self.expts = ['MC_on', 'MC_off']

    def build_mwvi_nodes(self):
        print('mwvi')
        for expt in self.expts:
            print(' ' + expt)
            out_g = self.dag.get_group('surf_timeseries_{}'.format(expt))

            g2 = self.dag.get_group('nc2_{}'.format(expt))
            g3 = self.dag.get_group('nc3_{}'.format(expt))

            for qvar in ['q', 'qcl', 'qcf', 'qrain', 'qgraup']:
                print('  ' + qvar)
                sec, item = self.config['variables'][qvar]['section'], self.config['variables'][qvar]['item']

                if self.dag.get_node('mwvi_{}.nc'.format(qvar), group_name=out_g.name):
                    continue

                node = self.dag._create_node('mwvi_{}.nc'.format(qvar), out_g, 
                                        process_name='modified_mass_weighted_vertical_integral',
                                        section=sec, item=item)
                node.from_nodes.extend(g2.nodes)
                node.from_nodes.extend(g3.nodes)
                self.dag.commit()
        self.dag.verify_status(True)

    def build_surf_ts_nodes(self):
        print('surf_ts')
        for expt in self.expts:
            print(' ' + expt)
            out_g = self.dag.get_group('surf_timeseries_{}'.format(expt))

            for qvar in ['q', 'qcl', 'qcf', 'qrain', 'qgraup']:
                print('  ' + qvar)
                sec, item = self.config['variables'][qvar]['section'], self.config['variables'][qvar]['item']

                from_node = self.dag.get_node('mwvi_{}.nc'.format(qvar), 
                                              group_name=out_g.name)
                if self.dag.get_node('dom_mean_mwvi_{}.nc'.format(qvar), 
                                     group_name=out_g.name):
                    continue

                new_node = self.dag._create_node('dom_mean_mwvi_{}.nc'.format(qvar), out_g, 
                                            process_name='domain_mean',
                                            section=sec, item=item)

                print(new_node)
                new_node.from_nodes.append(from_node)
                self.dag.commit()

            self.dag.verify_status(True)

    def build_plot_qvar_nodes(self):
        print('plot_qvar')
        for expt in self.expts:
            print(' ' + expt)
            in_g = self.dag.get_group('surf_timeseries_{}'.format(expt))
            out_g = self.dag.get_group('surf_ts_plots_{}'.format(expt))

            if self.dag.get_node('qvar_plots_{}.png'.format(expt), group_name=out_g.name):
                continue
            qvar_plots = self.dag._create_node('qvar_plots_{}.png'.format(expt), out_g,
                                               process_name='plot_qvars')

            for qvar in ['q', 'qcl', 'qcf', 'qrain', 'qgraup']:
                print('  ' + qvar)
                sec, item = self.config['variables'][qvar]['section'], self.config['variables'][qvar]['item']

                from_node = self.dag.get_node('dom_mean_mwvi_{}.nc'.format(qvar), 
                                              group_name=in_g.name)
                qvar_plots.from_nodes.append(from_node)
            self.dag.commit()
        self.dag.verify_status(True)


if __name__ == '__main__':
    cb = CustomBuilder()
    cb.build_mwvi_nodes()
    cb.build_surf_ts_nodes()
    cb.build_plot_qvar_nodes()
