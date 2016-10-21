from collections import OrderedDict as odict
import importlib

from omnium.processes import PylabProcess

OPTS = odict([(12, {182: {'l': 'Adv.', 'fmt': 'r-'}}),
             (9, {182: {'l': 'BL+cloud', 'fmt': 'r--'}}),
             (4, {182: {'l': 'LS rain', 'fmt': 'b-.'}}),
             (30, {182: {'l': 'Total', 'fmt': 'k-'}})])


class PlotMoistProfile(PylabProcess):
    name = 'plot_moist_profile'
    out_ext = 'png'

    def load_upstream(self):
        super(PlotMoistProfile, self).load_upstream()
        filenames = [n.filename(self.config) for n in self.node.from_nodes]
        profiles = self.iris.load(filenames)
        self.data = profiles

    def run(self, start_index=-1, end_index=None):
        super(PlotMoistProfile, self).run()
	s = slice(start_index, end_index)

        profiles = self.data

        fig = self.plt.figure()

        if self.node.name == 'moist_profile_plots_MC_on':
            name = 'MC on'
        elif self.node.name == 'moist_profile_plots_MC_off':
            name = 'MC off'
        title = 'q increments ({})'.format(name)

        fig.canvas.set_window_title(title)

        self.plt.title(title)

        ordered_opts_profiles = []
        for k, v in OPTS.items():
            for profile in profiles:
                section = profile.attributes['STASH'].section
                item = profile.attributes['STASH'].item
                if k == section and item in v:
                    opt = v[item]
                    ordered_opts_profiles.append((opt, profile))
                    break
        
        # Sum first 3 profiles (corresponds to q incs from adv, BL+cloud, LS rain). 
        sum_profile = ordered_opts_profiles[0][1].copy()
        sum_profile.rename('sum_of_q_incrs')
        for opt, profile in ordered_opts_profiles[1:3]:
            sum_profile.data += profile.data
        sum_opt = {'l': 'Sum of incrs', 'fmt': 'k--'}
        ordered_opts_profiles.append((sum_opt, sum_profile))

        for opt, profile in ordered_opts_profiles:
	    avg_profile = profile[s].collapsed(['time'], self.iris.analysis.MEAN)
            # profile data is in kg/kg/dt, 1440 turns into /day, 1000 turns into g/kg/day.
            # height is in m, /1000 turns into km.
            label = opt['l']
            fmt = opt['fmt']
            self.plt.plot(avg_profile.data * 1440 * 1000, 
                     avg_profile.coord('level_height').points / 1000,
                     fmt,
                     label=label)

        self.plt.xlim((-10, 10))
        self.plt.xlabel('(g kg$^{-1}$ day$^{-1}$)')
        self.plt.ylabel('Height (km)')

        self.plt.legend(loc=2)
        self.processed_data = fig
