import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import decimate
from scipy.ndimage.filters import uniform_filter1d
from sklearn.manifold import MDS

def plot_eigenvalues(*matrices, fig=None, return_fig=False):
    """Plots eigenvalues of a given matrix in the complex plane, as well
    as the unit circle for reference."""

    if fig is None:
        fig = plt.figure()
    theta = np.arange(0, 2*np.pi, 0.01)
    plt.plot(np.cos(theta), np.sin(theta), 'k', linestyle='--', linewidth=1.5)
    plt.axis('equal')

    for M in matrices:
        eigs, _ = np.linalg.eig(M)
        plt.plot(np.real(eigs), np.imag(eigs), '.', markersize=10)

    if return_fig:
        return fig

def plot_array_of_histograms(counts, weights, ticks=None, return_fig=True,
                             plot_zero_line=True, fig_size=(6,3), **kwargs):
    """Plots count data in the shape (n_samples, n_row, n_col) as an array
    of histograms with n_row rows and n_col cols."""

    fig, ax = plt.subplots(counts.shape[1], counts.shape[2],
                           figsize=fig_size)

    n_bins = 100
    if 'n_bins' in kwargs.keys():
        n_bins = kwargs['n_bins']

    weighted_medians = np.zeros((counts.shape[1], counts.shape[2]))

    for i in range(counts.shape[1]):
        for j in range(counts.shape[2]):
            if i <= j:
                fig.delaxes(ax[i, j])
                continue
            w = weights[:, i, j]
            hist, bins = np.histogram(counts[:, i, j],
                                      weights=w/w.sum(),
                                      bins=np.linspace(-1, 1, n_bins),
                                      density=True)
            bin_centers = bins[:-1] + (bins[1] - bins[0])/2
            #weighted_medians[i, j] = weighted_median(hist, bin_centers)
            weighted_medians[i, j] = np.mean(counts[:, i, j])
            hist = uniform_filter1d(hist, 10)
            #ax[i, j].hist(counts[:, i, j], bins=np.linspace(-1, 1, n_bins))
            ax[i, j].plot(bin_centers, hist, linewidth=0.7)
            ax[i, j].fill_between(bin_centers,
                                  np.zeros_like(bin_centers),
                                  hist,
                                  color='C0',
                                  alpha=0.3)
            ax[i, j].axvline(x=weighted_medians[i, j], color='C0',
                             linestyle='--', dashes=[1.5,0.75], linewidth=0.7)
            #ax[i, j].set_ylim([0, 2])
            if plot_zero_line:
                ax[i, j].axvline(x=0, color='k', linestyle='--',
                                 dashes=[1.5,0.75], linewidth=0.7)
            ax[i, j].set_yticks([])
            if ticks is not None:
                if i == counts.shape[1] - 1:
                    pass
                    ax[i, j].set_xticks([])
                    #ax[i, j].set_xlabel(ticks[j])
                else:
                    ax[i, j].set_xticks([])
                if j == 0:
                    pass
                    #ax[i, j].set_ylabel(ticks[i])

    if return_fig:
        return (fig, weighted_medians)

def plot_array_of_downsampled_signals(signals, ticks=None, return_fig=False,
                                      plot_zero_line=True, **kwargs):
    """Plots time series data in the shape (T, n_row, n_col) as an array
    of filtered signals with n_row rows and n_col cols."""

    fig, ax = plt.subplots(signals.shape[1], signals.shape[2],
                           figsize=(30, 10))

    n_bins = 100
    if 'n_bins' in kwargs.keys():
        n_bins = kwargs['n_bins']

    for i in range(signals.shape[1]):
        for j in range(signals.shape[2]):
            if i < j:
                fig.delaxes(ax[i, j])
                continue
            signal = decimate(decimate(decimate(signals[:, i, j], 10), 10), 10)
            #time_ = np.arange(0, signals.shape[0], 1000)
            #i_time_ticks = [len(time_)//5*i for i in range(5)]
            #time_ticks = time_[np.array(i_time_ticks)]
            ax[i, j].plot(signal)
            ax[i, j].set_ylim([-1, 1])
            if plot_zero_line:
                ax[i, j].axhline(y=0, color='k', linestyle='--')
            if ticks is not None:
                if i == signals.shape[1] - 1:
                    ax[i, j].set_xlabel(ticks[j])
                    #labels = ['{}k'.format(int(time_tick/1000)) for time_tick in time_ticks]
                    #ax[i, j].set_xticks(time_ticks, labels)
                    #set_trace()
                else:
                    ax[i, j].set_xticks([])
                if j == 0:
                    ax[i, j].set_ylabel(ticks[i])
                    ax[i, j].set_yticks([-1, 0, 1])
                else:
                    ax[i, j].set_yticks([])

    if return_fig:
        return fig

def plot_signal_xcorr(s1, s2, return_fig=False, finite_diff=True):
    """IN PROGRESS -- need principled method for computing xcorr for non-
    stationary signals."""

    assert s1.shape == s2.shape

    #finite_difference

    if finite_diff:
        s1 = (s1[1:] - s1[:-1])# / (np.abs(s1[1:]) + np.abs(s1[:-1]) + 1)
        s2 = (s2[1:] - s2[:-1])# / (np.abs(s2[1:]) + np.abs(s2[:-1]) + 1)

    n_pts = s1.shape[0]
    lags = np.arange(1 - n_pts, n_pts)
    #s1 = (s1 - s1.mean()) / np.std(s1)
    #s2 = (s2 - s2.mean()) / np.std(s2)

    xcorr = np.correlate(s1, s2, 'full') / max(len(s1), len(s2))

    fig = plt.figure()
    plt.plot(lags, xcorr)
    plt.axvline(x=0, color='k', linestyle='--')

    if return_fig:
        return fig

def plot_MDS_from_distance_matrix(distances, return_fig=False):
    """For a given set of pariwise distances, plots the elements in a 2-D space
    that maximally preserves specified distances."""

    mds = MDS(n_components=2, dissimilarity='precomputed')
    proj = mds.fit_transform(distances)

    fig = plt.figure()
    col = 'C0'
    plt.plot(proj[:1000,0], proj[:1000,1], color=col)
    plt.plot(proj[0,0], proj[0,1], 'x', color=col)
    plt.plot(proj[1000,0], proj[1000,1], '.', color=col)


    col = 'C1'
    plt.plot(proj[1000:,0], proj[1000:,1], color=col)
    plt.plot(proj[1000,0], proj[1000,1], 'x', color=col)
    plt.plot(proj[-1,0], proj[-1,1], '.', color=col)

    if return_fig:
        return fig


def plot_signals(signals, key_restriction=None, title=None,
                 signal_clips={}):
    """For a dictionary of 1D time series signals, plots each vertically
    in a min-max range from 0 to 1.

    Includes option to clip any signal from above for easier visualization,
    via the signal_clips dictionary."""

    keys = signals.keys()
    if key_restriction is not None:
        keys = key_restriction

    fig = plt.figure(figsize=(10, 2 * len(keys)))
    leg = []
    for i_key, key in enumerate(keys):

        x = signals[key].copy()

        if key in signal_clips.keys():
            x = np.clip(x, 0, signal_clips[key])

        x_max = np.amax(x)
        x_min = np.amin(x)

        x = (x - x_min) / (x_max - x_min)

        plt.plot(x - 1.2 * i_key, color='C{}'.format(i_key))
        leg.append(key)

    plt.legend(leg)
    plt.yticks([])
    if title is not None:
        plt.title(title)

    return fig
