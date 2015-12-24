import os

# traverse root directory, and list directories as dirs and files as files
def enumerate_datasets(path):
    retval = []
    for root, dirs, files in os.walk(path):  
        for file in files:
            if file.endswith('.csv'):
                dataset_path = os.path.join(root, file)
                retval.append(dataset_path)

    return retval
