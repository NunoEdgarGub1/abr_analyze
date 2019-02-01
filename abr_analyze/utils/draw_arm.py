#TODO: make this plot only a single ax object with parameters to either pass an
# ax object, if not one is created since we only want the one frame, otherwise
# get the grid layout done in a higher level script
import abr_jaco2
from abr_analyze.utils.data_visualizer import DataVisualizer
from abr_analyze.utils.draw_arm_proc import DrawArmProc
from abr_analyze.utils.draw_arm_vis import DrawArmVis

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from mpl_toolkits.mplot3d import Axes3D
import os
"""
"""
class DrawArm():
    '''

    '''
    def __init__(self, db_name, robot_config=None, interpolated_samples=100):
        '''

        '''
        self.interpolated_samples = interpolated_samples
        self.robot_config = robot_config
        # create a dict to store processed data
        self.data = {}
        # instantiate our process and visualize modules
        self.drawProc = DrawArmProc(db_name=db_name, robot_config=robot_config)
        self.drawVis = DrawArmVis(traj_color='b', link_color='y', joint_color='k', arm_color='k')
        self.vis = DataVisualizer()

    def plot(self, ax, save_location, step, show_filter=True, show_trajectory=True):
        '''

        '''
        if save_location not in self.data:
            self.data[save_location] = self.drawProc.generate(save_location=save_location,
                interpolated_samples=self.interpolated_samples, clear_memory=False)

        data = self.data[save_location]

        # plot our arm figure
        self.drawVis.plot_arm(ax=ax, joints_xyz=data['joints_xyz'][step],
                links_xyz=data['links_xyz'][step], ee_xyz=data['ee_xyz'][step])
        # plot the filtered target trajectory
        if show_filter:
            self.vis.plot_trajectory(ax=ax, data=data['filter'][:step], c='g')
        # plot the ee trajectory
        if show_trajectory:
            self.vis.plot_trajectory(ax=ax, data=data['ee_xyz'][:step])

        ax.set_title(save_location)
        ax.set_xlim3d(-0.5,0.5)
        ax.set_ylim3d(-0.5,0.5)
        ax.set_zlim3d(0,1)
        ax.set_aspect(1)

        return ax
