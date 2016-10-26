from collections import OrderedDict as odict
import importlib

from omnium.processes import Process

class LastFiveDayMean(Process):
    name = 'last_five_day_mean'
    out_ext = 'txt'

    def load_modules(self):
        self.iris = importlib.import_module('iris')

    def load_upstream(self):
        super(LastFiveDayMean, self).load_upstream()
        filenames = [n.filename(self.config) for n in self.node.from_nodes]
        all_timeseries = self.iris.load(filenames)
        self.data = all_timeseries
        return all_timeseries

    def run(self):
        super(LastFiveDayMean, self).run()
        all_timeseries = self.data
        self.processed_data = []
        for timeseries in all_timeseries:
            if self.node.name == 'surf_ts_means_large_dom':
                five_days = -144*5*3  # 20s ts. output every 10ts
            else:
                five_days = -144*5  # output every 10 min.

            time_in_hours = timeseries.coord('time').points[-1]\
                            - timeseries.coord('time').points[five_days]
            value = timeseries[five_days:]\
                    .collapsed('time', self.iris.analysis.MEAN)
            # print(timeseries.name(), value.data)
            self.processed_data.append('{},{},{},{}'.format(timeseries.name(),
                                                            time_in_hours,
                                                            value.data,
                                                            timeseries.units))

    def save(self):
        super(LastFiveDayMean, self).save()
        with open(self.node.filename(self.config), 'w') as f:
            f.write('\n'.join(self.processed_data))
