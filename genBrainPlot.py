# -----------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------

from mayavi import mlab
from tvtk.api import tvtk
import numpy as np

def loadVtkMesh(filename, figure):
  reader = tvtk.PolyDataReader(file_name=filename)
  mesh = reader.get_output()
  reader.update()

  nodes = np.array(mesh.points)
  nodes = nodes.transpose()
  triangles = np.array(mesh.polys.to_array())
  triangles = triangles.reshape((-1,4))[:,1:4]

  return mlab.triangular_mesh(*nodes, triangles, color=(0,0,0), opacity=0.1, figure=figure)



import numpy as np
from mayavi import mlab

# opacity_threshold is a t_value
# opacity only applies to things that are less than the opacity threshold
def plotBrainElectrodes(figure, filename, log10=None, single_subject=None, region_plot=None, opacity_threshold=0, opacity=0.2, clip=(None, None), label_subjects=False):
  # Setup
  figure.scene.disable_render = True
  
  # Load data
  # Nx5 array of that give electrode XYZ coordinates, t_values, regions, stim XYZ coordinates, and a list of settings
  data = np.load(filename, allow_pickle=True)
  subjects = data['subjects'] # strings
  coords = data['coords']  # [3] XYZ coords
  t_values = data['t_values']  # floats 
  regions = data['regions']  # strings
  stim_coords = data['stim_coords']  # [3] XYZ coords
  settings = data['settings'][0] # dict
  print('Number of electrodes: '+str(len(coords)))
  print(settings)
  #print(coords)
  #print(t_values)
  #print(regions)
  #print(stim_coords)
  
  # Configure plot settings
  colormap = settings.get('stim_colormap', None)
  vmin = clip[0] if clip[0] is not None else settings.get('vmin', None)
  vmax = clip[1] if clip[1] is not None else settings.get('vmax', None)
  colors = t_values

  if (vmin is None) and (vmax is None):
    vmax = np.amax(np.absolute(t_values))
    vmin = -1 * vmax

  @np.vectorize
  def twoSidedLog(val, base=10):
    assert(base > 0)
    if val > 0:
      return np.log(val) / np.log(base)
    elif val < 0:
      return -1 * np.log(np.absolute(val)) / np.log(base)
    else:  # val == 0
      return 0

  if log10 or (log10 is None and settings.get('log10_data', False)):
    # Take the log of all of the t_values for display
    colors = twoSidedLog(colors)

  # Label every electrode with subject
  if label_subjects:
    for sub, coord in zip(subjects, coords):
      mlab.text3d(coord[0], coord[1], coord[2], sub)

  # Set the scale, colors, and sizes
  if single_subject or (single_subject == None and settings.get('single_subject', False)):
    # Single subject data plotting
    scale_mode = 'none'
    colormap = settings.get('colormap', 'YlOrBr') # Override the default color scheme
    electrode_size = settings.get('electrode_size', 4) # The size of the electrodes
  else:
    scale_mode = 'vector'
    colormap = settings.get('colormap', 'PuOr') # Override the default color scheme
    electrode_size = settings.get('electrode_size', 2.5) # The size of the electrodes
  
  # Set up region plot
  if region_plot or (region_plot is None and settings.get('do_region_plot', False)):
    # True means region, else means tscore
    colormap = settings.get('colormap', 'gist_rainbow') # Override the default color scheme
    unique_regions = list(set(regions))
    step_size = 2.0 / (len(unique_regions) - 1) if len(unique_regions) > 1 else 0
    mapping = {region: -1 + i * step_size for i, region in enumerate(unique_regions)}
    colors = [mapping[region] for region in regions]
  
  # Make list of electrodes that don't pass opacity_threshold
  # Remove those electrodes from the original list
  opacity_filter_array = np.absolute(t_values) < opacity_threshold
  transparent_coords = coords[opacity_filter_array]
  transparent_t_values = t_values[opacity_filter_array]
  transparent_regions = regions[opacity_filter_array]
  transparent_colors = colors[opacity_filter_array]
  coords = coords[~opacity_filter_array]
  t_values = t_values[~opacity_filter_array]
  regions = regions[~opacity_filter_array]
  colors = colors[~opacity_filter_array]
    
  # Plot the electrodes
  normal_pts = mlab.points3d(coords[:, 0], coords[:, 1], coords[:, 2], colors,
                       vmin=vmin, vmax=vmax, scale_factor=electrode_size,
                       scale_mode=scale_mode, colormap=colormap, resolution=40)

  # Make the electrodes more opaque the higher the t_score (linspaced)
  #lut_table = normal_pts.module_manager.scalar_lut_manager.lut.table.to_array()
  #lut_table[:,3] = np.concatenate((np.linspace(255, 0, int(len(lut_table)/2)), np.linspace(0, 255, int(len(lut_table)/2))))
  #normal_pts.module_manager.scalar_lut_manager.lut.table = lut_table

  if opacity_threshold != 0:
    trans_pts = mlab.points3d(transparent_coords[:, 0], transparent_coords[:, 1], transparent_coords[:, 2], transparent_colors,
                       vmin=vmin, vmax=vmax, scale_factor=electrode_size, opacity=opacity,
                       scale_mode=scale_mode, colormap=colormap, resolution=40)
    
  if stim_coords.size != 0:
      stim_pt = mlab.points3d(stim_coords[:, 0], stim_coords[:, 1], stim_coords[:, 2], [1]*len(stim_coords),
                          vmin=vmin, vmax=vmax, scale_factor=electrode_size,
                          scale_mode=scale_mode, colormap='cool', resolution=40) #inferno # summer # magma #afmhot #jet #viridis

  # Plot the colorbar
  mlab.colorbar(object=normal_pts, title="t-scores", nb_labels=7, label_fmt="%.1f")

  # Teardown
  figure.scene.disable_render = False



