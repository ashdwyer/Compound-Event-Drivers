import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy as cart
import numpy as np
import scipy.stats as stats

def plot_avg_frequencies(lat, lon, average_freqs, cmap, vmin, vmax, title, colorbartitle, bootstrap_upper, bootstrap_lower, save = False, remove_random_chance = True):
    plt.figure(figsize=(12,6))
    ax = plt.axes(projection = ccrs.Robinson()) 
    plt.pcolormesh(lon, lat, average_freqs, cmap = cmap, transform = ccrs.PlateCarree(), vmin = vmin, vmax = vmax)
    plt.colorbar(label = colorbartitle)
    ax.coastlines()
    ax.add_feature(cart.feature.OCEAN, zorder = 100, edgecolor='k', color = 'gray')
    plt.title(title)
    if save:
        dpi = 600
        plt.savefig('AvgFreqCDHW_IV_1850_2000', dpi=dpi)
    plt.show()
    if remove_random_chance:
        random_chance = (average_freqs < bootstrap_upper) & (average_freqs > bootstrap_lower)
        ce_freq_nans = np.where(random_chance, np.nan, average_freqs)


        plt.figure(figsize=(12,6))
        ax = plt.axes(projection = ccrs.Robinson()) 
        plt.pcolormesh(lon, lat, ce_freq_nans, cmap = 'Reds', transform = ccrs.PlateCarree(), vmin = 0, vmax =4)
        plt.colorbar(label = colorbartitle)
        ax.coastlines()
        ax.add_feature(cart.feature.OCEAN, zorder = 100, edgecolor='k', color = 'gray')
        plt.title(title)
        plt.show()


def plot_regression(mode_values, location_var_values, title, xlabel, ylabel):
    plt.subplots(figsize=(10,6))
    plt.scatter(mode_values, location_var_values[0:1800], color = 'lightgray')
    slope, intercept, rvalue, pvalue, stderr = stats.linregress(mode_values, location_var_values[0:1800])
    plt.plot(mode_values, intercept + slope*mode_values, label = np.round(rvalue**2,2), color = 'black')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.show()

def bootstrap_histogram_plot(lat, lon, bootstrap_file, upper_bound, lower_bound, title ):
    # Choose the location you want
    lat_ts = lat
    lon_ts = lon

    # Call the bootstrapping frequencies for that certain location
    ts_oneloc = bootstrap_file.sel(lat = lat_ts, lon = lon_ts, method = 'nearest')

    # Plot the histogram
    plt.hist(ts_oneloc, bins = 9, color = 'gray')
    plt.xlabel(f"Average Random Frequency of CEs (%)")
    plt.ylabel("Number of Occurences")
    plt.title(title)

    # Plot the 95th and 5th quantiles and then plot the average frequency for that one location
    plt.axvline(lower_bound.sel(lat = lat_ts, lon = lon_ts, method = 'nearest'), color = 'blue')
    plt.axvline(upper_bound.sel(lat = lat_ts, lon = lon_ts, method = 'nearest'), color = 'blue')
    #plt.axvline(1.59277778, color = 'black')