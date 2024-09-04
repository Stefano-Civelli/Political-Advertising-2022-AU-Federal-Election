import matplotlib.pyplot as plt
import seaborn as sns

def apply_settings():
    # Set the style to a clean, professional look
    sns.set_style("whitegrid")

    # Increase the default figure size
    plt.rcParams['figure.figsize'] = (8, 6)

    # Increase the font size for better readability
    plt.rcParams['font.size'] = 15
    plt.rcParams['axes.labelsize'] = 17
    plt.rcParams['axes.titlesize'] = 19
    plt.rcParams['xtick.labelsize'] = 15
    plt.rcParams['ytick.labelsize'] = 15
    plt.rcParams['legend.fontsize'] = 15
    plt.rcParams['figure.titlesize'] = 21

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