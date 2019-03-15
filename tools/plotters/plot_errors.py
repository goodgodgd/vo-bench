import os
import os.path as op
import numpy as np
import pandas as pd
import glob
import matplotlib.backends.backend_qt5agg
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

import settings
from define_paths import *
import evaluation.eval_common as ec


def plot_dataset(dataset, save_path, ate_limit, rpte_limit, rpre_limit):
    matplotlib.rcParams.update({'font.size': 8})
    eval_path = op.join(OUTPUT_PATH, "eval_result")

    if dataset.startswith("euroc"):
        fignum, figsize, plot_layout, categories = get_euroc_params()
    elif dataset.startswith("tum"):
        fignum, figsize, plot_layout, categories = get_tumvi_params()
    else:
        return

    fig = plt.figure(num=fignum, figsize=figsize)
    fig.set_size_inches(figsize[0], figsize[1], forward=True)
    draw_ate(fig, eval_path, dataset, categories, plot_layout, ate_limit)
    save_name = op.join(save_path, f"{dataset}_ate.png")
    show_and_save(save_name)

    draw_rpe(fig, eval_path, dataset, plot_layout, rpte_limit, rpre_limit)
    save_name = op.join(save_path, f"{dataset}_rpe.png")
    show_and_save(save_name)


def get_euroc_params():
    fignum = 0
    figsize = (8, 6)
    plot_layout = 22
    categories = {"easy": ["MH01", "MH02", "V101", "V201"],
                  "medium": ["MH03", "V102", "V202"],
                  "diffcult": ["MH04", "MH05", "V103", "V203"]}
    return fignum, figsize, plot_layout, categories


def get_tumvi_params():
    fignum = 0
    figsize = (8, 9)
    plot_layout = 32
    tumvi_gtpath = op.join(OUTPUT_PATH, "ground_truth", "tum_vi/")
    envnames = ["corridor", "magistrale", "outdoors", "room", "slides"]
    categories = {}
    for env in envnames:
        files = glob.glob(tumvi_gtpath + env + "*")
        sequences = []
        for file in files:
            seqname = file.replace(tumvi_gtpath, "").replace(".csv", "")
            sequences.append(seqname)
        sequences.sort()
        categories[env] = sequences
    return fignum, figsize, plot_layout, categories


def draw_ate(fig, eval_path, dataset, categories, plot_layout, ate_limit):
    filename = op.join(eval_path, "ate", dataset, "collect_te_mean.csv")
    errors = pd.read_csv(filename, encoding="utf-8", index_col=False)
    errors = errors.drop(columns="Unnamed: 0")
    ax = fig.add_subplot(plot_layout*10 + 1)
    draw_error_plot(ax, errors, "MATE_total", ate_limit)

    for i, (tag, sequences) in enumerate(categories.items()):
        ax = fig.add_subplot(plot_layout*10 + i + 2)
        env_errors = errors[errors["sequence"].isin(sequences)]
        draw_error_plot(ax, env_errors, "MATE_" + tag, ate_limit)


def draw_rpe(fig, eval_path, dataset, plot_layout, rpte_limit, rpre_limit):
    filename = op.join(eval_path, "rpe", dataset, "collect_te_mean.csv")
    load_and_draw(fig, filename, plot_layout*10 + 1, rpte_limit, "RPTE_mean")

    filename = op.join(eval_path, "rpe", dataset, "collect_re_mean.csv")
    load_and_draw(fig, filename, plot_layout*10 + 2, rpre_limit, "RPRE_mean")

    filename = op.join(eval_path, "rpe", dataset, "collect_te_max.csv")
    load_and_draw(fig, filename, plot_layout*10 + 3, rpte_limit, "RPTE_max")

    filename = op.join(eval_path, "rpe", dataset, "collect_re_max.csv")
    load_and_draw(fig, filename, plot_layout*10 + 4, rpre_limit, "RPRE_max")


def load_and_draw(fig, filename, subplot_num, rpte_limit, vertical_tag):
    errors = pd.read_csv(filename, encoding="utf-8", index_col=False)
    errors = errors.drop(columns="Unnamed: 0")
    ax = fig.add_subplot(subplot_num)
    draw_error_plot(ax, errors, vertical_tag, rpte_limit)


def draw_error_plot(ax, data, ylabel, ylimit):
    colormap = matplotlib.cm.get_cmap('tab20', len(ec.ALGORITHMS))
    styles = ['-', '--', '-.', ':', '.', '+', 'x', '1']
    for i, column in enumerate(ec.ALGORITHMS):
        if column not in data.columns:
            continue
        coldata = data[column].values
        coldata = np.sort(coldata)
        coldata = coldata[~np.isnan(coldata)]
        linestyle = styles[i % len(styles)]
        ax.plot(list(range(len(coldata))), coldata,
                linestyle, color=colormap(i), label=column)

    ax.legend()
    ax.set_xlabel('runs')
    ax.set_ylabel(ylabel)
    x1, x2, y1, y2 = plt.axis()
    plt.axis([x1, x2, 0, ylimit])


def show_and_save(savename):
    plt.pause(0.1)
    plt.savefig(savename, dpi=100)
    print("savename:", savename)
    plt.waitforbuttonpress()
    plt.clf()


def main():
    assert op.isdir(OUTPUT_PATH)
    savepath = op.join(OUTPUT_PATH, "eval_result", "figures")
    os.makedirs(savepath, exist_ok=True)
    plot_dataset("euroc_mav", savepath, 2, 2, 0.4)
    plot_dataset("tum_vi", savepath, 5, 2, 0.4)
    # plt.show(block=True)


if __name__ == "__main__":
    main()
