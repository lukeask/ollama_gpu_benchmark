formatted_data = []
with open("data", "r") as f:
    data = f.readlines()
    data_list_strings = []
    devices = ""
    get_devices = False
    gather_data = False
    get_model_name = False
    for line in data:
        line = line[:-1]
        if get_model_name:
            model_name = line
            get_model_name = False

        if "Model:" in line:
            get_model_name = True

        if "Time Elapsed" in line:
            get_devices = False

        if get_devices:
            devices += line

        if "Devices:" in line:
            get_devices = True

        if get_devices and not ("Time Elapsed" in line):
            multiple_devices = True

        if line == "":
            gather_data = False
            formatted_data.append([model_name, devices, data_list_strings])
            data_list_strings = []
            devices = ""

        if gather_data:
            data_list_strings.append(line)

        if "-----------------------------------" in line:
            gather_data = True


import matplotlib.pyplot as plt


def plot_data(index_list, plot_title=None, file_name=None):
    if plot_title == None:
        plot_title = "Model: {data[0]}"

    if file_name == None:
        file_name = f"{data[0]}"

    for index in index_list:
        data = formatted_data[index]
        data_list = data[2]

        time_elapsed = [float(datum.split(",")[0][1:]) for datum in data_list]
        context = [int(datum.split(",")[1]) for datum in data_list]
        inference = [int(datum.split(",")[2][:-1]) for datum in data_list]

        inference_per_second = [
            inference[i] / time_elapsed[i] for i in range(len(time_elapsed))
        ]

        x = context
        y = inference_per_second

        plt.scatter(x, y, label=f"{data[1]}")

    plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
    plt.xlabel("Context Characters")
    plt.ylabel("Output Characters per Second")
    plt.title(plot_title)
    footnote_text = f"Model: {formatted_data[index_list[0]][0]}"
    plt.figtext(
        0.95, 0.01, footnote_text, wrap=True, horizontalalignment="center", fontsize=8
    )
    plt.savefig(f"./plots/{file_name}.png", bbox_inches="tight")
    plt.clf()


# all_llama3_indx = [datum for datum in range(len(formatted_data)) if "llama3" in formatted_data[datum][0]]

# all_commandr_indx = [datum for datum in range(len(formatted_data)) if "command-r" in formatted_data[datum][0]]

# plot_data(all_llama3_indx)
# plot_data(all_commandr_indx)


def get_models(formatted_data):
    models = []
    for i in range(len(formatted_data)):
        if formatted_data[i][0] not in models:
            models.append(formatted_data[i][0])

    return models


def cli():
    print("Models:")
    models = get_models(formatted_data)
    for i, model in enumerate(models):
        print(f"{i}:{model}")
    i = input("select a model to plot: ")
    i = int(i)
    model = models[i]
    potential_indicies = [
        datum
        for datum in range(len(formatted_data))
        if model in formatted_data[datum][0]
    ]
    indicies = []
    print("'y' to include, enter to exclude")
    for index in potential_indicies:
        yorn = input(f"include device: {formatted_data[index][1]}?")
        if yorn == "y":
            indicies.append(index)

    title = input("title for plot:")
    if title == "":
        title = None
    file_name = input("file name for plot:")
    if file_name == "":
        file_name = None

    plot_data(indicies, title, file_name)


from scipy.optimize import curve_fit
import numpy as np


def bar_chart(model):
    EVAL_CONTEXT = 4000

    list_to_plot = []

    def _model_func(x, a, b):
        return a * x + b

    indicies = [
        datum
        for datum in range(len(formatted_data))
        if model in formatted_data[datum][0]
    ]

    for index in indicies:
        data = formatted_data[index]
        data_list = data[2]

        time_elapsed = [float(datum.split(",")[0][1:]) for datum in data_list]
        context = [int(datum.split(",")[1]) for datum in data_list]
        inference = [int(datum.split(",")[2][:-1]) for datum in data_list]

        inference_per_second = [
            inference[i] / time_elapsed[i] for i in range(len(time_elapsed))
        ]

        x = context
        y = inference_per_second

        perams, _ = curve_fit(_model_func, x, y)

        bar_height = _model_func(EVAL_CONTEXT, *perams)

        list_to_plot.append([data[1], bar_height])

    list_to_plot.sort(key=lambda x: x[1])
    x_vals = [x[0] for x in list_to_plot]
    y_vals = [x[1] for x in list_to_plot]
    plt.figure(figsize=(12, 6))
    cmap = plt.get_cmap(
        "viridis"
    )  # You can choose other colormaps like 'plasma', 'inferno', 'magma', etc.
    colors = cmap(np.linspace(0, 1, len(x_vals)))
    plt.bar(x_vals, y_vals, color=colors)

    plt.ylabel("Characters per Second", fontsize=16)
    plt.title(f"Model: {model}", fontsize=20)
    plt.xticks(rotation=45, ha="right")
    plt.savefig(f"./plots/{model}_bar.png", bbox_inches="tight")
    # NOTE: Characters per second denotes the number of characters the model can generate in one second given a context of {EVAL_CONTEXT} characters determined via linear regression.'
    plt.clf()


def plot_extended_p40_data():
    data_list_strings = []
    with open("extended_p40", "r") as f:
        data = f.readlines()
        devices = ""
        get_devices = False
        gather_data = False
        get_model_name = False
        for line in data:
            line = line[:-1]
            if get_model_name:
                model_name = line
                get_model_name = False

            if "Model:" in line:
                get_model_name = True

            if "Time Elapsed" in line:
                get_devices = False

            if get_devices:
                devices += line

            if "Devices:" in line:
                get_devices = True

            if get_devices and not ("Time Elapsed" in line):
                multiple_devices = True

            if line == "":
                gather_data = False
                p40_formatted_data.append([model_name, devices, data_list_strings])
                data_list_strings = []
                devices = ""

            if gather_data:
                data_list_strings.append(line)

            if "-----------------------------------" in line:
                gather_data = True

    time_elapsed = [float(datum.split(",")[0][1:]) for datum in data_list_strings]
    context = [int(datum.split(",")[1]) for datum in data_list_strings]
    inference = [int(datum.split(",")[2][:-1]) for datum in data_list_strings]

    inference_per_second = [
        inference[i] / time_elapsed[i] for i in range(len(time_elapsed))
    ]

    x = context
    y = inference_per_second

    plt.scatter(x, y)
    plt.xlabel("Context Characters")
    plt.ylabel("Output Characters per Second")
    plt.title("Command-R Completions in P40 (125W)")

    plt.savefig(f"./plots/p40.png", bbox_inches="tight")
    plt.clf()


# bar_chart("llama3")
# bar_chart("command-r")

plot_extended_p40_data()


# cli()
