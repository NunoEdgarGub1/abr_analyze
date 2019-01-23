import subprocess
import os
class MakeGif():
    def __init__(self):
        pass
    def prep_fig_cache(self, use_cache=True):
        # set up save location for figures
        if use_cache:
            from abr_analyze.utils.paths import figures_dir
            save_loc = figures_dir
        else:
            save_loc = 'figures'
        # create save location if it does not exist
        if not os.path.exists(save_loc):
            os.makedirs(save_loc)

        if not os.path.exists('%s/gif_fig_cache'%save_loc):
            os.makedirs('%s/gif_fig_cache'%save_loc)

        # delete old files if they exist in the figure cache. These are used to
        # create a gif and need to be deleted to avoid the issue where the
        # current test has fewer images than what is already in the cache, this
        # would lead to the old images being appended to the end of the gif
        files = [f for f in os.listdir('%s/gif_fig_cache'%save_loc) if f.endswith(".png") ]
        for ii, f in enumerate(files):
            if ii == 0:
                print('Deleting old temporary figures for gif creation...')
            os.remove(os.path.join('%s/gif_fig_cache'%save_loc, f))
        return '%s/gif_fig_cache'%save_loc

    def create(self, fig_loc, save_loc, save_name, delay=5, res=[1200,2000]):
        """
        Module that checks fig_loc location for png files and creates a gif

        PARAMETERS
        ----------
        fig_loc: string
            location where .png files are saved
            NOTE: it is recommended to use a %03d numbering system (or more if more
            figures are used) to have leading zeros, otherwise gif may not be in
            order
        save_loc: string
            location to save gif
        save_name: string
            name to use for gif
        delay: int
            changs the delay between images in the gif
        """
        if not os.path.exists(save_loc):
            os.makedirs(save_loc)
        bashCommand = ("convert -delay %i -loop 0 -resize %ix%i %s/*.png %s/%s.gif") %(
                        delay, res[0], res[1], fig_loc, save_loc, save_name)
        # bashCommand = ("convert -delay %i -loop 0 -deconstruct -quantize"%delay
        #                + " transparent -layers optimize -resize %ix%i"%(res[0],res[1])
        #                + " %s/*.png %s/%s.gif"
        #                %(fig_loc, save_loc, save_name))
        print('Creating gif...')
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print('Finished')
