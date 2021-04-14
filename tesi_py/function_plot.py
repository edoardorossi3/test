#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 14:48:49 2021

@author: edoardo
"""
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import os
import astropy.io.fits as fits

def bisection(f, t_min, t_max, toll):
    if f(t_min)*f(t_max)>=0:
        return None
    while (t_max-t_min)>toll:
        t_m=(t_max+t_min)/2.0
        if f(t_min)*f(t_m)>0:
            t_min=t_m
            t_max=t_max
        elif f(t_max)*f(t_m)>0:
            t_max=t_m
            t_min=t_min
        elif f(t_m)==0:
            return t_m
    return (t_max+t_min)/2.0
        



def rms_1684(z):
    perc_16=np.percentile(z,16)
    perc_84=np.percentile(z,84)
    r_1684=(perc_84-perc_16)/2.0
    return r_1684

def perc_84(z):
    perc84=np.percentile(z,84)
    return perc84

def perc_16(z):
    perc16=np.percentile(z,16)
    return perc16

#density_map_5p is a thesis format...

def density_map_5p(x,y,par,mock_par,mock_err, par_name='', x_label='', y_label='', vmin=[], vmax=[], nx=3, ny=3, figsize=(5,10)):
    import function_plot 
    
    #nan_par=np.isnan(par)
    #nonan_par= ~nan_par
    #par=par[nonan_par]
    #nan_mock_par=np.isnan(mock_par)
    #nonan_mock_par= ~nan_mock_par
    #mock_par=mock_par[nonan_mock_par]
    
    idx_fin=np.isfinite(par*mock_par)
    par=par[idx_fin]
    mock_par=mock_par[idx_fin]
    mock_err=mock_err[idx_fin]
    x_fin=x[idx_fin]
    y_fin=y[idx_fin]
    idx_nofin= ~idx_fin
    print('total deleted (no finite values):', np.sum(idx_nofin))
    
    median_par=stats.binned_statistic_2d(x_fin, y_fin, par, bins=50, statistic='median')
    median_mock=stats.binned_statistic_2d(x_fin, y_fin, mock_par, bins=50, statistic='median')
    y_g, x_g=np.meshgrid(median_par.y_edge, median_par.x_edge)
    bias_par=stats.binned_statistic_2d(x_fin, y_fin, (mock_par-par), bins=50, statistic='median')
    rms_1684_bias=stats.binned_statistic_2d(x_fin, y_fin, (mock_par-par), bins=50, statistic=function_plot.rms_1684)
    median_bayes_err=stats.binned_statistic_2d(x_fin,y_fin,mock_err, bins=50, statistic='median')
    err_norm=stats.binned_statistic_2d(x_fin,y_fin,(mock_par-par)/(mock_err), bins=50, statistic=function_plot.rms_1684)
    
    median_in=stats.binned_statistic(par, par, statistic='median', bins=50)
    median_out=stats.binned_statistic(par, mock_par, statistic='median', bins=50)
    
    perc_84_in=stats.binned_statistic((par),(par), statistic=function_plot.perc_84, bins=50)
    perc_84_out=stats.binned_statistic((par),(mock_par), statistic=function_plot.perc_84, bins=50)
    perc_16_in=stats.binned_statistic((par),(par), statistic=function_plot.perc_16, bins=50)
    perc_16_out=stats.binned_statistic((par),(mock_par), statistic=function_plot.perc_16, bins=50)

    
    
    fig1,axs1=plt.subplots(ny,nx,figsize=figsize)
    
    _im=axs1[0,0].pcolormesh(x_g, y_g, median_par.statistic, cmap=cm.gist_rainbow, vmin=vmin[0], vmax=vmax[0])
    fig1.colorbar(_im, ax=axs1[0,0])
    axs1[0,0].set_title(par_name)
    
    _im=axs1[0,1].pcolormesh(x_g, y_g, median_mock.statistic, cmap=cm.gist_rainbow, vmin=vmin[0], vmax=vmax[0])
    fig1.colorbar(_im, ax=axs1[0,1])
    axs1[0,1].set_title(par_name+'_mock')
    
    #axs1[0,1].axis('off')
    axs1[0,2].axis('off')
    
    istpar=np.histogram((par), bins=50)
    istmock=np.histogram((mock_par), bins=50)
    frac_par=istpar[0]/np.size(par)
    frac_mock=istmock[0]/np.size(mock_par)
    frac_par=np.append(frac_par[0],frac_par)
    frac_mock=np.append(frac_mock[0], frac_mock)
    axs1[1,0].step((istpar[1]),frac_par,label='par')
    axs1[1,0].step((istmock[1]),frac_mock,label='mock')
    axs1[1,0].legend(loc='upper right')
    med_par=np.median(par)
    med_mock=np.median(mock_par)
    axs1[1,0].plot([med_par,med_par], axs1[1,0].get_ylim())
    axs1[1,0].plot([med_mock,med_mock], axs1[1,0].get_ylim())
  
    
    _im=axs1[1,2].pcolormesh(x_g,y_g, err_norm.statistic, cmap=cm.hot, vmin=vmin[2], vmax=vmax[2])
    axs1[1,2].set_facecolor('#d8dcd6')
    #_im=axs1[0,2].pcolormesh(x_g,y_g,rms_1684_bias.statistic/median_bayes_err.statistic , cmap=cm.rainbow, vmin=vmin[2], vmax=vmax[2], facecolor='grey')
    fig1.colorbar(_im, ax=axs1[1,2])
    axs1[1,2].set_title(par_name+'rms1684_(out-in)/errbayes')

    _im=axs1[1,1].pcolormesh(x_g, y_g, bias_par.statistic, cmap=cm.Spectral, vmin=vmin[1], vmax=vmax[1])
    fig1.colorbar(_im, ax=axs1[1,1])
    axs1[1,1].set_title(par_name+'_bias_out-in')
    axs1[1,1].set_facecolor('#d8dcd6')


    axs1[2,0].scatter((par), (mock_par), s=0.1)
    axs1[2,0].plot((par), (par), color='red')
    axs1[2,0].plot(perc_84_in.statistic, perc_84_out.statistic, color='orange')
    axs1[2,0].plot(perc_16_in.statistic, perc_16_out.statistic, color='orange')
    axs1[2,0].plot(median_in.statistic, median_out.statistic, color='green')


    _im=axs1[2,1].pcolormesh(x_g, y_g, rms_1684_bias.statistic, cmap=cm.hot, vmin=vmin[3], vmax=vmax[3])
    fig1.colorbar(_im, ax=axs1[2,1])
    axs1[2,1].set_facecolor('#d8dcd6')
    axs1[2,1].set_title(par_name+'_rms1684_out-in')
    #print('[1,1]:', np.nanmax(rms_1684_bias.statistic), np.nanmin(rms_1684_bias.statistic))
    #c=np.nanargmax(rms_1684_bias.statistic, axis=0)
    
    _im=axs1[2,2].pcolormesh(x_g, y_g, median_bayes_err.statistic, cmap=cm.hot, vmin=vmin[4], vmax=vmax[4])
    fig1.colorbar(_im, ax=axs1[2,2])
    axs1[2,2].set_facecolor('#d8dcd6')
    axs1[2,2].set_title(par_name+'_err_bayes')
    #print('[1,2]:', np.nanmax(median_bayes_err.statistic), np.nanmin(median_bayes_err.statistic))
    #a=np.nanargmin(median_bayes_err.statistic)
    #idx_x=a%np.size(x_g)
    #idx_y=int(a/np.size(x_g))
    #print('hdhg_min:', np.reshape(y_g, -1)[a])
    #print('d4000n_min:', np.reshape(x_g, -1)[a])
    #print('total 0:', np.nansum(median_bayes_err.statistic==0.0))
    axs1[2,2].set_xlabel(x_label)
    axs1[2,0].set_xlabel(par_name)
    axs1[0,0].set_ylabel(y_label)
    axs1[1,0].set_ylabel('fraction of model')
    axs1[2,1].set_xlabel(x_label)
    axs1[2,0].set_ylabel(par_name+'_mock')
    
    return fig1


def diff_density_map(x,y,par1,par2,statistic,name1='',name2='',xlabel='',ylabel='',figsize=(10,25),vmin=None,vmax=None):
    stat_diffpar=stats.binned_statistic_2d(x,y,par1-par2,bins=50,statistic=statistic)
    
    y_g,x_g=np.meshgrid(stat_diffpar.y_edge, stat_diffpar.x_edge)
    
    fig, ax=plt.subplots(figsize=figsize)
    im=ax.pcolormesh(x_g, y_g, stat_diffpar.statistic,cmap=cm.Spectral,vmin=vmin, vmax=vmax)
    fig.colorbar(im, ax=ax)
    ax.set_facecolor('grey')
    ax.set_title(name1+'-'+name2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    return fig, ax, stat_diffpar.statistic


def density_map(x,y,par,statistic,name='',xlabel='',ylabel='',figsize=(10,25),vmin=None,vmax=None, bins=50):
    stat_diffpar=stats.binned_statistic_2d(x,y,par,bins=bins,statistic=statistic)
    
    y_g,x_g=np.meshgrid(stat_diffpar.y_edge, stat_diffpar.x_edge)
    
    fig, ax=plt.subplots(figsize=figsize)
    im=ax.pcolormesh(x_g, y_g, stat_diffpar.statistic,cmap=cm.Spectral,vmin=vmin, vmax=vmax)
    fig.colorbar(im, ax=ax)
    ax.set_facecolor('grey')
    ax.set_title(name)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    return fig




def prior_comp(par_binned, par, mock_par, n_lim=3, figsize=(15,10), limits=[None, None, None],name_binned_par=''):
    
    idx_fin=np.isfinite(par*mock_par)
    #par=par[idx_fin]
    #mock_par=mock_par[idx_fin]
    idx_nofin= ~idx_fin
    par[idx_nofin]=6.0
    mock_par[idx_nofin]=6.0
    print('total deleted (no finite values):', np.sum(idx_nofin))
    
    fig, axs=plt.subplots(2,2,figsize=figsize)
    
    
    median=np.median(par)
    istpar_tot=np.histogram(par,bins=50)
    frac_partot=istpar_tot[0]/np.size(par)
    frac_partot=np.append(frac_partot[0],frac_partot)

    
    _i=np.argwhere(par_binned<limits[0])
    _idx=_i.reshape(np.shape(_i)[0])
    istpar=np.histogram(par[_idx], bins=50)
    istmock=np.histogram(mock_par[_idx], bins=50)
    frac_par=istpar[0]/np.size(par[_idx])
    frac_mock=istmock[0]/np.size(mock_par[_idx])
    frac_par=np.append(frac_par[0],frac_par)
    frac_mock=np.append(frac_mock[0], frac_mock)
    axs[0,0].step(istpar_tot[1],frac_partot, label='total')
    axs[0,0].step(istpar[1], frac_par, label='par')
    axs[0,0].step(istmock[1], frac_mock, label='mock')
    axs[0,0].legend(loc='upper right')
    axs[0,0].plot([median, median], axs[0,0].get_ylim())
    axs[0,0].set_title(name_binned_par+'<'+str(limits[0]))  
    
    _i=np.argwhere(np.logical_and((par_binned<limits[1]),(par_binned>limits[0])))
    _idx=_i.reshape(np.shape(_i)[0])
    istpar=np.histogram(par[_idx], bins=50)
    istmock=np.histogram(mock_par[_idx], bins=50)
    frac_par=istpar[0]/np.size(par[_idx])
    frac_mock=istmock[0]/np.size(mock_par[_idx])
    frac_par=np.append(frac_par[0],frac_par)
    frac_mock=np.append(frac_mock[0], frac_mock)
    axs[0,1].step(istpar_tot[1],frac_partot,label='total')
    axs[0,1].step(istpar[1], frac_par,label='par')
    axs[0,1].step(istmock[1], frac_mock,label='mock')
    axs[0,1].legend(loc='upper right')
    axs[0,1].plot([median, median], axs[0,1].get_ylim())
    axs[0,1].set_title(str(limits[0])+'<'+name_binned_par+'<'+str(limits[1]))

    
    _i=np.argwhere( np.logical_and((par_binned<limits[2]),(par_binned>limits[1])) )
    _idx=_i.reshape(np.shape(_i)[0])
    istpar=np.histogram(par[_idx], bins=50)
    istmock=np.histogram(mock_par[_idx], bins=50)
    frac_par=istpar[0]/np.size(par[_idx])
    frac_mock=istmock[0]/np.size(mock_par[_idx])
    frac_par=np.append(frac_par[0],frac_par)
    frac_mock=np.append(frac_mock[0], frac_mock)
    axs[1,0].step(istpar_tot[1],frac_partot,label='total')
    axs[1,0].step(istpar[1], frac_par,label='par')
    axs[1,0].step(istmock[1], frac_mock,label='mock')
    axs[1,0].legend(loc='upper right')
    axs[1,0].plot([median, median], axs[1,0].get_ylim())
    axs[1,0].set_title(str(limits[1])+'<'+name_binned_par+'<'+str(limits[2]))

    
    _i=np.argwhere(par_binned>limits[2])
    _idx=_i.reshape(np.shape(_i)[0])
    istpar=np.histogram(par[_idx], bins=50)
    istmock=np.histogram(mock_par[_idx], bins=50)
    frac_par=istpar[0]/np.size(par[_idx])
    frac_mock=istmock[0]/np.size(mock_par[_idx])
    frac_par=np.append(frac_par[0],frac_par)
    frac_mock=np.append(frac_mock[0], frac_mock)
    axs[1,1].step(istpar_tot[1],frac_partot,label='total')
    axs[1,1].step(istpar[1], frac_par,label='par')
    axs[1,1].step(istmock[1], frac_mock,label='mock')
    axs[1,1].legend(loc='upper right')
    axs[1,1].plot([median, median], axs[1,1].get_ylim())
    axs[1,1].set_title(name_binned_par+'>'+str(limits[2]))


    return fig

def scatter_comp(par_binned, par, mock_par, limits=[None, None, None], figsize=(15,10), name_binned_par=''):
    
    idx_fin=np.isfinite(par*mock_par)
    #par=par[idx_fin]
    #mock_par=mock_par[idx_fin]
    idx_nofin= ~idx_fin
    par[idx_nofin]=6.0
    mock_par[idx_nofin]=6.0
    print('total deleted (no finite values):', np.sum(idx_nofin))
    
    fig, axs=plt.subplots(2,2,figsize=figsize)
    
    _i=np.argwhere(par_binned<limits[0])
    _idx=_i.reshape(np.shape(_i)[0])
    axs[0,0].scatter(par[_idx], mock_par[_idx], s=0.1)
    axs[0,0].plot([5.8,10.5], [5.8,10.5], color='red')
    axs[0,0].set_title(name_binned_par+'<'+str(limits[0]))


    
    _i=np.argwhere(np.logical_and((par_binned<limits[1]),(par_binned>limits[0])))
    _idx=_i.reshape(np.shape(_i)[0])
    axs[0,1].scatter(par[_idx], mock_par[_idx], s=0.1)
    axs[0,1].plot([5.8,10.5], [5.8,10.5], color='red')
    axs[0,1].set_title(str(limits[0])+'<'+name_binned_par+'<'+str(limits[1]))

   
    _i=np.argwhere( np.logical_and((par_binned<limits[2]),(par_binned>limits[1])) )
    _idx=_i.reshape(np.shape(_i)[0])
    axs[1,0].scatter(par[_idx], mock_par[_idx], s=0.1)
    axs[1,0].plot([5.8,10.5], [5.8,10.5], color='red')
    axs[1,0].set_title(str(limits[1])+'<'+name_binned_par+'<'+str(limits[2]))


    _i=np.argwhere(par_binned>limits[2])
    _idx=_i.reshape(np.shape(_i)[0])
    axs[1,1].scatter(par[_idx], mock_par[_idx], s=0.8)
    axs[1,1].plot([5.8,10.5], [5.8,10.5], color='red')
    axs[1,1].set_title(name_binned_par+'>'+str(limits[2]))

    
    axs[0,0].set_ylabel('out')
    axs[1,0].set_ylabel('out')
    axs[1,0].set_xlabel('in')
    axs[1,1].set_xlabel('in')
    return fig

def scatter_norm(par_binned, par, mock_par, limits=[None, None, None], figsize=(15, 10), name_binned_par='', name_par=''):
    
    idx_fin=np.isfinite(par*mock_par)
    #par=par[idx_fin]
    #mock_par=mock_par[idx_fin]
    idx_nofin= ~idx_fin
    par[idx_nofin]=6.0
    mock_par[idx_nofin]=6.0
    print('total deleted (no finite values):', np.sum(idx_nofin))
    
    fig,axs=plt.subplots(1,2,figsize=figsize)
    
    median_tot=np.median(par)
    median_arr=[0.0]*4
    mock_median_arr=[0.0]*4
    
    _i=np.argwhere(par_binned<limits[0])
    _idx=_i.reshape(np.shape(_i)[0])
    median_arr[0]=np.median(par[_idx])
    mock_median_arr[0]=np.median(mock_par[_idx])
    _medpar_arr=[median_arr[0]]*np.size(par[_idx])
    _medmock_arr=[mock_median_arr[0]]*np.size(mock_par[_idx])
    axs[0].scatter(par[_idx], mock_par[_idx], color='red', s=0.6)
    axs[1].scatter(par[_idx]-_medpar_arr,mock_par[_idx]-_medmock_arr, color='blue', s=0.6)

    
    _i=np.argwhere(np.logical_and((par_binned<limits[1]),(par_binned>limits[0])))
    _idx=_i.reshape(np.shape(_i)[0])
    median_arr[1]=np.median(par[_idx])
    mock_median_arr[1]=np.median(mock_par[_idx])
    _medpar_arr=[median_arr[1]]*np.size(par[_idx])
    _medmock_arr=[mock_median_arr[1]]*np.size(mock_par[_idx])
    axs[0].scatter(par[_idx], mock_par[_idx], color='orange',s=0.6)
    axs[1].scatter(par[_idx]-_medpar_arr,mock_par[_idx]-_medmock_arr, color='blue', s=0.6)

    
    _i=np.argwhere( np.logical_and((par_binned<limits[2]),(par_binned>limits[1])) )
    _idx=_i.reshape(np.shape(_i)[0])
    median_arr[2]=np.median(par[_idx])
    mock_median_arr[2]=np.median(mock_par[_idx])
    _medpar_arr=[median_arr[2]]*np.size(par[_idx])
    _medmock_arr=[mock_median_arr[2]]*np.size(mock_par[_idx])
    axs[0].scatter(par[_idx], mock_par[_idx], color='violet',s=0.6)
    axs[1].scatter(par[_idx]-_medpar_arr,mock_par[_idx]-_medmock_arr, color='blue', s=0.6)


    _i=np.argwhere(par_binned>limits[2])
    _idx=_i.reshape(np.shape(_i)[0])
    median_arr[3]=np.median(par[_idx])
    mock_median_arr[3]=np.median(mock_par[_idx]) 
    _medpar_arr=[median_arr[3]]*np.size(par[_idx])
    _medmock_arr=[mock_median_arr[3]]*np.size(mock_par[_idx])
    axs[0].scatter(par[_idx], mock_par[_idx], color='blue',s=0.6)
    axs[1].scatter(par[_idx]-_medpar_arr,mock_par[_idx]-_medmock_arr, color='blue', s=0.6)


    #axs.scatter(par, mock_par, s=0.8)
    axs[0].scatter(median_arr[0], mock_median_arr[0], color='red',s=100, marker="X", label=name_binned_par+'<'+str(limits[0]))
    axs[0].scatter(median_arr[1], mock_median_arr[1], color='orange',s=100, marker="X", label=str(limits[0])+'<'+name_binned_par+'<'+str(limits[1]))    
    axs[0].scatter(median_arr[2], mock_median_arr[2], color='violet',s=100, marker="X", label=str(limits[1])+'<'+name_binned_par+'<'+str(limits[2]))
    axs[0].scatter(median_arr[3], mock_median_arr[3], color='blue',s=100, marker="X", label=name_binned_par+'>'+str(limits[2]))
    axs[0].plot([median_tot, median_tot], axs[0].get_ylim(), color='red')
    axs[1].plot([0.0, 0.0], axs[1].get_ylim(), color='red')
    axs[1].plot(axs[1].get_xlim(), [0.0, 0.0], color='red')
    axs[1].plot(axs[1].get_xlim(), axs[1].get_xlim(), color='red')

    axs[0].set_xlabel(name_par+'_in')
    axs[0].set_ylabel(name_par+'_out')
    axs[0].legend(loc='upper left')
    axs[1].set_xlabel(name_par+'_in-median')
    axs[1].set_ylabel(name_par+'_out-median')
    
def idx_resol(par, idx_1, idx_2, idx_3, idx_4, idx_5,par_name='', idx_name=['','','','',''], figsize=(10,5),s=1):
    
    fig, axs=plt.subplots(2, 3, figsize=figsize)
    
    axs[0,0].scatter(par, idx_1, s=s)
    axs[0,1].scatter(par, idx_2, s=s)
    axs[0,2].scatter(par, idx_3, s=s)
    axs[1,0].scatter(par, idx_4, s=s)
    axs[1,1].scatter(par, idx_5, s=s)
    
    axs[0,0].set_xlabel(par_name)
    axs[0,1].set_xlabel(par_name)
    axs[0,2].set_xlabel(par_name)
    axs[1,0].set_xlabel(par_name)
    axs[1,1].set_xlabel(par_name)
    
    axs[0,0].set_ylabel(idx_name[0])
    axs[0,1].set_ylabel(idx_name[1])
    axs[0,2].set_ylabel(idx_name[2])
    axs[1,0].set_ylabel(idx_name[3])
    axs[1,1].set_ylabel(idx_name[4])
    
    axs[1,2].axis('off')
    return fig
    
def idx_resol_stat(par,idx_1, idx_2, idx_3, idx_4,  idx_5,par_name='', idx_name=['','','','',''],statistic='median',bins=50, figsize=(10,5),s=1):
    
    fig, axs=plt.subplots(2, 3, figsize=figsize)
    axs[1,2].axis('off')
    
    stat_1=stats.binned_statistic(par, idx_1, statistic=statistic, bins=bins)
    stat_2=stats.binned_statistic(par, idx_2, statistic=statistic, bins=bins)
    stat_3=stats.binned_statistic(par, idx_3, statistic=statistic, bins=bins)
    stat_4=stats.binned_statistic(par, idx_4, statistic=statistic, bins=bins)
    stat_5=stats.binned_statistic(par, idx_5, statistic=statistic, bins=bins)
    
    
    axs[0,0].plot(stat_1.bin_edges[:-1],stat_1.statistic)
    axs[0,1].plot(stat_2.bin_edges[:-1],stat_2.statistic)
    axs[0,2].plot(stat_3.bin_edges[:-1],stat_3.statistic)
    axs[1,0].plot(stat_4.bin_edges[:-1],stat_4.statistic)
    axs[1,1].plot(stat_5.bin_edges[:-1],stat_5.statistic)
    
    axs[0,0].set_xlabel(par_name)
    axs[0,1].set_xlabel(par_name)
    axs[0,2].set_xlabel(par_name)
    axs[1,0].set_xlabel(par_name)
    axs[1,1].set_xlabel(par_name)
    
    axs[0,0].set_ylabel(idx_name[0])
    axs[0,1].set_ylabel(idx_name[1])
    axs[0,2].set_ylabel(idx_name[2])
    axs[1,0].set_ylabel(idx_name[3])
    axs[1,1].set_ylabel(idx_name[4])
    return fig
    
    
def idx_resol_stat4(par,i2,i3,i4,idx_1, idx_2, idx_3, idx_4,  idx_5,x_name='',par_name=['','',''], idx_name=['','','','',''],statistic='median',bins=50, figsize=(10,5),s=1):
    
    fig, axs=plt.subplots(2, 3, figsize=figsize)
    axs[1,2].axis('off')
    
    par2=par[i2]
    par3=par[i3]
    par4=par[i4]
    
    
    
    idx2_1=idx_1[i2]
    idx2_2=idx_2[i2]
    idx2_3=idx_3[i2]
    idx2_4=idx_4[i2]
    idx2_5=idx_5[i2]
    
    idx3_1=idx_1[i3]
    idx3_2=idx_2[i3]
    idx3_3=idx_3[i3]
    idx3_4=idx_4[i3]
    idx3_5=idx_5[i3]
    
    idx4_1=idx_1[i4]
    idx4_2=idx_2[i4]
    idx4_3=idx_3[i4]
    idx4_4=idx_4[i4]
    idx4_5=idx_5[i4]
    
    
    
    stat2_1=stats.binned_statistic(par2, idx2_1, statistic=statistic, bins=bins)
    stat2_2=stats.binned_statistic(par2, idx2_2, statistic=statistic, bins=bins)
    stat2_3=stats.binned_statistic(par2, idx2_3, statistic=statistic, bins=bins)
    stat2_4=stats.binned_statistic(par2, idx2_4, statistic=statistic, bins=bins)
    stat2_5=stats.binned_statistic(par2, idx2_5, statistic=statistic, bins=bins)
    
    stat3_1=stats.binned_statistic(par3, idx3_1, statistic=statistic, bins=bins)
    stat3_2=stats.binned_statistic(par3, idx3_2, statistic=statistic, bins=bins)
    stat3_3=stats.binned_statistic(par3, idx3_3, statistic=statistic, bins=bins)
    stat3_4=stats.binned_statistic(par3, idx3_4, statistic=statistic, bins=bins)
    stat3_5=stats.binned_statistic(par3, idx3_5, statistic=statistic, bins=bins)
    
    stat4_1=stats.binned_statistic(par4, idx4_1, statistic=statistic, bins=bins)
    stat4_2=stats.binned_statistic(par4, idx4_2, statistic=statistic, bins=bins)
    stat4_3=stats.binned_statistic(par4, idx4_3, statistic=statistic, bins=bins)
    stat4_4=stats.binned_statistic(par4, idx4_4, statistic=statistic, bins=bins)
    stat4_5=stats.binned_statistic(par4, idx4_5, statistic=statistic, bins=bins)
    
    
    
    axs[0,0].plot(stat2_1.bin_edges[:-1],stat2_1.statistic, label=par_name[0])
    axs[0,1].plot(stat2_2.bin_edges[:-1],stat2_2.statistic, label=par_name[0])
    axs[0,2].plot(stat2_3.bin_edges[:-1],stat2_3.statistic, label=par_name[0])
    axs[1,0].plot(stat2_4.bin_edges[:-1],stat2_4.statistic, label=par_name[0])
    axs[1,1].plot(stat2_5.bin_edges[:-1],stat2_5.statistic, label=par_name[0])
    
    axs[0,0].plot(stat3_1.bin_edges[:-1],stat3_1.statistic, label=par_name[1])
    axs[0,1].plot(stat3_2.bin_edges[:-1],stat3_2.statistic, label=par_name[1])
    axs[0,2].plot(stat3_3.bin_edges[:-1],stat3_3.statistic, label=par_name[1])
    axs[1,0].plot(stat3_4.bin_edges[:-1],stat3_4.statistic, label=par_name[1])
    axs[1,1].plot(stat3_5.bin_edges[:-1],stat3_5.statistic, label=par_name[1])
    
    axs[0,0].plot(stat4_1.bin_edges[:-1],stat4_1.statistic, label=par_name[2])
    axs[0,1].plot(stat4_2.bin_edges[:-1],stat4_2.statistic, label=par_name[2])
    axs[0,2].plot(stat4_3.bin_edges[:-1],stat4_3.statistic, label=par_name[2])
    axs[1,0].plot(stat4_4.bin_edges[:-1],stat4_4.statistic, label=par_name[2])
    axs[1,1].plot(stat4_5.bin_edges[:-1],stat4_5.statistic, label=par_name[2])
    
    
    axs[0,0].set_xlabel(x_name)
    axs[0,1].set_xlabel(x_name)
    axs[0,2].set_xlabel(x_name)
    axs[1,0].set_xlabel(x_name)
    axs[1,1].set_xlabel(x_name)
    
    axs[0,0].set_ylabel(idx_name[0])
    axs[0,1].set_ylabel(idx_name[1])
    axs[0,2].set_ylabel(idx_name[2])
    axs[1,0].set_ylabel(idx_name[3])
    axs[1,1].set_ylabel(idx_name[4])
    
    axs[0,0].legend(loc='upper right')
    axs[0,1].legend(loc='upper left')
    axs[0,2].legend(loc='upper right')
    axs[1,0].legend(loc='upper right')
    axs[1,1].legend(loc='upper left')
    
    return fig


def idx_resol_stat4col(par,i2,i3,i4,idx_1, idx_2, idx_3, idx_4, x_name='d1090n50',par_name=['age50<9.0','age50_9.0-9.5','age50>9.5'], idx_name=['u-r','g-r','r-i','r-z'],statistic='median',bins=50, figsize=(10,5),s=1):
    
    fig, axs=plt.subplots(2, 3, figsize=figsize)
    axs[1,2].axis('off')
    axs[1,1].axis('off')
    
    par2=par[i2]
    par3=par[i3]
    par4=par[i4]
    
    
    
    idx2_1=idx_1[i2]
    idx2_2=idx_2[i2]
    idx2_3=idx_3[i2]
    idx2_4=idx_4[i2]
    
    idx3_1=idx_1[i3]
    idx3_2=idx_2[i3]
    idx3_3=idx_3[i3]
    idx3_4=idx_4[i3]
    
    idx4_1=idx_1[i4]
    idx4_2=idx_2[i4]
    idx4_3=idx_3[i4]
    idx4_4=idx_4[i4]
    
    
    
    stat2_1=stats.binned_statistic(par2, idx2_1, statistic=statistic, bins=bins)
    stat2_2=stats.binned_statistic(par2, idx2_2, statistic=statistic, bins=bins)
    stat2_3=stats.binned_statistic(par2, idx2_3, statistic=statistic, bins=bins)
    stat2_4=stats.binned_statistic(par2, idx2_4, statistic=statistic, bins=bins)
    
    stat3_1=stats.binned_statistic(par3, idx3_1, statistic=statistic, bins=bins)
    stat3_2=stats.binned_statistic(par3, idx3_2, statistic=statistic, bins=bins)
    stat3_3=stats.binned_statistic(par3, idx3_3, statistic=statistic, bins=bins)
    stat3_4=stats.binned_statistic(par3, idx3_4, statistic=statistic, bins=bins)
    
    stat4_1=stats.binned_statistic(par4, idx4_1, statistic=statistic, bins=bins)
    stat4_2=stats.binned_statistic(par4, idx4_2, statistic=statistic, bins=bins)
    stat4_3=stats.binned_statistic(par4, idx4_3, statistic=statistic, bins=bins)
    stat4_4=stats.binned_statistic(par4, idx4_4, statistic=statistic, bins=bins)
    
    
    
    axs[0,0].plot(stat2_1.bin_edges[:-1],stat2_1.statistic, label=par_name[0])
    axs[0,1].plot(stat2_2.bin_edges[:-1],stat2_2.statistic, label=par_name[0])
    axs[0,2].plot(stat2_3.bin_edges[:-1],stat2_3.statistic, label=par_name[0])
    axs[1,0].plot(stat2_4.bin_edges[:-1],stat2_4.statistic, label=par_name[0])
    
    axs[0,0].plot(stat3_1.bin_edges[:-1],stat3_1.statistic, label=par_name[1])
    axs[0,1].plot(stat3_2.bin_edges[:-1],stat3_2.statistic, label=par_name[1])
    axs[0,2].plot(stat3_3.bin_edges[:-1],stat3_3.statistic, label=par_name[1])
    axs[1,0].plot(stat3_4.bin_edges[:-1],stat3_4.statistic, label=par_name[1])
    
    axs[0,0].plot(stat4_1.bin_edges[:-1],stat4_1.statistic, label=par_name[2])
    axs[0,1].plot(stat4_2.bin_edges[:-1],stat4_2.statistic, label=par_name[2])
    axs[0,2].plot(stat4_3.bin_edges[:-1],stat4_3.statistic, label=par_name[2])
    axs[1,0].plot(stat4_4.bin_edges[:-1],stat4_4.statistic, label=par_name[2])
    
    
    axs[0,0].set_xlabel(x_name)
    axs[0,1].set_xlabel(x_name)
    axs[0,2].set_xlabel(x_name)
    axs[1,0].set_xlabel(x_name)
    
    axs[0,0].set_ylabel(idx_name[0])
    axs[0,1].set_ylabel(idx_name[1])
    axs[0,2].set_ylabel(idx_name[2])
    axs[1,0].set_ylabel(idx_name[3])
    
    axs[0,0].legend(loc='upper right')
    axs[0,1].legend(loc='upper left')
    axs[0,2].legend(loc='upper right')
    axs[1,0].legend(loc='upper right')
    
    return fig
    
    
def chi_q(par,idx1, idx2, idx3, idx4, idx5, mag1, mag2, mag3, mag4, isel, iref,figsize=(15,10), title='', ylim=[None,None], xlim=[None, None], bins=50, xmin=-0.75, xmax=1.0, toll=0.1):
    import function_plot as f_plt
    fig, axs=plt.subplots(1,3,figsize=figsize)
    
    par_sel=par[isel]
    
    idx1_sel=idx1[isel]
    idx2_sel=idx2[isel]
    idx3_sel=idx3[isel]
    idx4_sel=idx4[isel]
    idx5_sel=idx5[isel]
    
    idx1_ref=np.median(idx1[iref])
    idx2_ref=np.median(idx2[iref])
    idx3_ref=np.median(idx3[iref])
    idx4_ref=np.median(idx4[iref])
    idx5_ref=np.median(idx5[iref])
    
    mag1_sel=mag1[isel]
    mag2_sel=mag2[isel]
    mag3_sel=mag3[isel]
    mag4_sel=mag4[isel]
    
    
    mag1_ref=np.median(mag1[iref])
    mag2_ref=np.median(mag2[iref])
    mag3_ref=np.median(mag3[iref])
    mag4_ref=np.median(mag4[iref])
    
    
    sigma_idx1=f_plt.perc_84(idx1[iref])-f_plt.perc_16(idx1[iref])
    sigma_idx2=f_plt.perc_84(idx2[iref])-f_plt.perc_16(idx2[iref])
    sigma_idx3=f_plt.perc_84(idx3[iref])-f_plt.perc_16(idx3[iref])
    sigma_idx4=f_plt.perc_84(idx4[iref])-f_plt.perc_16(idx4[iref])
    sigma_idx5=f_plt.perc_84(idx5[iref])-f_plt.perc_16(idx5[iref])
    
    sigma_mag1=f_plt.perc_84(mag1[iref])-f_plt.perc_16(mag1[iref])
    sigma_mag2=f_plt.perc_84(mag2[iref])-f_plt.perc_16(mag2[iref])
    sigma_mag3=f_plt.perc_84(mag3[iref])-f_plt.perc_16(mag3[iref])
    sigma_mag4=f_plt.perc_84(mag4[iref])-f_plt.perc_16(mag4[iref])
    
    
    chi_q_idx=((idx1_sel-idx1_ref)/sigma_idx1)**2+((idx2_sel-idx2_ref)/sigma_idx2)**2+((idx3_sel-idx3_ref)/sigma_idx3)**2+((idx4_sel-idx4_ref)/sigma_idx4)**2+((idx5_sel-idx5_ref)/sigma_idx5)**2
    chi_q_mag=((mag1_sel-mag1_ref)/sigma_mag1)**2+((mag2_sel-mag2_ref)/sigma_mag2)**2+((mag3_sel-mag3_ref)/sigma_mag3)**2+((mag4_sel-mag4_ref)/sigma_mag4)**2

    chi_q=chi_q_idx+chi_q_mag

    median_chi_idx=stats.binned_statistic(par_sel, chi_q_idx, statistic='median', bins=bins)
    #chi_16_idx=stats.binned_statistic(par_sel, chi_q_idx, statistic=f_plt.perc_16, bins=50)
    #chi_84_idx=stats.binned_statistic(par_sel, chi_q_idx, statistic=f_plt.perc_84, bins=50)
    
    median_chi_mag=stats.binned_statistic(par_sel, chi_q_mag, statistic='median', bins=bins)
    #chi_16_mag=stats.binned_statistic(par_sel, chi_q_mag, statistic=f_plt.perc_16, bins=50)
    #chi_84_mag=stats.binned_statistic(par_sel, chi_q_mag, statistic=f_plt.perc_84, bins=50)
    
    median_chi=stats.binned_statistic(par_sel, chi_q, statistic='median', bins=bins)
    #chi_16=stats.binned_statistic(par_sel, chi_q, statistic=f_plt.perc_16, bins=50)
    #chi_84=stats.binned_statistic(par_sel, chi_q, statistic=f_plt.perc_84, bins=50)
    
    idx_ref_chi=np.where(par_sel<-0.75)[0]
    median_chi_ref=np.median(chi_q[idx_ref_chi])
    p84_chi_ref=f_plt.perc_84(chi_q[idx_ref_chi])
    p16_chi_ref=f_plt.perc_16(chi_q[idx_ref_chi])
    
    median_chi_ref_idx=np.median(chi_q_idx[idx_ref_chi])
    p84_chi_ref_idx=f_plt.perc_84(chi_q_idx[idx_ref_chi])
    p16_chi_ref_idx=f_plt.perc_16(chi_q_idx[idx_ref_chi])
    
    median_chi_ref_mag=np.median(chi_q_mag[idx_ref_chi])
    p84_chi_ref_mag=f_plt.perc_84(chi_q_mag[idx_ref_chi])
    p16_chi_ref_mag=f_plt.perc_16(chi_q_mag[idx_ref_chi])
    
    x=[0.0]*bins
    
    for i in range(0,bins):
        x[i]=(median_chi.bin_edges[i+1]+median_chi.bin_edges[i])/2.0
    
    axs[0].scatter(par_sel,(chi_q),s=1)
    axs[0].plot(x, (median_chi.statistic), color='red')
    #axs[0].plot(chi_16.bin_edges[:-1], chi_16.statistic, color='red')
    #axs[0].plot(chi_84.bin_edges[:-1], chi_84.statistic, color='red')
    
    axs[0].plot([np.min(par_sel), np.max(par_sel)], [median_chi_ref, median_chi_ref], color='orange')
    axs[0].plot([np.min(par_sel), np.max(par_sel)], [p84_chi_ref, p84_chi_ref],color='#ff028d')
    axs[0].plot([np.min(par_sel), np.max(par_sel)],[p16_chi_ref,p16_chi_ref], color='#ff028d')
    axs[0].set_yscale("log")
    
    axs[0].set_ylim(ylim)
    
    axs[0].set_xlabel('d1090n50')
    axs[0].set_ylabel('chi_q')
    
    axs[1].scatter(par_sel,(chi_q_idx),s=1)
    axs[1].plot(x, (median_chi_idx.statistic), color='red')
    #axs[1].plot(chi_16_idx.bin_edges[:-1], chi_16_idx.statistic, color='red')
    #axs[1].plot(chi_84_idx.bin_edges[:-1], chi_84_idx.statistic, color='red')
    
    axs[1].plot([np.min(par_sel), np.max(par_sel)], [median_chi_ref_idx, median_chi_ref_idx], color='orange')
    axs[1].plot([np.min(par_sel), np.max(par_sel)], [p84_chi_ref_idx, p84_chi_ref_idx],color='#ff028d')
    axs[1].plot([np.min(par_sel), np.max(par_sel)],[p16_chi_ref_idx,p16_chi_ref_idx], color='#ff028d')
    

    axs[1].set_xlabel('d1090n50')
    axs[1].set_ylabel('chi_q_idx')
    
    axs[1].set_yscale("log")
    axs[1].set_ylim(ylim)

    
    axs[2].scatter(par_sel,(chi_q_mag),s=1)
    axs[2].plot(x, (median_chi_mag.statistic), color='red')
    #axs[2].plot(chi_16_mag.bin_edges[:-1], chi_16_mag.statistic, color='red')
    #axs[2].plot(chi_84_mag.bin_edges[:-1], chi_84_mag.statistic, color='red')
    
    axs[2].plot([np.min(par_sel), np.max(par_sel)], [median_chi_ref_mag, median_chi_ref_mag], color='orange')
    axs[2].plot([np.min(par_sel), np.max(par_sel)], [p84_chi_ref_mag, p84_chi_ref_mag],color='#ff028d')
    axs[2].plot([np.min(par_sel), np.max(par_sel)],[p16_chi_ref_mag,p16_chi_ref_mag], color='#ff028d')
    
    axs[2].set_yscale("log")
    axs[2].set_ylim(ylim)
    
    axs[2].set_xlabel('d1090n50')
    axs[2].set_ylabel('chi_q_col')
    
    axs[0].set_facecolor('#d8dcd6')
    axs[1].set_facecolor('#d8dcd6')
    axs[2].set_facecolor('#d8dcd6')

    axs[1].set_title(title)
    
    #inter_max=np.interp(xmax,x, median_chi.statistic)
    #inter_min=np.interp(xmin, x, median_chi.statistic)
    inter_chi=lambda t: np.interp(t, x, median_chi.statistic-p84_chi_ref)
    x_m=f_plt.bisection(inter_chi, xmin, xmax, toll)
    axs[0].scatter(x_m, inter_chi(x_m)+p84_chi_ref, s=20, color='red')
    
    print('d1090n50 limit:', x_m)
    
    return fig, x_m



def chi_q_num(par,idx1, idx2, idx3, idx4, idx5, mag1, mag2, mag3, mag4, isel, iref, bins=50, xmin=-0.75, xmax=1.0, toll=0.1):
    import function_plot as f_plt
    
    par_sel=par[isel]
    
    idx1_sel=idx1[isel]
    idx2_sel=idx2[isel]
    idx3_sel=idx3[isel]
    idx4_sel=idx4[isel]
    idx5_sel=idx5[isel]
    
    idx1_ref=np.median(idx1[iref])
    idx2_ref=np.median(idx2[iref])
    idx3_ref=np.median(idx3[iref])
    idx4_ref=np.median(idx4[iref])
    idx5_ref=np.median(idx5[iref])
    
    mag1_sel=mag1[isel]
    mag2_sel=mag2[isel]
    mag3_sel=mag3[isel]
    mag4_sel=mag4[isel]
    
    
    mag1_ref=np.median(mag1[iref])
    mag2_ref=np.median(mag2[iref])
    mag3_ref=np.median(mag3[iref])
    mag4_ref=np.median(mag4[iref])
    
    
    sigma_idx1=f_plt.perc_84(idx1[iref])-f_plt.perc_16(idx1[iref])
    sigma_idx2=f_plt.perc_84(idx2[iref])-f_plt.perc_16(idx2[iref])
    sigma_idx3=f_plt.perc_84(idx3[iref])-f_plt.perc_16(idx3[iref])
    sigma_idx4=f_plt.perc_84(idx4[iref])-f_plt.perc_16(idx4[iref])
    sigma_idx5=f_plt.perc_84(idx5[iref])-f_plt.perc_16(idx5[iref])
    
    sigma_mag1=f_plt.perc_84(mag1[iref])-f_plt.perc_16(mag1[iref])
    sigma_mag2=f_plt.perc_84(mag2[iref])-f_plt.perc_16(mag2[iref])
    sigma_mag3=f_plt.perc_84(mag3[iref])-f_plt.perc_16(mag3[iref])
    sigma_mag4=f_plt.perc_84(mag4[iref])-f_plt.perc_16(mag4[iref])
    
    
    chi_q_idx=((idx1_sel-idx1_ref)/sigma_idx1)**2+((idx2_sel-idx2_ref)/sigma_idx2)**2+((idx3_sel-idx3_ref)/sigma_idx3)**2+((idx4_sel-idx4_ref)/sigma_idx4)**2+((idx5_sel-idx5_ref)/sigma_idx5)**2
    chi_q_mag=((mag1_sel-mag1_ref)/sigma_mag1)**2+((mag2_sel-mag2_ref)/sigma_mag2)**2+((mag3_sel-mag3_ref)/sigma_mag3)**2+((mag4_sel-mag4_ref)/sigma_mag4)**2

    chi_q=chi_q_idx+chi_q_mag

   
    median_chi=stats.binned_statistic(par_sel, chi_q, statistic='median', bins=bins)
    #chi_16=stats.binned_statistic(par_sel, chi_q, statistic=f_plt.perc_16, bins=50)
    #chi_84=stats.binned_statistic(par_sel, chi_q, statistic=f_plt.perc_84, bins=50)
    
    idx_ref_chi=np.where(par_sel<-0.75)[0]
    p84_chi_ref=f_plt.perc_84(chi_q[idx_ref_chi])
    
   
    x=[0.0]*bins
    
    for i in range(0,bins):
        x[i]=(median_chi.bin_edges[i+1]+median_chi.bin_edges[i])/2.0
    
   
    #inter_max=np.interp(xmax,x, median_chi.statistic)
    #inter_min=np.interp(xmin, x, median_chi.statistic)
    inter_chi=lambda t: np.interp(t, x, median_chi.statistic-p84_chi_ref)
    x_m=f_plt.bisection(inter_chi, xmin, xmax, toll)
    
    print('d1090n50 limit:', x_m)
    
    return x_m


def chi_q_comp_idx(par,idx1, idx2, idx3, idx4, idx5,isel, iref, name_par='d1090n50', name_idx=['D4000n','HdHg','Hb','Mg2Fe','MgFep'],figsize=(15,10), title='', ylim=[None,None], xlim=[None, None], bins=50):
    
    import function_plot as f_plt
    fig, axs=plt.subplots(2,3,figsize=figsize)    
    axs[1,2].axis('off')
    
    par_sel=par[isel]
    
    idx1_sel=idx1[isel]
    idx2_sel=idx2[isel]
    idx3_sel=idx3[isel]
    idx4_sel=idx4[isel]
    idx5_sel=idx5[isel]
    
    idx1_ref=np.median(idx1[iref])
    idx2_ref=np.median(idx2[iref])
    idx3_ref=np.median(idx3[iref])
    idx4_ref=np.median(idx4[iref])
    idx5_ref=np.median(idx5[iref])

   
    sigma_idx1=f_plt.perc_84(idx1[iref])-f_plt.perc_16(idx1[iref])
    sigma_idx2=f_plt.perc_84(idx2[iref])-f_plt.perc_16(idx2[iref])
    sigma_idx3=f_plt.perc_84(idx3[iref])-f_plt.perc_16(idx3[iref])
    sigma_idx4=f_plt.perc_84(idx4[iref])-f_plt.perc_16(idx4[iref])
    sigma_idx5=f_plt.perc_84(idx5[iref])-f_plt.perc_16(idx5[iref])

    chi_q1=((idx1_sel-idx1_ref)/sigma_idx1)**2
    chi_q2=((idx2_sel-idx2_ref)/sigma_idx2)**2
    chi_q3=((idx3_sel-idx3_ref)/sigma_idx3)**2
    chi_q4=((idx4_sel-idx4_ref)/sigma_idx4)**2
    chi_q5=((idx5_sel-idx5_ref)/sigma_idx5)**2
    
    idx_ref_chi=np.where(par_sel<-0.75)[0]
    
    median_chi_ref1=np.median(chi_q1[idx_ref_chi])
    p84_chi_ref1=f_plt.perc_84(chi_q1[idx_ref_chi])
    p16_chi_ref1=f_plt.perc_16(chi_q1[idx_ref_chi])

    median_chi_ref2=np.median(chi_q2[idx_ref_chi])
    p84_chi_ref2=f_plt.perc_84(chi_q2[idx_ref_chi])
    p16_chi_ref2=f_plt.perc_16(chi_q2[idx_ref_chi])
    
    median_chi_ref3=np.median(chi_q3[idx_ref_chi])
    p84_chi_ref3=f_plt.perc_84(chi_q3[idx_ref_chi])
    p16_chi_ref3=f_plt.perc_16(chi_q3[idx_ref_chi])
    
    median_chi_ref4=np.median(chi_q4[idx_ref_chi])
    p84_chi_ref4=f_plt.perc_84(chi_q4[idx_ref_chi])
    p16_chi_ref4=f_plt.perc_16(chi_q4[idx_ref_chi])
    
    median_chi_ref5=np.median(chi_q5[idx_ref_chi])
    p84_chi_ref5=f_plt.perc_84(chi_q5[idx_ref_chi])
    p16_chi_ref5=f_plt.perc_16(chi_q5[idx_ref_chi])

    median_chi_idx1=stats.binned_statistic(par_sel, chi_q1, statistic='median', bins=bins)
    median_chi_idx2=stats.binned_statistic(par_sel, chi_q2, statistic='median', bins=bins)
    median_chi_idx3=stats.binned_statistic(par_sel, chi_q3, statistic='median', bins=bins)
    median_chi_idx4=stats.binned_statistic(par_sel, chi_q4, statistic='median', bins=bins)
    median_chi_idx5=stats.binned_statistic(par_sel, chi_q5, statistic='median', bins=bins)
    
    x=[0.0]*bins
    
    for i in range(0,bins):
        x[i]=(median_chi_idx1.bin_edges[i+1]+median_chi_idx1.bin_edges[i])/2.0

    axs[0,0].scatter(par_sel, chi_q1, s=1)
    axs[0,0].plot(x, median_chi_idx1.statistic, color='red')
    axs[0,0].plot([np.min(par_sel), np.max(par_sel)], [median_chi_ref1, median_chi_ref1], color='orange')
    axs[0,0].plot([np.min(par_sel), np.max(par_sel)], [p84_chi_ref1, p84_chi_ref1],color='#ff028d')
    axs[0,0].plot([np.min(par_sel), np.max(par_sel)],[p16_chi_ref1,p16_chi_ref1], color='#ff028d')
    axs[0,0].set_facecolor('#d8dcd6')
    axs[0,0].set_xlabel(name_par)
    axs[0,0].set_ylabel('chi_q '+name_idx[0])
    axs[0,0].set_ylim(ylim)
    axs[0,0].set_yscale("log")

    axs[0,1].scatter(par_sel, chi_q2, s=1)
    axs[0,1].plot(x, median_chi_idx2.statistic, color='red')
    axs[0,1].plot([np.min(par_sel), np.max(par_sel)], [median_chi_ref2, median_chi_ref2], color='orange')
    axs[0,1].plot([np.min(par_sel), np.max(par_sel)], [p84_chi_ref2, p84_chi_ref2],color='#ff028d')
    axs[0,1].plot([np.min(par_sel), np.max(par_sel)],[p16_chi_ref2,p16_chi_ref2], color='#ff028d')
    axs[0,1].set_facecolor('#d8dcd6')
    axs[0,1].set_xlabel(name_par)
    axs[0,1].set_ylabel('chi_q '+name_idx[1])
    axs[0,1].set_ylim(ylim)
    axs[0,1].set_title(title)
    axs[0,1].set_yscale("log")

    axs[0,2].scatter(par_sel, chi_q3, s=1)
    axs[0,2].plot(x, median_chi_idx3.statistic, color='red')
    axs[0,2].plot([np.min(par_sel), np.max(par_sel)], [median_chi_ref3, median_chi_ref3], color='orange')
    axs[0,2].plot([np.min(par_sel), np.max(par_sel)], [p84_chi_ref3, p84_chi_ref3],color='#ff028d')
    axs[0,2].plot([np.min(par_sel), np.max(par_sel)],[p16_chi_ref3,p16_chi_ref3], color='#ff028d')
    axs[0,2].set_facecolor('#d8dcd6')
    axs[0,2].set_xlabel(name_par)
    axs[0,2].set_ylabel('chi_q '+name_idx[2])
    axs[0,2].set_ylim(ylim)
    axs[0,2].set_yscale("log")
    
    axs[1,0].scatter(par_sel, chi_q4, s=1)
    axs[1,0].plot(x, median_chi_idx4.statistic, color='red')
    axs[1,0].plot([np.min(par_sel), np.max(par_sel)], [median_chi_ref4, median_chi_ref4], color='orange')
    axs[1,0].plot([np.min(par_sel), np.max(par_sel)], [p84_chi_ref4, p84_chi_ref4],color='#ff028d')
    axs[1,0].plot([np.min(par_sel), np.max(par_sel)],[p16_chi_ref4,p16_chi_ref4], color='#ff028d')
    axs[1,0].set_facecolor('#d8dcd6')
    axs[1,0].set_xlabel(name_par)
    axs[1,0].set_ylabel('chi_q '+name_idx[3])
    axs[1,0].set_ylim(ylim)
    axs[1,0].set_yscale("log")
    
    axs[1,1].scatter(par_sel, chi_q5, s=1)
    axs[1,1].plot(x, median_chi_idx5.statistic, color='red')
    axs[1,1].plot([np.min(par_sel), np.max(par_sel)], [median_chi_ref5, median_chi_ref5], color='orange')
    axs[1,1].plot([np.min(par_sel), np.max(par_sel)], [p84_chi_ref5, p84_chi_ref5],color='#ff028d')
    axs[1,1].plot([np.min(par_sel), np.max(par_sel)],[p16_chi_ref5,p16_chi_ref5], color='#ff028d')
    axs[1,1].set_facecolor('#d8dcd6')
    axs[1,1].set_xlabel(name_par)
    axs[1,1].set_ylabel('chi_q '+name_idx[4])
    axs[1,1].set_ylim(ylim)
    axs[1,1].set_yscale("log")
    
    return fig

def chi_q_comp_col(par,idx1, idx2, idx3, idx4,isel, iref, name_par='d1090n50', name_idx=['u-r','g-r','r-i','r-z'],figsize=(15,10), title='', ylim=[None,None], xlim=[None, None], bins=50):
    
    import function_plot as f_plt
    fig, axs=plt.subplots(2,3,figsize=figsize)    
    axs[1,2].axis('off')
    axs[1,1].axis('off')
    
    par_sel=par[isel]
    
    idx1_sel=idx1[isel]
    idx2_sel=idx2[isel]
    idx3_sel=idx3[isel]
    idx4_sel=idx4[isel]
        
    idx1_ref=np.median(idx1[iref])
    idx2_ref=np.median(idx2[iref])
    idx3_ref=np.median(idx3[iref])
    idx4_ref=np.median(idx4[iref])

   
    sigma_idx1=f_plt.perc_84(idx1[iref])-f_plt.perc_16(idx1[iref])
    sigma_idx2=f_plt.perc_84(idx2[iref])-f_plt.perc_16(idx2[iref])
    sigma_idx3=f_plt.perc_84(idx3[iref])-f_plt.perc_16(idx3[iref])
    sigma_idx4=f_plt.perc_84(idx4[iref])-f_plt.perc_16(idx4[iref])

    chi_q1=((idx1_sel-idx1_ref)/sigma_idx1)**2
    chi_q2=((idx2_sel-idx2_ref)/sigma_idx2)**2
    chi_q3=((idx3_sel-idx3_ref)/sigma_idx3)**2
    chi_q4=((idx4_sel-idx4_ref)/sigma_idx4)**2
    
    idx_ref_chi=np.where(par_sel<-0.75)[0]
    
    median_chi_ref1=np.median(chi_q1[idx_ref_chi])
    p84_chi_ref1=f_plt.perc_84(chi_q1[idx_ref_chi])
    p16_chi_ref1=f_plt.perc_16(chi_q1[idx_ref_chi])

    median_chi_ref2=np.median(chi_q2[idx_ref_chi])
    p84_chi_ref2=f_plt.perc_84(chi_q2[idx_ref_chi])
    p16_chi_ref2=f_plt.perc_16(chi_q2[idx_ref_chi])
    
    median_chi_ref3=np.median(chi_q3[idx_ref_chi])
    p84_chi_ref3=f_plt.perc_84(chi_q3[idx_ref_chi])
    p16_chi_ref3=f_plt.perc_16(chi_q3[idx_ref_chi])
    
    median_chi_ref4=np.median(chi_q4[idx_ref_chi])
    p84_chi_ref4=f_plt.perc_84(chi_q4[idx_ref_chi])
    p16_chi_ref4=f_plt.perc_16(chi_q4[idx_ref_chi])
    

    median_chi_idx1=stats.binned_statistic(par_sel, chi_q1, statistic='median', bins=bins)
    median_chi_idx2=stats.binned_statistic(par_sel, chi_q2, statistic='median', bins=bins)
    median_chi_idx3=stats.binned_statistic(par_sel, chi_q3, statistic='median', bins=bins)
    median_chi_idx4=stats.binned_statistic(par_sel, chi_q4, statistic='median', bins=bins)
    
    x=[0.0]*bins
    
    for i in range(0,bins):
        x[i]=(median_chi_idx1.bin_edges[i+1]+median_chi_idx1.bin_edges[i])/2.0

    axs[0,0].scatter(par_sel, chi_q1, s=1)
    axs[0,0].plot(x, median_chi_idx1.statistic, color='red')
    axs[0,0].plot([np.min(par_sel), np.max(par_sel)], [median_chi_ref1, median_chi_ref1], color='orange')
    axs[0,0].plot([np.min(par_sel), np.max(par_sel)], [p84_chi_ref1, p84_chi_ref1],color='#ff028d')
    axs[0,0].plot([np.min(par_sel), np.max(par_sel)],[p16_chi_ref1,p16_chi_ref1], color='#ff028d')
    axs[0,0].set_facecolor('#d8dcd6')
    axs[0,0].set_xlabel(name_par)
    axs[0,0].set_ylabel('chi_q '+name_idx[0])
    axs[0,0].set_ylim(ylim)
    axs[0,0].set_yscale("log")

    axs[0,1].scatter(par_sel, chi_q2, s=1)
    axs[0,1].plot(x, median_chi_idx2.statistic, color='red')
    axs[0,1].plot([np.min(par_sel), np.max(par_sel)], [median_chi_ref2, median_chi_ref2], color='orange')
    axs[0,1].plot([np.min(par_sel), np.max(par_sel)], [p84_chi_ref2, p84_chi_ref2],color='#ff028d')
    axs[0,1].plot([np.min(par_sel), np.max(par_sel)],[p16_chi_ref2,p16_chi_ref2], color='#ff028d')
    axs[0,1].set_facecolor('#d8dcd6')
    axs[0,1].set_xlabel(name_par)
    axs[0,1].set_ylabel('chi_q '+name_idx[1])
    axs[0,1].set_ylim(ylim)
    axs[0,1].set_title(title)
    axs[0,1].set_yscale("log")

    axs[0,2].scatter(par_sel, chi_q3, s=1)
    axs[0,2].plot(x, median_chi_idx3.statistic, color='red')
    axs[0,2].plot([np.min(par_sel), np.max(par_sel)], [median_chi_ref3, median_chi_ref3], color='orange')
    axs[0,2].plot([np.min(par_sel), np.max(par_sel)], [p84_chi_ref3, p84_chi_ref3],color='#ff028d')
    axs[0,2].plot([np.min(par_sel), np.max(par_sel)],[p16_chi_ref3,p16_chi_ref3], color='#ff028d')
    axs[0,2].set_facecolor('#d8dcd6')
    axs[0,2].set_xlabel(name_par)
    axs[0,2].set_ylabel('chi_q '+name_idx[2])
    axs[0,2].set_ylim(ylim)
    axs[0,2].set_yscale("log")
    
    axs[1,0].scatter(par_sel, chi_q4, s=1)
    axs[1,0].plot(x, median_chi_idx4.statistic, color='red')
    axs[1,0].plot([np.min(par_sel), np.max(par_sel)], [median_chi_ref4, median_chi_ref4], color='orange')
    axs[1,0].plot([np.min(par_sel), np.max(par_sel)], [p84_chi_ref4, p84_chi_ref4],color='#ff028d')
    axs[1,0].plot([np.min(par_sel), np.max(par_sel)],[p16_chi_ref4,p16_chi_ref4], color='#ff028d')
    axs[1,0].set_facecolor('#d8dcd6')
    axs[1,0].set_xlabel(name_par)
    axs[1,0].set_ylabel('chi_q '+name_idx[3])
    axs[1,0].set_ylim(ylim)
    axs[1,0].set_yscale("log")
    
    
    return fig
 


    
