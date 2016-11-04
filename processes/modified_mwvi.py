import omnium


def get_cube(cubes, section, item):
    for cube in cubes:
        STASH = cube.attributes['STASH']
        if STASH.section == section and STASH.item == item:
            return cube
    return None


class ModifiedMassWeightedVerticalIntegral(omnium.processes.MassWeightedVerticalIntegral):
    "Modified to load data for rho, other var from different cubes"
    name = 'modified_mass_weighted_vertical_integral'

    def load_upstream(self):
        super(omnium.processes.IrisProcess, self).load_upstream() 
        section, item = self.node.section, self.node.item

        def cube_iter():
            half_len = len(self.node.from_nodes)/2
            for n2, n3 in zip(self.node.from_nodes[:half_len], self.node.from_nodes[half_len:]):
                print((n2, n3))
                cbs2 = self.iris.load(n2.filename(self.config))
                cbs3 = self.iris.load(n3.filename(self.config))
                rho_R2 = get_cube(cbs2, 0, 253)
                cube = get_cube(cbs3, section, item)
                yield rho_R2, cube

        self.data = cube_iter()

