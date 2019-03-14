"""
Class for processing data including: interpolating for even sampling,
calculating average and confidence intervals, scaling data, filtering data, and
comparing to an ideal trajectory

Process for comparing to ideal trajectory
1. interpolate data for even sampling
2. generate ideal trajectory with the same sampling
3. calculate error from recorded path to ideal
4. filter data if desired (recommended for 2nd and 3rd order error)
5. scale to a baseline if desired
"""
import numpy as np
import os
import scipy.interpolate

from abr_analyze.utils.paths import cache_dir
from abr_analyze.utils import DataHandler
from abr_control.controllers import path_planners

class DataProcessor():
    def __init__(self):
        """
        """
        pass

    def get_mean_and_ci(self, raw_data):
        '''
        gets the mean and 95% confidence intervals of data *see Note

        NOTE: data has to be grouped along rows, for example: having 5 sets of
        100 data points would be a list of shape (5,100)
        '''
        sample = []
        upper_bound = []
        lower_bound = []
        sets = np.array(raw_data).shape[0]
        data_pts = np.array(raw_data).shape[1]
        print('Mean and CI calculation found %i sets of %i data points'
                %(sets, data_pts))
        raw_data = np.array(raw_data)
        for i in range(data_pts):
            data = raw_data[:,i]
            ci = self.bootstrapci(data, np.mean)
            sample.append(np.mean(data))
            lower_bound.append(ci[0])
            upper_bound.append(ci[1])

        data = {'mean': sample, 'lower_bound': lower_bound, 'upper_bound':
                upper_bound}
        return data

    def bootstrapci(self, data, func, n=3000, p=0.95):
        index=int(n*(1-p)/2)
        samples = np.random.choice(data, size=(n, len(data)))
        r = [func(s) for s in samples]
        r.sort()
        return r[index], r[-index]

    def list_to_function(self, data, time_intervals):
        time_intervals = np.cumsum(time_intervals)
        functions = []
        for kk in range(data.shape[1]):
            interp = scipy.interpolate.interp1d(time_intervals, data[:, kk])
            functions.append(interp)

        return functions

    def interpolate_data(self, data, time_intervals, n_points):
        run_time = sum(time_intervals)
        time_intervals = np.cumsum(time_intervals)
        dt = (run_time-time_intervals[0])/n_points
        # interpolate to even samples out
        data_interp = []
        for kk in range(data.shape[1]):
            interp = scipy.interpolate.interp1d(time_intervals, data[:, kk])
            data_interp.append(np.array([
                interp(t) for t in np.arange(time_intervals[0], run_time, dt)]))
        data_interp = np.array(data_interp).T

        return data_interp

    def scale_data(self, input_data, baseline_low, baseline_high, scaling_factor=1):
        """
        scale data to some baseline to get values from 0-1 relative
        to baseline times the scaling factor

        PARAMETERS
        input_data: list of floats
            the data to be scaled
        baseline_low: list of floats
            the lower error baseline that will be the zero
            reference
        baseline_high: list of floats
            the higher error baseline that will be the one
            reference
        """
        #TODO: add check for whether or not to np.array -ize
        input_data = np.array(input_data)
        baseline_low = np.array(baseline_low)
        baseline_high = np.array(baseline_high)
        scaled_data = ((input_data - baseline_low)
                       / (baseline_high - baseline_low))
        scaled_data *= scaling_factor

        return scaled_data

    # def generate_ideal_path(self, reaching_time, target_xyz, start_xyz, vmax=1,
    #         kp=20, kv=8, dt=0.005):

    #     #TODO: add a check to make sure that target is passed in as a list of
    #     #lists, even if one target is passed it should be [[x,y,z]] or else it
    #     #doesn't generate correctly
    #     if target_xyz is None:
    #         print('ERROR: Must provide target(s)')
    #     x_track = []
    #     u_track = []
    #     # create our point mass system dynamics dx = Ax + Bu
    #     x = np.hstack([start_xyz, np.zeros(3)])  # [x, y, z, dx, dy, dz]
    #     A = np.array([
    #         [0, 0, 0, 1, 0, 0],
    #         [0, 0, 0, 0, 1, 0],
    #         [0, 0, 0, 0, 0, 1],
    #         [0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0]])
    #     u = np.array([0, 0, 0])  # [u_x, u_y, u_z]
    #     B = np.array([
    #         [0, 0, 0],
    #         [0, 0, 0],
    #         [0, 0, 0],
    #         [1, 0, 0],
    #         [0, 1, 0],
    #         [0, 0, 1]])

    #     # interpolation sampling rate
    #     timesteps = int(reaching_time / dt)
    #     # print('time steps: ', timesteps)

    #     lamb = kp / kv

    #     path = path_planners.SecondOrder(
    #             None, w=1e4, zeta=3, threshold=0.05)

    #     for ii, target in enumerate(target_xyz):
    #         u = np.zeros(3)
    #         # print('II: ', ii)

    #         state=np.hstack((target, np.zeros(3)))
    #         for t in range(timesteps):
    #             # track trajectory
    #             x_track.append(np.copy(x))
    #             u_track.append(np.copy(u))

    #             # print('target: ', np.hstack((target,np.zeros(3))))
    #             # print('target pos: ', target)
    #             # print('dt: ', dt)
    #             temp_target = path.step(
    #                 state=state,
    #                 target_pos=target, dt=dt)

    #             # calculate the position error
    #             x_tilde = np.array(x[:3] - temp_target[:3])

    #             # implement velocity limiting
    #             sat = vmax / (lamb * np.abs(x_tilde))
    #             if np.any(sat < 1):
    #                 index = np.argmin(sat)
    #                 unclipped = kp * x_tilde[index]
    #                 clipped = kv * vmax * np.sign(x_tilde[index])
    #                 scale = np.ones(3, dtype='float32') * clipped / unclipped
    #                 scale[index] = 1
    #             else:
    #                 scale = np.ones(3, dtype='float32')

    #             u = -kv * (x[3:] - temp_target[3:] -
    #                                 np.clip(sat / scale, 0, 1) *
    #                                 -lamb * scale * x_tilde)

    #             # move simulation one time step forward
    #             dx = np.dot(A, x) + np.dot(B, u)
    #             x += dx * dt

    #     u_track = np.array(u_track)
    #     x_track = np.array(x_track)
    #     runtime = reaching_time * len(target_xyz)
    #     n_points = len(x_track)
    #     #print('N POINTS',n_points)
    #     t_track = np.ones(n_points) * runtime/n_points

    #     # import matplotlib
    #     # matplotlib.use("TkAgg")
    #     # import matplotlib.pyplot as plt
    #     # plt.figure()
    #     # plt.plot(x_track[:,3:])
    #     # plt.show()
    #     return [t_track, x_track]

    def filter_data(self, data, alpha=0.2):
        data_filtered = []
        for nn in range(0,len(data)):
            if nn == 0:
                data_filtered.append((alpha*data[nn]
                                          + (1-alpha)*0))
            else:
                data_filtered.append((alpha*data[nn]
                                          + (1-alpha)*data_filtered[nn-1]))
        data_filtered = np.array(data_filtered)

        return data_filtered

    # def two_norm_error(self, baseline_traj, traj):
    #     """
    #     accepts two nx3 arrays of xyz cartesian coordinates and returns the
    #     2norm error of traj to baseline_traj

    #     Parameters
    #     ----------
    #     baseline_traj: nx3 array
    #         coordinates of ideal trajectory over time
    #     traj: nx3 array
    #         coordinates of trajectory to compare to baseline
    #     order_of_error: int, Optional (Default: 0)
    #         the order of error to calculate
    #         0 == position error
    #         1 == velocity error
    #         2 == acceleration error
    #         3 == jerk error

    #     """
    #     # error relative to ideal path
    #     error = (np.sum(np.sqrt(np.sum(
    #         (ideal_path - recorded_path)**2,
    #         axis=1)))) #*dt
    #     #TODO: confirm whether or not we should be multiplying by dt

    #     return error
