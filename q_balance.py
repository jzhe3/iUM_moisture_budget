# coding: utf-8
import omnium as om
a3n = dag.get_nodes('atmos.096.3.nc')
a3n
a3ns = dag.get_nodes('atmos.096.3.nc')
a3n0 = a3ns[0]
a30 = proc_eng.load(a3n0)
a30
stash.rename_unknown_cubes(a30, True)
a30
[(i, c.name()) for i, c in enumerate(a30)]
q = a30[17]
q
dq = q[1] - q[0]
dq
q_inc = a30[23]
q_inc
q_inc[0]
q_inc[0].data
q_inc[0].data.shape
q_inc[0][0]
q_inc[0][0].data
(dq[0].data == dq[1].data).all()
dq[1]
dq[1].data
dq[1][0].data
dq.shape
dq[1].shape
q_inc[0][0].shape
dq[1].data
import pylab as plt

q_inc[1][0] * 60
q_inc[1][0].data * 60
dq[1].data
import numpy as np
np.allclose(dq[1].data, q_inc[1][0].data * 60)
[(i, c.name()) for i, c in enumerate(a30)]
qrain = a30[10]
dqrain = qrain[1] - qrain[0]
qrain_inc = a30[8]
np.allclose(dqrain[1].data, qrain_inc[1][0].data * 60)
qgraup = a30[11]
dqgraup = qgraup[1] - qgraup[0]
qgraup_inc = a30[9]
np.allclose(dqgraup[1].data, qgraup_inc[1][0].data * 60)
qcf = a30[16]
dqcf = qcf[1] - qcf[0]
qcf_inc = a30[19]
np.allclose(dqgraup[1].data, qcf_inc[1][0].data * 60)
np.allclose(dqgraup[1].data, qcf_inc[2][0].data * 60)
qcf_inc
qcf_inc.data
