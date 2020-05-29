import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from sklearn.decomposition import PCA
from file_handling import *
from selection import *


def main():
    print("Program: PCA")
    print("Release: 0.2.0")
    print("Date: 2020-05-29")
    print("Author: Brian Neely")
    print()
    print()
    print("This program reads a csv file and performs dimensionality reduction using PCA.")
    print()
    print()

    # Hide Tkinter GUI
    Tk().withdraw()

    # Find input file
    file_in = select_file_in()

    # Set output file
    file_out = select_file_out_csv(file_in)

    # Ask for delimination
    delimination = input("Enter Deliminator: ")

    # Open input csv using the unknown encoder function
    data = open_unknown_csv(file_in, delimination)

    # Ask whether to use all columns, exclude certain columns, or select certain columns
    column_selection_type_input = column_selection_type(0)

    # Get list of columns from PCA
    columns = column_list(data, column_selection_type_input)

    # Run PCA
    data_out, components_df = bn_pca(data, columns)

    # Write output file
    print("Writing output file...")
    data_out.to_csv(file_out, index=False)
    print("Output file wrote!")

    # Ask to export components
    if y_n_question("Write PCA Component Loadings: "):
        # Set components output file
        components_file_out = select_file_out_csv(file_in)

        # Write components CSV
        components_df.to_csv(components_file_out)


def bn_pca(data, pca_columns):
    # Get list of indices for complete data
    data_complete_index = data.dropna(subset=pca_columns).index

    # Drop na from original dataset
    data_na = data[~data.index.isin(data_complete_index)]

    # Get complete data
    data = data[data.index.isin(data_complete_index)]

    # Set input data
    x = data[pca_columns]

    # Set PCA factors
    pca = PCA()

    # Run PCA
    pca_results = pca.fit_transform(x)

    # Report Explained Variance Ratio
    explained_variance = pca.explained_variance_ratio_
    print("PCA explanation by factor")
    total_explained = 0
    for index, i in enumerate(explained_variance):
        total_explained = total_explained + i
        print("Factor " + str(index + 1) + ": " + str(round(i * 100, 1)) + "% - Cumulative: " + str(round(total_explained * 100, 1)) + "%")
    print()

    # Ask for number of factors to retain
    number_of_factors = int(input("How many factors to retain: "))

    # Create header list for the pca factors
    pca_column_header = list()
    for index, i in enumerate(pca.components_):
        pca_column_header.append("PCA_Factor_" + str(index))

    # Transform numpy array to data frame
    pca_factors = pd.DataFrame(data = pca_results, columns=pca_column_header)

    # Find unused columns in original dataset
    unused_columns = list()
    for i in list(data.columns.values):
        if i not in pca_columns:
            unused_columns.append(i)

    # If number of factors is greater than number of actual factors, lower
    if number_of_factors >= len(pca_column_header):
        number_of_factors = int(len(pca_column_header))

    # Reindex Data
    data_out = data[unused_columns]
    data_out.reset_index(inplace=True)

    # Concatenate unused columns to PCA results
    for i in range(0, number_of_factors):
        data_out["PCA_Factor_" + str(i)] = pca_factors["PCA_Factor_" + str(i)]

    # Reindex data_out to original index
    data_out = data_out.set_index('index')

    # Ask if the previous factors should be retained
    retain_pca_input = y_n_question("Retain columns used for PCA creation?: ")

    # If desired, concatenate pca data onto output file
    if retain_pca_input:
        data_out = pd.concat([data_out, data[pca_columns]], axis=1)

    # Union back null data making sure it exists in both datasets
    columns_to_append_lst = list()
    for i in list(data_out):
        for j in list(data_na):
            if i == j:
                columns_to_append_lst.append(i)

    # Union back null data
    data_out = data_out.append(data_na[columns_to_append_lst], sort=False).sort_index()

    # Get PCA Components
    components_df = pd.DataFrame(data=pca.components_, columns=pca_columns, index=pca_column_header)[:number_of_factors]

    # Return completed PCA
    return data_out, components_df


