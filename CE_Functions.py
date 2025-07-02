def ensemble_mean(twom_temp_files, precip_files, ts_files, start_index, end_index):
    import xarray as xr
    trefht_sum = 0
    prect_sum = 0
    ts_sum = 0
    for i, file in enumerate(twom_temp_files):
        trefht_ds = xr.open_dataset(file)
        trefht_var = trefht_ds['TREFHT'] - 273.15
        trefht_sum += trefht_var[start_index:end_index]
        trefht_ds.close()

        prect_ds = xr.open_dataset(precip_files[i])
        prect_var= prect_ds["PRECT"]
        prect_sum += prect_var[start_index:end_index]
        prect_ds.close()

        ts_ds = xr.open_dataset(ts_files[i])
        ts_var = ts_ds["TS"] - 273.15
        ts_sum += ts_var[start_index:end_index]
        ts_ds.close()
    
    trefht_avg = (trefht_sum / 100)
    prect_avg = (prect_sum / 100)
    ts_avg = (ts_sum / 100)

    return trefht_avg, prect_avg ,ts_avg 



def test_for_CES_hot_dry(trefht_files, prect_files, trefht_avg_d, prect_avg_d):
    import xarray as xr
    sum_freq = 0
    CES_all_locations_binary = []
    for prect_i, file in enumerate(trefht_files):
        trefht_ds = xr.open_dataset(file)
        trefht_anom_clim = trefht_ds["TREFHT"] - 273.15
        trefht_anom_clim = trefht_anom_clim - trefht_avg_d
        trefht_ds.close()

        prect_ds = xr.open_dataset(prect_files[prect_i])
        prect_anom_clim = prect_ds["PRECT"]
        prect_anom_clim = prect_anom_clim - prect_avg_d
        prect_ds.close()


        # Find Quantiles
        world_quant = trefht_anom_clim.quantile(0.90, dim = 'time')
        world_prect_quant = prect_anom_clim.quantile(0.10, dim = 'time')

        # Test for compound events
        ce_test = (trefht_anom_clim >= world_quant) & (prect_anom_clim <= world_prect_quant)

        # Switch to binary
        ce_binary = ce_test * 1

        # Count how many compound events for every location
        count_ces = (ce_binary == 1).sum(dim = 'time')
        #number_of_ces += count_ces

        CES_all_locations_binary.append(ce_binary)

        # Find the frequency of compound events (not percentage)
        ce_freq_raw = count_ces / len(ce_binary['time'])

        # add the frequency to the sum
        sum_freq += ce_freq_raw

        print(prect_i)
    return ce_binary, sum_freq, CES_all_locations_binary


def dif_from_random_chance(bootstrap_upper, bootstrap_lower, average_frequencies):
    import numpy as np
    # Find the Average of the two bounds
    test = (bootstrap_upper + bootstrap_lower) / 2

    # Middle value of random chance will be assigned to medians
    middle_value_of_random = test

    # Determine whether the average frequencies across all locations fall in random chance
    random_chance = (average_frequencies < bootstrap_upper) & (average_frequencies > bootstrap_lower)

    # Wherever random chance is true, we leave an np.nan, wherever it is not random chance we assign the average frequency number
    ce_freq_nans = np.where(random_chance, np.nan, average_frequencies)  

    # Finding difference from the random chance using the new array and the middle value of random array that we defined with the medians
    dif_from_random = ce_freq_nans - middle_value_of_random

    return dif_from_random

def surface_temperature_composite(members, lat, lon, ts_mems, ts_avg):
    import xarray as xr
    # Create list to hold all the true indices for compound events for one location
    true_indices_list = []

    # loop through all the members for the CE indices
    for mem in members:
        # pick out one location
        location_ces_each_member = mem.sel(lat = lat, lon = lon, method = 'nearest')
        # pull out the true indicies 
        true_indices = [index for index, value in enumerate(location_ces_each_member) if value]

        # append the true indices to a list to call later
        true_indices_list.append(true_indices)


    # temperature sum to average for the composite map
    temp_sum = 0
    # true indicies index to loop through the members from the true indices list
    true_indicies_i = 0
    # test to compare to the true indices sum earlier
    test_i = 0

    for file in ts_mems:
        # call the surface temperature file and values and convert to celsius
        ts_anom_clim = xr.open_dataset(file)["TS"] - 273.15
        ts_anom_clim = ts_anom_clim - ts_avg
        # call the true indicies for that specific member
        temp_list = true_indices_list[true_indicies_i]
        
        # loop through all the true indices for that member
        for i in temp_list:
            #if i == 0:
            #   print(i)
            #   next
            # add the temperature from whatever month you want around the index for the compound event to the sum
            temp_sum += ts_anom_clim[i] # -1 for the month before
            test_i += 1
        true_indicies_i += 1
    print(test_i)
    composite_map_temperature = temp_sum / test_i
    return composite_map_temperature, ts_anom_clim

def plot_united_states(lon_coords, lat_coords, plot_data, title = "", colorbar_label = "", cmap='', lat_marker = 41.94 , lon_marker = -87.63, vmin = 0, vmax = 3):
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import cartopy as cart

    LONW = -130
    LONE = -55
    LATS = 20
    LATN = 55

    CLAT = (LATN + LATS) / 2
    CLON = (LONW + LONE) / 2
    res = '110m'

    fig = plt.figure(figsize = (15, 10))
    ax = plt.subplot(1,1,1, projection = ccrs.PlateCarree())
    ax.set_extent([LONW, LONE, LATS, LATN], crs = ccrs.PlateCarree())
    ax.coastlines(resolution = res, color = 'black')
    ax.add_feature(cfeature.STATES, linewidth = 0.3, edgecolor = 'gray')
    ax.add_feature(cfeature.BORDERS, linewidth = 0.5, edgecolor = 'black')

    plt.pcolormesh(lon_coords, lat_coords, plot_data, transform = ccrs.PlateCarree(), cmap = cmap, vmin = vmin, vmax = vmax)
    ax.add_feature(cart.feature.OCEAN, zorder = 100, edgecolor='k', color = 'gray')
    plt.plot(lat_marker, lon_marker, marker = 'x', color = 'black')
    plt.title(title)
    plt.colorbar(label = colorbar_label, shrink = 0.6)
    plt.show()