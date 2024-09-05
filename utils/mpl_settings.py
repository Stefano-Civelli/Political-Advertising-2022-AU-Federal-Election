import matplotlib.pyplot as plt
import seaborn as sns

def apply_settings():
    # Set the style to a clean, professional look
    sns.set_style("whitegrid")

    # Increase the default figure size
    plt.rcParams['figure.figsize'] = (8, 6)

    # Increase the font size for better readability
    plt.rcParams['font.size'] = 18
    plt.rcParams['axes.labelsize'] = 20
    plt.rcParams['axes.titlesize'] = 22
    plt.rcParams['xtick.labelsize'] = 18
    plt.rcParams['ytick.labelsize'] = 18
    plt.rcParams['legend.fontsize'] = 18
    plt.rcParams['figure.titlesize'] = 24

    # Use a serif font for a more traditional scientific look
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

    # Increase the linewidth for better visibility
    plt.rcParams['axes.linewidth'] = 1.5
    plt.rcParams['lines.linewidth'] = 2

    # Set a higher DPI for better resolution
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['savefig.dpi'] = 300

    # Use a color-blind friendly palette
    colors = ['#0077BB', '#33BBEE', '#009988', '#EE7733', '#CC3311', '#EE3377', '#BBBBBB']
    sns.set_palette(colors)

    # Ensure that the output is in vector graphics format
    plt.rcParams['savefig.format'] = 'pdf'


def apply_settings_multiplot():
    # Set the style to a clean, professional look
    sns.set_style("whitegrid")

    # Increase the figure size for a 2x2 subplot layout
    plt.rcParams['figure.figsize'] = (16, 12)  # Doubled from (8, 6)

    # Adjust font sizes for readability in the multiplot layout
    plt.rcParams['font.size'] = 12  # Slightly reduced
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['figure.titlesize'] = 18

    # Use a serif font for a more traditional scientific look
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']

    # Increase the linewidth for better visibility
    plt.rcParams['axes.linewidth'] = 1.5
    plt.rcParams['lines.linewidth'] = 2

    # Set a higher DPI for better resolution
    plt.rcParams['figure.dpi'] = 300
    plt.rcParams['savefig.dpi'] = 300

    # Use a color-blind friendly palette
    colors = ['#0077BB', '#33BBEE', '#009988', '#EE7733', '#CC3311', '#EE3377', '#BBBBBB']
    sns.set_palette(colors)

    # Ensure that the output is in vector graphics format
    plt.rcParams['savefig.format'] = 'pdf'

    # Add some spacing between subplots
    plt.rcParams['figure.subplot.hspace'] = 0.3
    plt.rcParams['figure.subplot.wspace'] = 0.3


plot_settings = {'ytick.labelsize': 16,
                        'xtick.labelsize': 16,
                        'font.size': 22,
                        'figure.figsize': (10, 5),
                        'axes.titlesize': 22,
                        'axes.labelsize': 18,
                        'lines.linewidth': 2,
                        'lines.markersize': 3,
                        'legend.fontsize': 11,
                        'mathtext.fontset': 'stix',
                        'font.family': 'STIXGeneral'}
plt.style.use(plot_settings)