def column_list(data, column_selection_type_in):
    print("Reading Column List")
    headers = list(data.columns.values)
    if column_selection_type_in == 1:
        while True:
            try:
                print("Select columns to exclude from PCA...")
                for j, i in enumerate(headers):
                    print(str(j) + ": to exclude column [" + str(i) + "]")

                # Ask for index list
                column_index_list_string = input("Enter selections separated by spaces: ")

                # Check if input was empty
                if not column_index_list_string:
                    print("No selection was used, all columns will be used.")

                # Split string based on spaces
                column_index_list = column_index_list_string.split()

                # Get column names list
                column_name_list_excld = list()
                for i in column_index_list:
                    column_name_list_excld.append(headers[int(i)])

                column_name_list = list()
                for i in headers:
                    if i not in column_name_list_excld:
                        column_name_list.append(i)

                # Check if columns are valid for PCA
                try:
                    invalid_selection = 0
                    # Test open every column and convert to number
                    for i in column_name_list:
                        test_column = i
                        for j in data[i]:
                            float(j)
                except:
                    print(test_column + ' is invalid for PCA, please select a new column list.')
                    invalid_selection = 1
                    continue

                if invalid_selection == 1:
                    break

            except ValueError:
                print("An invalid column input was detected, please try again.")
                continue

            else:
                break
    elif column_selection_type_in == 2:
        while True:
            try:
                print("Select columns to include into the PCA...")
                for j, i in enumerate(headers):
                    print(str(j) + ": to include column [" + str(i) + "]")

                # Ask for index list
                column_index_list_string = input("Enter selections separated by spaces: ")

                # Check if input was empty
                while not column_index_list_string:
                    column_index_list_string = input("Input was blank, please select columns to include.")

                # Split string based on spaces
                column_index_list = column_index_list_string.split()

                # Check to make sure at least to columns were selected
                while len(column_index_list) < 2:
                    column_index_list_string = input("Only 1 column was selected for PCA, a minimum of 2 is required.")
                    column_index_list = column_index_list_string.split()

                # Get column names list
                column_name_list = list()
                for i in column_index_list:
                    column_name_list.append(headers[int(i)])

                # Check if columns are valid for PCA
                try:
                    invalid_selection = 0
                    # Test open every column and convert to number
                    for i in column_name_list:
                        test_column = i
                        for j in data[i]:
                            float(j)
                except:
                    print(test_column + ' is invalid for PCA, please select a new column list.')
                    invalid_selection = 1
                    continue

                if invalid_selection == 1:
                    break

            except:
                print("An invalid column input was detected, please try again.")
                continue

            else:
                break

    else:
        columns = list(data.columns.values)

        # Check if columns are valid for PCA
        try:
            invalid_selection = 0
            # Test open every column and convert to number
            for i in columns:
                test_column = i
                for j in data[i]:
                    float(j)
        except ValueError:
            print(test_column + ' is invalid for PCA.')
            invalid_selection = 1

        if invalid_selection == 1:
            print("Due to invalid columns for PCA, please change your column selection type.")
            print()
            new_selection = column_selection_type(int(1))
            print("New Selection")
            column_name_list = column_list(data, new_selection)

    # Return column_name list to original function
    return column_name_list


def column_selection_type(start_index: int):
    # Ask whether to use all columns, exclude certain columns, or select certain columns
    selection_type = ["Enter 0 to use all columns in dataset.",
                      "Enter 1 to use all columns excluding selected columns.",
                      "Enter 2 to select columns for PCA."]

    while True:
        try:
            for index, i in enumerate(selection_type):
                if start_index <= index:
                    print(i)
            index_selection = int(input("Enter Selection: "))
            selection_type[index_selection]
            if index_selection < start_index:
                int("Error")
        except (ValueError, IndexError):
            print("Input must be integer between " + str(start_index) + " and " + str(len(selection_type) - 1))
            continue
        else:
            break
    return index_selection


if __name__ == '__main__':
    main()
