import os
from collections import OrderedDict as odict
import importlib

from omnium.processes import Process

ordered_filenames = [
('surf_ts_means_2day_moist_profile_moist_cons.txt', 'MC on'),
('surf_ts_means_60s.txt', 'MC off, \\SI{60}{s}'),
('surf_ts_means_30s.txt', 'MC off, \\SI{30}{s}$^*$'),
('surf_ts_means_15s.txt', 'MC off, \\SI{15}{s}$^{**}$'),
('surf_ts_means_no_graupel.txt', 'MC off, no graupel$^*$'),
('surf_ts_means_large_dom.txt', 'MC off, \SI{256}{}x\SI{256}{km^2}'),
]

class LatexFluxTable(Process):
    name = 'latex_flux_table'
    out_ext = 'tex'

    def load_upstream(self):
        super(LatexFluxTable, self).load_upstream()
        filenames = [n.filename(self.config) for n in self.node.from_nodes]
        self.data = {}
        for filename in filenames:
            with open(filename, 'r') as f:
                lines = f.readlines()
            self.data[os.path.basename(filename)] = lines

        return self.data

    def run(self):
        super(LatexFluxTable, self).run()
        # Trying to repro something like this:
        # In tex doc:

        # \begin{center}
        # \begin{tabular}{ c|c c c }
        # & on & off, \SI{60}{s} & \\
        # \hline
        # PFE & cell5 & cell6 \\
        # LHF & cell8 & cell9 \\
        # SHF & cell8 & cell9 \\
        # \end{tabular}

        # In tex doc:
        # \end{center}

        latex_lines = []
        # Doesn't work:
        # latex_lines.append('\\begin{tabular}{c|' + 'S[table-format=3.2] '*len(self.data) + '}')
        latex_lines.append('\\begin{tabular}{c|' + 'r '*len(self.data) + '}')
        header = ' '
        for filename, headername in ordered_filenames:
            header += '&' + headername
        header += '\\\\'
        latex_lines.append(header)
        latex_lines.append('\\hline')

        vals = [[], [], []]
        for filename, headername in ordered_filenames:
            lines = self.data[filename]
            for valrow, line in zip(vals, lines):
                val = float(line.split(',')[2].strip())
                valrow.append('{0:.1f}'.format(val))

        valnames = ['PFE', 'LHF', 'SHF']
        for valname, valrow in zip(valnames, vals):
            row = valname + ' '
            for val in valrow:
                row += '& ' + val + ' '
            row += '\\\\'
            latex_lines.append(row)
        latex_lines.append('\\end{tabular}')
        self.processed_data = latex_lines

    def save(self):
        super(LatexFluxTable, self).save()
        with open(self.node.filename(self.config), 'w') as f:
            f.write('\n'.join(self.processed_data))
