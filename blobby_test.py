import sys

import pylab as plt
import iris

import omnium as om
import omnium.experimental.blobby


def get_cube(self, section, item):
    for cube in self:
        STASH = cube.attributes['STASH']
        if STASH.section == section and STASH.item == item:
            return cube
    return None

iris.cube.CubeList.get_cube = get_cube


def load_data():
    config = om.ConfigChecker.load_config()
    pcs = om.get_process_classes()
    dag = om.NodeDAG(config, pcs)
    pe = om.ProcessEngine(False, config, pcs, dag)
    stash = om.Stash()

    node = om.models.Node(name='Mqrain')
    proc = pcs['mass_weighted_vertical_integral'](config, node)
    proc.load_modules()
    atmos4ncs = dag.get_nodes('atmos.4.nc')

    Mqrains = []
    atmos4s = []
    for atmos4nc in atmos4ncs:
        cubes = pe.load(atmos4nc)
        atmos4s.append(cubes)
        stash.rename_unknown_cubes(cubes, True)
        rho_R2 = cubes.get_cube(0, 253)
        rain = cubes.get_cube(0, 272)
        proc.data = [(rho_R2, rain)]
        Mqrain = proc.run()
        Mqrains.append(Mqrain)

    atmos5ncs = dag.get_nodes('atmos.5.nc')
    atmos5s = []
    for atmos5nc in atmos5ncs:
        cubes = pe.load(atmos5nc)
        atmos5s.append(cubes)
        stash.rename_unknown_cubes(cubes, True)

    atmos6ncs = dag.get_nodes('atmos.6.nc')
    atmos6s = []
    for atmos6nc in atmos6ncs:
        cubes = pe.load(atmos6nc)
        atmos6s.append(cubes)
        stash.rename_unknown_cubes(cubes, True)

    return Mqrains, atmos4s, atmos5s, atmos6s


def tracked_profiles(Mqrains, atmos4s, atmos5s, atmos6s, ts0, ba0, ts1, ba1):
    all_qvars = []
    itrs = []
    for Mqrain, atmos4, atmos5, atmos6, ts, ba, start_coord in zip(Mqrains, atmos4s, atmos5s, atmos6s,
                                                                   [ts0, ts1], 
                                                                   [ba0, ba1],
                                                                   [(0, 6), (0, 2)]):
        sb = ts[start_coord[0]][start_coord[1]]
        print(sb)
        q = atmos4.get_cube(0, 10)
        qrain = atmos4.get_cube(0, 272)
        qcl = atmos4.get_cube(0, 254)
        qgraup = atmos4.get_cube(0, 273)
        qcf = atmos4.get_cube(0, 12)

        dq = atmos6.get_cube(30, 182)
        dqcl = atmos6.get_cube(30, 183)
        dqcf = atmos6.get_cube(30, 184)

        # I messed up and didn't add GRAUPEL TOTAL INC to stash.
        # Fortunately you can calc it from ls_rain/adv graupel incs:
        dqgraup_ls_rain = atmos5.get_cube(4, 190)
        dqgraup_adv = atmos6.get_cube(12, 190)
        dqgraup = dqgraup_ls_rain + dqgraup_adv
        dqgraup.rename('Graupel total inc (calcd)')
        
        # calc rain same way as this seems to be 0:
        # dqrain = atmos6.get_cube(30, 189)
        dqrain_ls_rain = atmos5.get_cube(4, 189)
        dqrain_adv = atmos6.get_cube(12, 189)
        dqrain = dqrain_ls_rain + dqrain_adv
        dqrain.rename('Graupel total inc (calcd)')


        qvars = [('q', q), 
                 ('qrain', qrain), 
                 ('qcl', qcl), 
                 ('qcf', qcf),
                 ('qgraup', qgraup)]
        dqvars = [('dq', dq), 
                  ('dqrain', dqrain), 
                  ('dqcl', dqcl), 
                  ('dqcf', dqcf),
                  ('dqgraup', dqgraup)]
        itr = om.experimental.blobby.get_max_val(sb, ba, Mqrain)
        all_qvars.append(qvars)
        itrs.append(itr)

    while True:
        for title, qvars, itr in zip(['MC_on', 'MC_off'], all_qvars, itrs):
            if title == 'MC_on':
                continue
            b, cmax = itr.next()
            print(title)
            plt.figure(title)
            plt.clf()
            for qvarname, qvar in qvars:
                plt.plot(qvar[b.time_index, :, cmax[0], cmax[1]].data,
                         qvar.coord('level_height').points, label=qvarname)
            plt.xlim((0, 0.016))
            plt.ylim((0, 18000))
            plt.title('{}: {}'.format(title, b.time_index))
            plt.legend()
            plt.pause(0.1)

            plt.figure('incrs ' + title)
            plt.clf()
            for dqvarname, dqvar in dqvars:
                plt.plot(dqvar[b.time_index, :, cmax[0], cmax[1]].data,
                         dqvar.coord('level_height').points, label=dqvarname)
            plt.title('{}: {}'.format(title, b.time_index))
            plt.ylim((0, 18000))
            plt.xlim((-0.002, 0.002))
            plt.legend()
            plt.pause(0.1)
        #raw_input()
            

if __name__ == '__main__':
    thresh = float(sys.argv[1])
    Mqrains, atmos4s, atmos5s, atmos6s = load_data()
    ts0, ba0 = om.experimental.blobby.create_blob_timeseries(Mqrains[0], thresh)
    # om.experimental.blobby.render_graph(ts0, 'MC_on.png')
    ts1, ba1 = om.experimental.blobby.create_blob_timeseries(Mqrains[1], thresh)
    # om.experimental.blobby.render_graph(ts1, 'MC_off.png')
    # om.experimental.blobby.plot(Mqrains, thresh)
    tracked_profiles(Mqrains, atmos4s, atmos5s, atmos6s, ts0, ba0, ts1, ba1)