from mayavi import mlab

# When using this, make sure "mlab.options.offscreen = False" before creating the first figure
def showBrainPlot(figure, rotation=0, elevation=0, distance=0):
  # Validate mlab setup
  if mlab.options.offscreen == True:
    print("Remove the line \"mlab.options.offscreen = True\" at the top of your code"
          "Also, genRotatingVideo() will not do anything while offscreen is set to False or is not specified")
    return

  # Show Plot
  mlab.view(figure=figure, azimuth=90+rotation, elevation=90-elevation, distance=450+distance, focalpoint=[0,0,0])
  mlab.show()



from mayavi import mlab
from PIL import Image
import ffmpeg

# When using this, make sure "mlab.options.offscreen = True" before creating the first figure
def genRotatingVideo(figure, duration_s, degrees, fps, width, height, filename="spinningBrainPlot"):
  # Validate mlab setup
  if mlab.options.offscreen == False:
    print("You need to put the line \"mlab.options.offscreen = True\" at the top of your code"
          "Also, showBrainPlot() will not do anything while offscreen is set to True")
    return

  # Initialise ffmpeg process
  output_args = {
      'pix_fmt': 'yuv444p',
      'vcodec': 'libx264',
      'r': fps,
  }
  
  process = (
      ffmpeg
          .input('pipe:', format='rawvideo', pix_fmt='rgb24', s=f'{width}x{height}')
          .output(filename+'.mp4', **output_args)
          .overwrite_output()
          .run_async(pipe_stdin=True)
  )
  
  # Throws an error without this.
  figure.scene._lift()

  # Create photos
  num_frames = fps * duration_s
  deg_per_frame = degrees / num_frames
  rot = 0
  for i in range(num_frames):
    print("{:.2f}% or {}°".format(i/num_frames*100, rot))
    rot = i * deg_per_frame
    mlab.view(figure=figure, azimuth=90+rot, elevation=83, distance=450, focalpoint=[0,0,0])
    screenshot = mlab.screenshot(figure=figure, mode='rgb', antialiased=True)
    frame = Image.fromarray(screenshot, 'RGB')
    process.stdin.write(frame.tobytes())

  # Flush video
  process.stdin.close()
  process.wait()

# -----------------------------------------------------------
# Start Code
# -----------------------------------------------------------

from mayavi import mlab
import numpy as np

# Constants
vtkFile_l = 'lh.vtk' 
vtkFile_r = 'rh.vtk'
WIDTH = 1080
HEIGHT = 1080
DURATION_S = 8
DEGREES = 360
FPS = 25
FILE_NAME = "brain_plot_data.npz"
#FILE_NAME = "crazy_brain_plot_data.npz"

GEN_VIDEO = True

# Setup the scene
if GEN_VIDEO:
  mlab.options.offscreen = True  # Stops the view window popping up and makes sure you get the correct size screenshots.
figure = mlab.figure(1, size=(WIDTH, HEIGHT), bgcolor=(1,1,1), fgcolor=(0,0,0))

# Setup brain surfaces
loadVtkMesh(vtkFile_l, figure)
loadVtkMesh(vtkFile_r, figure)

# Plot electrodes
plotBrainElectrodes(figure, FILE_NAME)
#plotBrainElectrodes(figure, FILE_NAME, clip=(-3, 3), opacity_threshold=2, opacity=0, label_subjects=True)

# Generate image/video
if GEN_VIDEO:
  # When using this, make sure mlab.options.offscreen = True
  genRotatingVideo(figure, DURATION_S, DEGREES, FPS, WIDTH, HEIGHT)
else:
  # When using this, make sure mlab.options.offscreen = False (it's False by default)
  showBrainPlot(figure)

